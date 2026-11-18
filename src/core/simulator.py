"""
simulator.py – Core Logic for Hub What-if Simulation Scenarios
Smart E-Mobility Hub – ĐHQG-HCM

Features (PLAN.md 4.6 & 4.7):
  • simulate_metro_surge()  – Reproducible Metro surge simulation with unserved arrivals tracking
  • simulate_port_failure() – Port failure simulation distinguishing free vs busy ports with session interruption
  • generate_demand_forecast() – Seeded reproducible queue and wait time forecasting
"""

import random
import copy
import datetime
from typing import Dict, List, Any, Tuple, Optional
import uuid

class HubEventSimulator:
    """
    Bộ mô phỏng sự kiện cho mạng lưới Hub với deepcopy isolation.
    """

    def __init__(self, hubs_data: List[Dict[str, Any]]) -> None:
        self._original = hubs_data

    def simulate_metro_surge(
        self,
        target_hub_id: str = "HUB-002",
        num_new_students: int = 20,
        seed: Optional[int] = 42
    ) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
        """
        Mô phỏng đợt sinh viên đổ về Hub gần ga Metro (KTX Khu B).
        Bảo toàn sức chứa, theo dõi unserved_arrivals nếu trạm hết chỗ.
        """
        rng = random.Random(seed)
        hubs = copy.deepcopy(self._original)
        log: List[str] = []
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        target_hub = next((h for h in hubs if h["hub_id"] == target_hub_id), None)
        if not target_hub:
            return hubs, [f"[{timestamp}] ❌ Không tìm thấy Hub {target_hub_id}."], {}

        log.append(f"[{timestamp}] ⚡ BẮT ĐẦU mô phỏng Metro Surge tại {target_hub['name']} (+{num_new_students} SV, Seed={seed})")

        avail_slots = target_hub.get("available_slots", 0)
        admitted = min(num_new_students, avail_slots)
        unserved = max(0, num_new_students - avail_slots)

        target_hub["available_slots"] -= admitted
        log.append(f"[{timestamp}]   • Chỗ đỗ tiếp nhận: {admitted} xe | Hết chỗ từ chối: {unserved} SV")

        vehicle_types = ["scooter", "bike"]
        new_vehicles = []
        for i in range(admitted):
            v_type = rng.choice(vehicle_types)
            soc = rng.randint(15, 45)
            v_id = f"EV-SURGE-{uuid.uuid4().hex.upper()}"
            veh = {
                "vehicle_id": v_id,
                "type": v_type,
                "battery_soc": soc,
                "status": "AVAILABLE",
                "ownership": "SHARED",
                "hub_id": target_hub_id
            }
            target_hub.setdefault("current_vehicles", []).append(veh)
            new_vehicles.append(veh)

        # Cổng sạc có thể bị chiếm thêm nếu xe pin thấp
        need_charge = sum(1 for v in new_vehicles if v["battery_soc"] < 25)
        ports_avail = target_hub["charging_ports"].get("available", 0)
        ports_taken = min(need_charge, ports_avail)
        target_hub["charging_ports"]["available"] = max(0, ports_avail - ports_taken)

        if ports_taken > 0:
            log.append(f"[{timestamp}]   • {ports_taken} xe pin yếu (<25%) kết nối cổng sạc khả dụng.")

        occupancy = (1 - target_hub["available_slots"] / target_hub["total_slots"]) * 100
        if occupancy >= 85.0:
            log.append(f"[{timestamp}] 🚨 CẢNH BÁO: Hub {target_hub['name']} quá tải ({occupancy:.1f}% lấp đầy)!")

        metrics = {
            "admitted_students": admitted,
            "unserved_students": unserved,
            "new_vehicles_count": admitted,
            "ports_allocated": ports_taken,
            "final_occupancy_pct": round(occupancy, 1)
        }

        return hubs, log, metrics

    def simulate_port_failure(
        self,
        target_hub_id: str = "HUB-004",
        num_ports_down: int = 3,
        seed: Optional[int] = 42
    ) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
        """
        Mô phỏng sự cố cổng sạc:
        - Phân biệt cổng đang rảnh (free port) và cổng đang sạc (busy port).
        - Cổng đang sạc bị ngắt: phiên bị gián đoạn, xe chuyển sang WAITING.
        - Cổng rảnh bị hỏng: giảm available ports.
        """
        rng = random.Random(seed)
        hubs = copy.deepcopy(self._original)
        log: List[str] = []
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        hub = next((h for h in hubs if h["hub_id"] == target_hub_id), None)
        if not hub:
            return hubs, [f"[{timestamp}] ❌ Không tìm thấy Hub {target_hub_id}."], {}

        ports = hub.get("charging_ports", {})
        total_p = ports.get("total", 0)
        avail_p = ports.get("available", 0)
        offline_p = ports.get("offline", 0)
        busy_p = max(0, total_p - avail_p - offline_p)

        actual_down = min(max(0, num_ports_down), total_p - offline_p)
        log.append(f"[{timestamp}] 🔧 BẮT ĐẦU mô phỏng sự cố {actual_down} cổng sạc tại {hub['name']} (Tổng {total_p} cổng, Rảnh: {avail_p}, Đang sạc: {busy_p})")

        # Phân bổ số cổng hỏng vào cổng bận trước rồi đến cổng rảnh
        busy_affected = min(actual_down, busy_p)
        free_affected = actual_down - busy_affected

        # Xử lý cổng rảnh bị hỏng
        ports["available"] = max(0, avail_p - free_affected)
        ports["offline"] = min(total_p, ports.get("offline", 0) + actual_down)

        # Xử lý xe đang sạc bị ngắt quãng
        interrupted_vehicles = []
        if busy_affected > 0:
            for v in hub.get("current_vehicles", []):
                if v.get("status") in ["CHARGING", "charging"] and len(interrupted_vehicles) < busy_affected:
                    v["status"] = "WAITING"
                    interrupted_vehicles.append(v["vehicle_id"])
                    log.append(f"[{timestamp}]   • Xe {v['vehicle_id']} bị gián đoạn sạc do hỏng cổng, chuyển về trạng thái WAITING.")

        log.append(f"[{timestamp}]   • Cổng sạc còn khả dụng tại trạm: {ports['available']} cổng.")
        if ports["available"] == 0:
            log.append(f"[{timestamp}] 🚨 CẢNH BÁO: Hub {hub['name']} đã hết sạch cổng sạc khả dụng!")

        metrics = {
            "failed_ports_total": actual_down,
            "busy_ports_interrupted": busy_affected,
            "free_ports_disabled": free_affected,
            "interrupted_vehicles": interrupted_vehicles,
            "remaining_available_ports": ports["available"]
        }

        return hubs, log, metrics

    @staticmethod
    def generate_demand_forecast(
        base_arrival_rate: float = 10.0,
        surge_multiplier: float = 1.0,
        hours: int = 24,
        seed: Optional[int] = 42
    ) -> List[Dict[str, Any]]:
        """
        Dự đoán nhu cầu có thể tái lập (reproducible forecast).
        Service rate: 8 xe/giờ theo PLAN.md 4.6.
        """
        rng = random.Random(seed)
        forecast = []
        queue = 0
        service_rate = 8

        for h in range(hours):
            hour_label = (6 + h) % 24
            if hour_label in (7, 8, 17, 18):
                peak_factor = 2.5
            elif hour_label in (9, 16, 19):
                peak_factor = 1.5
            else:
                peak_factor = 1.0

            arrivals = int(base_arrival_rate * peak_factor * surge_multiplier + rng.gauss(0, 1.5))
            arrivals = max(0, arrivals)

            queue = max(0, queue + arrivals - service_rate)
            wait_time = round(queue / max(service_rate, 1) * 60, 1)

            forecast.append({
                "hour": f"{hour_label:02d}:00",
                "arrivals": arrivals,
                "queue_length": queue,
                "wait_time_min": wait_time,
            })

        return forecast
