# backend/app/routers/personal_ev.py
import uuid, math
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.schemas import RegisterPersonalEVRequest, ReservePersonalSlotRequest, CheckoutPersonalRequest
from app.database import supabase
from app.security import get_current_user
from app.policies import (
    PARKING_HOURLY_VND, PEV_OFFPEAK_KWH_RATE, PEV_PEAK_KWH_RATE,
    PEV_RESERVATION_DEPOSIT_VND, PEV_ARRIVAL_EXPIRY_MINUTES,
    OVERSTAY_GRACE_MINUTES, OVERSTAY_RATE_PER_BLOCK_VND, is_peak_hour
)

router = APIRouter(prefix="/api/personal-ev", tags=["SS2 Personal EV"])

@router.get("/my")
async def get_my_personal_evs(current_user: dict = Depends(get_current_user)):
    evs = supabase.table("personal_evs").select("*").eq("owner_id", current_user["user_id"]).execute().data
    res = supabase.table("personal_reservations").select("*").eq("owner_id", current_user["user_id"]).order("arrival_deadline", desc=True).execute().data
    return {"vehicles": evs, "reservations": res}

@router.post("/register")
async def register_pev(body: RegisterPersonalEVRequest, current_user: dict = Depends(get_current_user)):
    clean_plate = body.plate.strip().upper()
    dup = supabase.table("personal_evs").select("ev_id").eq("plate", clean_plate).execute()
    if dup.data:
        raise HTTPException(status_code=400, detail="Biển số xe đã tồn tại trong hệ thống.")
    ev_id = f"PEV-{uuid.uuid4().hex[:6].upper()}"
    res = supabase.table("personal_evs").insert({
        "ev_id": ev_id,
        "owner_id": current_user["user_id"],
        "plate": clean_plate,
        "type": body.type,
        "brand": body.brand.strip(),
        "battery_kwh": body.battery_kwh
    }).execute()
    return {"message": "Đăng ký xe cá nhân thành công!", "ev": res.data[0]}

