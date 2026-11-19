import uuid
import random
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.schemas import CreateBookingRequest, PickupRequest, ReturnRequest
from app.database import supabase
from app.security import get_current_user
from app.policies import (
    SHARED_DEPOSIT_VND, SHARED_EXPIRY_MINUTES, SHARED_FREE_MINUTES,
    SHARED_RATE_PER_MINUTE_VND, MIN_SOC_BOOKING, SHARED_VOUCHERS
)

router = APIRouter(prefix="/api/bookings", tags=["SS1 Shared EV Bookings"])

@router.get("/my")
async def get_my_bookings(current_user: dict = Depends(get_current_user)):
    res = supabase.table("bookings").select("*").eq("student_id", current_user["user_id"]).order("created_at", desc=True).execute()
    return res.data

@router.post("/create")
async def create_booking(body: CreateBookingRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    # 1. Kiểm tra booking đang hoạt động
    active = supabase.table("bookings").select("booking_id").eq("student_id", user_id).in_("status", ["RESERVED", "IN_USE"]).execute()
    if active.data:
        raise HTTPException(status_code=400, detail=f"Bạn đang có lượt đặt xe #{active.data[0]['booking_id']} chưa hoàn tất.")

    # 2. Kiểm tra xe & pin
    veh_res = supabase.table("vehicles").select("*").eq("vehicle_id", body.vehicle_id).eq("hub_id", body.hub_id).execute()
    if not veh_res.data:
        raise HTTPException(status_code=404, detail="Không tìm thấy phương tiện tại trạm.")
    veh = veh_res.data[0]
    if veh["status"] != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Xe hiện không ở trạng thái sẵn sàng.")
    if veh["battery_soc"] < MIN_SOC_BOOKING:
        raise HTTPException(status_code=400, detail=f"Pin xe ({veh['battery_soc']}%) thấp hơn mức tối thiểu {MIN_SOC_BOOKING}%.")

    # 3. Kiểm tra ví & khóa cọc 50,000đ
    wallet = supabase.table("wallets").select("*").eq("user_id", user_id).execute().data[0]
    if wallet["debt"] > 0:
        raise HTTPException(status_code=400, detail=f"Tài khoản đang có nợ {wallet['debt']:,}đ. Vui lòng thanh toán trước.")
    if wallet["balance"] < SHARED_DEPOSIT_VND:
        raise HTTPException(status_code=400, detail="Số dư ví không đủ 50,000đ để đặt cọc.")

    # 4. Kiểm tra Hub đích nếu chọn giữ chỗ trước
    dest_held = False
    if body.destination_hub_id:
        dest_hub = supabase.table("hubs").select("*").eq("hub_id", body.destination_hub_id).execute().data
        if not dest_hub or dest_hub[0]["available_slots"] <= 0:
            raise HTTPException(status_code=400, detail="Hub đích đã hết chỗ trống.")
        supabase.table("hubs").update({
            "available_slots": dest_hub[0]["available_slots"] - 1,
            "destination_holds": dest_hub[0]["destination_holds"] + 1
        }).eq("hub_id", body.destination_hub_id).execute()
        dest_held = True

    booking_id = f"BK-{uuid.uuid4().hex[:6].upper()}"
    pin_code = str(random.randint(1000, 9999))
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=SHARED_EXPIRY_MINUTES)

    # Cập nhật ví & ghi sổ cái
    new_bal = wallet["balance"] - SHARED_DEPOSIT_VND
    new_held = wallet["held_deposit"] + SHARED_DEPOSIT_VND
    supabase.table("wallets").update({"balance": new_bal, "held_deposit": new_held}).eq("user_id", user_id).execute()
    supabase.table("ledger_transactions").insert({
        "tx_id": f"TX-{uuid.uuid4().hex[:8].upper()}",
        "user_id": user_id,
        "tx_type": "HOLD_DEPOSIT",
        "amount": -SHARED_DEPOSIT_VND,
        "balance_after": new_bal,
        "held_after": new_held,
        "debt_after": wallet["debt"],
        "booking_id": booking_id,
        "note": f"Tạm khóa cọc đặt xe {body.vehicle_id}"
    }).execute()

    # Khóa xe & tạo booking
    supabase.table("vehicles").update({"status": "RESERVED"}).eq("vehicle_id", body.vehicle_id).execute()
    voucher = body.voucher_code.strip().upper() if body.voucher_code else None
    booking_data = {
        "booking_id": booking_id,
        "student_id": user_id,
        "hub_id": body.hub_id,
        "vehicle_id": body.vehicle_id,
        "destination_hub_id": body.destination_hub_id,
        "destination_held": dest_held,
        "voucher_code": voucher if voucher in SHARED_VOUCHERS else None,
        "pin_code": pin_code,
        "deposit_held": SHARED_DEPOSIT_VND,
        "status": "RESERVED",
        "expires_at": expires_at.isoformat()
    }
    res = supabase.table("bookings").insert(booking_data).execute()
    return {"message": "Đặt giữ xe thành công!", "booking": res.data[0]}

