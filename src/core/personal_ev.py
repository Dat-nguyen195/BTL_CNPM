"""
personal_ev.py – Core Personal EV Management & Lifecycle
Smart E-Mobility Hub – ĐHQG-HCM

Manages the 4 canonical Use Cases of Subsystem 2:
  • UC_SS2_01: Đăng ký thông tin xe điện cá nhân (UC_Dang_Ki_EV)
  • UC_SS2_02: Đặt trước chỗ đỗ & yêu cầu sạc (UC_Dat_Cho_Va_Sac)
  • UC_SS2_03: Check-in xác thực vào trạm (UC_Check_In)
  • UC_SS2_04: Check-out, quyết toán biểu phí tích hợp & xuất hóa đơn (UC_Check_Out_Thanh_Toan)
"""

from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime, timedelta
import uuid
import math
import os

from core.state import VehicleStatus, ReservationStatus, bump_state_version
from core.policies import (
    PEV_PARKING_FEE_PER_VISIT_VND,
    PEV_OFFPEAK_KWH_RATE_VND,
    PEV_PEAK_KWH_RATE_VND,
    OVERSTAY_GRACE_MINUTES,
    OVERSTAY_RATE_PER_BLOCK_VND,
    PEV_RESERVATION_DEPOSIT_VND,
    PEV_ARRIVAL_EXPIRY_MINUTES,
    PEV_NOSHOW_PENALTY_VND,
    PEV_NOSHOW_REFUND_VND,
    is_peak_hour
)
from core.billing import (
    hold_deposit,
    release_held_deposit_full,
    record_wallet_debt,
    record_transaction,
    settle_pev_noshow_penalty
)

# Xe cá nhân chỉ gửi đỗ: trạng thái riêng, không dùng AVAILABLE (dành cho xe cho thuê SS1),
# để SS1 không đếm là "xe sẵn sàng" và SS4 không chọn để cách ly như xe dùng chung.
PERSONAL_PARKED_STATUS = "PARKED"

def parse_time(t_str: str) -> datetime:
    try:
        return datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now()

def format_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

ALLOWED_EV_TYPES = ("scooter", "bike", "car")
MAX_BATTERY_KWH = 120.0

def normalize_plate(raw_plate: str) -> str:
    """Chuẩn hóa biển số để so trùng: viết hoa, bỏ khoảng trắng, gạch ngang và dấu chấm."""
    return "".join(ch for ch in raw_plate.upper() if not ch.isspace() and ch not in "-.")

