"""
test_streamlit_navigation.py – Automated Streamlit AppTest for All 7 Subsystems
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from core.booking import create_shared_booking, pickup_shared_vehicle
from core.personal_ev import check_in_personal_ev, register_personal_ev, reserve_personal_ev_slot
from core.state import get_initial_session_state

REPO_ROOT = Path(__file__).resolve().parent.parent

def test_all_subsystems_render_without_exceptions():
    at = AppTest.from_file(str(REPO_ROOT / "src" / "app.py"))
    at.run()

    assert not at.exception, f"App had exception on startup: {at.exception}"

    # Radio options for 7 subsystems
    subsystems = [
        "1️⃣ Đặt xe & Chỗ đỗ (SV)",
        "2️⃣ Xe cá nhân – Đăng ký",
        "3️⃣ Giám sát Hub (Operator)",
        "4️⃣ Điều phối & Sự cố",
        "5️⃣ Lập lịch Sạc thông minh",
        "6️⃣ Mô phỏng: Nhu cầu SV",
        "7️⃣ Mô phỏng: Sự cố Hạ tầng",
    ]

    for label in subsystems:
        at.sidebar.radio[0].set_value(label).run()
        assert not at.exception, f"Subsystem '{label}' threw an exception: {at.exception}"


@pytest.mark.parametrize(("duration", "cost", "refund"), [(30, 0, 50_000), (45, 10_000, 40_000)])
def test_ss1_checkout_invoice_and_trip_history_agree(duration, cost, refund):
    state = get_initial_session_state()
    origin, destination = state["hubs"][:2]
    vehicle = next(v for v in origin["current_vehicles"] if v["status"] == "AVAILABLE" and v["battery_soc"] >= 20)
    ok, booking, msg = create_shared_booking(
        state, "SV-2211234", origin["hub_id"], vehicle["vehicle_id"], "SV-ECO", destination["hub_id"]
    )
    assert ok, msg
    assert pickup_shared_vehicle(state, booking["booking_id"], booking["pin_code"])[0]

    at = AppTest.from_file(str(REPO_ROOT / "src" / "app.py"))
    for key, value in state.items():
        at.session_state[key] = value
    at.run()
    at.number_input(key="sb_sim_trip_duration").set_value(duration)
    at.button(key="sb_btn_return").click().run()

    assert not at.exception
    invoice = at.session_state["last_invoice"]
    assert invoice["total_fee"] == cost
    assert invoice["refund_amount"] == refund
    assert invoice["deducted_from_available"] == 0
    assert any("Chi phí thực tế" in m.value and f"{cost:,.0f} ₫" in m.value for m in at.markdown)
    history = next(table.value for table in at.dataframe if "Chi phí" in table.value.columns)
    assert history.loc[history["Mã đặt chỗ"] == booking["booking_id"], "Chi phí"].item() == f"{cost:,.0f}₫"


def test_ss2_can_simulate_charging_and_settle_without_switching_tabs(monkeypatch):
    monkeypatch.setenv("EMOBILITY_PARKING_HOURLY_VND", "5000")
    state = get_initial_session_state()
    student_id = "SV-2211234"
    hub = state["hubs"][0]
    free_ports = hub["charging_ports"]["available"]
    ok, ev, msg = register_personal_ev(state, student_id, "Nguyễn Văn A", "59-X1 888.88", "scooter", "Klara", 3.5)
    assert ok, msg
    ok, booking, msg = reserve_personal_ev_slot(state, student_id, ev["ev_id"], hub["hub_id"], True, 90)
    assert ok, msg
    assert check_in_personal_ev(state, booking["reservation_id"])[0]

    at = AppTest.from_file(str(REPO_ROOT / "src" / "app.py"))
    for key, value in state.items():
        at.session_state[key] = value
    at.run()
    at.sidebar.radio[0].set_value("2️⃣ Xe cá nhân – Đăng ký").run()
    # One step charges the 0.35 kWh needed to reach 100%. Two more steps hold the port.
    for _ in range(3):
        at.button(key="ss2_advance_demo_clock").click().run()
        assert not at.exception

    at.button(key=f"btn_checkout_{booking['reservation_id']}").click().run()
    assert not at.exception
    invoice = at.session_state["last_pev_invoice"]
    assert invoice["kwh_charged"] == 0.35
    assert invoice["energy_fee"] == 2_450
    assert invoice["overstay_minutes"] == 30
    assert invoice["overstay_fee"] == 10_000
    assert invoice["parking_fee"] == 5_000
    assert invoice["total_amount"] == 17_450
    assert at.session_state["hubs"][0]["charging_ports"]["available"] == free_ports
    assert any("Điện năng sạc" in m.value and "17,450" in m.value for m in at.markdown)
