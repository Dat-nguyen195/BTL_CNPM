"""
state.py – Typed Vocabularies, Invariants, and Session State Management
Smart E-Mobility Hub – ĐHQG-HCM
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import copy
import json
import os

# ──────────────────────────────────────────────
# 1. TYPED VOCABULARIES (UPPER_CASE)
# ──────────────────────────────────────────────
class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    IN_USE = "IN_USE"
    CHARGING = "CHARGING"
    DISPATCHED = "DISPATCHED"
    INCIDENT = "INCIDENT"
    OFFLINE = "OFFLINE"

class ReservationStatus(str, Enum):
    RESERVED = "RESERVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class PortStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"
    CHARGING = "CHARGING"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"

class ChargingStatus(str, Enum):
    WAITING = "WAITING"
    SCHEDULED = "SCHEDULED"
    CHARGING = "CHARGING"
    COMPLETED = "COMPLETED"
    GRACE_PERIOD = "GRACE_PERIOD"
    OVERSTAY = "OVERSTAY"

class Ownership(str, Enum):
    SHARED = "SHARED"
    PERSONAL = "PERSONAL"

class UserRole(str, Enum):
    STUDENT = "STUDENT"
    OPERATOR = "OPERATOR"
    TECHNICIAN = "TECHNICIAN"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"

# Mapping for backward-compatibility with raw seed files
LEGACY_STATUS_MAP = {
    "parked": VehicleStatus.AVAILABLE.value,
    "charging": VehicleStatus.CHARGING.value,
    "reserved": VehicleStatus.RESERVED.value,
    "available": VehicleStatus.AVAILABLE.value,
    "in_use": VehicleStatus.IN_USE.value,
    "dispatched": VehicleStatus.DISPATCHED.value,
    "incident": VehicleStatus.INCIDENT.value,
    "offline": VehicleStatus.OFFLINE.value,
}

def normalize_status(status_str: str) -> str:
    """Converts any lowercase/legacy status to canonical UPPER_CASE."""
    if not status_str:
        return VehicleStatus.AVAILABLE.value
    cleaned = status_str.strip().lower()
    return LEGACY_STATUS_MAP.get(cleaned, status_str.upper())

# ──────────────────────────────────────────────
# 2. INVARIANT CHECKERS
# ──────────────────────────────────────────────
def validate_hub_capacity(hub: Dict[str, Any]) -> bool:
    """
    Enforces slot capacity conservation:
    available_slots + present_vehicles + destination_holds + background_occupied == total_slots
    """
    total = hub.get("total_slots", 0)
    avail = hub.get("available_slots", 0)
    bg = hub.get("background_occupied", 0)
    holds = hub.get("destination_holds", 0)
    
    # Listed vehicles that are physically occupying a slot in the Hub
    present = len([v for v in hub.get("current_vehicles", []) if v.get("status") != VehicleStatus.IN_USE.value])
    return (avail + present + holds + bg) == total

def validate_state_invariants(state: Dict[str, Any]) -> List[str]:
    """Returns list of invariant violation messages, or empty list if valid."""
    errors = []
    hubs = state.get("hubs", [])
    for h in hubs:
        if not validate_hub_capacity(h):
            total = h.get("total_slots", 0)
            avail = h.get("available_slots", 0)
            bg = h.get("background_occupied", 0)
            holds = h.get("destination_holds", 0)
            present = len([v for v in h.get("current_vehicles", []) if v.get("status") != VehicleStatus.IN_USE.value])
            errors.append(
                f"Hub {h.get('hub_id')}: capacity mismatch (avail={avail} + present={present} + holds={holds} + bg={bg} != total={total})"
            )
            
    wallet = state.get("wallet", {})
    if wallet:
        balance = wallet.get("balance", 0)
        held = wallet.get("held_deposit", 0)
        debt = wallet.get("debt", 0)
        if balance < 0:
            errors.append(f"Wallet balance negative: {balance}")
        if held < 0:
            errors.append(f"Wallet held deposit negative: {held}")
        if debt < 0:
            errors.append(f"Wallet debt negative: {debt}")
            
    return errors

# ──────────────────────────────────────────────
# 3. SESSION INITIALIZATION & RESET
# ──────────────────────────────────────────────
DEFAULT_INITIAL_SIM_TIME = "2026-10-21 08:00:00"

def get_default_seed_path() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock_hubs.json")

def load_and_normalize_hubs(seed_path: Optional[str] = None) -> List[Dict[str, Any]]:
    if not seed_path:
        seed_path = get_default_seed_path()
    with open(seed_path, "r", encoding="utf-8") as f:
        raw_hubs = json.load(f)

    normalized = []
    for raw in raw_hubs:
        h = copy.deepcopy(raw)
        vehicles = h.get("current_vehicles", [])
        for v in vehicles:
            v["status"] = normalize_status(v.get("status", "AVAILABLE"))
            v["ownership"] = Ownership.SHARED.value
            if "hub_id" not in v:
                v["hub_id"] = h["hub_id"]

        h["destination_holds"] = h.get("destination_holds", 0)
        
        # Calculate background load explicitly
        total = h.get("total_slots", 40)
        avail = h.get("available_slots", 15)
        present = len([v for v in vehicles if v["status"] != VehicleStatus.IN_USE.value])
        bg = total - avail - present - h["destination_holds"]
        if bg < 0:
            bg = 0
            h["available_slots"] = total - present - h["destination_holds"]
        h["background_occupied"] = bg
        
        # Ports normalization
        ports = h.get("charging_ports", {"total": 10, "available": 4})
        h["charging_ports"] = ports
        normalized.append(h)
    return normalized

def init_session_state(session_state_dict: Any, force_reset: bool = False):
    """
    Centralizes all session_state keys once.
    Only seeds missing keys; preserves existing empty logs unless force_reset=True.
    """
    if force_reset or "hubs" not in session_state_dict:
        session_state_dict["hubs"] = load_and_normalize_hubs()

    if force_reset or "state_version" not in session_state_dict:
        session_state_dict["state_version"] = 1

    if force_reset or "current_sim_time" not in session_state_dict:
        session_state_dict["current_sim_time"] = DEFAULT_INITIAL_SIM_TIME

    if force_reset or "active_user" not in session_state_dict:
        session_state_dict["active_user"] = {
            "user_id": "SV-2026",
            "name": "Nguyễn Thành Đạt",
            "mssv": "2410709",
            "role": UserRole.STUDENT.value
        }

    if force_reset or "wallet" not in session_state_dict:
        session_state_dict["wallet"] = {
            "balance": 150_000,
            "held_deposit": 0,
            "debt": 0,
            "ledger": [
                {
                    "tx_id": "TX-INIT-001",
                    "time": "2026-10-21 07:30:00",
                    "type": "DEPOSIT_TOPUP",
                    "amount": 150_000,
                    "balance_after": 150_000,
                    "booking_id": None,
                    "note": "Nạp tiền khởi tạo tài khoản sinh viên VNU"
                }
            ]
        }

    if force_reset or "bookings" not in session_state_dict:
        session_state_dict["bookings"] = []

    if force_reset or "personal_evs" not in session_state_dict:
        session_state_dict["personal_evs"] = [
            {
                "ev_id": "PEV-2026",
                "owner": "Nguyễn Anh Tài",
                "mssv": "2413035",
                "plate": "59-X1 12345",
                "type": "scooter",
                "brand": "VinFast Klara S",
                "battery_kwh": 2.0,
                "registered_at": "2026-10-18 08:30",
                "status": "REGISTERED",
                "ownership": Ownership.PERSONAL.value
            },
            {
                "ev_id": "PEV-2027",
                "owner": "Trần Thị B",
                "mssv": "2212345",
                "plate": "59-V2 67890",
                "type": "scooter",
                "brand": "VinFast Feliz",
                "battery_kwh": 2.2,
                "registered_at": "2026-10-18 09:15",
                "status": "REGISTERED",
                "ownership": Ownership.PERSONAL.value
            }
        ]

    if force_reset or "personal_reservations" not in session_state_dict:
        session_state_dict["personal_reservations"] = []

    if force_reset or "charging_queue" not in session_state_dict:
        session_state_dict["charging_queue"] = []

    if force_reset or "charging_sessions" not in session_state_dict:
        session_state_dict["charging_sessions"] = []

    if force_reset or "dispatch_log" not in session_state_dict:
        session_state_dict["dispatch_log"] = [
            {
                "dispatch_id": "DISP-001",
                "time": "2026-10-19 07:45:00",
                "from_hub": "Hub KTX Khu B",
                "to_hub": "Hub KTX Khu A",
                "vehicle_ids": ["EV-B001", "EV-B003", "EV-B004", "EV-B007", "EV-B008"],
                "vehicles_count": 5,
                "reason": "Cân bằng tải giờ cao điểm sáng Metro",
                "status": "COMPLETED"
            }
        ]

    if force_reset or "incident_log" not in session_state_dict:
        session_state_dict["incident_log"] = [
            {
                "incident_id": "INC-001",
                "time": "2026-10-19 08:10:00",
                "hub_id": "HUB-004",
                "hub_name": "Hub Trường ĐH Bách Khoa",
                "target_type": "VEHICLE",
                "target_id": "EV-D007",
                "type": "Lỗi cổng sạc / cáp",
                "severity": "Cao",
                "status": "RESOLVED",
                "resolved_at": "2026-10-19 09:30:00",
                "note": "Cổng #3 không nhận tiếp xúc điện; kỹ thuật viên đã thay cáp"
            }
        ]

    if force_reset or "notifications" not in session_state_dict:
        session_state_dict["notifications"] = []

    if force_reset or "sim_preview_ss6" not in session_state_dict:
        session_state_dict["sim_preview_ss6"] = None

    if force_reset or "sim_preview_ss7" not in session_state_dict:
        session_state_dict["sim_preview_ss7"] = None

def advance_sim_time(session_state_dict: Any, minutes: int = 15) -> str:
    """Advances simulated clock by given minutes without python sleep."""
    current_str = session_state_dict.get("current_sim_time", DEFAULT_INITIAL_SIM_TIME)
    try:
        dt = datetime.strptime(current_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.strptime(DEFAULT_INITIAL_SIM_TIME, "%Y-%m-%d %H:%M:%S")
    new_dt = dt + timedelta(minutes=minutes)
    new_str = new_dt.strftime("%Y-%m-%d %H:%M:%S")
    session_state_dict["current_sim_time"] = new_str
    session_state_dict["state_version"] = session_state_dict.get("state_version", 1) + 1
    return new_str

def advance_demo_clock(state: Any, minutes: int = 15) -> None:
    """Advance the shared demo clock and the charging sessions it drives."""
    scheduler = state.get("charging_scheduler")
    if scheduler is not None:
        events = scheduler.advance_simulation_tick(
            minutes=minutes, sim_time=state.get("current_sim_time")
        )
        state.setdefault("charging_notifications", []).extend(events)
    advance_sim_time(state, minutes)

def bump_state_version(session_state_dict: Any):
    """Increments the monotonic state version."""
    session_state_dict["state_version"] = session_state_dict.get("state_version", 1) + 1

def get_initial_session_state() -> Dict[str, Any]:
    """Returns a freshly initialized dictionary representing session_state."""
    st_dict: Dict[str, Any] = {}
    init_session_state(st_dict, force_reset=True)
    return st_dict

