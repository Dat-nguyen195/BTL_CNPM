"""Acceptance evidence for prototype workflows, not production IoT/payment claims."""
from copy import deepcopy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from core.state import get_initial_session_state, validate_state_invariants
from core.personal_ev import register_personal_ev, reserve_personal_ev_slot, check_in_personal_ev, check_out_personal_ev, sweep_expired_personal_reservations
from core.booking import create_shared_booking, pickup_shared_vehicle, apply_rerouting_to_booking, return_shared_vehicle
from core.routing import find_alternative_hubs
from core.simulator import HubEventSimulator
from core.scheduler import SmartChargingScheduler, ChargingRequest

ROOT = Path(__file__).resolve().parents[1]


def state():
    result = get_initial_session_state()
    result["current_sim_time"] = "2026-10-21 08:00:00"
    return result


def app(subsystem):
    at = AppTest.from_file(str(ROOT / "src/app.py"), default_timeout=15).run()
    at.session_state["current_sim_time"] = "2026-10-21 08:00:00"
    at.sidebar.radio[0].set_value(at.sidebar.radio[0].options[subsystem - 1]).run()
    assert not at.exception
    return at


def test_personal_future_arrival_and_exact_expiry():
    s = state()
    _, ev, _ = register_personal_ev(s, "SV-TEST", "Test", "59T12345", "scooter", "Test", 3.5)
    hub = s["hubs"][0]
    before = hub["available_slots"]
    ok, res, msg = reserve_personal_ev_slot(s, "SV-TEST", ev["ev_id"], hub["hub_id"], booking_start_time="2026-10-21 10:00:00")
    assert ok, msg
    assert res["arrival_deadline"] == "2026-10-21 10:30:00"
    assert res["deposit_held"] == s["wallet"]["held_deposit"] == 50_000
    assert not check_in_personal_ev(s, res["reservation_id"])[0]
    s["current_sim_time"] = "2026-10-21 10:29:59"
    assert sweep_expired_personal_reservations(s) == 0
    s["current_sim_time"] = res["arrival_deadline"]
    assert sweep_expired_personal_reservations(s) == 1
    assert hub["available_slots"] == before
    assert s["wallet"]["held_deposit"] == 0
    assert s["wallet"]["balance"] == 140_000
    ledger = deepcopy(s["wallet"]["ledger"])
    assert sweep_expired_personal_reservations(s) == 0
    assert s["wallet"]["ledger"] == ledger
    assert not check_in_personal_ev(s, res["reservation_id"])[0]
    assert validate_state_invariants(s) == []


@pytest.mark.parametrize("owner,start", [("OTHER", None), ("OWNER", "bad-time"), ("OWNER", "2026-10-20 08:00:00")])
def test_personal_invalid_reservation_has_no_financial_or_capacity_effect(owner, start):
    s = state()
    _, ev, _ = register_personal_ev(s, "OWNER", "Test", "59T12345", "scooter", "Test", 3.5)
    before = deepcopy(s)
    assert not reserve_personal_ev_slot(s, owner, ev["ev_id"], s["hubs"][0]["hub_id"], booking_start_time=start)[0]
    assert s == before


def test_forecast_24h_queue_wait_and_reproducibility():
    rows = HubEventSimulator.generate_demand_forecast(10, 1.5, hours=24, seed=42)
    assert rows == HubEventSimulator.generate_demand_forecast(10, 1.5, hours=24, seed=42)
    assert len(rows) == 24 and len({r["hour"] for r in rows}) == 24
    queue = 0
    for row in rows:
        assert row["arrivals"] >= 0
        queue = max(0, queue + row["arrivals"] - 8)
        assert row["queue_length"] == queue
        assert row["wait_time_min"] == round(queue / 8 * 60, 1)
    low = HubEventSimulator.generate_demand_forecast(10, 1, 24, seed=42)
    assert sum(r["arrivals"] for r in rows) > sum(r["arrivals"] for r in low)
    at = app(6)
    at.slider(key="ss6_sim_hours").set_value(24).run()
    assert not at.exception
    assert len(at.get("plotly_chart")) >= 1


