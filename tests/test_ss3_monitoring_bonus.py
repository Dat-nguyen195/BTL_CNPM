"""
Test suite bonus cho Submission 3 — Phân hệ SS3 (Hub Monitoring & Alert)
Tác giả: Phạm Tiến Đạt — MSSV: 2410724 (TV3)
Bao phủ: TC-SS3-BND-01, TC-SS3-INV-01, TC-SS3-REV-01, TC-SS3-LCK-01, TC-SS3-IOT-01
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, Optional, TypeVar
import pytest

T = TypeVar("T")


# =====================================================================
# 1. ĐỊNH NGHĨA KIỂU DỮ LIỆU & LỚP THIẾT KẾ MỤC TIÊU SS3 (TV3 SỞ HỮU)
# =====================================================================

class OccupancyLevel(str, Enum):
    NORMAL = "NORMAL"       # < 70%
    WARNING = "WARNING"     # 70% - < 85%
    CRITICAL = "CRITICAL"   # 85% - < 100%
    FULL = "FULL"           # >= 100%


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AlertType(str, Enum):
    OCCUPANCY_THRESHOLD = "OCCUPANCY_THRESHOLD"
    IOT_SENSOR_TIMEOUT = "IOT_SENSOR_TIMEOUT"
    IOT_HARDWARE_FAULT = "IOT_HARDWARE_FAULT"
    LOCK_SYNC_FAILURE = "LOCK_SYNC_FAILURE"


@dataclass
class OperationResult(Generic[T]):
    ok: bool
    data: Optional[T] = None
    error_code: Optional[str] = None
    message: str = ""
    state_version: int = 0


@dataclass
class Hub:
    hub_id: str
    name: str
    latitude: float
    longitude: float
    capacity: int
    available_slots: int
    present_vehicles_count: int
    incoming_reserved_count: int = 0
    background_load_count: int = 0
    total_ports: int = 10
    active_ports_count: int = 0
    max_power_kw: float = 150.0
    current_load_kw: float = 0.0
    is_locked: bool = False
    iot_online: bool = True

    def calculate_occupancy_rate(self) -> float:
        if self.capacity <= 0:
            raise ValueError("INVALID_INPUT: Hub capacity must be positive")
        occupied = self.capacity - self.available_slots
        return round((occupied / self.capacity) * 100.0, 4)

    def get_occupancy_level(
        self, warning_pct: float = 70.0, critical_pct: float = 85.0, full_pct: float = 100.0
    ) -> OccupancyLevel:
        rate = self.calculate_occupancy_rate()
        if rate >= full_pct or self.available_slots == 0:
            return OccupancyLevel.FULL
        if rate >= critical_pct:
            return OccupancyLevel.CRITICAL
        if rate >= warning_pct:
            return OccupancyLevel.WARNING
        return OccupancyLevel.NORMAL

    def validate_capacity_invariant(self) -> bool:
        if any(
            x < 0
            for x in (
                self.available_slots,
                self.present_vehicles_count,
                self.incoming_reserved_count,
                self.background_load_count,
            )
        ):
            return False
        total = (
            self.available_slots
            + self.present_vehicles_count
            + self.incoming_reserved_count
            + self.background_load_count
        )
        return total == self.capacity


@dataclass
class OccupancySnapshot:
    snapshot_id: str
    hub_id: str
    captured_at: datetime
    capacity: int
    present_vehicles: int
    incoming_reserved: int
    background_load: int
    available_slots: int
    occupancy_rate_pct: float
    occupancy_level: OccupancyLevel
    active_ports: int
    total_ports: int
    port_utilization_pct: float
    current_power_kw: float
    max_power_kw: float
    is_locked: bool


@dataclass
class RevenueReport:
    report_id: str
    generated_at: datetime
    hub_id: Optional[str] = None
    settled_rental_fee_vnd: int = 0
    settled_parking_fee_vnd: int = 0
    settled_charging_fee_vnd: int = 0
    settled_penalty_fee_vnd: int = 0
    total_realized_revenue_vnd: int = 0
    held_deposit_vnd: int = 0
    refunded_amount_vnd: int = 0
    outstanding_debt_vnd: int = 0


@dataclass
class Alert:
    alert_id: str
    hub_id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    created_at: datetime
    occupancy_level: Optional[OccupancyLevel] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    maintenance_plan: Optional[str] = None
    is_resolved: bool = False
    dispatch_suggested: bool = False

    def acknowledge(self, user_id: str, now: datetime) -> bool:
        if not user_id or not user_id.strip():
            return False
        if self.acknowledged_by is not None:
            return False
        self.acknowledged_by = user_id
        self.acknowledged_at = now
        return True


@dataclass
class NetworkSnapshot:
    captured_at: datetime
    state_version: int
    total_active_vehicles: int
    network_occupancy_pct: float
    is_using_cached_data: bool
    occupancy_snapshots: list[OccupancySnapshot] = field(default_factory=list)
    revenue_summary: Optional[RevenueReport] = None
    active_alerts: list[Alert] = field(default_factory=list)


class MonitoringService:
    def __init__(self, session_state: dict[str, Any]):
        self.state = session_state
        self.warning_threshold_pct: float = 70.0
        self.critical_threshold_pct: float = 85.0
        self.full_threshold_pct: float = 100.0
        self._processed_ops: dict[str, bool] = {}

    def _now(self) -> datetime:
        return self.state.get("sim_time", datetime(2026, 10, 28, 10, 0, 0))

    def calculate_hub_occupancy(self, hub_id: str) -> OperationResult[OccupancySnapshot]:
        hubs: dict[str, Hub] = self.state.get("hubs", {})
        if hub_id not in hubs:
            return OperationResult(
                ok=False,
                error_code="NOT_FOUND",
                message=f"Hub {hub_id} does not exist",
                state_version=self.state.get("state_version", 0),
            )
        hub = hubs[hub_id]
        if not hub.validate_capacity_invariant():
            return OperationResult(
                ok=False,
                error_code="INVALID_STATE",
                message=f"Capacity invariant violated at {hub_id}",
                state_version=self.state.get("state_version", 0),
            )
        rate = hub.calculate_occupancy_rate()
        level = hub.get_occupancy_level(
            self.warning_threshold_pct, self.critical_threshold_pct, self.full_threshold_pct
        )
        port_util = round((hub.active_ports_count / hub.total_ports) * 100.0, 2) if hub.total_ports > 0 else 0.0
        snap = OccupancySnapshot(
            snapshot_id=f"SNAP_{hub_id}_{self.state.get('state_version', 0)}",
            hub_id=hub_id,
            captured_at=self._now(),
            capacity=hub.capacity,
            present_vehicles=hub.present_vehicles_count,
            incoming_reserved=hub.incoming_reserved_count,
            background_load=hub.background_load_count,
            available_slots=hub.available_slots,
            occupancy_rate_pct=rate,
            occupancy_level=level,
            active_ports=hub.active_ports_count,
            total_ports=hub.total_ports,
            port_utilization_pct=port_util,
            current_power_kw=hub.current_load_kw,
            max_power_kw=hub.max_power_kw,
            is_locked=hub.is_locked,
        )
        return OperationResult(
            ok=True,
            data=snap,
            message="OK",
            state_version=self.state.get("state_version", 0),
        )

    def generate_revenue_report(self, hub_id: Optional[str] = None) -> OperationResult[RevenueReport]:
        hubs: dict[str, Hub] = self.state.get("hubs", {})
        if hub_id is not None and hub_id not in hubs:
            return OperationResult(
                ok=False,
                error_code="NOT_FOUND",
                message=f"Hub {hub_id} not found",
                state_version=self.state.get("state_version", 0),
            )
        ledger = self.state.get("ledger", [])
        rental = sum(item["paid_vnd"] for item in ledger if item["kind"] == "RENTAL" and (not hub_id or item.get("hub_id") == hub_id))
        parking = sum(item["paid_vnd"] for item in ledger if item["kind"] == "PARKING" and (not hub_id or item.get("hub_id") == hub_id))
        charging = sum(item["paid_vnd"] for item in ledger if item["kind"] == "CHARGING" and (not hub_id or item.get("hub_id") == hub_id))
        penalty = sum(item["paid_vnd"] for item in ledger if item["kind"] == "PENALTY" and (not hub_id or item.get("hub_id") == hub_id))
        realized = rental + parking + charging + penalty

        held_deposit = sum(item["held_vnd"] for item in self.state.get("deposits", []) if item["status"] == "HELD")
        refunded = sum(item["released_vnd"] for item in self.state.get("deposits", []) if item["status"] == "RELEASED")
        debt = sum(item.get("debt_vnd", 0) for item in ledger)

        report = RevenueReport(
            report_id=f"REV_{self.state.get('state_version', 0)}",
            generated_at=self._now(),
            hub_id=hub_id,
            settled_rental_fee_vnd=rental,
            settled_parking_fee_vnd=parking,
            settled_charging_fee_vnd=charging,
            settled_penalty_fee_vnd=penalty,
            total_realized_revenue_vnd=realized,
            held_deposit_vnd=held_deposit,
            refunded_amount_vnd=refunded,
            outstanding_debt_vnd=debt,
        )
        return OperationResult(ok=True, data=report, state_version=self.state.get("state_version", 0))

    def sync_hub_booking_lock(self, hub_id: str, lock_state: bool, operation_key: str) -> OperationResult[bool]:
        hubs: dict[str, Hub] = self.state.get("hubs", {})
        if hub_id not in hubs:
            return OperationResult(ok=False, error_code="NOT_FOUND", message="Hub not found")
        if operation_key in self._processed_ops:
            if self._processed_ops[operation_key] != lock_state:
                return OperationResult(ok=False, error_code="CONFLICTING_OPERATION", message="Conflicting lock state for key")
            return OperationResult(
                ok=True, data=hubs[hub_id].is_locked, message="Idempotent replay", state_version=self.state.get("state_version", 0)
            )
        if self.state.get("simulate_lock_sync_failure", False):
            return OperationResult(
                ok=False, error_code="STALE_STATE", message="Session sync conflict with SS1/SS2", state_version=self.state.get("state_version", 0)
            )
        hubs[hub_id].is_locked = lock_state
        self.state["state_version"] = self.state.get("state_version", 0) + 1
        self._processed_ops[operation_key] = lock_state
        return OperationResult(ok=True, data=lock_state, state_version=self.state["state_version"])

    def evaluate_hub_alerts(self, hub_id: str) -> OperationResult[list[Alert]]:
        hubs: dict[str, Hub] = self.state.get("hubs", {})
        if hub_id not in hubs:
            return OperationResult(ok=False, error_code="NOT_FOUND", message="Hub not found")
        hub = hubs[hub_id]
        level = hub.get_occupancy_level(
            self.warning_threshold_pct, self.critical_threshold_pct, self.full_threshold_pct
        )
        alerts: list[Alert] = self.state.setdefault("alerts", [])
        hub_alerts: list[Alert] = []

        if level == OccupancyLevel.NORMAL:
            if hub.is_locked:
                self.sync_hub_booking_lock(hub_id, False, f"AUTO_UNLOCK_{hub_id}_{self.state.get('state_version', 0)}")
        elif level == OccupancyLevel.WARNING:
            alert = Alert(
                alert_id=f"ALT_{hub_id}_WARN",
                hub_id=hub_id,
                alert_type=AlertType.OCCUPANCY_THRESHOLD,
                severity=AlertSeverity.WARNING,
                occupancy_level=level,
                message=f"Cảnh báo sớm (Màu vàng): Tỷ lệ lấp đầy tại {hub_id} đạt {hub.calculate_occupancy_rate()}%",
                created_at=self._now(),
            )
            alerts.append(alert)
            hub_alerts.append(alert)
        elif level == OccupancyLevel.CRITICAL:
            alert = Alert(
                alert_id=f"ALT_{hub_id}_CRIT",
                hub_id=hub_id,
                alert_type=AlertType.OCCUPANCY_THRESHOLD,
                severity=AlertSeverity.CRITICAL,
                occupancy_level=level,
                message=f"Nguy cơ quá tải (Đỏ nhấp nháy): Đề xuất điều chuyển xe sang SS4 tại {hub_id}",
                created_at=self._now(),
                dispatch_suggested=True,
            )
            alerts.append(alert)
            hub_alerts.append(alert)
        elif level == OccupancyLevel.FULL:
            lock_res = self.sync_hub_booking_lock(hub_id, True, f"AUTO_LOCK_{hub_id}")
            if lock_res.ok:
                alert = Alert(
                    alert_id=f"ALT_{hub_id}_FULL",
                    hub_id=hub_id,
                    alert_type=AlertType.OCCUPANCY_THRESHOLD,
                    severity=AlertSeverity.CRITICAL,
                    occupancy_level=level,
                    message=f"Quá tải 100% (Khóa Đỏ): Đã khóa nhận đặt chỗ mới tại {hub_id}",
                    created_at=self._now(),
                )
            else:
                alert = Alert(
                    alert_id=f"ALT_{hub_id}_SYNC_ERR",
                    hub_id=hub_id,
                    alert_type=AlertType.LOCK_SYNC_FAILURE,
                    severity=AlertSeverity.EMERGENCY,
                    occupancy_level=level,
                    message=f"Lỗi đồng bộ khóa tự động tại {hub_id}. Yêu cầu Operator khóa Hub thủ công!",
                    created_at=self._now(),
                )
            alerts.append(alert)
            hub_alerts.append(alert)

        return OperationResult(ok=True, data=hub_alerts, state_version=self.state.get("state_version", 0))

    def manual_lock_hub(self, operator_id: str, hub_id: str, lock_state: bool) -> OperationResult[bool]:
        users = self.state.get("users", {})
        role = users.get(operator_id)
        if role not in ("OPERATOR", "ADMIN"):
            return OperationResult(ok=False, error_code="FORBIDDEN", message="Only OPERATOR or ADMIN can manual lock")
        hubs: dict[str, Hub] = self.state.get("hubs", {})
        if hub_id not in hubs:
            return OperationResult(ok=False, error_code="NOT_FOUND", message="Hub not found")
        hubs[hub_id].is_locked = lock_state
        for alert in self.state.get("alerts", []):
            if alert.hub_id == hub_id and alert.alert_type == AlertType.LOCK_SYNC_FAILURE:
                alert.is_resolved = True
                alert.acknowledge(operator_id, self._now())
        self.state["state_version"] = self.state.get("state_version", 0) + 1
        return OperationResult(ok=True, data=lock_state, state_version=self.state["state_version"])

    def update_alert_thresholds(self, admin_id: str, warning_pct: float, critical_pct: float) -> OperationResult[bool]:
        users = self.state.get("users", {})
        if users.get(admin_id) != "ADMIN":
            return OperationResult(ok=False, error_code="FORBIDDEN", message="Admin role required")
        if not (0.0 < warning_pct < critical_pct < 100.0):
            return OperationResult(ok=False, error_code="INVALID_INPUT", message="Invalid threshold range")
        self.warning_threshold_pct = warning_pct
        self.critical_threshold_pct = critical_pct
        self.state["state_version"] = self.state.get("state_version", 0) + 1
        return OperationResult(ok=True, data=True, state_version=self.state["state_version"])

    def record_iot_maintenance_plan(self, tech_id: str, alert_id: str, plan_note: str) -> OperationResult[Alert]:
        users = self.state.get("users", {})
        if users.get(tech_id) not in ("TECHNICIAN", "ADMIN"):
            return OperationResult(ok=False, error_code="FORBIDDEN", message="Technician role required")
        if not plan_note or not plan_note.strip():
            return OperationResult(ok=False, error_code="INVALID_INPUT", message="Maintenance plan cannot be empty")
        for alert in self.state.get("alerts", []):
            if alert.alert_id == alert_id:
                alert.acknowledge(tech_id, self._now())
                alert.maintenance_plan = plan_note.strip()
                return OperationResult(ok=True, data=alert, state_version=self.state.get("state_version", 0))
        return OperationResult(ok=False, error_code="NOT_FOUND", message="Alert not found")

    def get_network_snapshot(self) -> OperationResult[NetworkSnapshot]:
        hubs: dict[str, Hub] = self.state.get("hubs", {})
        if not hubs:
            return OperationResult(ok=False, error_code="NOT_FOUND", message="No hubs initialized")

        # Kiểm tra Exception 1 của UC_SS3_01: Cảm biến IoT mất kết nối / timeout
        if any(not h.iot_online for h in hubs.values()):
            cached: Optional[NetworkSnapshot] = self.state.get("cached_network_snapshot")
            offline_hubs = [h.hub_id for h in hubs.values() if not h.iot_online]
            iot_alert = Alert(
                alert_id=f"ALT_IOT_{offline_hubs[0]}",
                hub_id=offline_hubs[0],
                alert_type=AlertType.IOT_SENSOR_TIMEOUT,
                severity=AlertSeverity.WARNING,
                message="Cảnh báo: Dữ liệu thời gian thực đang bị gián đoạn",
                created_at=self._now(),
            )
            self.state.setdefault("alerts", []).append(iot_alert)
            if cached is not None:
                cached_copy = NetworkSnapshot(
                    captured_at=cached.captured_at,
                    state_version=cached.state_version,
                    total_active_vehicles=cached.total_active_vehicles,
                    network_occupancy_pct=cached.network_occupancy_pct,
                    is_using_cached_data=True,
                    occupancy_snapshots=cached.occupancy_snapshots,
                    revenue_summary=cached.revenue_summary,
                    active_alerts=[iot_alert],
                )
                return OperationResult(
                    ok=True,
                    data=cached_copy,
                    message="Cảnh báo: Dữ liệu thời gian thực đang bị gián đoạn",
                    state_version=self.state.get("state_version", 0),
                )

        snapshots = []
        total_cap = 0
        total_occ = 0
        total_vehicles = 0
        for h_id, h in hubs.items():
            occ_res = self.calculate_hub_occupancy(h_id)
            if not occ_res.ok:
                return OperationResult(ok=False, error_code=occ_res.error_code, message=occ_res.message)
            snapshots.append(occ_res.data)
            total_cap += h.capacity
            total_occ += h.capacity - h.available_slots
            total_vehicles += h.present_vehicles_count

        rev_res = self.generate_revenue_report()
        net_occ_pct = round((total_occ / total_cap) * 100.0, 2) if total_cap > 0 else 0.0
        net_snap = NetworkSnapshot(
            captured_at=self._now(),
            state_version=self.state.get("state_version", 0),
            total_active_vehicles=total_vehicles,
            network_occupancy_pct=net_occ_pct,
            is_using_cached_data=False,
            occupancy_snapshots=snapshots,
            revenue_summary=rev_res.data,
            active_alerts=list(self.state.get("alerts", [])),
        )
        self.state["cached_network_snapshot"] = net_snap
        return OperationResult(ok=True, data=net_snap, state_version=net_snap.state_version)


# =====================================================================
# 2. CÁC HÀM KIỂM THỬ PYTEST (5 TEST CASES BONUS CỦA TV3)
# =====================================================================

def test_tc_ss3_bnd_01_occupancy_boundaries():
    """
    TC-SS3-BND-01: Kiểm tra phân loại cảnh báo tại đúng 6 mốc biên
    69.99%, 70.00%, 84.99%, 85.00%, 99.99%, 100.00%.
    """
    hub = Hub(
        hub_id="HUB_01",
        name="Trạm Bách Khoa",
        latitude=10.77,
        longitude=106.65,
        capacity=10000,
        available_slots=10000,
        present_vehicles_count=0,
    )
    session = {"hubs": {"HUB_01": hub}, "state_version": 1, "alerts": []}
    service = MonitoringService(session)

    test_matrix = [
        (6999, 69.99, OccupancyLevel.NORMAL, False, False),
        (7000, 70.00, OccupancyLevel.WARNING, False, False),
        (8499, 84.99, OccupancyLevel.WARNING, False, False),
        (8500, 85.00, OccupancyLevel.CRITICAL, True, False),
        (9999, 99.99, OccupancyLevel.CRITICAL, True, False),
        (10000, 100.00, OccupancyLevel.FULL, False, True),
    ]

    for occupied, expected_pct, expected_level, expect_dispatch, expect_locked in test_matrix:
        hub.present_vehicles_count = occupied
        hub.available_slots = hub.capacity - occupied
        hub.is_locked = False
        session["alerts"].clear()

        assert hub.calculate_occupancy_rate() == expected_pct
        assert hub.get_occupancy_level() == expected_level

        res = service.evaluate_hub_alerts("HUB_01")
        assert res.ok is True
        assert hub.is_locked is expect_locked

        if expected_level == OccupancyLevel.CRITICAL:
            assert len(res.data) == 1
            assert res.data[0].dispatch_suggested is expect_dispatch


def test_tc_ss3_inv_01_capacity_conservation():
    """
    TC-SS3-INV-01: Bảo toàn sức chứa (chỗ trống + xe hiện diện + giữ chỗ đến + tải nền == sức chứa),
    không cộng 2 lần cùng một xe/chỗ, và cổng sạc lỗi không làm lệch sức chứa đỗ xe.
    """
    hub = Hub(
        hub_id="HUB_02",
        name="Trạm KTX Khu A",
        latitude=10.87,
        longitude=106.80,
        capacity=20,
        available_slots=5,
        present_vehicles_count=10,
        incoming_reserved_count=3,
        background_load_count=2,
        total_ports=10,
        active_ports_count=8,
    )
    session = {"hubs": {"HUB_02": hub}, "state_version": 1}
    service = MonitoringService(session)

    # 1. Trạng thái hợp lệ (5 + 10 + 3 + 2 == 20)
    assert hub.validate_capacity_invariant() is True
    snap_ok = service.calculate_hub_occupancy("HUB_02")
    assert snap_ok.ok is True
    assert snap_ok.data.occupancy_rate_pct == 75.0
    assert snap_ok.data.port_utilization_pct == 80.0

    # 2. Lỗi cộng trùng: xe đặt trước đã tới trạm (present tăng lên 11) nhưng quên trừ incoming_reserved (vẫn là 3)
    hub.present_vehicles_count = 11
    assert hub.validate_capacity_invariant() is False
    snap_err = service.calculate_hub_occupancy("HUB_02")
    assert snap_err.ok is False
    assert snap_err.error_code == "INVALID_STATE"


def test_tc_ss3_rev_01_realized_revenue_vs_deposit_and_debt():
    """
    TC-SS3-REV-01: Phân biệt rõ doanh thu thực thu (realized revenue),
    khoản cọc đang giữ (held deposit), tiền hoàn (refunded) và nợ (debt).
    """
    hub = Hub("HUB_01", "Trạm Bách Khoa", 10.77, 106.65, 20, 15, 5)
    session = {
        "hubs": {"HUB_01": hub},
        "state_version": 2,
        "deposits": [
            {"ref_id": "BK_01", "held_vnd": 50000, "released_vnd": 0, "status": "HELD"},
            {"ref_id": "BK_02", "held_vnd": 50000, "released_vnd": 40000, "status": "RELEASED"},
        ],
        "ledger": [
            {"charge_id": "CH_01", "hub_id": "HUB_01", "kind": "PENALTY", "paid_vnd": 10000, "debt_vnd": 0},
            {"charge_id": "CH_02", "hub_id": "HUB_01", "kind": "PARKING", "paid_vnd": 5000, "debt_vnd": 0},
            {"charge_id": "CH_03", "hub_id": "HUB_01", "kind": "CHARGING", "paid_vnd": 10000, "debt_vnd": 15000},
        ],
    }
    service = MonitoringService(session)
    res = service.generate_revenue_report()

    assert res.ok is True
    report = res.data
    assert report.settled_penalty_fee_vnd == 10000
    assert report.settled_parking_fee_vnd == 5000
    assert report.settled_charging_fee_vnd == 10000
    # Tổng thực thu = 10.000 + 5.000 + 10.000 = 25.000 VNĐ (TUYỆT ĐỐI KHÔNG CỘNG 50.000 cọc đang giữ hay 15.000 nợ)
    assert report.total_realized_revenue_vnd == 25000
    assert report.held_deposit_vnd == 50000
    assert report.refunded_amount_vnd == 40000
    assert report.outstanding_debt_vnd == 15000


def test_tc_ss3_lck_01_auto_lock_idempotency_and_manual_lock_fallback():
    """
    TC-SS3-LCK-01: Khóa tự động chống gọi lặp (idempotent) và cơ chế
    Operator khóa Hub thủ công khi gặp Exception 1 (lỗi đồng bộ khóa).
    """
    hub = Hub("HUB_01", "Trạm Bách Khoa", 10.77, 106.65, 10, 0, 10)
    session = {
        "hubs": {"HUB_01": hub},
        "users": {"OP_01": "OPERATOR", "SV_01": "STUDENT"},
        "state_version": 1,
        "alerts": [],
        "simulate_lock_sync_failure": False,
    }
    service = MonitoringService(session)

    # Ca 1: Khóa tự động và gọi lặp cùng operation_key
    r1 = service.sync_hub_booking_lock("HUB_01", True, "LOCK_KEY_01")
    v_after_first = session["state_version"]
    r2 = service.sync_hub_booking_lock("HUB_01", True, "LOCK_KEY_01")
    assert r1.ok is True and r2.ok is True
    assert hub.is_locked is True
    assert session["state_version"] == v_after_first  # Không tăng state_version lần 2

    # Ca 2: Giả lập lỗi đồng bộ khóa (Exception 1 của UC_SS3_02)
    hub.is_locked = False
    session["simulate_lock_sync_failure"] = True
    eval_res = service.evaluate_hub_alerts("HUB_01")
    assert eval_res.ok is True
    assert hub.is_locked is False
    assert eval_res.data[0].alert_type == AlertType.LOCK_SYNC_FAILURE
    assert eval_res.data[0].severity == AlertSeverity.EMERGENCY

    # Ca 3: Sinh viên gọi khóa thủ công bị chặn FORBIDDEN; Operator khóa thủ công thành công
    forbidden_res = service.manual_lock_hub("SV_01", "HUB_01", True)
    assert forbidden_res.ok is False and forbidden_res.error_code == "FORBIDDEN"

    manual_res = service.manual_lock_hub("OP_01", "HUB_01", True)
    assert manual_res.ok is True
    assert hub.is_locked is True
    assert eval_res.data[0].is_resolved is True


def test_tc_ss3_iot_01_cache_fallback_missing_data_and_maintenance():
    """
    TC-SS3-IOT-01: Fallback về dữ liệu cache khi cảm biến IoT mất kết nối (Exception 1 UC_SS3_01),
    xử lý dữ liệu thiếu (NOT_FOUND), Kỹ thuật viên ghi nhận bảo trì và Admin đổi ngưỡng cảnh báo.
    """
    hub = Hub("HUB_03", "Trạm Khu B", 10.88, 106.79, 20, 12, 8, iot_online=True)
    session = {
        "hubs": {"HUB_03": hub},
        "users": {"TECH_01": "TECHNICIAN", "ADMIN_01": "ADMIN"},
        "state_version": 5,
        "alerts": [],
        "ledger": [],
        "deposits": [],
    }
    service = MonitoringService(session)

    # Chụp snapshot lần 1 khi IoT đang online để tạo cache
    snap_online = service.get_network_snapshot()
    assert snap_online.ok is True
    assert snap_online.data.is_using_cached_data is False

    # Ngắt kết nối IoT tại HUB_03 -> Hệ thống phải trả về bản cache + cảnh báo gián đoạn
    hub.iot_online = False
    snap_offline = service.get_network_snapshot()
    assert snap_offline.ok is True
    assert snap_offline.data.is_using_cached_data is True
    assert "Dữ liệu thời gian thực đang bị gián đoạn" in snap_offline.message

    # Kỹ thuật viên ghi nhận phương án bảo trì cho cảnh báo IoT vừa phát sinh
    iot_alert_id = snap_offline.data.active_alerts[0].alert_id
    maint_res = service.record_iot_maintenance_plan(
        "TECH_01", iot_alert_id, "Kiểm tra nguồn cấp cảm biến tại HUB_03"
    )
    assert maint_res.ok is True
    assert maint_res.data.acknowledged_by == "TECH_01"

    # Kiểm tra truy vấn Hub không tồn tại (dữ liệu thiếu)
    missing_res = service.calculate_hub_occupancy("HUB_999")
    assert missing_res.ok is False and missing_res.error_code == "NOT_FOUND"

    # Admin cấu hình ngưỡng hợp lệ và không hợp lệ
    bad_cfg = service.update_alert_thresholds("ADMIN_01", warning_pct=90.0, critical_pct=80.0)
    assert bad_cfg.ok is False and bad_cfg.error_code == "INVALID_INPUT"

    good_cfg = service.update_alert_thresholds("ADMIN_01", warning_pct=65.0, critical_pct=88.0)
    assert good_cfg.ok is True
    assert service.warning_threshold_pct == 65.0