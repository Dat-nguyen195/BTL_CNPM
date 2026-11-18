"""
smart_charging.py – Subsystem 5: Lập lịch sạc thông minh (Smart Charging)
Smart E-Mobility Hub – ĐHQG-HCM

Chức năng chuẩn hóa:
  • Thuật toán chấm điểm ưu tiên Score = 0.5*(100-SoC) + 100*I(SoC<20) + 60*I(has_booking) + 30*I(SoC<50)
  • Kiểm soát trần công suất trạm 150 kW & phân bổ cổng sạc
  • Mô phỏng bước sạc (Tick): Cảnh báo 90%, Hoàn tất 100%, Ân hạn 15 phút & Phí phạt Overstay
  • Rút sạc (Unplug) và giải phóng cổng sạc cho xe kế tiếp
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from core.scheduler import SmartChargingScheduler, ChargingRequest, allocate_hub_ports, release_charging_session
from core.policies import HUB_POWER_CAP_KW, OVERSTAY_GRACE_MINUTES, OVERSTAY_RATE_PER_BLOCK_VND, get_kwh_rate
from core.billing import settle_overstay_charging
from core.state import bump_state_version

def _init_ss5():
    hubs = st.session_state.get("hubs", [])
    if "charging_scheduler" not in st.session_state:
        scheduler = SmartChargingScheduler(cap_kw=HUB_POWER_CAP_KW)
        for h in hubs:
            for v in h["current_vehicles"]:
                if v.get("status") in ["CHARGING", "WAITING", "parked"] and v.get("battery_soc", 100) < 60:
                    scheduler.add_request(ChargingRequest(
                        vehicle_id=v["vehicle_id"],
                        hub_id=h["hub_id"],
                        battery_soc=float(v["battery_soc"]),
                        has_student_booking=(v.get("status") == "RESERVED")
                    ))
        st.session_state["charging_scheduler"] = scheduler

def render():
    """Render giao diện Subsystem 5 – Lập lịch sạc thông minh."""
    _init_ss5()

    st.header("⚡ Lập lịch Sạc thông minh & Quản trị Công suất")
    st.caption("Phân hệ SS5 — Smart Charging & Queue Scheduling (FR-09, FR-10, FR-10b, FR-11).")

    scheduler: SmartChargingScheduler = st.session_state["charging_scheduler"]
    hubs = st.session_state.get("hubs", [])

    # KPI Thống kê
    queue = scheduler.get_sorted_queue()
    critical_count = sum(1 for r in queue if r.battery_soc < 20)
    booking_count = sum(1 for r in queue if r.has_student_booking)
    active_count = len(scheduler._active_sessions)

    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric("📋 Xe trong hàng đợi", f"{scheduler.queue_length} xe")
    kc2.metric("⚡ Đang sạc thực tế", f"{active_count} xe")
    kc3.metric("🔴 Xe pin khẩn cấp (<20%)", f"{critical_count} xe")
    kc4.metric("🎓 Xe có SV đặt chỗ", f"{booking_count} xe")

    st.divider()

    tab_q, tab_active, tab_overstay, tab_add = st.tabs([
        "📋 1. Hàng đợi ưu tiên (Queue)",
        "⚡ 2. Phiên sạc & Công suất lưới (150 kW Cap)",
        "⏳ 3. Quá hạn rút sạc (Overstay)",
        "➕ 4. Thêm yêu cầu sạc mới",
    ])

    # ═══════════════════════════════════════════════
    # TAB 1: HÀNG ĐỢI ƯU TIÊN
    # ═══════════════════════════════════════════════
    with tab_q:
        st.subheader("📋 Hàng đợi sạc (Đã sắp xếp tự động theo thuật toán)")
        with st.expander("📖 Chi tiết công thức tính điểm ưu tiên (PLAN.md 4.5)", expanded=False):
            st.markdown(f"""