def test_dispatch_ui_moves_vehicle_and_conserves_capacity():
    at = app(4)
    hubs = deepcopy(at.session_state["hubs"])
    source = next(h for h in hubs if h["name"] == at.selectbox(key="disp_src_name").value)
    dest = next(h for h in hubs if h["name"] == at.selectbox(key="disp_dst_name").value)
    vehicle_option = at.multiselect(key="disp_chosen_veh").options[0]
    vid = vehicle_option.split(" – ")[0]
    at.multiselect(key="disp_chosen_veh").set_value([vehicle_option])
    at.button(key="btn_create_dispatch").click().run()
    assert not at.exception
    dispatch = at.session_state["active_dispatches"][-1]
    assert dispatch["status"] == "IN_TRANSIT"
    assert dispatch["vehicles"][0]["status"] == "DISPATCHED"
    now = at.session_state["hubs"]
    src_now = next(h for h in now if h["hub_id"] == source["hub_id"])
    dst_now = next(h for h in now if h["hub_id"] == dest["hub_id"])
    assert src_now["available_slots"] == source["available_slots"] + 1
    assert dst_now["available_slots"] == dest["available_slots"] - 1
    assert not any(v["vehicle_id"] == vid for v in src_now["current_vehicles"])
    at.button(key=f"btn_recv_{dispatch['dispatch_id']}").click().run()
    assert not at.exception
    completed = at.session_state["active_dispatches"][-1]
    assert completed["status"] == "COMPLETED"
    dst_now = next(h for h in at.session_state["hubs"] if h["hub_id"] == dest["hub_id"])
    assert any(v["vehicle_id"] == vid and v["status"] == "AVAILABLE" for v in dst_now["current_vehicles"])
    assert dst_now["destination_holds"] == dest.get("destination_holds", 0)
    assert at.session_state["dispatch_log"][-1]["dispatch_id"] == dispatch["dispatch_id"]


def test_incident_ui_report_acknowledge_resolve_and_history():
    at = app(4)
    vid = at.selectbox(key="inc_vehicle").value
    at.text_input(key="inc_desc").set_value("Kiểm thử phanh xe tại trạm")
    next(b for b in at.button if b.label == "🚨 Ghi nhận sự cố & Cách ly").click().run()
    assert not at.exception
    inc = at.session_state["incident_log"][-1]
    assert inc["status"] == "REPORTED" and inc["description"] == "Kiểm thử phanh xe tại trạm"
    assert any(v["vehicle_id"] == vid and v["status"] == "INCIDENT" for h in at.session_state["hubs"] for v in h["current_vehicles"])
    at.button(key=f"ack_{inc['incident_id']}").click().run()
    assert at.session_state["incident_log"][-1]["status"] == "ACKNOWLEDGED"
    at.session_state["current_sim_time"] = "2026-10-21 08:25:00"
    at.button(key=f"rec_{inc['incident_id']}").click().run()
    assert not at.exception
    resolved = at.session_state["incident_log"][-1]
    assert resolved["status"] == "RESOLVED" and resolved["resolved_at"] == "2026-10-21 08:25:00"
    assert any(v["vehicle_id"] == vid and v["status"] == "AVAILABLE" for h in at.session_state["hubs"] for v in h["current_vehicles"])
    tables = [d.value for d in at.dataframe]
    assert any("incident_id" in d.columns and inc["incident_id"] in d["incident_id"].values for d in tables)


