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
    check_out_personal_ev
)
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
                if st.button(f"🚗 Xác thực check-in cho xe {r['plate']}", key=f"btn_checkin_{r['reservation_id']}"):
                    ok, msg = check_in_personal_ev(st.session_state, r["reservation_id"])
                    if ok:
                        st.success(f"🎉 {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    # ═══════════════════════════════════════════════
    # TAB 4: CHECK-OUT & QUYẾT TOÁN
    # ═══════════════════════════════════════════════
    with tab_out:
        st.subheader("🧾 Check-out, Giải phóng cổng sạc & Quyết toán chi phí")
        checked_in_res = [
            r for r in st.session_state.get("personal_reservations", [])
            if r.get("owner_id") == user["user_id"] and r.get("status") == "CHECKED_IN"
        ]

        if not checked_in_res:
            st.info("📭 Không có xe nào đang đỗ/sạc tại Hub cần check-out.")
            last_inv = st.session_state.get("last_pev_invoice")
            if last_inv:
                st.divider()
                st.subheader("🧾 Hóa đơn quyết toán xe cá nhân gần nhất")
                st.json(last_inv)
        else:
            for r in checked_in_res:
                st.warning(
                    f"**Xe đang tại Hub:** {r['plate']} (Hub: **{r['hub_name']}**)\n\n"
                    f"- Check-in lúc: `{r['check_in_time']}`\n"
                    f"- Đăng ký sạc: **{'Có' if r.get('request_charging') else 'Không'}**"
                )

                col_sim1, col_sim2, col_sim3 = st.columns(3)
                with col_sim1:
                    dur_hrs = st.number_input("Thời gian đỗ (giờ) [Mô phỏng]:", min_value=0.5, max_value=48.0, value=2.5, step=0.5, key=f"dur_{r['reservation_id']}")
                with col_sim2:
                    kwh = st.number_input("Điện năng đã nạp (kWh) [Mô phỏng]:", min_value=0.0, max_value=50.0, value=4.2 if r.get('request_charging') else 0.0, step=0.1, key=f"kwh_{r['reservation_id']}")
                with col_sim3:
                    overstay = st.number_input("Thời gian quá hạn rút sạc (phút) [Mô phỏng]:", min_value=0, max_value=180, value=20, step=5, key=f"over_{r['reservation_id']}")

                if st.button(f"💳 Quyết toán & Rời trạm ({r['plate']})", type="primary", key=f"btn_checkout_{r['reservation_id']}"):
                    ok, inv, msg = check_out_personal_ev(
                        state=st.session_state,
                        reservation_id=r["reservation_id"],
                        duration_hours=dur_hrs,
                        kwh_charged=kwh,
                        overstay_minutes=overstay
                    )
                    if ok and inv:
                        st.session_state["last_pev_invoice"] = inv
                        st.success(f"🎉 {msg}")
                        st.markdown(f"""
| Hạng mục quyết toán | Chi tiết thanh toán |
|:---|:---|
| **Mã hóa đơn** | `{inv['invoice_id']}` |
| **Biển số xe** | **{inv['plate']}** |
| **Phí đỗ xe** | **{inv['parking_fee']:,.0f} ₫** |
| **Điện năng sạc** | {inv['kwh_charged']} kWh × {inv['energy_rate']:,.0f} ₫ = **{inv['energy_fee']:,.0f} ₫** |
| **Biểu giá áp dụng** | **{'GIỜ CAO ĐIỂM (7,000₫/kWh)' if inv['is_peak_tariff'] else 'GIỜ THẤP ĐIỂM (3,000₫/kWh)'}** |
| **Phí đỗ quá hạn (Overstay)** | {inv['overstay_minutes']} phút (Miễn phí {OVERSTAY_GRACE_MINUTES}p) = **{inv['overstay_fee']:,.0f} ₫** |
| **Tổng chi phí** | **{inv['total_amount']:,.0f} ₫** |
| **Đã trừ từ ví** | **-{inv['deducted_from_wallet']:,.0f} ₫** |
| **Ghi nhận nợ** | **{inv['debt_incurred']:,.0f} ₫** |
                        """)
                        if inv["debt_incurred"] > 0:
                            st.error(f"⚠️ Do số dư khả dụng không đủ, khoản nợ **{inv['debt_incurred']:,.0f} ₫** đã được ghi nợ vào tài khoản.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

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