def register_personal_ev(
    state: Dict[str, Any],
    owner_id: str,
    owner_name: str,
    plate_number: str,
    ev_type: str,
    brand: str,
    battery_kwh: float
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Registers a personal EV to the system (UC_SS2_01).
    Validates duplicate plate numbers.
    """
    clean_plate = normalize_plate(plate_number) if isinstance(plate_number, str) else ""
    if not clean_plate:
        return False, None, "Biển số xe không được để trống."
    if not str(owner_id or "").strip():
        return False, None, "Chưa xác định được tài khoản chủ xe."
    if ev_type not in ALLOWED_EV_TYPES:
        return False, None, f"Loại phương tiện không hợp lệ (chỉ nhận: {', '.join(ALLOWED_EV_TYPES)})."
    try:
        battery_kwh = float(battery_kwh)
    except (TypeError, ValueError):
        return False, None, "Dung lượng pin không hợp lệ."
    if not math.isfinite(battery_kwh) or battery_kwh <= 0 or battery_kwh > MAX_BATTERY_KWH:
        return False, None, f"Dung lượng pin phải lớn hơn 0 và không quá {MAX_BATTERY_KWH:g} kWh."

    existing = state.setdefault("personal_evs", [])
    for ev in existing:
        ep = normalize_plate(ev.get("plate") or "")
        if ep == clean_plate:
            return False, None, f"Biển số xe '{plate_number}' đã được đăng ký trong hệ thống."

    ev_id = f"PEV-{uuid.uuid4().hex[:6].upper()}"
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    new_ev = {
        "ev_id": ev_id,
        "owner_id": owner_id,
        "owner_name": owner_name,
        "plate": plate_number.strip().upper(),
        "type": ev_type,
        "brand": brand.strip(),
        "battery_kwh": float(battery_kwh),
        "ownership": "PERSONAL",
        "registered_at": sim_now_str,
        "status": "REGISTERED"
    }
    existing.append(new_ev)
    bump_state_version(state)
    return True, new_ev, f"Đăng ký xe cá nhân thành công! Mã định danh: {ev_id}"

def reserve_personal_ev_slot(
    state: Dict[str, Any],
    owner_id: str,
    ev_id: str,
    hub_id: str,
    request_charging: bool = False,
    current_soc: float = 50.0,
    booking_start_time: Optional[str] = None
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Reserves a parking slot & optional charging for a personal EV (UC_SS2_02).
    Holds slot at Hub (destination_holds += 1, available_slots -= 1) without
    physically inserting vehicle into hub.current_vehicles yet.
    """
    # 1. Locate EV
    ev = next((e for e in state.get("personal_evs", []) if e.get("ev_id") == ev_id), None)
    if not ev:
        return False, None, f"Không tìm thấy phương tiện {ev_id}."
    if ev.get("owner_id") != owner_id:
        return False, None, "Phương tiện không thuộc tài khoản đang đặt chỗ."
    try:
        current_soc = float(current_soc)
    except (TypeError, ValueError):
        return False, None, "Phần trăm pin không hợp lệ."
    if not math.isfinite(current_soc) or not 0 <= current_soc <= 100:
        return False, None, "Phần trăm pin phải nằm trong khoảng 0–100%."

    sim_now_str = state.get("current_sim_time", format_time(datetime.now()))
    sim_now = parse_time(sim_now_str)
    try:
        start = datetime.strptime(booking_start_time, "%Y-%m-%d %H:%M:%S") if booking_start_time else sim_now
    except (ValueError, TypeError):
        return False, None, "Thời gian đến trạm không hợp lệ."
    if start < sim_now:
        return False, None, "Thời gian đến trạm không được ở trong quá khứ."

    # Check existing active reservations for this vehicle
    for r in state.get("personal_reservations", []):
        if r.get("ev_id") == ev_id and r.get("status") in [
            ReservationStatus.RESERVED.value,
            "CHECKED_IN"
        ]:
            return False, None, f"Phương tiện {ev_id} đang có lượt đặt chỗ #{r['reservation_id']} chưa hoàn tất."

    # 2. Check Hub capacity
    hubs = state.get("hubs", [])
    hub = next((h for h in hubs if h.get("hub_id") == hub_id), None)
    if not hub:
        return False, None, f"Không tìm thấy Hub {hub_id}."

    if hub.get("available_slots", 0) <= 0:
        return False, None, f"Hub {hub.get('name')} hiện không còn chỗ đỗ trống."

    if request_charging and hub.get("charging_ports", {}).get("available", 0) <= 0:
        return False, None, f"Hub {hub.get('name')} hiện không còn cổng sạc trống khả dụng."

    # 3. Hold deposit via wallet
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)
    wallet = state.setdefault("wallet", {})

    res_id = f"PRES-{uuid.uuid4().hex[:6].upper()}"
    ok_hold, msg_hold = hold_deposit(
        wallet=wallet,
        amount=PEV_RESERVATION_DEPOSIT_VND,
        booking_id=res_id,
        sim_time=sim_now_str
    )
    if not ok_hold:
        return False, None, f"Không thể khóa cọc đặt chỗ: {msg_hold}"

    # 4. Mutate slot count (held)
    hub["destination_holds"] = hub.get("destination_holds", 0) + 1
    hub["available_slots"] = hub.get("available_slots", 0) - 1

    expires_at_str = format_time(start + timedelta(minutes=PEV_ARRIVAL_EXPIRY_MINUTES))

    reservation = {
        "reservation_id": res_id,
        "owner_id": owner_id,
        "ev_id": ev_id,
        "plate": ev.get("plate"),
        "hub_id": hub_id,
        "hub_name": hub.get("name"),
        "request_charging": request_charging,
        "current_soc": float(current_soc),
        "deposit_held": PEV_RESERVATION_DEPOSIT_VND,
        "created_at": sim_now_str,
        "booking_start_time": format_time(start),
        "arrival_deadline": expires_at_str,
        "check_in_time": None,
        "check_out_time": None,
        "status": ReservationStatus.RESERVED.value,
        "invoice": None
    }

    state.setdefault("personal_reservations", []).append(reservation)
    bump_state_version(state)
    return True, reservation, f"Đặt chỗ xe cá nhân thành công tại {hub.get('name')}! Hạn chót check-in: {expires_at_str}"