@router.post("/pickup")
async def pickup_vehicle(body: PickupRequest, current_user: dict = Depends(get_current_user)):
    b_res = supabase.table("bookings").select("*").eq("booking_id", body.booking_id).eq("student_id", current_user["user_id"]).execute()
    if not b_res.data:
        raise HTTPException(status_code=404, detail="Không tìm thấy mã đặt chỗ.")
    booking = b_res.data[0]
    if booking["status"] != "RESERVED":
        raise HTTPException(status_code=400, detail="Trạng thái đặt chỗ không hợp lệ để nhận xe.")
    if booking["pin_code"] != body.pin_code.strip():
        raise HTTPException(status_code=400, detail="Mã PIN nhận xe không chính xác.")

    # Giải phóng 1 chỗ đỗ tại Hub xuất phát
    hub = supabase.table("hubs").select("*").eq("hub_id", booking["hub_id"]).execute().data[0]
    supabase.table("hubs").update({"available_slots": hub["available_slots"] + 1}).eq("hub_id", hub["hub_id"]).execute()
    supabase.table("vehicles").update({"status": "IN_USE"}).eq("vehicle_id", booking["vehicle_id"]).execute()
    supabase.table("bookings").update({
        "status": "IN_USE",
        "pickup_time": datetime.now(timezone.utc).isoformat()
    }).eq("booking_id", booking["booking_id"]).execute()

    return {"message": f"Mở khóa xe {booking['vehicle_id']} thành công!"}

