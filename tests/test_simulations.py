"""
test_simulations.py – Unit tests for Subsystem 6 & 7 What-if Simulations
"""

import pytest
from core.state import get_initial_session_state
from core.simulator import HubEventSimulator

@pytest.fixture
def clean_state():
    return get_initial_session_state()

def test_metro_surge_deepcopy_isolation_and_unserved_students(clean_state):
    orig_hubs = clean_state["hubs"]
    orig_ktxb_slots = orig_hubs[1]["available_slots"]

    sim = HubEventSimulator(orig_hubs)
    # Request more students than available slots (e.g. 50 students when slots is 4)
    mod_hubs, log, metrics = sim.simulate_metro_surge(
        target_hub_id="HUB-002",
        num_new_students=50,
        seed=42
    )

    # 1. Deepcopy isolation: Original hubs must NOT be modified
    assert orig_hubs[1]["available_slots"] == orig_ktxb_slots

    # 2. Modified hubs must have 0 slots remaining and tracked unserved
    assert mod_hubs[1]["available_slots"] == 0
    assert metrics["admitted_students"] == orig_ktxb_slots
    assert metrics["unserved_students"] == 50 - orig_ktxb_slots

def test_port_failure_distinguishes_free_vs_busy_ports(clean_state):
    orig_hubs = clean_state["hubs"]
    hub_bk = orig_hubs[3]  # HUB-004 BK

    sim = HubEventSimulator(orig_hubs)
    mod_hubs, log, metrics = sim.simulate_port_failure(
        target_hub_id="HUB-004",
        num_ports_down=4,
        seed=42
    )

    # Original hubs untouched
    assert orig_hubs[3]["charging_ports"]["available"] == hub_bk["charging_ports"]["available"]
    assert metrics["failed_ports_total"] == 4

def test_repeated_failures_do_not_count_offline_ports_as_busy():
    hubs = [{"hub_id": "H", "name": "Test", "charging_ports": {"total": 2, "available": 2}, "current_vehicles": []}]
    for expected in (1, 2, 2):
        hubs, _, metrics = HubEventSimulator(hubs).simulate_port_failure("H", 1)
        ports = hubs[0]["charging_ports"]
        assert ports["offline"] == expected
        assert ports["available"] == 2 - expected
        assert metrics["busy_ports_interrupted"] == 0

def test_personal_vehicle_cannot_be_booked_as_shared(clean_state):
    import copy
    from core.booking import create_shared_booking
    hub = clean_state['hubs'][0]
    vehicle = hub['current_vehicles'][0]
    vehicle.update(ownership='PERSONAL', status='AVAILABLE', battery_soc=90)
    before = copy.deepcopy(clean_state)
    ok, _, _ = create_shared_booking(clean_state, 'student', hub['hub_id'], vehicle['vehicle_id'])
    assert not ok
    assert clean_state == before

def test_surge_ids_are_unique_across_previews_from_changed_state():
    hubs = [{"hub_id": "H", "name": "Test", "total_slots": 30, "available_slots": 30,
             "charging_ports": {"total": 0, "available": 0}, "current_vehicles": []}]
    first, _, metrics1 = HubEventSimulator(hubs).simulate_metro_surge('H', 5, 42)
    second, _, metrics2 = HubEventSimulator(first).simulate_metro_surge('H', 5, 42)
    assert len({v['vehicle_id'] for v in second[0]['current_vehicles']}) == 10
    assert metrics1['new_vehicles_count'] == metrics2['new_vehicles_count'] == 5
