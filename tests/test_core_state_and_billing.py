"""
tests/test_core_state_and_billing.py – Acceptance Unit Tests for Phase 3
Tests state initialization, capacity conservation, wallet ledger, no-show expiry,
and threshold logic.
"""

import pytest
from core.state import (
    init_session_state,
    advance_sim_time,
    validate_state_invariants,
    VehicleStatus,
    ReservationStatus,
    Ownership
)
from core.policies import (
    get_occupancy_level,
    is_peak_hour,
    SHARED_DEPOSIT_VND,
    SHARED_NOSHOW_PENALTY_VND,
    SHARED_NOSHOW_REFUND_VND
)
from core.billing import (
    hold_deposit,
    release_held_deposit_full,
    settle_noshow_penalty,
    calculate_shared_rental_cost,
    settle_shared_rental,
    calculate_private_ev_bill
)
from core.booking import (
    create_shared_booking,
    pickup_shared_vehicle,
    return_shared_vehicle,
    cancel_shared_booking,
    process_expired_bookings
)
from core.routing import haversine_distance_km, find_nearest_alternative_hubs
from datetime import time

def test_state_initialization_and_invariants():
    state = {}
    init_session_state(state, force_reset=True)
    
    assert "hubs" in state
    assert len(state["hubs"]) == 6
    assert "wallet" in state
    assert state["wallet"]["balance"] == 150_000
    assert state["wallet"]["held_deposit"] == 0
    assert state["wallet"]["debt"] == 0
    assert "bookings" in state
    assert "personal_evs" in state
    assert state["state_version"] >= 1
    
    # Invariant check must have zero errors on initialized seed
    errors = validate_state_invariants(state)
    assert errors == [], f"Invariant violations: {errors}"

def test_personal_vs_shared_separation():
    state = {}
    init_session_state(state, force_reset=True)
    
    for h in state["hubs"]:
        for v in h["current_vehicles"]:
            assert v["ownership"] == Ownership.SHARED.value
            assert v["status"] in [s.value for s in VehicleStatus]
            
    for pev in state["personal_evs"]:
        assert pev["ownership"] == Ownership.PERSONAL.value

def test_occupancy_threshold_levels():
    assert get_occupancy_level(60.0) == "NORMAL"
    assert get_occupancy_level(69.9) == "NORMAL"
    assert get_occupancy_level(70.0) == "WARNING"
    assert get_occupancy_level(84.9) == "WARNING"
    assert get_occupancy_level(85.0) == "CRITICAL"
    assert get_occupancy_level(99.9) == "CRITICAL"
    assert get_occupancy_level(100.0) == "FULL"
    assert get_occupancy_level(105.0) == "FULL"

def test_peak_hour_boundaries():
    assert not is_peak_hour(time(5, 59))
    assert is_peak_hour(time(6, 0))
    assert is_peak_hour(time(8, 59))
    assert not is_peak_hour(time(9, 0))
    
    assert not is_peak_hour(time(15, 59))
    assert is_peak_hour(time(16, 0))
    assert is_peak_hour(time(19, 29))
    assert not is_peak_hour(time(19, 30))

def test_booking_pickup_return_capacity_conservation():
    state = {}
    init_session_state(state, force_reset=True)
    
    hub_a = state["hubs"][0]  # HUB-001
    hub_b = state["hubs"][1]  # HUB-002
    
    orig_a_avail = hub_a["available_slots"]
    orig_b_avail = hub_b["available_slots"]
    
    # 1. Create booking at HUB-001 with destination HUB-002
    v = [x for x in hub_a["current_vehicles"] if x["status"] == "AVAILABLE" and x["battery_soc"] >= 20][0]
    vid = v["vehicle_id"]
    
    ok, b, msg = create_shared_booking(
        state=state,
        student_id="SV-TEST-01",
        hub_id=hub_a["hub_id"],
        vehicle_id=vid,
        voucher_code="SV-ECO",
        destination_hub_id=hub_b["hub_id"]
    )
    assert ok, msg
    assert v["status"] == VehicleStatus.RESERVED.value
    # Destination hold consumes 1 slot at Hub B
    assert hub_b["available_slots"] == orig_b_avail - 1
    assert hub_b["destination_holds"] == 1
    # Origin slot not consumed yet (vehicle still physically at Hub A)
    assert hub_a["available_slots"] == orig_a_avail
    
    # Invariant validation
    assert validate_state_invariants(state) == []
    
    # 2. Pickup vehicle at Hub A -> Frees origin slot at Hub A!
    ok, msg = pickup_shared_vehicle(state, b["booking_id"], b["pin_code"])
    assert ok, msg
    assert hub_a["available_slots"] == orig_a_avail + 1
    assert v["status"] == VehicleStatus.IN_USE.value
    assert validate_state_invariants(state) == []
    
    # 3. Advance time by 45 minutes
    advance_sim_time(state, minutes=45)
    
    # 4. Return vehicle at Hub B
    ok, inv, msg = return_shared_vehicle(state, b["booking_id"], hub_b["hub_id"])
    assert ok, msg
    assert inv["duration_minutes"] == 45
    assert inv["free_minutes"] == 30
    assert inv["billable_minutes"] == 15
    # Base fee: 15,000 - voucher 5,000 = 10,000 VNĐ
    assert inv["total_fee"] == 10_000
    # Hub B destination hold released
    assert hub_b["destination_holds"] == 0
    # Vehicle now in Hub B
    assert any(x["vehicle_id"] == vid for x in hub_b["current_vehicles"])
    assert validate_state_invariants(state) == []

