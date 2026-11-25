import random
from fastapi import APIRouter, Depends, HTTPException
from app.database import supabase
from app.security import get_current_user, require_roles
from app.schemas import SimMetroSurgeRequest, SimPortFailureRequest

router = APIRouter(prefix="/api/hubs", tags=["Hubs & Monitoring"])

@router.get("")
async def list_hubs(current_user: dict = Depends(get_current_user)):
    hubs = supabase.table("hubs").select("*").order("hub_id").execute().data
    vehicles = supabase.table("vehicles").select("*").execute().data
    for h in hubs:
        h["current_vehicles"] = [v for v in vehicles if v["hub_id"] == h["hub_id"]]
        occ = ((h["total_slots"] - h["available_slots"]) / h["total_slots"] * 100) if h["total_slots"] > 0 else 0
        h["occupancy_pct"] = round(occ, 1)
        h["alert_level"] = "FULL" if occ >= 100 else ("CRITICAL" if occ >= 85 else ("WARNING" if occ >= 70 else "NORMAL"))
    return hubs

@router.get("/forecast")
async def demand_forecast(
    base_rate: float = 15.0,
    surge_multiplier: float = 1.5,
    hours: int = 24,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    rng = random.Random(42)
    forecast = []
    queue = 0
    service_rate = 8
    for h in range(hours):
        hour_label = (6 + h) % 24
        peak_factor = 2.5 if hour_label in (7, 8, 17, 18) else (1.5 if hour_label in (9, 16, 19) else 1.0)
        arrivals = max(0, int(base_rate * peak_factor * surge_multiplier + rng.gauss(0, 1.5)))
        queue = max(0, queue + arrivals - service_rate)
        forecast.append({
            "hour": f"{hour_label:02d}:00",
            "arrivals": arrivals,
            "queue_length": queue,
            "wait_time_min": round(queue / service_rate * 60, 1)
        })
    return forecast

@router.post("/simulate/metro-surge")
async def simulate_metro_surge(
    body: SimMetroSurgeRequest,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    hub = supabase.table("hubs").select("*").eq("hub_id", body.target_hub_id).execute().data
    if not hub:
        raise HTTPException(status_code=404, detail="Không tìm thấy Hub.")
    h = hub[0]
    admitted = min(body.num_new_students, h["available_slots"])
    unserved = max(0, body.num_new_students - h["available_slots"])
    new_avail = h["available_slots"] - admitted
    occ = round((1 - new_avail / h["total_slots"]) * 100, 1) if h["total_slots"] > 0 else 0
    return {
        "hub_name": h["name"],
        "admitted_students": admitted,
        "unserved_students": unserved,
        "before_slots": h["available_slots"],
        "after_slots": new_avail,
        "final_occupancy_pct": occ
    }

@router.post("/simulate/port-failure")
async def simulate_port_failure(
    body: SimPortFailureRequest,
    current_user: dict = Depends(require_roles(["OPERATOR", "ADMIN"]))
):
    hubs = supabase.table("hubs").select("*").execute().data
    h = next((x for x in hubs if x["hub_id"] == body.target_hub_id), None)
    if not h:
        raise HTTPException(status_code=404, detail="Không tìm thấy Hub.")
    vehicles = supabase.table("vehicles").select("*").eq("hub_id", body.target_hub_id).execute().data
    charging_vs = [v for v in vehicles if v["status"] == "CHARGING"]
    busy_p = max(0, h["ports_total"] - h["ports_available"])
    actual_down = min(body.num_ports_down, h["ports_total"])
    busy_affected = min(actual_down, busy_p)
    free_affected = actual_down - busy_affected
    remaining_ports = max(0, h["ports_available"] - free_affected)
    alternatives = [
        {"hub_id": x["hub_id"], "name": x["name"], "available_ports": x["ports_available"], "available_slots": x["available_slots"]}
        for x in hubs if x["hub_id"] != body.target_hub_id and x["ports_available"] > 0
    ][:2]
    return {
        "hub_name": h["name"],
        "failed_ports_total": actual_down,
        "busy_ports_interrupted": busy_affected,
        "interrupted_vehicles": [v["vehicle_id"] for v in charging_vs[:busy_affected]],
        "remaining_available_ports": remaining_ports,
        "alternatives": alternatives
    }