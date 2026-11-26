"""
personal_ev.py – Subsystem 2: Quản lý & Đăng ký dịch vụ cho Xe cá nhân
Smart E-Mobility Hub – ĐHQG-HCM

Cung cấp đầy đủ 4 luồng thao tác trực tiếp tương ứng 4 Use Case chuẩn hóa:
  • Tab 1: Đăng ký xe điện cá nhân (UC_Dang_Ki_EV / UC_SS2_01)
  • Tab 2: Đặt trước chỗ đỗ & yêu cầu sạc (UC_Dat_Cho_Va_Sac / UC_SS2_02)
  • Tab 3: Check-in xác thực vào trạm (UC_Check_In / UC_SS2_03)
  • Tab 4: Check-out & Quyết toán biểu phí kết hợp (UC_Check_Out_Thanh_Toan / UC_SS2_04)

FR Covered: FR-03, FR-03b, FR-04, FR-05b, FR-15b
US Covered: US-08, US-09, US-10, US-11, US-11b, US-12
"""

import streamlit as st
import os
import pandas as pd
from datetime import datetime, timedelta

from core.personal_ev import (
    register_personal_ev,
    reserve_personal_ev_slot,
    check_in_personal_ev,
    check_out_personal_ev,
    cancel_personal_reservation
)
from core.state import advance_demo_clock
from core.policies import (
    PEV_PARKING_FEE_PER_VISIT_VND,
    PEV_OFFPEAK_KWH_RATE_VND,
    PEV_PEAK_KWH_RATE_VND,
    OVERSTAY_GRACE_MINUTES,
    OVERSTAY_RATE_PER_BLOCK_VND,
    PEV_RESERVATION_DEPOSIT_VND,
    PEV_ARRIVAL_EXPIRY_MINUTES
)

def _init_pev_state():
    if "personal_evs" not in st.session_state:
        st.session_state["personal_evs"] = []
    if "personal_reservations" not in st.session_state:
        st.session_state["personal_reservations"] = []
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = {
            "user_id": "SV-2211234",
            "name": "Nguyễn Văn A",
            "role": "STUDENT"
        }

def _render_personal_invoice(invoice):
    rate = f"{invoice['energy_rate']:,.0f} ₫/kWh" if invoice["kwh_charged"] else "Không phát sinh điện năng"
    st.subheader("🧾 Hóa đơn quyết toán xe cá nhân gần nhất")
    st.markdown(f"""
| Hạng mục quyết toán | Chi tiết thanh toán |
|:---|:---|
| **Mã hóa đơn** | `{invoice['invoice_id']}` |
| **Biển số xe** | **{invoice['plate']}** |
| **Thời gian đỗ** | {invoice['duration_hours']:g} giờ · **{invoice['parking_fee']:,.0f} ₫** |
| **Điện năng sạc** | {invoice['kwh_charged']} kWh · **{invoice['energy_fee']:,.0f} ₫** |
| **Đơn giá điện bình quân** | {rate} |
| **Phí chiếm cổng sau khi đầy pin** | {invoice['overstay_minutes']} phút (ân hạn {OVERSTAY_GRACE_MINUTES} phút) · **{invoice['overstay_fee']:,.0f} ₫** |
| **Tổng chi phí** | **{invoice['total_amount']:,.0f} ₫** |
| **Đã trừ từ ví** | **{invoice['deducted_from_wallet']:,.0f} ₫** |
| **Ghi nhận nợ** | **{invoice['debt_incurred']:,.0f} ₫** |
    """)

