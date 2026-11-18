"""
app.py – Streamlit Main Entry Point
Smart E-Mobility Hub – Hệ thống điều phối phương tiện điện trong ĐHQG-HCM

Chạy ứng dụng:
    streamlit run src/app.py
"""

import streamlit as st
import json
import os

# ──────────────────────────────────────────────
# CẤU HÌNH TRANG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Smart E-Mobility Hub – ĐHQG-HCM",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# KHỞI TẠO DỮ LIỆU VÀ TRẠNG THÁI HỆ THỐNG
# ──────────────────────────────────────────────
from core.state import init_session_state, advance_sim_time, UserRole
from core.booking import process_expired_bookings
from core.personal_ev import sweep_expired_personal_reservations

# Centralized session state initialization
init_session_state(st.session_state)

# Automatically sweep expired reservations (shared EV 30-min & personal EV 30-min after scheduled arrival) before rendering any view
process_expired_bookings(st.session_state)
sweep_expired_personal_reservations(st.session_state)


# ──────────────────────────────────────────────
# SIDEBAR – NAVIGATION
# ──────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "assets", "vnu_logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=80)
else:
    st.sidebar.markdown("## 🚲")
st.sidebar.title("🚲 Smart E-Mobility Hub")
st.sidebar.caption("Khu đô thị ĐHQG-HCM")
st.sidebar.divider()

# Danh sách 7 subsystem
SUBSYSTEMS = {
    "1️⃣ Đặt xe & Chỗ đỗ (SV)":        "student_booking",
    "2️⃣ Xe cá nhân – Đăng ký":          "personal_ev",
    "3️⃣ Giám sát Hub (Operator)":       "hub_monitor",
    "4️⃣ Điều phối & Sự cố":             "dispatch_incident",
    "5️⃣ Lập lịch Sạc thông minh":       "smart_charging",
    "6️⃣ Mô phỏng: Nhu cầu SV":         "sim_demand",
    "7️⃣ Mô phỏng: Sự cố Hạ tầng":      "sim_infrastructure",
}

selected_label = st.sidebar.radio(
    "📋 Chọn Subsystem:",
    list(SUBSYSTEMS.keys()),
    index=0,
)

st.sidebar.divider()

# Điều khiển thời gian giả lập & Demo State
sim_time_str = st.session_state.get("current_sim_time", "2026-10-21 08:00:00")
st.sidebar.markdown(f"🕒 **Đồng hồ Demo:** `{sim_time_str}`")
col_t1, col_t2 = st.sidebar.columns([1, 1])
with col_t1:
    if st.button("⏩ +15 phút", use_container_width=True, help="Tua nhanh 15 phút để kiểm thử đếm ngược hết hạn, ân hạn sạc"):
        advance_sim_time(st.session_state, minutes=15)
        st.rerun()
with col_t2:
    if st.button("🔄 Reset", use_container_width=True, help="Khôi phục trạng thái ban đầu (Reset Demo)"):
        init_session_state(st.session_state, force_reset=True)
        st.rerun()

st.sidebar.divider()

# Thông tin nhanh ở sidebar
st.sidebar.markdown("### 📊 Thống kê nhanh")
hubs = st.session_state.get("hubs", [])
total_vehicles = sum(len(h["current_vehicles"]) for h in hubs)
total_slots = sum(h["total_slots"] for h in hubs)
total_available = sum(h["available_slots"] for h in hubs)
total_ports = sum(h["charging_ports"]["total"] for h in hubs)
total_ports_avail = sum(h["charging_ports"]["available"] for h in hubs)

st.sidebar.metric("Tổng Hub", len(hubs))
st.sidebar.metric("Xe đang có", total_vehicles)
st.sidebar.metric("Chỗ trống", f"{total_available}/{total_slots}")
st.sidebar.metric("Cổng sạc trống", f"{total_ports_avail}/{total_ports}")

st.sidebar.divider()
st.sidebar.caption("© 2026 – Nhóm SV HCMUT | Môn Công nghệ Phần mềm")


# ──────────────────────────────────────────────
# IMPORT VÀ RENDER SUBSYSTEM TƯƠNG ỨNG
# ──────────────────────────────────────────────
selected_module = SUBSYSTEMS[selected_label]

# Import động từ thư mục components
if selected_module == "student_booking":
    from components.student_booking import render
elif selected_module == "personal_ev":
    from components.personal_ev import render
elif selected_module == "hub_monitor":
    from components.hub_monitor import render
elif selected_module == "dispatch_incident":
    from components.dispatch_incident import render
elif selected_module == "smart_charging":
    from components.smart_charging import render
elif selected_module == "sim_demand":
    from components.sim_demand import render
elif selected_module == "sim_infrastructure":
    from components.sim_infrastructure import render

# Gọi hàm render() của subsystem đã chọn
if os.environ.get("EMOBILITY_IOT_ENABLED") == "1":
    from core.telemetry import consume_events
    @st.fragment(run_every="2s")
    def live_view():
        consume_events(st.session_state)
        render()
        if st.session_state.get("telemetry_log"):
            st.subheader("Sự kiện cảm biến")
            st.dataframe(st.session_state["telemetry_log"][-10:], use_container_width=True)
    live_view()
else:
    render()