@router.post("/return")
async def return_vehicle(body: ReturnRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    b_res = supabase.table("bookings").select("*").eq("booking_id", body.booking_id).eq("student_id", user_id).execute()
    if not b_res.data or b_res.data[0]["status"] != "IN_USE":
        raise HTTPException(status_code=400, detail="Không tìm thấy chuyến đi đang hoạt động.")
    booking = b_res.data[0]

    dest_hub = supabase.table("hubs").select("*").eq("hub_id", body.return_hub_id).execute().data[0]
    is_pre_held = (booking["destination_hub_id"] == body.return_hub_id and booking["destination_held"])

    if is_pre_held:
        supabase.table("hubs").update({
            "destination_holds": max(0, dest_hub["destination_holds"] - 1)
        }).eq("hub_id", dest_hub["hub_id"]).execute()
    else:
        if dest_hub["available_slots"] <= 0:
            raise HTTPException(status_code=400, detail="Hub trả xe đã hết chỗ trống!")
        supabase.table("hubs").update({
            "available_slots": dest_hub["available_slots"] - 1
        }).eq("hub_id", dest_hub["hub_id"]).execute()

    # Cập nhật pin & vị trí xe
    veh = supabase.table("vehicles").select("*").eq("vehicle_id", booking["vehicle_id"]).execute().data[0]
    new_soc = max(5, veh["battery_soc"] - min(30, body.duration_minutes // 3))
    new_v_status = "CHARGING" if new_soc < MIN_SOC_BOOKING else "AVAILABLE"
    supabase.table("vehicles").update({
        "hub_id": body.return_hub_id,
        "battery_soc": new_soc,
        "status": new_v_status
    }).eq("vehicle_id", veh["vehicle_id"]).execute()

    # Quyết toán phí thuê xe
    billable_min = max(0, body.duration_minutes - SHARED_FREE_MINUTES - booking.get("extra_free_minutes", 0))
    base_fee = billable_min * SHARED_RATE_PER_MINUTE_VND
    discount = min(base_fee, SHARED_VOUCHERS.get(booking["voucher_code"], 0)) if booking["voucher_code"] else 0
    final_fee = max(0, base_fee - discount)

    wallet = supabase.table("wallets").select("*").eq("user_id", user_id).execute().data[0]
    held = wallet["held_deposit"]
    new_held = max(0, held - SHARED_DEPOSIT_VND)
    refund = max(0, SHARED_DEPOSIT_VND - final_fee)
    extra_needed = max(0, final_fee - SHARED_DEPOSIT_VND)

    if wallet["balance"] + refund >= extra_needed:
        new_bal = wallet["balance"] + refund - extra_needed
        debt_incurred = 0
    else:
        debt_incurred = extra_needed - wallet["balance"]
        new_bal = 0

    new_debt = wallet["debt"] + debt_incurred
    supabase.table("wallets").update({
        "balance": new_bal,
        "held_deposit": new_held,
        "debt": new_debt
    }).eq("user_id", user_id).execute()

    invoice = {
        "invoice_id": f"INV-{uuid.uuid4().hex[:8].upper()}",
        "duration_minutes": body.duration_minutes,
        "billable_minutes": billable_min,
        "base_fee": base_fee,
        "discount": discount,
        "final_fee": final_fee,
        "refund_to_wallet": refund,
        "debt_incurred": debt_incurred
    }

    supabase.table("ledger_transactions").insert({
        "tx_id": f"TX-{uuid.uuid4().hex[:8].upper()}",
        "user_id": user_id,
        "tx_type": "SETTLE_RENTAL_FEE",
        "amount": -final_fee,
        "balance_after": new_bal,
        "held_after": new_held,
        "debt_after": new_debt,
        "booking_id": booking["booking_id"],
        "note": f"Quyết toán chuyến đi {booking['booking_id']} ({final_fee:,}đ)"
    }).execute()

    supabase.table("bookings").update({
        "status": "COMPLETED",
        "return_time": datetime.now(timezone.utc).isoformat(),
        "destination_held": False,
        "invoice": invoice
    }).eq("booking_id", booking["booking_id"]).execute()

    return {"message": "Trả xe & quyết toán thành công!", "invoice": invoice}

@router.post("/cancel/{booking_id}")
async def cancel_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    b_res = supabase.table("bookings").select("*").eq("booking_id", booking_id).eq("student_id", user_id).execute()
    if not b_res.data or b_res.data[0]["status"] != "RESERVED":
        raise HTTPException(status_code=400, detail="Không thể hủy lượt đặt này.")
    booking = b_res.data[0]

    supabase.table("vehicles").update({"status": "AVAILABLE"}).eq("vehicle_id", booking["vehicle_id"]).execute()
    if booking["destination_hub_id"] and booking["destination_held"]:
        dh = supabase.table("hubs").select("*").eq("hub_id", booking["destination_hub_id"]).execute().data[0]
        supabase.table("hubs").update({
            "available_slots": dh["available_slots"] + 1,
            "destination_holds": max(0, dh["destination_holds"] - 1)
        }).eq("hub_id", dh["hub_id"]).execute()

    wallet = supabase.table("wallets").select("*").eq("user_id", user_id).execute().data[0]
    new_bal = wallet["balance"] + SHARED_DEPOSIT_VND
    new_held = max(0, wallet["held_deposit"] - SHARED_DEPOSIT_VND)
    supabase.table("wallets").update({"balance": new_bal, "held_deposit": new_held}).eq("user_id", user_id).execute()
    supabase.table("ledger_transactions").insert({
        "tx_id": f"TX-{uuid.uuid4().hex[:8].upper()}",
        "user_id": user_id,
        "tx_type": "REFUND_DEPOSIT_FULL",
        "amount": SHARED_DEPOSIT_VND,
        "balance_after": new_bal,
        "held_after": new_held,
        "debt_after": wallet["debt"],
        "booking_id": booking_id,
        "note": "Hoàn 100% cọc do hủy đặt xe hợp lệ"
    }).execute()

    supabase.table("bookings").update({"status": "CANCELLED", "destination_held": False}).eq("booking_id", booking_id).execute()
    return {"message": "Hủy đặt xe thành công! Đã hoàn 50,000đ về ví."}