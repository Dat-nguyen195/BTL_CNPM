"""
test_personal_ev.py – Unit tests for Subsystem 2 Personal EV Lifecycle
"""

import pytest
from datetime import datetime
from core.state import get_initial_session_state, VehicleStatus, ReservationStatus
from core.personal_ev import (
    register_personal_ev,
    reserve_personal_ev_slot,
    check_in_personal_ev,
    check_out_personal_ev
)

@pytest.fixture
def clean_state():
    state = get_initial_session_state()
    state["current_sim_time"] = "2026-10-21 08:00:00"  # Peak hour 06:00-09:00
    return state

def test_register_personal_ev_success_and_duplicate(clean_state):
    # 1. Register first EV with brand new plate
    ok, ev, msg = register_personal_ev(
        state=clean_state,
        owner_id="SV-2211234",
        owner_name="Nguyễn Văn A",
        plate_number="59-X1 77777",
        ev_type="scooter",
        brand="VinFast Klara",
        battery_kwh=3.5
    )
    assert ok is True
    assert ev["plate"] == "59-X1 77777"
    assert ev["ownership"] == "PERSONAL"

    # 2. Duplicate plate registration must fail
    ok2, ev2, msg2 = register_personal_ev(
        state=clean_state,
        owner_id="SV-9999999",
        owner_name="Trần Văn B",
        plate_number="59X1-77777",  # Same plate formatted differently
        ev_type="scooter",
        brand="VinFast",
        battery_kwh=3.0
    )
    assert ok2 is False
    assert "đã được đăng ký" in msg2

def test_reserve_and_checkin_checkout_lifecycle(clean_state):
    # Register EV
    _, ev, _ = register_personal_ev(
        state=clean_state,
        owner_id="SV-2211234",
        owner_name="Nguyễn Văn A",
        plate_number="59-X1 99999",
        ev_type="scooter",
        brand="VinFast Feliz",
        battery_kwh=3.5
    )

    hub = clean_state["hubs"][0]
    initial_avail = hub["available_slots"]
    initial_holds = hub.get("destination_holds", 0)

    # Reserve slot
    ok_res, res, _ = reserve_personal_ev_slot(
        state=clean_state,
        owner_id="SV-2211234",
        ev_id=ev["ev_id"],
        hub_id=hub["hub_id"],
        request_charging=True,
        current_soc=30.0
    )
    assert ok_res is True
    assert hub["destination_holds"] == initial_holds + 1
    assert hub["available_slots"] == initial_avail - 1
    assert clean_state["wallet"]["held_deposit"] == 50000
    assert res["arrival_deadline"] == "2026-10-21 08:30:00"

    # Check-in
    ok_in, msg_in = check_in_personal_ev(clean_state, res["reservation_id"])
    assert ok_in is True
    # Holds decremented, slot stays consumed, vehicle physically present
    assert hub["destination_holds"] == initial_holds
    present_pev = [v for v in hub["current_vehicles"] if v["vehicle_id"] == ev["ev_id"]]
    assert len(present_pev) == 1
    assert present_pev[0]["ownership"] == "PERSONAL"

    # No tick has delivered energy yet. Client-supplied energy/overstay cannot override measured zero.
    ok_out, inv, msg_out = check_out_personal_ev(
        state=clean_state,
        reservation_id=res["reservation_id"],
        duration_hours=2.0,
        kwh_charged=4.0,
        overstay_minutes=20
    )
    assert ok_out is True
    assert inv["parking_fee"] == 10000
    assert inv["is_peak_tariff"] is True
    assert inv["energy_fee"] == 0  # measured zero
    assert inv["overstay_fee"] == 0     # no actual overstay
    assert inv["total_amount"] == 10000  # two hourly blocks
    # Physical slot freed!
    assert hub["available_slots"] == initial_avail

def test_checkin_waits_if_port_fails_after_reservation(clean_state):
    _, ev, _ = register_personal_ev(clean_state, 'u', 'User', 'TEST-123', 'scooter', 'X', 3.5)
    hub = clean_state['hubs'][0]
    _, res, _ = reserve_personal_ev_slot(clean_state, 'u', ev['ev_id'], hub['hub_id'], True)
    hub['charging_ports']['offline'] = hub['charging_ports']['total']
    hub['charging_ports']['available'] = 0
    assert check_in_personal_ev(clean_state, res['reservation_id'])[0]
    v = next(v for v in hub['current_vehicles'] if v['vehicle_id'] == ev['ev_id'])
    assert v['status'] == 'WAITING'
    assert not res['charging_port_allocated']
    ok, invoice, _ = check_out_personal_ev(clean_state, res['reservation_id'], kwh_charged=4, overstay_minutes=20)
    assert ok and invoice['energy_fee'] == invoice['overstay_fee'] == 0

def test_waiting_personal_vehicle_can_be_allocated_once(clean_state):
    from core.scheduler import allocate_hub_ports
    _, ev, _ = register_personal_ev(clean_state, 'u', 'User', 'TEST-456', 'scooter', 'X', 3.5)
    hub = clean_state['hubs'][0]
    _, res, _ = reserve_personal_ev_slot(clean_state, 'u', ev['ev_id'], hub['hub_id'], True)
    hub['charging_ports']['available'] = 0
    assert check_in_personal_ev(clean_state, res['reservation_id'])[0]
    hub['charging_ports']['available'] = 1
    assert len(allocate_hub_ports(clean_state, hub['hub_id'])) == 1
    assert allocate_hub_ports(clean_state, hub['hub_id']) == []
    assert res['charging_port_allocated']
    assert len([s for s in clean_state['charging_scheduler']._active_sessions.values() if s.vehicle_id == ev['ev_id']]) == 1