def test_rerouting_selects_two_hubs_and_transfers_hold_once():
    s = state()
    origin, old_dest = s["hubs"][:2]
    vehicle = next(v for v in origin["current_vehicles"] if v["status"] == "AVAILABLE")
    ok, booking, msg = create_shared_booking(s, "SV-TEST", origin["hub_id"], vehicle["vehicle_id"], destination_hub_id=old_dest["hub_id"])
    assert ok, msg
    alternatives = find_alternative_hubs(s["hubs"], old_dest["hub_id"], need_slots=True, limit=2)
    assert len(alternatives) == 2
    assert all(a["hub_id"] != old_dest["hub_id"] and a["available_slots"] > 0 for a in alternatives)
    assert alternatives[0]["distance_km"] <= alternatives[1]["distance_km"]
    wallet = deepcopy(s["wallet"])
    old_avail = old_dest["available_slots"]
    new_dest = next(h for h in s["hubs"] if h["hub_id"] == alternatives[0]["hub_id"])
    new_avail = new_dest["available_slots"]
    assert apply_rerouting_to_booking(s, booking["booking_id"], new_dest["hub_id"])[0]
    assert old_dest["available_slots"] == old_avail + 1 and old_dest["destination_holds"] == 0
    assert new_dest["available_slots"] == new_avail - 1 and new_dest["destination_holds"] == 1
    assert s["wallet"] == wallet and booking["extra_free_minutes"] == 15
    assert apply_rerouting_to_booking(s, booking["booking_id"], alternatives[1]["hub_id"])[0]
    assert new_dest["available_slots"] == new_avail and booking["extra_free_minutes"] == 15
    assert validate_state_invariants(s) == []


def test_dashboard_shows_actual_booking_ledger_and_revenue():
    s = state()
    hub = s["hubs"][0]
    vehicle = next(v for v in hub["current_vehicles"] if v["status"] == "AVAILABLE")
    ok, booking, _ = create_shared_booking(s, "SV-TEST", hub["hub_id"], vehicle["vehicle_id"], voucher_code="SVBK50")
    assert ok and pickup_shared_vehicle(s, booking["booking_id"], booking["pin_code"])[0]
    s["current_sim_time"] = "2026-10-21 08:45:00"
    ok, invoice, msg = return_shared_vehicle(s, booking["booking_id"], s["hubs"][1]["hub_id"])
    assert ok, msg
    assert invoice["total_fee"] == 10_000
    at = app(3)
    for key in ["wallet", "bookings", "hubs"]:
        at.session_state[key] = s[key]
    at.run()
    assert not at.exception
    metric = next(m for m in at.metric if m.label == "💵 Tổng doanh thu thu về")
    assert metric.value == "10,000 ₫"
    assert next(m for m in at.metric if m.label == "📋 Tổng số giao dịch ledger").value == str(len(s["wallet"]["ledger"]))
    assert any("booking_id" in d.value.columns and booking["booking_id"] in d.value["booking_id"].values for d in at.dataframe)


def test_student_ui_filters_available_vehicles_and_books_voucher():
    at = app(1)
    at.multiselect(key="sb_type_filter").set_value(["scooter"])
    at.slider(key="sb_soc_filter").set_value(80).run()
    assert not at.exception
    options = at.selectbox(key="sb_chosen_veh").options
    hub = at.session_state["hubs"][0]
    expected = {v["vehicle_id"] for v in hub["current_vehicles"] if v["type"] == "scooter" and v["status"] == "AVAILABLE" and v["battery_soc"] >= 80}
    assert expected and all(any(vid in option for vid in expected) for option in options)
    assert len(options) == len(expected)
    at.text_input(key="sb_voucher").set_value("SVBK50")
    at.button(key="sb_btn_confirm").click().run()
    assert not at.exception
    booking = at.session_state["bookings"][-1]
    assert booking["status"] == "RESERVED" and booking["voucher_code"] == "SVBK50"
    assert at.session_state["wallet"]["held_deposit"] == 50_000