def test_noshow_expiry_and_penalty():
    state = {}
    init_session_state(state, force_reset=True)
    
    hub = state["hubs"][0]
    v = [x for x in hub["current_vehicles"] if x["status"] == "AVAILABLE" and x["battery_soc"] >= 20][0]
    
    initial_balance = state["wallet"]["balance"]
    
    ok, b, msg = create_shared_booking(
        state=state,
        student_id="SV-TEST-02",
        hub_id=hub["hub_id"],
        vehicle_id=v["vehicle_id"]
    )
    assert ok, msg
    assert state["wallet"]["balance"] == initial_balance - 50_000
    assert state["wallet"]["held_deposit"] == 50_000
    
    # Advance time by 31 minutes (> 30 minutes TTL)
    advance_sim_time(state, minutes=31)
    
    # Processing expired bookings
    expired = process_expired_bookings(state)
    assert expired == 1
    assert b["status"] == ReservationStatus.EXPIRED.value
    # Settle: 10,000 penalty deducted, 40,000 refunded
    assert state["wallet"]["held_deposit"] == 0
    assert state["wallet"]["balance"] == initial_balance - 10_000
    # Vehicle returns to AVAILABLE
    assert v["status"] == VehicleStatus.AVAILABLE.value

def test_early_cancellation_full_refund():
    state = {}
    init_session_state(state, force_reset=True)
    
    hub = state["hubs"][0]
    v = [x for x in hub["current_vehicles"] if x["status"] == "AVAILABLE" and x["battery_soc"] >= 20][0]
    initial_balance = state["wallet"]["balance"]
    
    ok, b, msg = create_shared_booking(
        state=state,
        student_id="SV-TEST-03",
        hub_id=hub["hub_id"],
        vehicle_id=v["vehicle_id"]
    )
    assert ok
    # Advance only 5 minutes (< 30 min TTL)
    advance_sim_time(state, minutes=5)
    
    ok_cancel, msg_cancel = cancel_shared_booking(state, b["booking_id"])
    assert ok_cancel
    assert b["status"] == ReservationStatus.CANCELLED.value
    assert state["wallet"]["balance"] == initial_balance
    assert state["wallet"]["held_deposit"] == 0
    assert v["status"] == VehicleStatus.AVAILABLE.value

def test_no_silent_debt_loss():
    wallet = {"balance": 5_000, "held_deposit": 50_000, "debt": 0, "ledger": []}
    # Trip cost = 70,000 (after exhausting 50,000 deposit, 20,000 is owed)
    cost = {"duration_minutes": 100, "free_minutes": 30, "billable_minutes": 70, "base_fee": 70_000, "discount": 0, "final_fee": 70_000}
    inv = settle_shared_rental(wallet, cost, booking_id="BK-DEBT-01")
    
    assert inv["status"] == "PARTIAL_DEBT"
    assert inv["refund_amount"] == 0
    assert inv["deducted_from_available"] == 5_000
    assert inv["debt_incurred"] == 15_000
    assert wallet["balance"] == 0
    assert wallet["debt"] == 15_000  # Explicitly recorded debt!
    assert wallet["held_deposit"] == 0

def test_haversine_distance_accuracy():
    # KTX A (10.8781, 106.8056) to KTX B (10.8755, 106.8012)
    dist = haversine_distance_km(10.8781, 106.8056, 10.8755, 106.8012)
    assert 0.4 < dist < 0.7  # Approx ~0.56 km
