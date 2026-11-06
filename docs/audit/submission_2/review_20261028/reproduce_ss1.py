"""Targeted review reproductions; prints observations without changing app code.

Run with venv/bin/python from the project root. AppTest uses an isolated session.
This script is evidence for the review, not part of the existing pytest suite.
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

from streamlit.testing.v1 import AppTest
from core.state import get_initial_session_state
from core.booking import (
    create_shared_booking, pickup_shared_vehicle, return_shared_vehicle,
)


def reproduce():
    at = AppTest.from_file(str(ROOT / "src/app.py"), default_timeout=15).run()
    at.text_input(key="sb_voucher").set_value("")
    at.selectbox(key="sb_dest_hub").set_value("Hub KTX Khu B")
    at.button(key="sb_btn_confirm").click().run()
    assert not at.exception, "Unexpected failure before pickup"
    at.button(key="sb_btn_pickup").click().run()
    assert not at.exception, "Unexpected failure before return"
    at.number_input(key="sb_sim_trip_duration").set_value(45)
    at.button(key="sb_btn_return").click().run()
    results = {
        "return_ui": {
            "exceptions": [e.message for e in at.exception],
            "booking_status": at.session_state["bookings"][-1]["status"],
            "balance": at.session_state["wallet"]["balance"],
            "held": at.session_state["wallet"]["held_deposit"],
            "stored_invoice_total": at.session_state["last_invoice"]["total_fee"],
        }
    }

    state = get_initial_session_state()
    hub = state["hubs"][0]
    vehicle = next(v for v in hub["current_vehicles"]
                   if v["status"] == "AVAILABLE" and v["battery_soc"] >= 20)
    ok, booking, message = create_shared_booking(
        state, "REVIEW", hub["hub_id"], vehicle["vehicle_id"],
        voucher_code="SAIMA123",
    )
    assert ok, message
    assert pickup_shared_vehicle(state, booking["booking_id"], booking["pin_code"])[0]
    ok, invoice, message = return_shared_vehicle(
        state, booking["booking_id"], state["hubs"][1]["hub_id"],
        override_duration_minutes=45,
    )
    assert ok, message
    results["invalid_voucher"] = {
        "code": "SAIMA123", "expected_total": 15_000,
        "actual_total": invoice["total_fee"], "discount": invoice["discount"],
    }
    return results


if __name__ == "__main__":
    print(json.dumps(reproduce(), ensure_ascii=False, indent=2))
