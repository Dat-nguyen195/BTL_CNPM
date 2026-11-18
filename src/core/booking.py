"""
booking.py – Core Shared EV Booking, Pickup, Return, Cancellation & Expiry Lifecycle
Smart E-Mobility Hub – ĐHQG-HCM
"""

from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import random
import uuid

from core.state import VehicleStatus, ReservationStatus, bump_state_version
from core.policies import (
    SHARED_DEPOSIT_VND,
    SHARED_EXPIRY_MINUTES,
    MIN_SOC_BOOKING,
    REROUTING_EXTRA_FREE_MINUTES
)
from core.billing import (
    hold_deposit,
    release_held_deposit_full,
    settle_noshow_penalty,
    calculate_shared_rental_cost,
    settle_shared_rental
)

def parse_time(t_str: str) -> datetime:
    try:
        return datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now()

def format_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_active_student_booking(state: Dict[str, Any], student_id: str) -> Optional[Dict[str, Any]]:
    """Returns currently active (RESERVED or IN_USE) booking for the student."""
    for b in state.get("bookings", []):
        if b.get("student_id") == student_id and b.get("status") in [
            ReservationStatus.RESERVED.value,
            VehicleStatus.IN_USE.value
        ]:
            return b
    return None

def process_expired_bookings(state: Dict[str, Any]) -> int:
    """
    Checks all RESERVED bookings. If current_sim_time >= expires_at,
    expires the reservation, deducts no-show fee (10k), refunds remainder (40k),
    frees held slot and returns vehicle to AVAILABLE.
    """
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)
    wallet = state.setdefault("wallet", {})
    hubs = state.get("hubs", [])
    
    expired_count = 0
    for b in state.get("bookings", []):
        if b.get("status") == ReservationStatus.RESERVED.value:
            expires_at = parse_time(b.get("expires_at", sim_now_str))
            if sim_now >= expires_at:
                # Expire this booking
                b["status"] = ReservationStatus.EXPIRED.value
                b["expired_at"] = sim_now_str
                expired_count += 1
                
                # Settle financial penalty
                settle_noshow_penalty(wallet, booking_id=b["booking_id"], sim_time=sim_now_str)
                
                # Revert vehicle status at origin Hub
                origin_hub = next((h for h in hubs if h.get("hub_id") == b.get("hub_id")), None)
                if origin_hub:
                    for v in origin_hub.get("current_vehicles", []):
                        if v.get("vehicle_id") == b.get("vehicle_id"):
                            if v.get("status") == VehicleStatus.RESERVED.value:
                                v["status"] = VehicleStatus.AVAILABLE.value
                                
                # Release destination hold if held
                dest_hub_id = b.get("destination_hub_id")
                if dest_hub_id and b.get("destination_held"):
                    dest_hub = next((h for h in hubs if h.get("hub_id") == dest_hub_id), None)
                    if dest_hub:
                        dest_hub["destination_holds"] = max(0, dest_hub.get("destination_holds", 0) - 1)
                        dest_hub["available_slots"] = dest_hub.get("available_slots", 0) + 1
                        b["destination_held"] = False
                        
                # Add notification
                state.setdefault("notifications", []).append({
                    "id": f"NOTIF-{uuid.uuid4().hex[:6].upper()}",
                    "time": sim_now_str,
                    "type": "WARNING",
                    "title": "Hết hạn giữ chỗ đặt xe",
                    "message": f"Đặt chỗ #{b['booking_id']} đã hết hạn {SHARED_EXPIRY_MINUTES} phút. Phí giữ chỗ không nhận (10,000 VNĐ) đã được áp dụng."
                })

    if expired_count > 0:
        bump_state_version(state)
    return expired_count