def render():
    """Render giao diện Subsystem 2 – Đăng ký & Vận hành dịch vụ Xe điện Cá nhân."""
    _init_pev_state()

    st.caption("Biểu phí demo giả định: tính theo giờ bắt đầu, mặc định 5.000đ/giờ; cấu hình EMOBILITY_PARKING_HOURLY_VND.")
    st.header("🔌 Quản lý & Vận hành Dịch vụ Xe điện Cá nhân")
    st.caption("Phân hệ SS2 — Personal EV Services | Đăng ký → Đặt chỗ/Sạc → Check-in → Check-out")

    hubs = st.session_state.get("hubs", [])
    user = st.session_state["current_user"]
    wallet = st.session_state.get("wallet", {})

    # Thẻ thông tin ví & chính sách
    wc1, wc2, wc3, wc4 = st.columns(4)
    wc1.metric("👤 Chủ xe / SV", f"{user['name']} ({user['user_id']})")
    wc2.metric("💰 Ví khả dụng", f"{wallet.get('balance', 0):,.0f} ₫")
    wc3.metric("🔒 Tiền cọc giữ chỗ", f"{wallet.get('held_deposit', 0):,.0f} ₫")
    wc4.metric("🅿️ Phí đỗ xe", f"{int(os.environ.get('EMOBILITY_PARKING_HOURLY_VND', '5000')):,.0f} ₫/giờ bắt đầu (demo)")

    st.divider()

    tab_reg, tab_res, tab_in, tab_out = st.tabs([
        "📋 1. Đăng ký xe mới (UC_SS2_01)",
        "⚡ 2. Đặt chỗ & Sạc (UC_SS2_02)",
        "🚪 3. Check-in trạm (UC_SS2_03)",
        "🧾 4. Check-out & Quyết toán (UC_SS2_04)",
    ])

    # ═══════════════════════════════════════════════
    # TAB 1: ĐĂNG KÝ XE MỚI
    # ═══════════════════════════════════════════════
    with tab_reg:
        st.subheader("📋 Đăng ký xe điện cá nhân vào hệ thống ĐHQG-HCM")
        with st.form("pev_reg_form"):
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                owner_name = st.text_input("Họ tên chủ xe:", value=user["name"])
                plate = st.text_input("Biển số xe (Ví dụ: 59-X1 123.45):", value="59-X1 888.88")
            with r_col2:
                ev_type = st.selectbox("Loại phương tiện:", ["scooter", "bike", "car"], key="reg_ev_type")
                brand = st.text_input("Hãng / Dòng xe:", value="VinFast Klara S")
            battery_kwh = st.number_input("Dung lượng pin danh định (kWh):", min_value=0.5, max_value=120.0, value=3.5, step=0.5)

            if st.form_submit_button("✅ Đăng ký phương tiện", type="primary"):
                ok, new_ev, msg = register_personal_ev(
                    state=st.session_state,
                    owner_id=user["user_id"],
                    owner_name=owner_name,
                    plate_number=plate,
                    ev_type=ev_type,
                    brand=brand,
                    battery_kwh=battery_kwh
                )
                if ok:
                    st.success(f"🎉 {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    # ═══════════════════════════════════════════════
    # TAB 2: ĐẶT CHỖ & SẠC
    # ═══════════════════════════════════════════════
    with tab_res:
        st.subheader("⚡ Đặt trước chỗ đỗ & Đăng ký dịch vụ sạc thông minh")
        my_evs = [ev for ev in st.session_state.get("personal_evs", []) if ev.get("owner_id") == user["user_id"]]

        if not my_evs:
            st.info("💡 Bạn chưa có xe cá nhân nào trong hệ thống. Vui lòng đăng ký tại tab **1. Đăng ký xe mới**.")
        else:
            with st.form("pev_res_form"):
                ev_options = [f"{ev['ev_id']} — {ev['plate']} ({ev['brand']})" for ev in my_evs]
                chosen_ev_str = st.selectbox("Chọn xe cá nhân của bạn:", ev_options)
                chosen_ev_id = chosen_ev_str.split(" — ")[0]

                hub_options = [f"{h['hub_id']} – {h['name']} (Còn {h['available_slots']} chỗ, {h['charging_ports']['available']} cổng sạc)" for h in hubs]
                chosen_hub_str = st.selectbox("Chọn Hub điểm đến:", hub_options)
                chosen_hub_id = chosen_hub_str.split(" – ")[0]

                arrival_offset = st.number_input("Dự kiến đến trạm sau (phút):", min_value=0, max_value=1440, value=0, step=15, key="pev_arrival_offset")
                sim_now = datetime.strptime(st.session_state["current_sim_time"], "%Y-%m-%d %H:%M:%S")
                booking_start = sim_now + timedelta(minutes=arrival_offset)
                st.caption(f"Thời gian đến: {booking_start:%d/%m/%Y %H:%M}. Hạn check-in: {PEV_ARRIVAL_EXPIRY_MINUTES} phút sau giờ đã đặt. Prototype giữ chỗ đỗ ngay khi xác nhận; cổng sạc được cấp khi check-in.")

                service_charge = st.checkbox("⚡ Đăng ký sử dụng dịch vụ sạc tại Hub", value=True)
                current_soc = st.slider("Phần trăm pin ước tính khi đến trạm (%):", min_value=5, max_value=95, value=35)

                with st.expander("📊 Biểu phí dịch vụ xe cá nhân", expanded=True):
                    st.markdown(f"""
| Khoản mục | Đơn giá quy định |
|:---|:---|
| **Phí đỗ xe** | **{int(os.environ.get('EMOBILITY_PARKING_HOURLY_VND', '5000')):,.0f} ₫/giờ bắt đầu (demo)** |
| **Giá điện giờ thấp điểm** | **{PEV_OFFPEAK_KWH_RATE_VND:,.0f} ₫/kWh** |
| **Giá điện giờ cao điểm** | **{PEV_PEAK_KWH_RATE_VND:,.0f} ₫/kWh** (06:00-09:00 & 16:00-19:30) |
| **Tiền cọc giữ chỗ** | **{PEV_RESERVATION_DEPOSIT_VND:,.0f} ₫** (Khóa tạm trong ví, hoàn 100% khi quyết toán check-out) |
| **Phạt đỗ quá giờ (Overstay)** | Miễn phí {OVERSTAY_GRACE_MINUTES} phút sau khi sạc đầy, sau đó **{OVERSTAY_RATE_PER_BLOCK_VND:,.0f} ₫/15 phút** |
                    """)

                if st.form_submit_button(f"✅ Đặt chỗ giữ chỗ trước (Khóa cọc {PEV_RESERVATION_DEPOSIT_VND:,.0f}₫)", type="primary"):
                    ok, res, msg = reserve_personal_ev_slot(
                        state=st.session_state,
                        owner_id=user["user_id"],
                        ev_id=chosen_ev_id,
                        hub_id=chosen_hub_id,
                        request_charging=service_charge,
                        current_soc=current_soc,
                        booking_start_time=booking_start.strftime("%Y-%m-%d %H:%M:%S")
                    )
                    if ok:
                        st.success(f"🎉 {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    # ═══════════════════════════════════════════════
    # TAB 3: CHECK-IN TRẠM
    # ═══════════════════════════════════════════════
    with tab_in:
        st.subheader("🚪 Check-in vào trạm & Mở barie thông minh")
        pending_res = [
            r for r in st.session_state.get("personal_reservations", [])
            if r.get("owner_id") == user["user_id"] and r.get("status") == "RESERVED"
        ]

        if not pending_res:
            st.info("📭 Hiện không có lệnh đặt chỗ nào đang chờ check-in.")
        else:
            for r in pending_res:
                st.info(
                    f"**Mã đặt chỗ:** `{r['reservation_id']}`\n\n"
                    f"- Xe: **{r['plate']}** | Hub: **{r['hub_name']}**\n"
                    f"- Dịch vụ sạc: **{'Có' if r.get('request_charging') else 'Không'}**\n"
                    f"- Hạn chót check-in: `{r['arrival_deadline']}`"
                )
                b_in, b_cancel = st.columns(2)
                with b_in:
                    if st.button(f"🚗 Xác thực check-in cho xe {r['plate']}", key=f"btn_checkin_{r['reservation_id']}"):
                        ok, msg = check_in_personal_ev(st.session_state, r["reservation_id"])
                        if ok:
                            st.success(f"🎉 {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                with b_cancel:
                    if st.button(f"✖️ Hủy đặt chỗ (hoàn 100% cọc trước hạn)", key=f"btn_cancel_{r['reservation_id']}"):
                        ok, msg = cancel_personal_reservation(st.session_state, r["reservation_id"], owner_id=user["user_id"])
                        if ok:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

    # ═══════════════════════════════════════════════
    # TAB 4: CHECK-OUT & QUYẾT TOÁN
    # ═══════════════════════════════════════════════
    with tab_out:
        st.subheader("🧾 Check-out, Giải phóng cổng sạc & Quyết toán chi phí")
        checkout_message = st.session_state.pop("personal_checkout_message", None)
        if checkout_message:
            st.success(f"🎉 {checkout_message}")
        checked_in_res = [
            r for r in st.session_state.get("personal_reservations", [])
            if r.get("owner_id") == user["user_id"] and r.get("status") == "CHECKED_IN"
        ]

        if not checked_in_res:
            st.info("📭 Không có xe nào đang đỗ/sạc tại Hub cần check-out.")
        else:
            if st.button("⏩ Mô phỏng thêm 15 phút", key="ss2_advance_demo_clock",
                         help="Tua đồng hồ chung và cập nhật điện năng, thời gian chiếm cổng của phiên sạc."):
                advance_demo_clock(st.session_state)
                st.rerun()
            for r in checked_in_res:
                st.warning(
                    f"**Xe đang tại Hub:** {r['plate']} (Hub: **{r['hub_name']}**)\n\n"
                    f"- Check-in lúc: `{r['check_in_time']}`\n"
                    f"- Đăng ký sạc: **{'Có' if r.get('request_charging') else 'Không'}**"
                )

                col_sim1, col_sim2, col_sim3 = st.columns(3)
                with col_sim1:
                    # Thời gian đỗ lấy theo đồng hồ demo: giờ hiện tại - giờ check-in.
                    _fmt = "%Y-%m-%d %H:%M:%S"
                    _now = datetime.strptime(st.session_state["current_sim_time"], _fmt)
                    _cin = datetime.strptime(r["check_in_time"], _fmt)
                    dur_hrs = max(0.0, (_now - _cin).total_seconds() / 3600)
                    _mins = int(round(dur_hrs * 60))
                    st.metric("Thời gian đỗ (đồng hồ demo)", f"{_mins // 60} giờ {_mins % 60:02d} phút")
                    st.caption("Phí đỗ tính theo giờ bắt đầu, tối thiểu 1 giờ.")
                _sched = st.session_state.get("charging_scheduler")
                _sess = None
                if _sched is not None and r.get("charging_session_id"):
                    _sess = getattr(_sched, "_active_sessions", {}).get(r["charging_session_id"])
                with col_sim2:
                    if r.get("charging_ever_allocated"):
                        # Xe có phiên sạc thật: SS2 chỉ đọc điện năng do SS5 đo (INT-02).
                        _measured = r.get("delivered_kwh", 0) + (_sess.energy_delivered_kwh if _sess else 0)
                        kwh = _measured
                        st.metric("Điện năng đo từ SS5", f"{_measured:.2f} kWh")
                        if _measured <= 0:
                            st.caption("Bấm Mô phỏng thêm 15 phút để phiên sạc tích lũy điện năng.")
                    elif r.get("request_charging"):
                        kwh = 0.0
                        st.metric("Điện năng đo từ SS5", "0.00 kWh")
                        st.caption("Xe đang chờ cổng sạc (WAITING), chưa được cấp cổng.")
                    else:
                        kwh = 0.0
                        st.metric("Điện năng", "Không đăng ký sạc")
                with col_sim3:
                    # Phí quá giờ do SS5 tính trên phiên sạc; SS2 chỉ hiển thị và quyết toán một lần.
                    _over_fee = r.get("accrued_overstay_fee", 0) + (_sess.overstay_fee if _sess else 0)
                    _over_min = r.get("accrued_overstay_minutes", 0) + (_sess.overstay_minutes if _sess else 0)
                    st.metric("Phí quá giờ (SS5)", f"{_over_fee:,.0f} ₫")
                    if _over_min or (_sess and _sess.status in ("GRACE_PERIOD", "OVERSTAY")):
                        st.caption(f"Chiếm cổng sau khi đầy pin: {_over_min} phút (ân hạn {OVERSTAY_GRACE_MINUTES} phút mỗi phiên).")

                if st.button(f"💳 Quyết toán & Rời trạm ({r['plate']})", type="primary", key=f"btn_checkout_{r['reservation_id']}"):
                    ok, inv, msg = check_out_personal_ev(
                        state=st.session_state,
                        reservation_id=r["reservation_id"],
                        duration_hours=dur_hrs,
                        kwh_charged=kwh,
                    )
                    if ok and inv:
                        st.session_state["last_pev_invoice"] = inv
                        st.session_state["personal_checkout_message"] = msg
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        last_inv = st.session_state.get("last_pev_invoice")
        if last_inv:
            st.divider()
            _render_personal_invoice(last_inv)

    # ═══════════════════════════════════════════════
    # BẢNG TỔNG KẾT XE ĐÃ ĐĂNG KÝ
    # ═══════════════════════════════════════════════
    all_pevs = st.session_state.get("personal_evs", [])
    if all_pevs:
        st.divider()
        st.subheader("🚗 Danh sách xe điện cá nhân trong hệ thống")
        st.dataframe(pd.DataFrame([{
            "Mã xe": ev.get("ev_id", "—"),
            "Chủ xe": ev.get("owner_name", ev.get("owner", "Sinh viên")),
            "Biển số": ev.get("plate", "—"),
            "Hãng xe": ev.get("brand", "—"),
            "Dung lượng pin": f"{ev.get('battery_kwh', 2.0)} kWh",
            "Ngày đăng ký": ev.get("registered_at", "—")
        } for ev in all_pevs]), use_container_width=True, hide_index=True)