@router.post("/reserve")
async def reserve_slot(body: ReservePersonalSlotRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    vehicles = (
        supabase.table("personal_evs")
        .select("ev_id")
        .eq("ev_id", body.ev_id)
        .eq("owner_id", user_id)
        .execute()
        .data
    )
    if not vehicles:
        raise HTTPException(status_code=404, detail="Không tìm thấy xe cá nhân.")

    hubs = supabase.table("hubs").select("*").eq("hub_id", body.hub_id).execute().data
    if not hubs:
        raise HTTPException(status_code=404, detail="Không tìm thấy Hub.")
    hub = hubs[0]
    if hub["available_slots"] <= 0:
        raise HTTPException(status_code=400, detail="Hub đã hết chỗ đỗ.")
    if body.request_charging and hub["ports_available"] <= 0:
        raise HTTPException(status_code=400, detail="Hub đã hết cổng sạc trống.")

    wallets = supabase.table("wallets").select("*").eq("user_id", user_id).execute().data
    if not wallets:
        raise HTTPException(status_code=409, detail="Tài khoản chưa có ví.")
    wallet = wallets[0]
    if wallet["balance"] < PEV_RESERVATION_DEPOSIT_VND:
        raise HTTPException(status_code=400, detail="Số dư ví không đủ 50,000đ đặt cọc.")

    res_id = f"PRES-{uuid.uuid4().hex[:6].upper()}"
    supabase.table("wallets").update({
        "balance": wallet["balance"] - PEV_RESERVATION_DEPOSIT_VND,
        "held_deposit": wallet["held_deposit"] + PEV_RESERVATION_DEPOSIT_VND
    }).eq("user_id", user_id).execute()

    supabase.table("hubs").update({
        "available_slots": hub["available_slots"] - 1,
        "destination_holds": hub["destination_holds"] + 1
    }).eq("hub_id", body.hub_id).execute()

    deadline = datetime.now(timezone.utc) + timedelta(minutes=PEV_ARRIVAL_EXPIRY_MINUTES)
    created = supabase.table("personal_reservations").insert({
        "reservation_id": res_id,
        "owner_id": user_id,
        "ev_id": body.ev_id,
        "hub_id": body.hub_id,
        "request_charging": body.request_charging,
        "current_soc": body.current_soc,
        "arrival_deadline": deadline.isoformat()
    }).execute()
    return {"message": "Đặt chỗ xe cá nhân thành công!", "reservation": created.data[0]}

@router.post("/checkin/{reservation_id}")
async def checkin_pev(reservation_id: str, current_user: dict = Depends(get_current_user)):
    r_res = supabase.table("personal_reservations").select("*").eq("reservation_id", reservation_id).eq("owner_id", current_user["user_id"]).execute()
    if not r_res.data or r_res.data[0]["status"] != "RESERVED":
        raise HTTPException(status_code=400, detail="Lệnh đặt chỗ không hợp lệ.")
    res = r_res.data[0]
    hub = supabase.table("hubs").select("*").eq("hub_id", res["hub_id"]).execute().data[0]
    updates = {"destination_holds": max(0, hub["destination_holds"] - 1)}
    if res["request_charging"] and hub["ports_available"] > 0:
        updates["ports_available"] = hub["ports_available"] - 1
    supabase.table("hubs").update(updates).eq("hub_id", hub["hub_id"]).execute()
    supabase.table("personal_reservations").update({
        "status": "CHECKED_IN",
        "check_in_time": datetime.now(timezone.utc).isoformat()
    }).eq("reservation_id", reservation_id).execute()
    return {"message": "Check-in thành công! Barie đã mở."}

@router.post("/checkout")
async def checkout_pev(body: CheckoutPersonalRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    r_res = supabase.table("personal_reservations").select("*").eq("reservation_id", body.reservation_id).eq("owner_id", user_id).execute()
    if not r_res.data or r_res.data[0]["status"] != "CHECKED_IN":
        raise HTTPException(status_code=400, detail="Xe chưa check-in.")
    res = r_res.data[0]
    hub = supabase.table("hubs").select("*").eq("hub_id", res["hub_id"]).execute().data[0]

    hub_updates = {"available_slots": hub["available_slots"] + 1}
    if res["request_charging"]:
        hub_updates["ports_available"] = min(hub["ports_total"], hub["ports_available"] + 1)
    supabase.table("hubs").update(hub_updates).eq("hub_id", hub["hub_id"]).execute()

    parking_fee = math.ceil(body.duration_hours) * PARKING_HOURLY_VND
    now_local = datetime.now()
    rate = PEV_PEAK_KWH_RATE if is_peak_hour(now_local.time()) else PEV_OFFPEAK_KWH_RATE
    energy_fee = round(body.kwh_charged * rate) if res["request_charging"] else 0
    billable_overstay = max(0, body.overstay_minutes - OVERSTAY_GRACE_MINUTES) if res["request_charging"] else 0
    overstay_fee = ((billable_overstay + 14) // 15) * OVERSTAY_RATE_PER_BLOCK_VND
    total_amount = parking_fee + energy_fee + overstay_fee

    wallet = supabase.table("wallets").select("*").eq("user_id", user_id).execute().data[0]
    released_bal = wallet["balance"] + PEV_RESERVATION_DEPOSIT_VND
    new_held = max(0, wallet["held_deposit"] - PEV_RESERVATION_DEPOSIT_VND)
    deducted = min(released_bal, total_amount)
    debt = max(0, total_amount - released_bal)

    supabase.table("wallets").update({
        "balance": released_bal - deducted,
        "held_deposit": new_held,
        "debt": wallet["debt"] + debt
    }).eq("user_id", user_id).execute()

    invoice = {
        "invoice_id": f"PINV-{uuid.uuid4().hex[:6].upper()}",
        "parking_fee": parking_fee,
        "energy_fee": energy_fee,
        "overstay_fee": overstay_fee,
        "total_amount": total_amount,
        "debt_incurred": debt
    }
    supabase.table("personal_reservations").update({
        "status": "COMPLETED",
        "check_out_time": datetime.now(timezone.utc).isoformat(),
        "invoice": invoice
    }).eq("reservation_id", body.reservation_id).execute()

    return {"message": f"Check-out hoàn tất! Tổng chi phí: {total_amount:,}đ", "invoice": invoice}