def sweep_expired_personal_reservations(state: Dict[str, Any]) -> int:
    """
    Checks all RESERVED personal EV reservations. If current_sim_time >= arrival_deadline,
    expires the reservation, restores available slot at Hub, settles held deposit (no-show penalty + refund),
    and logs immutable ledger transactions.
    """
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)
    wallet = state.setdefault("wallet", {})
    hubs = state.get("hubs", [])

    expired_count = 0
    for res in state.get("personal_reservations", []):
        if res.get("status") == ReservationStatus.RESERVED.value:
            deadline = parse_time(res.get("arrival_deadline", sim_now_str))
            if sim_now >= deadline:
                res["status"] = ReservationStatus.EXPIRED.value
                res["expired_at"] = sim_now_str
                expired_count += 1

                # Release hold & restore slot capacity
                hub = next((h for h in hubs if h.get("hub_id") == res.get("hub_id")), None)
                if hub:
                    hub["destination_holds"] = max(0, hub.get("destination_holds", 0) - 1)
                    hub["available_slots"] = hub.get("available_slots", 0) + 1

                # Settle deposit held
                dep = res.get("deposit_held", PEV_RESERVATION_DEPOSIT_VND)
                settle_pev_noshow_penalty(
                    wallet=wallet,
                    deposit_amount=dep,
                    penalty_amount=PEV_NOSHOW_PENALTY_VND,
                    booking_id=res.get("reservation_id"),
                    sim_time=sim_now_str
                )

    if expired_count > 0:
        bump_state_version(state)
    return expired_count