$$Score = 0.5 \\times (100 - SoC) + 100 \\times I(SoC < 20) + 60 \\times I(has\\_booking) + 30 \\times I(SoC < 50)$$
- **Pin < 20%:** Khẩn cấp, cộng ngay 100 điểm.
- **Có SV đặt xe:** Ưu tiên phục vụ sinh viên, cộng 60 điểm.
- **Pin < 50%:** Mức thấp, cộng thêm 30 điểm.
- **Bonus tuyến tính:** $0.5 \\times (100 - SoC)$ điểm.
            """)

        queue_data = scheduler.get_queue_as_dicts()
        if queue_data:
            df = pd.DataFrame(queue_data)
            df.columns = ["Mã xe", "Hub", "Pin (%)", "Có SV đặt", "Điểm ưu tiên", "Thời gian yêu cầu"]
            df.insert(0, "Thứ tự", range(1, len(df) + 1))

            def _highlight_score(row):
                s = row["Điểm ưu tiên"]
                if s >= 150:
                    return ["background-color: #ffe0e0"] * len(row)
                elif s >= 80:
                    return ["background-color: #fff3cd"] * len(row)
                return [""] * len(row)

            st.dataframe(df.style.apply(_highlight_score, axis=1), use_container_width=True, hide_index=True)

            # Nút phân bổ cổng tự động
            st.markdown("##### 🔌 Phân bổ cổng sạc tự động cho Hub:")
            hub_names = [h["name"] for h in hubs]
            sel_h_name = st.selectbox("Chọn Hub để phân bổ cổng:", hub_names, key="alloc_hub_name")
            sel_h = next(h for h in hubs if h["name"] == sel_h_name)

            if st.button(f"⚡ Phân bổ cổng tại {sel_h_name}", type="primary", key="btn_run_alloc"):
                avail_p = sel_h["charging_ports"]["available"]
                if avail_p <= 0:
                    st.error("❌ Hub này hiện không còn cổng sạc trống khả dụng!")
                else:
                    allocs = allocate_hub_ports(st.session_state, sel_h["hub_id"])
                    if allocs:
                        st.success(f"✅ Đã phân bổ cổng thành công cho {len(allocs)} xe tại {sel_h_name}!")
                        st.rerun()
                    else:
                        st.info("Không có xe nào thuộc Hub này trong hàng đợi cần phân bổ.")
        else:
            st.info("Hàng đợi sạc hiện đang trống.")

    # ═══════════════════════════════════════════════
    # TAB 2: PHIÊN SẠC & CÔNG SUẤT LƯỚI
    # ═══════════════════════════════════════════════
    with tab_active:
        st.subheader("⚡ Quản lý Phiên sạc & Giám sát Công suất trạm")
        st.caption(f"Trần công suất an toàn (Power Cap): **{HUB_POWER_CAP_KW} kW**.")

        # Mô phỏng bước thời gian
        sim_cols = st.columns([3, 1])
        with sim_cols[0]:
            st.info("Mô phỏng nạp pin thời gian thực: mỗi bước nạp năng lượng tương ứng vào pin xe.")
        with sim_cols[1]:
            if st.button("⏩ Mô phỏng +15 phút sạc", key="btn_tick_ss5"):
                events = scheduler.advance_simulation_tick(minutes=15, sim_time=st.session_state.get("current_sim_time"))
                from core.state import advance_sim_time
                advance_sim_time(st.session_state, minutes=15)
                bump_state_version(st.session_state)
                st.session_state.setdefault("charging_notifications", []).extend(events)
                st.rerun()

        for ev in st.session_state.get("charging_notifications", [])[-10:]:
            st.warning(f"📢 [{ev['type']}] {ev['message']}")

        active_sess = list(scheduler._active_sessions.values())
        if active_sess:
            sess_rows = []
            for s in active_sess:
                sess_rows.append({
                    "Mã phiên": s.session_id,
                    "Mã xe": s.vehicle_id,
                    "Cổng": s.port_id,
                    "Công suất (kW)": s.port_kw,
                    "Pin hiện tại": f"{s.current_soc:.1f}%",
                    "Đã nạp (kWh)": f"{s.energy_delivered_kwh:.2f}",
                    "Trạng thái": s.status,
                    "Quá hạn (phút)": s.overstay_minutes,
                    "Phí phạt Overstay": f"{s.overstay_fee:,.0f}₫" if s.overstay_fee > 0 else "0₫"
                })
            st.dataframe(pd.DataFrame(sess_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có phiên sạc nào đang cắm cổng. Hãy phân bổ cổng tại Tab 1.")

    # ═══════════════════════════════════════════════
    # TAB 3: QUÁ HẠN RÚT SẠC (OVERSTAY)
    # ═══════════════════════════════════════════════
    with tab_overstay:
        st.subheader("⏳ Quản lý Đỗ quá hạn sau sạc & Rút sạc (Unplug)")
        st.caption(f"Chính sách: Miễn phí **{OVERSTAY_GRACE_MINUTES} phút** ân hạn. Sau đó phạt **{OVERSTAY_RATE_PER_BLOCK_VND:,.0f} ₫/15 phút**.")

        completed_sess = [s for s in scheduler._active_sessions.values() if s.status in ["GRACE_PERIOD", "OVERSTAY"]]
        if completed_sess:
            for s in completed_sess:
                status_color = "red" if s.status == "OVERSTAY" else "orange"
                st.warning(
                    f"**Phiên #{s.session_id}** — Xe **{s.vehicle_id}** tại cổng `{s.port_id}`: "
                    f"Pin **{s.current_soc:.1f}%** | Trạng thái: **{s.status}** | "
                    f"Quá hạn: **{s.overstay_minutes} phút** | Phạt: **{s.overstay_fee:,.0f} VNĐ**"
                )
                if st.button(f"🔌 Rút sạc & Giải phóng cổng ({s.vehicle_id})", key=f"unplug_{s.session_id}"):
                    unplugged = release_charging_session(st.session_state, s.session_id)
                    if unplugged:
                        for h in hubs:
                            if h["hub_id"] == unplugged.hub_id:
                                for v in h.get("current_vehicles", []):
                                    if v.get("vehicle_id") == unplugged.vehicle_id:
                                        v["battery_soc"] = unplugged.current_soc
                                        if v.get("status") == "CHARGING":
                                            v["status"] = "AVAILABLE" if unplugged.current_soc >= 20 else "MAINTENANCE"
                                break

                        # Quyết toán ví/ghi nợ phí quá hạn (Overstay)
                        sim_now_str = st.session_state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        wallet = st.session_state.setdefault("wallet", {})
                        # Personal EVs pay once on their consolidated SS2 invoice.
                        personal_reservation = next((r for r in st.session_state.get("personal_reservations", []) if r.get("ev_id") == unplugged.vehicle_id and r.get("status") == "CHECKED_IN"), None)
                        energy_fee = round(unplugged.energy_cost_vnd)
                        invoice = settle_overstay_charging(
                            wallet=wallet,
                            session_id=unplugged.session_id,
                            vehicle_id=unplugged.vehicle_id,
                            overstay_fee=0 if personal_reservation else unplugged.overstay_fee,
                            energy_fee=0 if personal_reservation else energy_fee,
                            kwh_charged=unplugged.energy_delivered_kwh,
                            sim_time=sim_now_str
                        )
                        if personal_reservation:
                            personal_reservation["charging_port_allocated"] = False
                            invoice["billing_note"] = "Điện năng và quá giờ quyết toán một lần tại Check-out SS2."
                        st.session_state.setdefault("charging_invoices", []).append(invoice)
                        st.session_state["last_charging_invoice"] = invoice
                        bump_state_version(st.session_state)

                        if invoice.get("overstay_fee", 0) > 0:
                            st.success(
                                f"✅ Đã rút sạc xe {unplugged.vehicle_id}. Cổng sạc đã giải phóng! "
                                f"Đã quyết toán phí Overstay: {invoice['total_due']:,} VNĐ "
                                f"(Đã trừ ví: {invoice['deducted']:,} VNĐ, Ghi nợ: {invoice['debt']:,} VNĐ)."
                            )
                        else:
                            st.success(f"✅ Đã rút sạc an toàn cho xe {unplugged.vehicle_id}. Cổng sạc đã được giải phóng!")
                        st.rerun()
        else:
            st.success("✅ Không có xe nào đang đỗ quá hạn rút sạc.")

        if st.session_state.get("last_charging_invoice"):
            st.subheader("Biên nhận sạc và phí chiếm dụng gần nhất")
            st.json(st.session_state["last_charging_invoice"])

    # ═══════════════════════════════════════════════
    # TAB 4: THÊM YÊU CẦU SẠC MỚI
    # ═══════════════════════════════════════════════
    with tab_add:
        st.subheader("➕ Thêm yêu cầu sạc mới vào hàng đợi")
        with st.form("add_charging_req_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                new_vid = st.text_input("Mã xe điện:", value="EV-BK-999")
                new_hub_id = st.selectbox("Hub sạc:", [h["hub_id"] for h in hubs])
            with fc2:
                new_soc = st.slider("Mức pin hiện tại (%):", min_value=0, max_value=99, value=15)
                has_book = st.checkbox("Xe có sinh viên đặt trước (Priority Bonus +60)", value=True)

            if st.form_submit_button("⚡ Thêm vào hàng đợi", type="primary"):
                req = ChargingRequest(
                    vehicle_id=new_vid,
                    hub_id=new_hub_id,
                    battery_soc=float(new_soc),
                    has_student_booking=has_book
                )
                scheduler.add_request(req)
                st.success(f"🎉 Đã thêm xe **{new_vid}** vào hàng đợi với điểm ưu tiên: **{req.priority_score:.1f}**!")
                st.rerun()
