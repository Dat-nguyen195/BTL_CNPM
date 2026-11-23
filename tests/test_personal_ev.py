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
    check_out_personal_ev,
    cancel_personal_reservation,
    sweep_expired_personal_reservations,
)
from core.state import validate_state_invariants

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


# ---------------------------------------------------------------------------
# Bổ sung 23/11/2026: hủy đơn, chuẩn hóa biển số, kiểm tra đầu vào,
# loại xe khi check-in, cấp cổng cho xe chờ, TC-SS2-04 và TC-SS2-08.
# ---------------------------------------------------------------------------

def _reserve(state, plate="59-H1 10001", charging=False, owner="SV-2211234", soc=40.0):
    _, ev, _ = register_personal_ev(state, owner, "Test", plate, "scooter", "Test", 3.5)
    ok, res, msg = reserve_personal_ev_slot(state, owner, ev["ev_id"], state["hubs"][0]["hub_id"],
                                            request_charging=charging, current_soc=soc)
    assert ok, msg
    return ev, res


def test_cancel_before_deadline_refunds_full_deposit(clean_state):
    hub = clean_state["hubs"][0]
    avail0, holds0 = hub["available_slots"], hub.get("destination_holds", 0)
    _, res = _reserve(clean_state)
    clean_state["current_sim_time"] = "2026-10-21 08:29:59"
    assert not cancel_personal_reservation(clean_state, res["reservation_id"], owner_id="OTHER")[0]
    ok, msg = cancel_personal_reservation(clean_state, res["reservation_id"], owner_id="SV-2211234")
    assert ok, msg
    assert res["status"] == ReservationStatus.CANCELLED.value
    assert clean_state["wallet"]["balance"] == 150_000
    assert clean_state["wallet"]["held_deposit"] == 0
    assert hub["available_slots"] == avail0 and hub.get("destination_holds", 0) == holds0
    # Không hủy lặp, không check-in đơn đã hủy, sweep không phạt đơn đã hủy
    assert not cancel_personal_reservation(clean_state, res["reservation_id"])[0]
    assert not check_in_personal_ev(clean_state, res["reservation_id"])[0]
    clean_state["current_sim_time"] = "2026-10-21 09:00:00"
    assert sweep_expired_personal_reservations(clean_state) == 0
    assert clean_state["wallet"]["balance"] == 150_000
    assert validate_state_invariants(clean_state) == []


def test_cancel_at_deadline_is_settled_as_no_show(clean_state):
    _, res = _reserve(clean_state)
    clean_state["current_sim_time"] = "2026-10-21 08:30:00"
    ok, msg = cancel_personal_reservation(clean_state, res["reservation_id"])
    assert not ok and "quá hạn" in msg
    assert res["status"] == ReservationStatus.EXPIRED.value
    assert clean_state["wallet"]["balance"] == 140_000
    assert clean_state["wallet"]["held_deposit"] == 0


@pytest.mark.parametrize("dup", ["59X1 88888", "59-x1 888.88 ", "59.X1-888 88"])
def test_plate_duplicate_ignores_dots_spaces_and_dashes(clean_state, dup):
    assert register_personal_ev(clean_state, "A", "A", "59-X1 888.88", "scooter", "V", 3.5)[0]
    n = len(clean_state["personal_evs"])
    ok, ev, msg = register_personal_ev(clean_state, "B", "B", dup, "scooter", "V", 3.5)
    assert not ok and ev is None and "đã được đăng ký" in msg
    assert len(clean_state["personal_evs"]) == n


@pytest.mark.parametrize("ev_type,battery", [("scooter", -5), ("scooter", 0), ("scooter", 500), ("plane", 3.5), ("scooter", float("nan"))])
def test_register_rejects_invalid_input(clean_state, ev_type, battery):
    n = len(clean_state["personal_evs"])
    assert not register_personal_ev(clean_state, "A", "A", "59-V1 00001", ev_type, "V", battery)[0]
    assert len(clean_state["personal_evs"]) == n


@pytest.mark.parametrize("soc", [-1, 101, 250, float("nan")])
def test_reserve_rejects_invalid_soc_without_side_effects(clean_state, soc):
    _, ev, _ = register_personal_ev(clean_state, "SV-2211234", "A", "59-V2 00002", "scooter", "V", 3.5)
    balance = clean_state["wallet"]["balance"]
    avail = clean_state["hubs"][0]["available_slots"]
    assert not reserve_personal_ev_slot(clean_state, "SV-2211234", ev["ev_id"], clean_state["hubs"][0]["hub_id"], True, soc)[0]
    assert clean_state["wallet"]["balance"] == balance
    assert clean_state["hubs"][0]["available_slots"] == avail