def cancel_personal_reservation(
    state: Dict[str, Any],
    reservation_id: str,
    owner_id: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Hủy đơn đặt chỗ trước Check-in (UC_SS2_02, Alternative 3).
    Cùng chính sách với SS1: hủy trước hạn check-in (booking_start_time + 30 phút)
    hoàn 100% cọc và trả chỗ giữ; đến hạn thì đơn đã EXPIRED và quyết toán no-show.
    """
    sweep_expired_personal_reservations(state)
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    res = next((r for r in state.get("personal_reservations", []) if r.get("reservation_id") == reservation_id), None)
    if not res:
        return False, f"Không tìm thấy đặt chỗ #{reservation_id}."
    if owner_id is not None and res.get("owner_id") != owner_id:
        return False, "Đặt chỗ không thuộc tài khoản đang thao tác."
    if res.get("status") == ReservationStatus.EXPIRED.value:
        return False, "Đặt chỗ đã quá hạn check-in; cọc đã được quyết toán no-show (phạt 10.000 VNĐ, hoàn 40.000 VNĐ)."
    if res.get("status") != ReservationStatus.RESERVED.value:
        return False, f"Không thể hủy đặt chỗ ở trạng thái hiện tại ({res.get('status')})."

    hub = next((h for h in state.get("hubs", []) if h.get("hub_id") == res.get("hub_id")), None)
    if hub:
        hub["destination_holds"] = max(0, hub.get("destination_holds", 0) - 1)
        hub["available_slots"] = hub.get("available_slots", 0) + 1

    wallet = state.setdefault("wallet", {})
    dep = res.get("deposit_held", PEV_RESERVATION_DEPOSIT_VND)
    release_held_deposit_full(wallet, amount=dep, booking_id=reservation_id, sim_time=sim_now_str)

    res["status"] = ReservationStatus.CANCELLED.value
    res["cancelled_at"] = sim_now_str
    bump_state_version(state)
    return True, f"Hủy đặt chỗ thành công! Hoàn 100% tiền cọc ({dep:,} VNĐ) về ví."

def check_in_personal_ev(
    state: Dict[str, Any],
    reservation_id: str
) -> Tuple[bool, str]:
    """
    Validates QR/arrival and checks-in the personal EV at the Hub (UC_SS2_03).
    Converts held slot into physical occupancy without double decrement.
    If charging requested, queues into SS5.
    """
    # Sweep any expired reservations first
    sweep_expired_personal_reservations(state)

    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)

    res = next((r for r in state.get("personal_reservations", []) if r.get("reservation_id") == reservation_id), None)
    if not res:
        return False, f"Không tìm thấy đặt chỗ #{reservation_id}."

    if res.get("status") == ReservationStatus.EXPIRED.value:
        return False, "Đặt chỗ đã quá hạn đón tiếp. Hệ thống đã hủy lượt đặt chỗ tự động và quyết toán tiền cọc."

    if res.get("status") != ReservationStatus.RESERVED.value:
        return False, f"Đặt chỗ không ở trạng thái chờ check-in (Hiện tại: {res.get('status')})."

    if sim_now < parse_time(res.get("booking_start_time", res["created_at"])):
        return False, "Chưa đến thời gian check-in đã đặt."

    deadline = parse_time(res.get("arrival_deadline", sim_now_str))
    if sim_now >= deadline:
        sweep_expired_personal_reservations(state)
        return False, "Đặt chỗ đã quá hạn đón tiếp. Hệ thống đã hủy lượt đặt chỗ tự động và quyết toán tiền cọc."

    # Convert hold to physical vehicle presence
    hubs = state.get("hubs", [])
    hub = next((h for h in hubs if h.get("hub_id") == res.get("hub_id")), None)
    if not hub:
        return False, "Không tìm thấy thông tin Hub."

    hub["destination_holds"] = max(0, hub.get("destination_holds", 0) - 1)
    # Physical slot is now occupied, available_slots does NOT change (already decremented during reservation)

    ev = next((e for e in state.get("personal_evs", []) if e.get("ev_id") == res["ev_id"]), {})
    veh_record = {
        "vehicle_id": res["ev_id"],
        "plate": res.get("plate"),
        "type": ev.get("type", "scooter"),
        "battery_soc": res.get("current_soc", 50.0),
        "status": (VehicleStatus.CHARGING.value if hub.get("charging_ports", {}).get("available", 0) > 0 else "WAITING") if res.get("request_charging") else PERSONAL_PARKED_STATUS,
        "ownership": "PERSONAL",
        "owner_id": res.get("owner_id"),
        "hub_id": res["hub_id"]
    }
    hub.setdefault("current_vehicles", []).append(veh_record)

    res["status"] = "CHECKED_IN"
    res["check_in_time"] = sim_now_str
    if res.get("request_charging"):
        from core.scheduler import ChargingRequest, SmartChargingScheduler, allocate_hub_ports
        scheduler = state.setdefault("charging_scheduler", SmartChargingScheduler())
        res["charging_port_allocated"] = False
        veh_record["status"] = "WAITING"
        scheduler.add_request(ChargingRequest(vehicle_id=res["ev_id"], hub_id=res["hub_id"],
                                              battery_soc=res.get("current_soc", 50),
                                              ownership="PERSONAL", owner_id=res.get("owner_id")))
        allocate_hub_ports(state, res["hub_id"])
    bump_state_version(state)
    return True, f"Check-in thành công cho xe {res['plate']} tại {hub.get('name')}! Barie đã mở."

def check_out_personal_ev(
    state: Dict[str, Any],
    reservation_id: str,
    duration_hours: float = 2.0,
    kwh_charged: float = 3.5,
    overstay_minutes: int = 0
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Check-out, settles combined parking, energy and overstay invoice (UC_SS2_04).
    Frees physical parking slot and charging port.
    """
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)

    res = next((r for r in state.get("personal_reservations", []) if r.get("reservation_id") == reservation_id), None)
    if not res:
        return False, None, f"Không tìm thấy thông tin đặt chỗ #{reservation_id}."

    if res.get("status") != "CHECKED_IN":
        return False, None, f"Lượt xe không ở trạng thái CHECKED_IN (Hiện tại: {res.get('status')})."

    hourly_rate = int(os.environ.get("EMOBILITY_PARKING_HOURLY_VND", "5000"))
    if hourly_rate < 0:
        return False, None, "Biểu phí đỗ không hợp lệ."
    from core.scheduler import release_charging_session
    if any(not math.isfinite(value) or value < 0 for value in (duration_hours, kwh_charged, overstay_minutes)):
        return False, None, "Giá trị sử dụng không được âm."

    scheduler = state.get("charging_scheduler")
    if scheduler:
        scheduler.remove_request(res["ev_id"])
        session_id = res.get("charging_session_id")
        if session_id:
            release_charging_session(state, session_id)

    # Remove EV from physical hub and free slot
    hubs = state.get("hubs", [])
    hub = next((h for h in hubs if h.get("hub_id") == res.get("hub_id")), None)
    if hub:
        for i, v in enumerate(hub.get("current_vehicles", [])):
            if v.get("vehicle_id") == res.get("ev_id"):
                hub["current_vehicles"].pop(i)
                break
        hub["available_slots"] = hub.get("available_slots", 0) + 1
        if res.get("charging_port_allocated"):
            hub["charging_ports"]["available"] = min(
                hub["charging_ports"]["total"] - hub["charging_ports"].get("offline", 0),
                hub["charging_ports"]["available"] + 1
            )

    # Financial settlement
    wallet = state.setdefault("wallet", {})
    # 1. Release held deposit
    dep_amount = res.get("deposit_held", PEV_RESERVATION_DEPOSIT_VND)
    release_held_deposit_full(wallet, amount=dep_amount, booking_id=reservation_id, sim_time=sim_now_str)

    if "delivered_kwh" in res:
        kwh_charged = res["delivered_kwh"]

    # 2. Tariff calculation
    # Mỗi giờ bắt đầu tính một block; xe đã vào bãi là giờ đầu tiên đã bắt đầu.
    parking_fee = max(1, math.ceil(duration_hours)) * hourly_rate
    is_peak = is_peak_hour(sim_now.time())
    energy_rate = PEV_PEAK_KWH_RATE_VND if is_peak else PEV_OFFPEAK_KWH_RATE_VND
    energy_fee = round(res.get("measured_energy_fee", kwh_charged * energy_rate)) if res.get("charging_ever_allocated") else 0
    # Hiển thị đơn giá theo thời điểm SẠC (không phải lúc check-out): đơn giá bình quân = tiền điện / kWh.
    # Sau khi pin đầy, SS5 không tính thêm tiền điện; chỉ tính phí quá giờ.
    if res.get("charging_ever_allocated") and kwh_charged > 0:
        energy_rate = round(energy_fee / kwh_charged)
        is_peak = energy_rate > PEV_OFFPEAK_KWH_RATE_VND

    # 3. Overstay fee calculation
    billable_overstay_minutes = max(0, overstay_minutes - OVERSTAY_GRACE_MINUTES) if res.get("charging_port_allocated") else 0
    overstay_blocks = (billable_overstay_minutes + 14) // 15
    overstay_fee = res.get("accrued_overstay_fee", 0) + overstay_blocks * OVERSTAY_RATE_PER_BLOCK_VND

    total_amount = parking_fee + energy_fee + overstay_fee

    # 4. Wallet deduction & debt handling
    current_bal = wallet.get("balance", 0)
    if current_bal >= total_amount:
        wallet["balance"] -= total_amount
        deducted = total_amount
        debt = 0
    else:
        deducted = current_bal
        wallet["balance"] = 0
        debt = total_amount - deducted
        record_wallet_debt(wallet, amount=debt, reason=f"Thanh toán dịch vụ xe cá nhân #{reservation_id}", sim_time=sim_now_str)
    # Ghi sổ cái khoản đã thu từ ví (mỗi biến động số dư đều có một bản ghi giao dịch).
    if deducted > 0:
        record_transaction(
            wallet=wallet,
            tx_type="SETTLE_PEV_INVOICE",
            amount=-deducted,
            booking_id=reservation_id,
            note=f"Thanh toán hóa đơn tổng hợp xe cá nhân #{reservation_id} (đỗ + điện + quá giờ)",
            sim_time=sim_now_str
        )

    invoice = {
        "invoice_id": f"PINV-{uuid.uuid4().hex[:6].upper()}",
        "reservation_id": reservation_id,
        "plate": res.get("plate"),
        "hub_name": hub.get("name") if hub else res.get("hub_name"),
        "duration_hours": round(duration_hours, 1),
        "parking_fee": parking_fee,
        "kwh_charged": round(kwh_charged, 3) if res.get("charging_ever_allocated") else 0,
        "energy_rate": energy_rate if res.get("charging_ever_allocated") else 0,
        "energy_fee": energy_fee,
        "is_peak_tariff": is_peak,
        "overstay_minutes": res.get("accrued_overstay_minutes", 0) + (overstay_minutes if res.get("charging_port_allocated") else 0),
        "overstay_fee": overstay_fee,
        "total_amount": total_amount,
        "deducted_from_wallet": deducted,
        "debt_incurred": debt,
        "settled_at": sim_now_str
    }

    res["status"] = ReservationStatus.COMPLETED.value
    res["check_out_time"] = sim_now_str
    invoice["energy_fee_source"] = "Tích lũy phiên sạc mô phỏng" if "measured_energy_fee" in res else "Đầu vào mô phỏng"
    res["invoice"] = invoice

    # Cổng sạc vừa được trả: cấp ngay cho xe đang chờ (WAITING) tại Hub, nếu có.
    if hub and state.get("charging_scheduler"):
        from core.scheduler import allocate_hub_ports
        allocate_hub_ports(state, hub["hub_id"])

    bump_state_version(state)
    return True, invoice, f"Check-out thành công cho xe {res['plate']}! Tổng chi phí: {total_amount:,.0f} VNĐ."
