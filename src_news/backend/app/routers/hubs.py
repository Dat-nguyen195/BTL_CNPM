import random
from fastapi import APIRouter, Depends, HTTPException
from app.database import supabase
from app.security import get_current_user, require_roles

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