def test_checkin_keeps_registered_vehicle_type(clean_state):
    _, ev, _ = register_personal_ev(clean_state, "SV-2211234", "A", "51A-123.45", "car", "VF5", 37.2)
    _, res, _ = reserve_personal_ev_slot(clean_state, "SV-2211234", ev["ev_id"], clean_state["hubs"][0]["hub_id"])
    assert check_in_personal_ev(clean_state, res["reservation_id"])[0]
    v = next(v for v in clean_state["hubs"][0]["current_vehicles"] if v["vehicle_id"] == ev["ev_id"])
    assert v["type"] == "car"


def test_waiting_vehicle_gets_port_when_another_checks_out(clean_state):
    hub = clean_state["hubs"][0]
    _, first = _reserve(clean_state, plate="59-W1 00001", charging=True)
    assert check_in_personal_ev(clean_state, first["reservation_id"])[0]
    assert first["charging_port_allocated"]
    _, second = _reserve(clean_state, plate="59-W1 00002", charging=True)
    hub["charging_ports"]["available"] = 0          # các cổng còn lại vừa bị chiếm
    assert check_in_personal_ev(clean_state, second["reservation_id"])[0]
    assert not second["charging_port_allocated"]    # WAITING
    ok, _, msg = check_out_personal_ev(clean_state, first["reservation_id"], duration_hours=1)
    assert ok, msg
    assert second["charging_port_allocated"] and second["charging_session_id"]
    waiting = next(v for v in hub["current_vehicles"] if v["vehicle_id"] == second["ev_id"])
    assert waiting["status"] == "CHARGING"
    assert hub["charging_ports"]["available"] == 0  # cổng vừa trả đã cấp cho xe chờ


def test_tc_ss2_04_reserve_rejections_have_no_side_effects(clean_state):
    hub = clean_state["hubs"][0]
    ev, _ = _reserve(clean_state, plate="59-R1 00001")
    before = (clean_state["wallet"]["balance"], clean_state["wallet"]["held_deposit"], hub["available_slots"])
    # (1) xe đang có đơn chưa hoàn tất
    ok, r2, msg = reserve_personal_ev_slot(clean_state, "SV-2211234", ev["ev_id"], hub["hub_id"])
    assert not ok and r2 is None and "chưa hoàn tất" in msg
    # (2) Hub hết chỗ
    _, ev2, _ = register_personal_ev(clean_state, "SV-2211234", "A", "59-R1 00002", "scooter", "V", 3.5)
    saved = hub["available_slots"]
    hub["available_slots"] = 0
    assert not reserve_personal_ev_slot(clean_state, "SV-2211234", ev2["ev_id"], hub["hub_id"])[0]
    hub["available_slots"] = saved
    # (3) ví đang có nợ
    clean_state["wallet"]["debt"] = 20_000
    ok, _, msg = reserve_personal_ev_slot(clean_state, "SV-2211234", ev2["ev_id"], hub["hub_id"])
    assert not ok and "nợ" in msg
    assert (clean_state["wallet"]["balance"], clean_state["wallet"]["held_deposit"], hub["available_slots"]) == before


def test_tc_ss2_08_checkout_with_insufficient_balance_records_debt_once(clean_state):
    hub = clean_state["hubs"][0]
    _, res = _reserve(clean_state, plate="59-D1 00001")
    assert check_in_personal_ev(clean_state, res["reservation_id"])[0]
    avail_in = hub["available_slots"]
    clean_state["wallet"]["balance"] = 0            # sau khi hoàn cọc ví còn đúng 50.000
    ok, inv, msg = check_out_personal_ev(clean_state, res["reservation_id"], duration_hours=11)
    assert ok, msg
    assert inv["total_amount"] == 55_000             # 11 giờ x 5.000, không sạc
    assert inv["deducted_from_wallet"] == 50_000 and inv["debt_incurred"] == 5_000
    assert clean_state["wallet"]["balance"] == 0 and clean_state["wallet"]["debt"] == 5_000
    assert res["status"] == ReservationStatus.COMPLETED.value
    assert hub["available_slots"] == avail_in + 1
    # Check-out lặp bị từ chối, không ghi nợ hay trả chỗ lần hai
    assert not check_out_personal_ev(clean_state, res["reservation_id"], duration_hours=11)[0]
    assert clean_state["wallet"]["debt"] == 5_000
    assert hub["available_slots"] == avail_in + 1