def test_infrastructure_preview_isolated_apply_and_stale_rejected():
    at = app(7)
    baseline = deepcopy(at.session_state["hubs"])
    at.button(key="btn_run_port_failure").click().run()
    assert not at.exception
    preview = deepcopy(at.session_state["sim_preview_ss7"])
    assert at.session_state["hubs"] == baseline
    assert preview["metrics"]["failed_ports_total"] == 4
    at.session_state["state_version"] += 1
    at.button(key="btn_apply_ss7").click().run()
    assert at.session_state["hubs"] == baseline
    assert any("đã thay đổi" in e.value for e in at.error)
    at.button(key="btn_run_port_failure").click().run()
    expected = deepcopy(at.session_state["sim_preview_ss7"]["modified_hubs"])
    at.button(key="btn_apply_ss7").click().run()
    assert not at.exception and at.session_state["hubs"] == expected
    at.sidebar.radio[0].set_value(at.sidebar.radio[0].options[2]).run()
    assert not at.exception
    assert any("IoT mô phỏng" in w.value and "OFFLINE" in w.value for w in at.warning)


def test_charging_completion_notification_survives_rerun_and_receipt_is_recorded():
    at = app(5)
    sched = SmartChargingScheduler(cap_kw=150)
    sched.add_request(ChargingRequest(vehicle_id="EV-TEST", hub_id="HUB-001", battery_soc=98, port_kw=7.4))
    sched.allocate_ports(hub_id="HUB-001", available_port_count=1)
    session = next(iter(sched._active_sessions.values()))
    at.session_state["charging_scheduler"] = sched
    at.run()
    at.button(key="btn_tick_ss5").click().run()
    assert not at.exception
    assert at.session_state["charging_notifications"]
    assert any("COMPLETED_100" in w.value for w in at.warning)
    at.run()
    assert any("COMPLETED_100" in w.value for w in at.warning)
    at.button(key=f"unplug_{session.session_id}").click().run()
    assert not at.exception
    invoice = at.session_state["last_charging_invoice"]
    assert invoice["vehicle_id"] == "EV-TEST" and invoice["kwh_charged"] > 0
    assert invoice["energy_fee"] == round(invoice["kwh_charged"] * 7000)
    assert invoice["total_due"] == invoice["energy_fee"]
    assert at.session_state["charging_invoices"][-1] == invoice
    assert any(invoice["invoice_id"] in j.value for j in at.json)


def test_personal_charging_is_billed_once_on_consolidated_checkout():
    s = state()
    _, ev, _ = register_personal_ev(s, "OWNER", "Test", "59T12345", "scooter", "Test", 3.5)
    ok, reservation, _ = reserve_personal_ev_slot(s, "OWNER", ev["ev_id"], "HUB-001", request_charging=True, current_soc=98)
    assert ok and check_in_personal_ev(s, reservation["reservation_id"])[0]
    at = app(5)
    for key in ["wallet", "hubs", "personal_reservations"]:
        at.session_state[key] = s[key]
    sched = s["charging_scheduler"]
    session = next(iter(sched._active_sessions.values()))
    at.session_state["charging_scheduler"] = sched
    at.run()
    balance = at.session_state["wallet"]["balance"]
    held = at.session_state["wallet"]["held_deposit"]
    at.button(key="btn_tick_ss5").click().run()
    at.button(key=f"unplug_{session.session_id}").click().run()
    assert not at.exception
    deferred = at.session_state["last_charging_invoice"]
    assert deferred["total_due"] == 0 and "SS2" in deferred["billing_note"]
    assert at.session_state["wallet"]["balance"] == balance
    for key in ["wallet", "hubs", "personal_reservations"]:
        s[key] = at.session_state[key]
    ok, final, msg = check_out_personal_ev(s, reservation["reservation_id"], duration_hours=1, kwh_charged=deferred["kwh_charged"], overstay_minutes=0)
    assert ok, msg
    assert final["energy_fee"] == round(deferred["kwh_charged"] * 7000)
    assert s["wallet"]["balance"] == balance + held - final["total_amount"]
    assert s["wallet"]["held_deposit"] == 0
    assert s["hubs"][0]["charging_ports"]["available"] == 4

