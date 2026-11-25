import uuid
from fastapi import APIRouter, Depends, HTTPException
from app.schemas import DispatchCreateRequest, IncidentIsolateRequest
from app.database import supabase
from app.security import get_current_user, require_roles
from app.policies import HUB_POWER_CAP_KW, DEFAULT_PORT_KW

router = APIRouter(prefix="/api/operations", tags=["SS4 & SS5 Operations"])

@router.get("/charging-queue")
async def get_charging_queue(current_user: dict = Depends(get_current_user)):
    vehicles = supabase.table("vehicles").select("*").lt("battery_soc", 70).execute().data
    queue = []
    for v in vehicles:
        soc = float(v["battery_soc"])
        has_booking = (v["status"] == "RESERVED")
        score = 0.5 * (100.0 - soc) + (100.0 if soc < 20 else 0) + (60.0 if has_booking else 0) + (30.0 if soc < 50 else 0)
        queue.append({**v, "priority_score": round(score, 1)})
    queue.sort(key=lambda x: (-x["priority_score"], x["vehicle_id"]))
    return queue

@router.post("/charging/allocate/{hub_id}")
async def allocate_charging_ports(
    hub_id: str,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    hub = supabase.table("hubs").select("*").eq("hub_id", hub_id).execute().data
    if not hub:
        raise HTTPException(status_code=404, detail="Không tìm thấy Hub.")
    h = hub[0]
    avail_ports = h["charging_ports"]["available"] if isinstance(h.get("charging_ports"), dict) else h["ports_available"]
    if avail_ports <= 0:
        raise HTTPException(status_code=400, detail="Hub không còn cổng sạc trống.")

    vehicles = supabase.table("vehicles").select("*").eq("hub_id", hub_id).execute().data
    charging_now = [v for v in vehicles if v["status"] == "CHARGING"]
    power_used = len(charging_now) * DEFAULT_PORT_KW

    candidates = [v for v in vehicles if v["status"] == "AVAILABLE" and v["battery_soc"] < 70]
    candidates.sort(key=lambda v: -(0.5 * (100 - v["battery_soc"]) + (100 if v["battery_soc"] < 20 else 0) + (30 if v["battery_soc"] < 50 else 0)))

    allocated = []
    for v in candidates:
        if avail_ports <= 0 or power_used + DEFAULT_PORT_KW > HUB_POWER_CAP_KW:
            break
        supabase.table("vehicles").update({"status": "CHARGING"}).eq("vehicle_id", v["vehicle_id"]).execute()
        allocated.append(v["vehicle_id"])
        avail_ports -= 1
        power_used += DEFAULT_PORT_KW

    if not allocated:
        return {"message": "Không có xe đủ điều kiện hoặc đã chạm trần công suất 150kW.", "allocated": []}

    supabase.table("hubs").update({"ports_available": avail_ports}).eq("hub_id", hub_id).execute()
    return {"message": f"Đã cấp cổng sạc cho {len(allocated)} xe ({', '.join(allocated)}).", "allocated": allocated}

@router.post("/charging/unplug/{vehicle_id}")
async def unplug_charging_vehicle(
    vehicle_id: str,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    v_res = supabase.table("vehicles").select("*").eq("vehicle_id", vehicle_id).execute().data
    if not v_res or v_res[0]["status"] != "CHARGING":
        raise HTTPException(status_code=400, detail="Xe không ở trạng thái đang sạc.")
    v = v_res[0]
    hub = supabase.table("hubs").select("*").eq("hub_id", v["hub_id"]).execute().data[0]
    new_soc = min(100, v["battery_soc"] + 30)
    supabase.table("vehicles").update({"status": "AVAILABLE", "battery_soc": new_soc}).eq("vehicle_id", vehicle_id).execute()
    supabase.table("hubs").update({"ports_available": min(hub["ports_total"], hub["ports_available"] + 1)}).eq("hub_id", hub["hub_id"]).execute()
    return {"message": f"Đã rút sạc xe {vehicle_id} (Pin: {new_soc}%) và giải phóng cổng sạc."}

@router.get("/dispatches")
async def list_dispatches(current_user: dict = Depends(get_current_user)):
    return supabase.table("dispatches").select("*").order("created_at", desc=True).execute().data

@router.post("/dispatch")
async def create_dispatch(
    body: DispatchCreateRequest,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    if body.source_hub_id == body.destination_hub_id:
        raise HTTPException(status_code=400, detail="Hub nguồn và đích phải khác nhau.")
    if not body.vehicle_ids:
        raise HTTPException(status_code=400, detail="Vui lòng chọn ít nhất 1 xe.")
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

@router.post("/dispatch/{dispatch_id}/receive")
async def receive_dispatch(
    dispatch_id: str,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    d_res = supabase.table("dispatches").select("*").eq("dispatch_id", dispatch_id).execute().data
    if not d_res:
        raise HTTPException(status_code=404, detail="Không tìm thấy lệnh điều phối.")
    disp = d_res[0]
    vids = disp.get("vehicle_ids") or []
    dst_hub = supabase.table("hubs").select("*").eq("hub_id", disp["destination_hub_id"]).execute().data[0]

    for vid in vids:
        supabase.table("vehicles").update({"hub_id": dst_hub["hub_id"], "status": "AVAILABLE"}).eq("vehicle_id", vid).execute()

    supabase.table("hubs").update({
        "destination_holds": max(0, dst_hub["destination_holds"] - len(vids))
    }).eq("hub_id", dst_hub["hub_id"]).execute()
    return {"message": f"Đã tiếp nhận {len(vids)} xe tại {dst_hub['name']}!"}

@router.post("/incidents/isolate")
async def isolate_incident(
    body: IncidentIsolateRequest,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    hub = supabase.table("hubs").select("*").eq("hub_id", body.hub_id).execute().data[0]
    if body.target_type == "VEHICLE":
        if not body.vehicle_id:
            raise HTTPException(status_code=400, detail="Thiếu mã xe cần cách ly.")
        supabase.table("vehicles").update({"status": "INCIDENT"}).eq("vehicle_id", body.vehicle_id).execute()
        return {"message": f"Đã cách ly xe {body.vehicle_id} sang trạng thái INCIDENT."}
    else:
        if hub["ports_available"] <= 0:
            raise HTTPException(status_code=400, detail="Không còn cổng khả dụng để ngắt.")
        supabase.table("hubs").update({"ports_available": hub["ports_available"] - 1}).eq("hub_id", hub["hub_id"]).execute()
        return {"message": f"Đã cách ly 1 cổng sạc tại {hub['name']}."}

@router.post("/incidents/recover")
async def recover_incident(
    body: IncidentIsolateRequest,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    hub = supabase.table("hubs").select("*").eq("hub_id", body.hub_id).execute().data[0]
    if body.target_type == "VEHICLE":
        if not body.vehicle_id:
            raise HTTPException(status_code=400, detail="Thiếu mã xe cần khôi phục.")
        supabase.table("vehicles").update({"status": "AVAILABLE"}).eq("vehicle_id", body.vehicle_id).execute()
        return {"message": f"Đã khôi phục xe {body.vehicle_id} về AVAILABLE."}
    else:
        if hub["ports_available"] >= hub["ports_total"]:
            raise HTTPException(status_code=400, detail="Tất cả cổng sạc tại trạm đã hoạt động.")
        supabase.table("hubs").update({"ports_available": hub["ports_available"] + 1}).eq("hub_id", hub["hub_id"]).execute()
        return {"message": f"Đã khôi phục 1 cổng sạc tại {hub['name']}."}