def create_shared_booking(
    state: Dict[str, Any],
    student_id: str,
    hub_id: str,
    vehicle_id: str,
    voucher_code: Optional[str] = None,
    destination_hub_id: Optional[str] = None
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Creates a new shared EV booking with 30-minute countdown and deposit hold.
    """
    # Reject personal vehicles before any expiry sweep or financial mutation.
    candidate_hub = next((h for h in state.get("hubs", []) if h.get("hub_id") == hub_id), None)
    candidate = next((v for v in (candidate_hub or {}).get("current_vehicles", [])
                      if v.get("vehicle_id") == vehicle_id), None)
    if candidate and candidate.get("ownership") != "SHARED":
        return False, None, "Chỉ phương tiện SHARED mới được phép thuê."

    # 1. Clean up any expired bookings first
    process_expired_bookings(state)
    
    # 2. Check active booking limitation
    active_b = get_active_student_booking(state, student_id)
    if active_b:
        return False, None, f"Bạn đang có lượt đặt chỗ chưa hoàn tất (#{active_b['booking_id']}). Vui lòng hoàn thành hoặc hủy trước."
        
    # 3. Locate Hub and Vehicle
    hubs = state.get("hubs", [])
    hub = next((h for h in hubs if h.get("hub_id") == hub_id), None)
    if not hub:
        return False, None, f"Không tìm thấy Hub {hub_id}."
        
    vehicle = next((v for v in hub.get("current_vehicles", []) if v.get("vehicle_id") == vehicle_id), None)
    if not vehicle:
        return False, None, f"Không tìm thấy phương tiện {vehicle_id} tại trạm."
        
    if vehicle.get("status") != VehicleStatus.AVAILABLE.value:
        return False, None, f"Phương tiện {vehicle_id} hiện không khả dụng (Trạng thái: {vehicle.get('status')})."
        
    if vehicle.get("battery_soc", 0) < MIN_SOC_BOOKING:
        return False, None, f"Dung lượng pin ({vehicle.get('battery_soc')}%) dưới mức tối thiểu {MIN_SOC_BOOKING}% cho phép vận hành."
        
    # 4. Check destination Hub if chosen
    dest_held = False
    if destination_hub_id:
        dest_hub = next((h for h in hubs if h.get("hub_id") == destination_hub_id), None)
        if not dest_hub:
            return False, None, f"Không tìm thấy Hub đích {destination_hub_id}."
        if dest_hub.get("available_slots", 0) <= 0:
            return False, None, f"Hub đích {dest_hub.get('name')} hiện đã hết chỗ đỗ khả dụng."
            
    # 5. Financial hold
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)
    wallet = state.setdefault("wallet", {})
    
    booking_id = f"BK-{uuid.uuid4().hex[:6].upper()}"
    ok, msg = hold_deposit(
        wallet=wallet,
        amount=SHARED_DEPOSIT_VND,
        booking_id=booking_id,
        sim_time=sim_now_str
    )
    if not ok:
        return False, None, msg
        
    # 6. Apply state mutations atomically
    vehicle["status"] = VehicleStatus.RESERVED.value
    
    if destination_hub_id:
        dest_hub = next((h for h in hubs if h.get("hub_id") == destination_hub_id), None)
        dest_hub["destination_holds"] = dest_hub.get("destination_holds", 0) + 1
        dest_hub["available_slots"] = dest_hub.get("available_slots", 0) - 1
        dest_held = True
        
    pin_code = str(random.randint(1000, 9999))
    expires_at_dt = sim_now + timedelta(minutes=SHARED_EXPIRY_MINUTES)
    expires_at_str = format_time(expires_at_dt)
    
    booking_record = {
        "booking_id": booking_id,
        "student_id": student_id,
        "hub_id": hub_id,
        "hub_name": hub.get("name"),
        "vehicle_id": vehicle_id,
        "vehicle_type": vehicle.get("type"),
        "battery_soc": vehicle.get("battery_soc"),
        "destination_hub_id": destination_hub_id,
        "destination_held": dest_held,
        "voucher_code": voucher_code,
        "pin_code": pin_code,
        "deposit_held": SHARED_DEPOSIT_VND,
        "created_at": sim_now_str,
        "expires_at": expires_at_str,
        "pickup_time": None,
        "return_time": None,
        "extra_free_minutes": 0,
        "status": ReservationStatus.RESERVED.value
    }
    
    state.setdefault("bookings", []).append(booking_record)
    bump_state_version(state)
    return True, booking_record, f"Đặt giữ chỗ xe thành công! Mã PIN nhận xe có hiệu lực trong {SHARED_EXPIRY_MINUTES} phút."

def pickup_shared_vehicle(
    state: Dict[str, Any],
    booking_id: str,
    entered_pin: str
) -> Tuple[bool, str]:
    """
    Validates QR/PIN, verifies deadline, converts vehicle to IN_USE,
    and CRITICALLY frees the origin parking slot (available_slots += 1).
    """
    process_expired_bookings(state)
    
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)
    
    booking = next((b for b in state.get("bookings", []) if b.get("booking_id") == booking_id), None)
    if not booking:
        return False, f"Không tìm thấy thông tin đặt chỗ #{booking_id}."
        
    if booking.get("status") != ReservationStatus.RESERVED.value:
        return False, f"Lượt đặt chỗ không ở trạng thái chờ nhận xe (Trạng thái: {booking.get('status')})."
        
    expires_at = parse_time(booking.get("expires_at", sim_now_str))
    if sim_now >= expires_at:
        process_expired_bookings(state)
        return False, f"Mã PIN nhận xe đã quá hạn {SHARED_EXPIRY_MINUTES} phút. Lượt đặt chỗ đã bị hủy tự động."
        
    if str(booking.get("pin_code")).strip() != str(entered_pin).strip():
        return False, "Mã PIN nhận xe không chính xác. Vui lòng kiểm tra lại."
        
    # Locate origin Hub and vehicle
    hubs = state.get("hubs", [])
    origin_hub = next((h for h in hubs if h.get("hub_id") == booking.get("hub_id")), None)
    if not origin_hub:
        return False, "Không tìm thấy thông tin Hub xuất phát."
        
    vehicle = next((v for v in origin_hub.get("current_vehicles", []) if v.get("vehicle_id") == booking.get("vehicle_id")), None)
    if not vehicle:
        return False, "Không tìm thấy phương tiện tại trạm."
        
    # Free origin slot capacity!
    origin_hub["available_slots"] = origin_hub.get("available_slots", 0) + 1
    
    # Update vehicle & booking status
    vehicle["status"] = VehicleStatus.IN_USE.value
    booking["status"] = VehicleStatus.IN_USE.value
    booking["pickup_time"] = sim_now_str
    
    bump_state_version(state)
    return True, f"Nhận xe {booking['vehicle_id']} thành công! Chỗ đỗ tại {origin_hub['name']} đã được giải phóng. Chúc bạn có chuyến đi an toàn!"

def cancel_shared_booking(
    state: Dict[str, Any],
    booking_id: str
) -> Tuple[bool, str]:
    """
    Cancels an active RESERVED booking.
    If within 30 minutes: 100% deposit refunded.
    If overdue: settles no-show penalty.
    """
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)
    
    booking = next((b for b in state.get("bookings", []) if b.get("booking_id") == booking_id), None)
    if not booking:
        return False, f"Không tìm thấy đặt chỗ #{booking_id}."
        
    if booking.get("status") != ReservationStatus.RESERVED.value:
        return False, f"Lượt đặt chỗ không thể hủy ở trạng thái hiện tại ({booking.get('status')})."
        
    expires_at = parse_time(booking.get("expires_at", sim_now_str))
    wallet = state.setdefault("wallet", {})
    hubs = state.get("hubs", [])
    
    # Revert vehicle status at origin Hub
    origin_hub = next((h for h in hubs if h.get("hub_id") == booking.get("hub_id")), None)
    if origin_hub:
        for v in origin_hub.get("current_vehicles", []):
            if v.get("vehicle_id") == booking.get("vehicle_id"):
                v["status"] = VehicleStatus.AVAILABLE.value
                
    # Release destination hold if held
    dest_hub_id = booking.get("destination_hub_id")
    if dest_hub_id and booking.get("destination_held"):
        dest_hub = next((h for h in hubs if h.get("hub_id") == dest_hub_id), None)
        if dest_hub:
            dest_hub["destination_holds"] = max(0, dest_hub.get("destination_holds", 0) - 1)
            dest_hub["available_slots"] = dest_hub.get("available_slots", 0) + 1
            booking["destination_held"] = False
            
    if sim_now < expires_at:
        # Full refund
        release_held_deposit_full(wallet, booking_id=booking_id, sim_time=sim_now_str)
        booking["status"] = ReservationStatus.CANCELLED.value
        booking["cancelled_at"] = sim_now_str
        bump_state_version(state)
        return True, "Hủy đặt chỗ thành công! 100% tiền cọc (50,000 VNĐ) đã được hoàn trả về ví điện tử."
    else:
        # Overdue
        settle_noshow_penalty(wallet, booking_id=booking_id, sim_time=sim_now_str)
        booking["status"] = ReservationStatus.EXPIRED.value
        booking["expired_at"] = sim_now_str
        bump_state_version(state)
        return False, f"Đặt chỗ đã quá hạn {SHARED_EXPIRY_MINUTES} phút. Hệ thống đã tự động khấu trừ 10,000 VNĐ phí no-show và hoàn trả 40,000 VNĐ."

def return_shared_vehicle(
    state: Dict[str, Any],
    booking_id: str,
    return_hub_id: str,
    override_duration_minutes: Optional[int] = None
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Completes a trip: consumes destination slot, moves vehicle,
    computes duration, settles payment via wallet, and persists invoice.
    """
    sim_now_str = state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sim_now = parse_time(sim_now_str)
    
    booking = next((b for b in state.get("bookings", []) if b.get("booking_id") == booking_id), None)
    if not booking:
        return False, None, f"Không tìm thấy đặt chỗ #{booking_id}."
        
    if booking.get("status") != VehicleStatus.IN_USE.value:
        return False, None, f"Lượt thuê không ở trạng thái đang di chuyển (Trạng thái: {booking.get('status')})."
        
    hubs = state.get("hubs", [])
    dest_hub = next((h for h in hubs if h.get("hub_id") == return_hub_id), None)
    if not dest_hub:
        return False, None, f"Không tìm thấy Hub trả xe {return_hub_id}."
        
    # Check slot consumption at destination Hub
    is_pre_held = (booking.get("destination_hub_id") == return_hub_id and booking.get("destination_held"))
    if not is_pre_held and dest_hub.get("available_slots", 0) <= 0:
        return False, None, "Hub đích hết chỗ."
    if is_pre_held:
        # Slot was already accounted for in destination_holds
        dest_hub["destination_holds"] = max(0, dest_hub.get("destination_holds", 0) - 1)
        booking["destination_held"] = False
    else:
        # Release hold at old destination hub if return is to a different Hub
        old_dest_id = booking.get("destination_hub_id")
        if old_dest_id and booking.get("destination_held"):
            old_hub = next((h for h in hubs if h.get("hub_id") == old_dest_id), None)
            if old_hub:
                old_hub["destination_holds"] = max(0, old_hub.get("destination_holds", 0) - 1)
                old_hub["available_slots"] = old_hub.get("available_slots", 0) + 1
            booking["destination_held"] = False

        # Must consume 1 free slot at return Hub
        if dest_hub.get("available_slots", 0) <= 0:
            return False, None, f"Hub trả xe {dest_hub.get('name')} hiện không còn chỗ đỗ trống! Vui lòng chọn Hub lân cận."
        dest_hub["available_slots"] = dest_hub.get("available_slots", 0) - 1
        
    # Move vehicle to destination Hub
    origin_hub = next((h for h in hubs if h.get("hub_id") == booking.get("hub_id")), None)
    moved_vehicle = None
    if origin_hub:
        for i, v in enumerate(origin_hub.get("current_vehicles", [])):
            if v.get("vehicle_id") == booking.get("vehicle_id"):
                moved_vehicle = origin_hub["current_vehicles"].pop(i)
                break
                
    if not moved_vehicle:
        # Fallback create vehicle structure if missing
        moved_vehicle = {
            "vehicle_id": booking["vehicle_id"],
            "type": booking.get("vehicle_type", "scooter"),
            "battery_soc": booking.get("battery_soc", 50),
            "status": VehicleStatus.AVAILABLE.value,
            "ownership": "SHARED",
            "hub_id": return_hub_id
        }
        
    # Calculate battery consumption based on trip (e.g. 5% per 15 min)
    if override_duration_minutes is not None:
        duration_minutes = max(1, override_duration_minutes)
    else:
        pickup_time = parse_time(booking.get("pickup_time", sim_now_str))
        duration_minutes = max(1, int((sim_now - pickup_time).total_seconds() / 60))
    battery_consumed = min(30, int(duration_minutes / 3))
    new_soc = max(5, moved_vehicle.get("battery_soc", 80) - battery_consumed)
    moved_vehicle["battery_soc"] = new_soc
    moved_vehicle["hub_id"] = return_hub_id
    
    # If battery SoC < 20%, status transitions to CHARGING/WAITING
    if new_soc < MIN_SOC_BOOKING:
        moved_vehicle["status"] = VehicleStatus.CHARGING.value
    else:
        moved_vehicle["status"] = VehicleStatus.AVAILABLE.value
        
    dest_hub.setdefault("current_vehicles", []).append(moved_vehicle)
    
    # Financial settlement
    rental_cost = calculate_shared_rental_cost(
        duration_minutes=duration_minutes,
        has_voucher=bool(booking.get("voucher_code")),
        extra_free_minutes=booking.get("extra_free_minutes", 0)
    )
    
    wallet = state.setdefault("wallet", {})
    invoice = settle_shared_rental(
        wallet=wallet,
        rental_cost=rental_cost,
        booking_id=booking_id,
        sim_time=sim_now_str
    )
    invoice["distance_km"] = round(duration_minutes / 60 * 15, 2)
    invoice["distance_source"] = "Mô phỏng tốc độ trung bình 15 km/h"

    
    # Complete booking
    booking["status"] = ReservationStatus.COMPLETED.value
    booking["return_time"] = sim_now_str
    booking["return_hub_id"] = return_hub_id
    booking["return_hub_name"] = dest_hub.get("name")
    booking["invoice"] = invoice
    booking["final_soc"] = new_soc
    
    bump_state_version(state)
    return True, invoice, f"Trả xe thành công tại {dest_hub.get('name')}! Hóa đơn chuyến đi đã được quyết toán."

def apply_rerouting_to_booking(
    state: Dict[str, Any],
    booking_id: str,
    new_destination_hub_id: str
) -> Tuple[bool, str]:
    """
    Transfers destination reservation to new Hub and grants 15 extra free rental minutes.
    """
    booking = next((b for b in state.get("bookings", []) if b.get("booking_id") == booking_id), None)
    if not booking:
        return False, f"Không tìm thấy đặt chỗ #{booking_id}."
        
    if booking.get("status") not in [ReservationStatus.RESERVED.value, VehicleStatus.IN_USE.value]:
        return False, "Không thể điều hướng lượt đặt chỗ đã kết thúc."
        
    hubs = state.get("hubs", [])
    new_dest = next((h for h in hubs if h.get("hub_id") == new_destination_hub_id), None)
    if not new_dest:
        return False, "Không tìm thấy Hub đích mới."
        
    if new_dest.get("available_slots", 0) <= 0:
        return False, f"Hub {new_dest.get('name')} hiện không còn chỗ trống."
        
    # Release old destination hold if any
    old_dest_id = booking.get("destination_hub_id")
    if old_dest_id and booking.get("destination_held"):
        old_dest = next((h for h in hubs if h.get("hub_id") == old_dest_id), None)
        if old_dest:
            old_dest["destination_holds"] = max(0, old_dest.get("destination_holds", 0) - 1)
            old_dest["available_slots"] = old_dest.get("available_slots", 0) + 1
            
    # Hold slot at new destination
    new_dest["destination_holds"] = new_dest.get("destination_holds", 0) + 1
    new_dest["available_slots"] = new_dest.get("available_slots", 0) - 1
    
    booking["destination_hub_id"] = new_destination_hub_id
    booking["destination_held"] = True
    
    # Grant 15 extra free rental minutes once
    if booking.get("extra_free_minutes", 0) == 0:
        booking["extra_free_minutes"] = REROUTING_EXTRA_FREE_MINUTES
        
    bump_state_version(state)
    return True, f"Đã chuyển điểm đến sang {new_dest.get('name')} và cộng thêm 15 phút thuê xe miễn phí!"