# ---------------------------------------------------------------------------
# Tương thích liên phân hệ (23/11/2026): SS1, SS3, SS4, SS5, SS7
# ---------------------------------------------------------------------------

def test_parked_personal_vehicle_is_not_counted_as_rentable(clean_state):
    hub = clean_state["hubs"][0]
    ready_before = len([v for v in hub["current_vehicles"] if v["status"] == "AVAILABLE"])
    ev, res = _reserve(clean_state, plate="59-P1 00001")          # chỉ gửi đỗ, không sạc
    assert check_in_personal_ev(clean_state, res["reservation_id"])[0]
    v = next(v for v in hub["current_vehicles"] if v["vehicle_id"] == ev["ev_id"])
    assert v["status"] == "PARKED"
    # SS1 "Xe sẵn sàng" và danh sách cách ly sự cố của SS4 chỉ lấy xe AVAILABLE
    assert len([v for v in hub["current_vehicles"] if v["status"] == "AVAILABLE"]) == ready_before
    assert validate_state_invariants(clean_state) == []


def test_checkout_payment_is_recorded_in_wallet_ledger(clean_state):
    _, res = _reserve(clean_state, plate="59-L1 00001")
    assert check_in_personal_ev(clean_state, res["reservation_id"])[0]
    n = len(clean_state["wallet"]["ledger"])
    ok, inv, _ = check_out_personal_ev(clean_state, res["reservation_id"], duration_hours=2)
    assert ok
    new = clean_state["wallet"]["ledger"][n:]
    pay = [t for t in new if t["type"] == "SETTLE_PEV_INVOICE"]
    assert len(pay) == 1 and pay[0]["amount"] == -inv["deducted_from_wallet"] == -10_000
    assert pay[0]["booking_id"] == res["reservation_id"]


def test_ss3_revenue_includes_ss2_payment_and_no_show_once():
    from test_submission_2_acceptance import app, state
    s = state()
    hub = s["hubs"][0]
    # Một đơn no-show (phạt 10.000) và một lượt check-out thu 10.000
    _, ev1, _ = register_personal_ev(s, "SV-2211234", "A", "59-N1 00001", "scooter", "V", 3.5)
    reserve_personal_ev_slot(s, "SV-2211234", ev1["ev_id"], hub["hub_id"])
    _, ev2, _ = register_personal_ev(s, "SV-2211234", "A", "59-N1 00002", "scooter", "V", 3.5)
    _, r2, _ = reserve_personal_ev_slot(s, "SV-2211234", ev2["ev_id"], hub["hub_id"])
    assert check_in_personal_ev(s, r2["reservation_id"])[0]
    s["current_sim_time"] = "2026-10-21 08:30:00"
    assert sweep_expired_personal_reservations(s) == 1
    assert check_out_personal_ev(s, r2["reservation_id"], duration_hours=2)[0]
    at = app(3)
    for key in ["wallet", "hubs", "personal_reservations", "personal_evs", "current_sim_time"]:
        at.session_state[key] = s[key]
    at.run()
    assert not at.exception
    metric = next(m for m in at.metric if m.label == "💵 Tổng doanh thu thu về")
    assert metric.value == "20,000 ₫"   # 10.000 phạt no-show + 10.000 phí đỗ, không đếm trùng


def test_port_failure_reallocates_interrupted_vehicle_to_free_port(clean_state):
    import copy
    from core.scheduler import apply_hub_snapshot
    hub = clean_state["hubs"][0]
    ev, res = _reserve(clean_state, plate="59-F1 00001", charging=True, soc=30)
    assert check_in_personal_ev(clean_state, res["reservation_id"])[0]
    old_session = res["charging_session_id"]
    hubs = copy.deepcopy(clean_state["hubs"])
    ports = hubs[0]["charging_ports"]
    ports["offline"] = ports.get("offline", 0) + 1                # một cổng hỏng, Hub vẫn còn cổng trống
    apply_hub_snapshot(clean_state, hubs)
    hub = clean_state["hubs"][0]
    assert res["charging_port_allocated"] and res["charging_session_id"] != old_session
    v = next(v for v in hub["current_vehicles"] if v["vehicle_id"] == ev["ev_id"])
    assert v["status"] == "CHARGING"
    assert validate_state_invariants(clean_state) == []
