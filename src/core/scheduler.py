"""
scheduler.py – Logic lõi cho hàng đợi sạc & ưu tiên (Smart Charging Scheduler)
Smart E-Mobility Hub – ĐHQG-HCM

Thuật toán ưu tiên chuẩn hóa (PLAN.md 4.5):
  Score = 0.5 * (100 - SoC) + 100 * I(SoC < 20) + 60 * I(has_booking) + 30 * I(SoC < 50)
  Tie-breaking: (-Score, requested_at, vehicle_id)
  Power Allocation: sum(active_ports * port_kw) <= HUB_POWER_CAP_KW (150 kW)
  Lifecycle: WAITING -> CHARGING -> 90% Alert -> 100% Completed -> GRACE_PERIOD (15 min) -> OVERSTAY
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import datetime
import uuid
from core.policies import get_kwh_rate

from core.policies import (
    HUB_POWER_CAP_KW,
    DEFAULT_PORT_CHARGING_KW,
    OVERSTAY_GRACE_MINUTES,
    OVERSTAY_RATE_PER_BLOCK_VND
)
from core.state import PortStatus, bump_state_version

SOC_CRITICAL = 20.0   # % pin nguy hiểm
SOC_MEDIUM   = 50.0   # % pin trung bình

@dataclass
class ChargingRequest:
    """Một yêu cầu sạc trong hàng đợi."""
    vehicle_id: str
    hub_id: str
    battery_soc: float                          # % pin hiện tại (0 - 100)
    has_student_booking: bool = False            # có booking SV hay không
    requested_at: datetime.datetime = field(
        default_factory=datetime.datetime.now
    )
    priority_score: float = 0.0                 # Điểm ưu tiên
    ownership: str = "SHARED"                   # SHARED hoặc PERSONAL
    owner_id: Optional[str] = None
    target_soc: float = 100.0                   # Ngưỡng pin mong muốn
    port_kw: float = DEFAULT_PORT_CHARGING_KW   # Công suất sạc dự kiến (kW)

    def __post_init__(self):
        if self.priority_score == 0.0:
            self.priority_score = SmartChargingScheduler.calculate_priority(self)

    def __repr__(self) -> str:
        return (
            f"ChargingRequest(vehicle={self.vehicle_id}, "
            f"soc={self.battery_soc}%, priority={self.priority_score:.1f})"
        )

@dataclass
class ChargingSession:
    """Một phiên sạc đang hoạt động hoặc hoàn thành tại cổng."""
    session_id: str
    vehicle_id: str
    hub_id: str
    port_id: str
    port_kw: float
    current_soc: float
    target_soc: float = 100.0
    status: str = "CHARGING"                    # CHARGING, GRACE_PERIOD, OVERSTAY, COMPLETED
    started_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    completed_at: Optional[datetime.datetime] = None
    alert_90_sent: bool = False
    grace_deadline: Optional[datetime.datetime] = None
    overstay_minutes: int = 0
    overstay_fee: int = 0
    energy_delivered_kwh: float = 0.0
    energy_cost_vnd: float = 0.0

class SmartChargingScheduler:
    """
    Bộ lập lịch sạc thông minh dựa trên ưu tiên và giới hạn công suất trần trạm (150 kW).
    """

    def __init__(self, cap_kw: float = HUB_POWER_CAP_KW) -> None:
        self.cap_kw = cap_kw
        self._queue: List[ChargingRequest] = []
        self._active_sessions: Dict[str, ChargingSession] = {} # session_id -> session

    @staticmethod
    def calculate_priority(request: ChargingRequest) -> float:
        """
        Công thức chuẩn hóa theo PLAN.md:
        0.5 * (100 - SoC) + 100 * I(SoC < 20) + 60 * I(has_booking) + 30 * I(SoC < 50)
        """
        score = 0.0
        soc = float(request.battery_soc)

        if soc < SOC_CRITICAL:
            score += 100.0
        if request.has_student_booking:
            score += 60.0
        if soc < SOC_MEDIUM:
            score += 30.0
        score += (100.0 - soc) * 0.5

        return score

    def add_request(self, request: ChargingRequest) -> None:
        """Thêm yêu cầu sạc, loại bỏ trùng lặp xe."""
        # Deduplicate
        self._queue = [r for r in self._queue if r.vehicle_id != request.vehicle_id]
        request.priority_score = self.calculate_priority(request)
        self._queue.append(request)

    def remove_request(self, vehicle_id: str) -> Optional[ChargingRequest]:
        """Xóa yêu cầu sạc khỏi hàng đợi."""
        for i, req in enumerate(self._queue):
            if req.vehicle_id == vehicle_id:
                return self._queue.pop(i)
        return None

    def get_sorted_queue(self) -> List[ChargingRequest]:
        """
        Sắp xếp theo thứ tự ưu tiên:
        1. Điểm ưu tiên giảm dần
        2. Thời gian yêu cầu tăng dần (FIFO)
        3. Mã xe tăng dần (Deterministic tie-break)
        """
        return sorted(
            self._queue,
            key=lambda r: (-r.priority_score, r.requested_at, r.vehicle_id)
        )

    def allocate_ports(
        self,
        hub_id: str,
        available_port_count: int,
        current_active_kw: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Phân bổ cổng sạc cho các yêu cầu trong hàng đợi tuân thủ Hub Cap.
        Tự động tính toán công suất của các phiên sạc đang hoạt động tại Hub.
        """
        allocations = []
        sorted_q = [r for r in self.get_sorted_queue() if r.hub_id == hub_id]
        remaining_ports = available_port_count
        
        # Tự động tính tổng công suất đang chạy tại Hub
        existing_power = sum(
            s.port_kw for s in self._active_sessions.values()
            if s.hub_id == hub_id and s.status in ["CHARGING"]
        )
        power_usage = existing_power + current_active_kw

        for req in sorted_q:
            if remaining_ports <= 0:
                break
            if power_usage + req.port_kw > self.cap_kw:
                # Không đủ công suất trần
                continue

            session_id = f"CHG-{uuid.uuid4().hex[:6].upper()}"
            used_ports = {session.port_id for session in self._active_sessions.values() if session.hub_id == hub_id}
            port_number = 1
            while f"PORT-{hub_id[-3:]}-{port_number}" in used_ports:
                port_number += 1
            port_id = f"PORT-{hub_id[-3:]}-{port_number}"
            sess = ChargingSession(
                session_id=session_id,
                vehicle_id=req.vehicle_id,
                hub_id=hub_id,
                port_id=port_id,
                port_kw=req.port_kw,
                current_soc=req.battery_soc,
                target_soc=req.target_soc
            )
            self._active_sessions[session_id] = sess
            allocations.append({
                "session_id": session_id,
                "vehicle_id": req.vehicle_id,
                "port_id": port_id,
                "allocated_kw": req.port_kw
            })
            self.remove_request(req.vehicle_id)
            remaining_ports -= 1
            power_usage += req.port_kw

        return allocations

    def advance_simulation_tick(self, minutes: int = 15, sim_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Tiến hành 1 bước mô phỏng thời gian cho tất cả phiên sạc:
        - Tăng pin theo công suất
        - Cảnh báo 90%
        - Hoàn tất 100% và kích hoạt Grace Period 15 phút
        - Quá 15 phút chuyển sang OVERSTAY và tính phạt
        """
        events = []
        for sess in list(self._active_sessions.values()):
            if sess.status == "CHARGING":
                # Nạp năng lượng: e = P * t (kWh)
                hrs = minutes / 60.0
                kwh_added = min(sess.port_kw * hrs, max(0, sess.target_soc - sess.current_soc) / 100 * 3.5)
                start = datetime.datetime.fromisoformat(sim_time) if sim_time else sess.started_at
                remaining = kwh_added
                for minute in range(minutes):
                    energy = min(remaining, sess.port_kw / 60)
                    sess.energy_cost_vnd += energy * get_kwh_rate((start + datetime.timedelta(minutes=minute)).time())
                    remaining -= energy
                sess.started_at = start + datetime.timedelta(minutes=minutes)
                sess.energy_delivered_kwh += kwh_added
                # Giả định xe pin 3.5 kWh: % tăng = kwh_added / 3.5 * 100
                soc_added = (kwh_added / 3.5) * 100.0
                sess.current_soc = min(sess.target_soc, sess.current_soc + soc_added)

                # Kiểm tra cảnh báo 90%
                if sess.current_soc >= 90.0 and not sess.alert_90_sent and sess.current_soc < 100.0:
                    sess.alert_90_sent = True
                    events.append({
                        "type": "ALERT_90",
                        "session_id": sess.session_id,
                        "vehicle_id": sess.vehicle_id,
                        "message": f"Xe {sess.vehicle_id} đã đạt {sess.current_soc:.1f}% pin! Vui lòng chuẩn bị nhận xe."
                    })

                # Kiểm tra hoàn tất 100%
                if sess.current_soc >= 100.0:
                    sess.status = "GRACE_PERIOD"
                    sess.completed_at = datetime.datetime.now()
                    sess.grace_deadline = sess.completed_at + datetime.timedelta(minutes=OVERSTAY_GRACE_MINUTES)
                    events.append({
                        "type": "COMPLETED_100",
                        "session_id": sess.session_id,
                        "vehicle_id": sess.vehicle_id,
                        "message": f"Xe {sess.vehicle_id} đã sạc đầy 100%! Thời gian ân hạn miễn phí: {OVERSTAY_GRACE_MINUTES} phút."
                    })

            elif sess.status in ["GRACE_PERIOD", "OVERSTAY"]:
                sess.overstay_minutes += minutes
                if sess.overstay_minutes > OVERSTAY_GRACE_MINUTES:
                    sess.status = "OVERSTAY"
                    billable = sess.overstay_minutes - OVERSTAY_GRACE_MINUTES
                    blocks = (billable + 14) // 15
                    sess.overstay_fee = blocks * OVERSTAY_RATE_PER_BLOCK_VND
                    events.append({
                        "type": "OVERSTAY_PENALTY",
                        "session_id": sess.session_id,
                        "vehicle_id": sess.vehicle_id,
                        "message": f"Xe {sess.vehicle_id} đã quá hạn rút sạc ({sess.overstay_minutes} phút). Phí overstay: {sess.overstay_fee:,.0f} VNĐ."
                    })

        return events

    def unplug_vehicle(self, session_id: str) -> Optional[ChargingSession]:
        """Rút sạc phương tiện, giải phóng cổng sạc."""
        if session_id in self._active_sessions:
            sess = self._active_sessions.pop(session_id)
            sess.status = "COMPLETED"
            return sess
        return None

    @property
    def queue_length(self) -> int:
        return len(self._queue)

    def get_queue_as_dicts(self) -> list:
        return [
            {
                "vehicle_id": r.vehicle_id,
                "hub_id": r.hub_id,
                "battery_soc": r.battery_soc,
                "has_booking": r.has_student_booking,
                "priority_score": r.priority_score,
                "requested_at": r.requested_at.strftime("%H:%M:%S"),
            }
            for r in self.get_sorted_queue()
        ]


def allocate_hub_ports(state: Dict[str, Any], hub_id: str) -> List[Dict[str, Any]]:
    """Allocate queued requests and update the operational hub and reservations together."""
    hub = next((h for h in state.get("hubs", []) if h.get("hub_id") == hub_id), None)
    scheduler = state.get("charging_scheduler")
    if not hub or not scheduler:
        return []
    allocations = scheduler.allocate_ports(hub_id, hub["charging_ports"].get("available", 0))
    if allocations:
        hub["charging_ports"]["available"] -= len(allocations)
        for allocation in allocations:
            vehicle_id = allocation["vehicle_id"]
            vehicle = next((v for v in hub.get("current_vehicles", []) if v.get("vehicle_id") == vehicle_id), None)
            if vehicle:
                vehicle["status"] = "CHARGING"
            reservation = next((r for r in state.get("personal_reservations", []) if r.get("ev_id") == vehicle_id and r.get("status") == "CHECKED_IN"), None)
            if reservation:
                reservation.update(charging_port_allocated=True, charging_ever_allocated=True, charging_session_id=allocation["session_id"])
        bump_state_version(state)
    return allocations


def release_charging_session(state, session_id):
    """Release once and preserve personal billing across unplug, failure and checkout."""
    scheduler = state.get("charging_scheduler")
    session = scheduler.unplug_vehicle(session_id) if scheduler else None
    if not session:
        return None
    reservation = next((r for r in state.get("personal_reservations", [])
                        if r.get("charging_session_id") == session_id), None)
    if reservation:
        reservation["measured_energy_fee"] = reservation.get("measured_energy_fee", 0) + session.energy_cost_vnd
        reservation["delivered_kwh"] = reservation.get("delivered_kwh", 0) + session.energy_delivered_kwh
        reservation["accrued_overstay_fee"] = reservation.get("accrued_overstay_fee", 0) + session.overstay_fee
        reservation["accrued_overstay_minutes"] = reservation.get("accrued_overstay_minutes", 0) + session.overstay_minutes
        reservation["charging_port_allocated"] = False
        reservation["charging_session_id"] = None
    hub = next((h for h in state["hubs"] if h["hub_id"] == session.hub_id), None)
    if hub:
        ports = hub["charging_ports"]
        ports["available"] = min(ports["total"] - ports.get("offline", 0), ports["available"] + 1)
    bump_state_version(state)
    return session


def apply_hub_snapshot(state, hubs):
    """Commit a simulated hub snapshot and interrupt affected live charging sessions."""
    scheduler = state.get("charging_scheduler")
    if scheduler:
        for hub in hubs:
            old = next(h for h in state["hubs"] if h["hub_id"] == hub["hub_id"])
            newly_offline = max(0, hub["charging_ports"].get("offline", 0) -
                                old["charging_ports"].get("offline", 0))
            sessions = [s for s in scheduler._active_sessions.values() if s.hub_id == hub["hub_id"]]
            for session in sessions[:newly_offline]:
                release_charging_session(state, session.session_id)
                vehicle = next((v for v in hub["current_vehicles"] if v["vehicle_id"] == session.vehicle_id), None)
                if vehicle:
                    vehicle["status"] = "WAITING"
                    vehicle["battery_soc"] = session.current_soc
                    scheduler.add_request(ChargingRequest(vehicle_id=session.vehicle_id,
                        hub_id=hub["hub_id"], battery_soc=session.current_soc,
                        ownership=vehicle.get("ownership", "SHARED"), owner_id=vehicle.get("owner_id")))
    state["hubs"] = hubs
    bump_state_version(state)
