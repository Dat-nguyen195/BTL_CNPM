from datetime import datetime, timezone, timedelta
from copy import deepcopy

from core.state import get_initial_session_state
from core.personal_ev import register_personal_ev, reserve_personal_ev_slot, check_in_personal_ev, check_out_personal_ev
from core.scheduler import release_charging_session, apply_hub_snapshot
from core.simulator import HubEventSimulator
from core.telemetry import publish_event, consume_events


def charging_state():
    state = get_initial_session_state()
    _, ev, _ = register_personal_ev(state, "owner", "Test", "59TEST", "scooter", "Test", 3.5)
    _, reservation, _ = reserve_personal_ev_slot(state, "owner", ev["ev_id"], "HUB-001", True, 98)
    assert check_in_personal_ev(state, reservation["reservation_id"])[0]
    return state, reservation


def test_overstay_survives_unplug_and_checkout_once():
    state, reservation = charging_state()
    scheduler = state["charging_scheduler"]
    for _ in range(3):
        scheduler.advance_simulation_tick(15)
    session = release_charging_session(state, reservation["charging_session_id"])
    assert session.overstay_fee == 10000
    assert round(session.energy_delivered_kwh, 2) == 0.07
    ok, invoice, _ = check_out_personal_ev(state, reservation["reservation_id"], duration_hours=1)
    assert ok and invoice["overstay_fee"] == 10000
    before = deepcopy(state["wallet"])
    assert not check_out_personal_ev(state, reservation["reservation_id"])[0]
    assert state["wallet"] == before


def test_failure_stops_real_session_without_losing_measured_energy():
    state, reservation = charging_state()
    scheduler = state["charging_scheduler"]
    session_id = reservation["charging_session_id"]
    hubs, _, _ = HubEventSimulator(state["hubs"]).simulate_port_failure("HUB-001", 10)
    apply_hub_snapshot(state, hubs)
    assert session_id not in scheduler._active_sessions
    assert reservation["delivered_kwh"] == 0
    scheduler.advance_simulation_tick(15)
    assert reservation["delivered_kwh"] == 0
    assert not reservation["charging_port_allocated"]


def test_feed_shared_idempotent_stale_invalid_and_preview_version(tmp_path):
    path = tmp_path / "events.db"
    states = [get_initial_session_state(), get_initial_session_state()]
    now = datetime.now(timezone.utc)
    event = dict(event_id="one", hub_id="HUB-001", port_id="1", event_type="OFFLINE", occurred_at=now.isoformat())
    assert publish_event(event, path)
    assert not publish_event(event, path)
    for state in states:
        version = state["state_version"]
        assert consume_events(state, path) == 1
        assert state["state_version"] > version
        assert consume_events(state, path) == 0
    assert states[0]["hubs"] == states[1]["hubs"]
    assert publish_event(dict(event, event_id="old", event_type="ONLINE",
                              occurred_at=(now-timedelta(seconds=1)).isoformat()), path)
    assert publish_event(dict(event, event_id="bad", hub_id="MISSING"), path)
    assert consume_events(states[0], path) == 0
    assert [e["result"] for e in states[0]["telemetry_log"]] == ["APPLIED", "STALE", "REJECTED"]
    restarted = get_initial_session_state()
    consume_events(restarted, path)
    assert restarted["hubs"] == states[0]["hubs"]


def test_live_fragment_observers_consume_same_independent_feed(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    path = tmp_path / "live.db"
    monkeypatch.setenv("EMOBILITY_IOT_ENABLED", "1")
    monkeypatch.setenv("EMOBILITY_IOT_DB", str(path))
    app = str(Path(__file__).resolve().parents[1] / "src/app.py")
    observers = [AppTest.from_file(app, default_timeout=20).run() for _ in range(2)]
    event = dict(event_id="outside", hub_id="HUB-001", port_id="1",
                 event_type="OFFLINE", occurred_at=datetime.now(timezone.utc).isoformat())
    publish_event(event, path)
    for observer in observers:
        observer.run()
        assert not observer.exception
        assert observer.session_state["telemetry_log"][-1]["event_id"] == "outside"
        assert observer.session_state["telemetry_log"][-1]["result"] == "APPLIED"


def test_tariff_tick_crosses_peak_boundary():
    from core.scheduler import SmartChargingScheduler, ChargingRequest
    scheduler = SmartChargingScheduler()
    scheduler.add_request(ChargingRequest("v", "h", 0, port_kw=1))
    scheduler.allocate_ports("h", 1)
    scheduler.advance_simulation_tick(2, "2026-10-21 08:59:00")
    session = next(iter(scheduler._active_sessions.values()))
    from core.policies import get_kwh_rate
    expected = (get_kwh_rate(datetime(2026,10,21,8,59).time()) +
                get_kwh_rate(datetime(2026,10,21,9,0).time())) / 60
    assert abs(session.energy_cost_vnd - expected) < 1e-8


def test_personal_unplug_overstay_ui_then_operator_confirmation():
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    state, reservation = charging_state()
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "src/app.py"), default_timeout=20).run()
    for key in ("wallet", "hubs", "personal_reservations", "charging_scheduler"):
        app.session_state[key] = state[key]
    app.sidebar.radio[0].set_value(app.sidebar.radio[0].options[4]).run()
    for _ in range(3):
        app.button(key="btn_tick_ss5").click().run()
    session_id = reservation["charging_session_id"]
    app.button(key="unplug_" + session_id).click().run()
    assert not app.exception
    for key in ("wallet", "hubs", "personal_reservations", "charging_scheduler"):
        state[key] = app.session_state[key]
    ok, invoice, _ = check_out_personal_ev(state, reservation["reservation_id"], duration_hours=1)
    assert ok and invoice["overstay_fee"] == 10000
    app.session_state["personal_reservations"] = state["personal_reservations"]
    app.session_state["wallet"] = state["wallet"]
    app.sidebar.radio[0].set_value(app.sidebar.radio[0].options[2]).run()
    wallet_before = deepcopy(app.session_state["wallet"])
    app.button(key="confirm_" + invoice["invoice_id"]).click().run()
    assert not app.exception
    assert app.session_state["personal_reservations"][0]["invoice"]["operator_confirmed_at"]
    assert app.session_state["wallet"] == wallet_before


def test_dashboard_separates_offline_ports_from_occupied_ports(tmp_path, monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    feed = tmp_path / "dashboard.db"
    monkeypatch.setenv("EMOBILITY_IOT_ENABLED", "1")
    monkeypatch.setenv("EMOBILITY_IOT_DB", str(feed))
    event = dict(event_id="dashboard-offline", hub_id="HUB-001", port_id="1",
                 event_type="OFFLINE", occurred_at=datetime.now(timezone.utc).isoformat())
    assert publish_event(event, feed)
    app_file = Path(__file__).resolve().parents[1] / "src/app.py"
    app = AppTest.from_file(str(app_file)).run()
    app.sidebar.radio[0].set_value(app.sidebar.radio[0].options[2]).run()

    assert not app.exception
    assert any("OFFLINE" in alert.value for alert in app.warning)
    assert not any("Bình thường / Đồng bộ" in alert.value for alert in app.info)
    energy = next(table.value for table in app.dataframe if "Cổng offline" in table.value)
    hub = energy.iloc[0]
    assert hub["Cổng offline"] == 1
    assert hub["Cổng đang chiếm dụng"] + hub["Cổng trống"] + hub["Cổng offline"] == 10
