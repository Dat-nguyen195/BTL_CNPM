# backend/app/routers/operations.py (SS4 Dispatch/Incident & SS5 Priority Calculation)
import uuid
from fastapi import APIRouter, Depends, HTTPException
from app.schemas import DispatchCreateRequest
from app.database import supabase
from app.security import get_current_user, require_roles

router = APIRouter(prefix="/api/operations", tags=["SS4 & SS5 Operations"])

@router.get("/charging-queue")
async def get_charging_queue(current_user: dict = Depends(get_current_user)):
    """Tính điểm ưu tiên chuẩn hóa SS5: Score = 0.5*(100-SoC) + 100*I(SoC<20) + 60*I(has_booking) + 30*I(SoC<50)"""
    vehicles = supabase.table("vehicles").select("*").lt("battery_soc", 70).execute().data
    queue = []
    for v in vehicles:
        soc = float(v["battery_soc"])
        has_booking = (v["status"] == "RESERVED")
        score = 0.5 * (100.0 - soc) + (100.0 if soc < 20 else 0) + (60.0 if has_booking else 0) + (30.0 if soc < 50 else 0)
        queue.append({**v, "priority_score": round(score, 1)})
    queue.sort(key=lambda x: (-x["priority_score"], x["vehicle_id"]))
    return queue

@router.post("/dispatch")
async def create_dispatch(
    body: DispatchCreateRequest,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    if body.source_hub_id == body.destination_hub_id:
        raise HTTPException(status_code=400, detail="Hub nguồn và đích phải khác nhau.")
    dst_hub = supabase.table("hubs").select("*").eq("hub_id", body.destination_hub_id).execute().data[0]
    if len(body.vehicle_ids) > dst_hub["available_slots"]:
        raise HTTPException(status_code=400, detail="Hub đích không đủ chỗ trống tiếp nhận.")

    src_hub = supabase.table("hubs").select("*").eq("hub_id", body.source_hub_id).execute().data[0]
    for vid in body.vehicle_ids:
        supabase.table("vehicles").update({"status": "DISPATCHED"}).eq("vehicle_id", vid).execute()

    supabase.table("hubs").update({"available_slots": src_hub["available_slots"] + len(body.vehicle_ids)}).eq("hub_id", src_hub["hub_id"]).execute()
    supabase.table("hubs").update({
        "available_slots": dst_hub["available_slots"] - len(body.vehicle_ids),
        "destination_holds": dst_hub["destination_holds"] + len(body.vehicle_ids)
    }).eq("hub_id", dst_hub["hub_id"]).execute()

    disp_id = f"DISP-{uuid.uuid4().hex[:6].upper()}"
    res = supabase.table("dispatches").insert({
        "dispatch_id": disp_id,
        "source_hub_id": body.source_hub_id,
        "destination_hub_id": body.destination_hub_id,
        "vehicle_ids": body.vehicle_ids,
        "reason": body.reason
    }).execute()
    return {"message": f"Tạo lệnh điều phối {disp_id} thành công!", "dispatch": res.data[0]}