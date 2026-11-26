"""
student_booking.py – Subsystem 1 (PM): Quản lý & Đặt xe/chỗ đỗ cho Sinh viên
Smart E-Mobility Hub – ĐHQG-HCM

Chức năng chuẩn hóa (UC_SS1_01 → UC_SS1_03):
  • Đặt giữ xe 30 phút, khóa cọc 50,000₫ (UC_SS1_01)
  • Nhận xe bằng QR/PIN → Giải phóng slot xuất phát, xe IN_USE (UC_SS1_01)
  • Trả xe One-way, quyết toán ví qua core ledger, xuất e-invoice bền vững (UC_SS1_02)
  • Hủy đặt xe (hoàn 100% cọc nếu trước 30p, no-show 10,000₫ nếu quá hạn) (UC_SS1_03)

FR Covered: FR-01, FR-01b, FR-01c, FR-02, FR-15b, FR-15c
US Covered: US-01 → US-07 (US-07 ủy quyền SS3)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional

from core.policies import (
    SHARED_DEPOSIT_VND,
    SHARED_FREE_MINUTES,
    SHARED_RATE_PER_MINUTE,
    SHARED_NOSHOW_PENALTY_VND,
    SHARED_EXPIRY_MINUTES,
    MIN_SOC_BOOKING,
    SHARED_VOUCHERS
)
from core.state import VehicleStatus, ReservationStatus
from core.booking import (
    create_shared_booking,
    pickup_shared_vehicle,
    cancel_shared_booking,
    return_shared_vehicle,
    apply_rerouting_to_booking,
    process_expired_bookings,
    get_active_student_booking
)
from core.routing import find_alternative_hubs

def _ensure_active_user():
    """Đảm bảo tài khoản sinh viên được đồng bộ từ session_state."""
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = {
            "user_id": "SV-2211234",
            "name": "Nguyễn Văn A",
            "role": "STUDENT",
            "email": "vana.nguyen@vnuhcm.edu.vn"
        }
    if "wallet" not in st.session_state:
        st.session_state["wallet"] = {
            "balance": 150_000,
            "held": 0,
            "debt": 0,
            "transactions": []
        }
    if "bookings" not in st.session_state:
        st.session_state["bookings"] = []

def _wallet_card():
    """Hiển thị thẻ thông tin ví điện tử, số dư khả dụng, tiền cọc và công nợ."""
    user = st.session_state["current_user"]
    wallet = st.session_state.get("wallet", {})
    sim_time = st.session_state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👤 Sinh viên", f"{user['name']} ({user['user_id']})")
    c2.metric("💰 Số dư ví", f"{wallet.get('balance', 0):,.0f} ₫")
    c3.metric("🔒 Tiền khóa cọc", f"{wallet.get('held_deposit', 0):,.0f} ₫")
    
    debt = wallet.get("debt", 0)
    if debt > 0:
        c4.metric("⚠️ Dư nợ chưa trả", f"{debt:,.0f} ₫", delta=f"-{debt:,.0f} ₫", delta_color="inverse")
    else:
        c4.metric("⏱️ Giờ hệ thống", sim_time.split(" ")[-1])

def _tab_book():
    """Luồng đặt giữ xe: Chọn Hub → Lọc xe (SoC >= 20%) → Voucher → Khóa cọc."""
    user = st.session_state["current_user"]
    wallet = st.session_state.get("wallet", {})
    hubs = st.session_state.get("hubs", [])

    # Dọn dẹp booking quá hạn trước khi hiển thị
    process_expired_bookings(st.session_state)

    active_b = get_active_student_booking(st.session_state, user["user_id"])
    if active_b:
        st.warning(
            f"⚠️ Bạn đang có lượt đặt xe **{active_b['vehicle_id']}** (Mã: `{active_b['booking_id']}`) "
            f"ở trạng thái **{active_b['status']}**. "
            f"Vui lòng nhận xe hoặc hủy lượt đặt trước khi thực hiện lượt mới."
        )
        return

    st.subheader("📍 Bước 1 — Chọn Hub xuất phát & Hub trả xe dự kiến")
    hub_names = [h["name"] for h in hubs]
    col_orig, col_dest = st.columns(2)
    
    with col_orig:
        orig_name = st.selectbox("Hub xuất phát:", hub_names, key="sb_orig_hub")
        orig_hub = next(h for h in hubs if h["name"] == orig_name)
        st.caption(f"Chỗ trống: **{orig_hub['available_slots']}/{orig_hub['total_slots']}** | "
                   f"Xe sẵn sàng: **{len([v for v in orig_hub['current_vehicles'] if v['status'] == VehicleStatus.AVAILABLE.value])}**")
                   
    with col_dest:
        dest_opts = ["(Chưa xác định - Chọn khi trả)"] + hub_names
        dest_choice = st.selectbox("Hub đích giữ chỗ trước (Khuyên dùng):", dest_opts, key="sb_dest_hub")
        dest_hub_id = None
        if dest_choice != "(Chưa xác định - Chọn khi trả)":
            chosen_dest = next(h for h in hubs if h["name"] == dest_choice)
            dest_hub_id = chosen_dest["hub_id"]
            if chosen_dest["available_slots"] <= 0:
                st.error(f"❌ Hub **{dest_choice}** hiện đã hết chỗ đỗ trống! Vui lòng chọn Hub khác.")
            else:
                st.caption(f"Chỗ trống tại đích: **{chosen_dest['available_slots']}/{chosen_dest['total_slots']}**")

    st.divider()

    st.subheader("🔍 Bước 2 — Tìm xe khả dụng")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        type_filter = st.multiselect(
            "Loại xe:", ["bike", "scooter", "car"],
            default=["bike", "scooter", "car"],
            key="sb_type_filter"
        )
    with f_col2:
        user_soc = st.slider(
            "Pin tối thiểu (%):",
            min_value=0, max_value=100, value=MIN_SOC_BOOKING,
            key="sb_soc_filter"
        )
        effective_soc = max(MIN_SOC_BOOKING, user_soc)
        if user_soc < MIN_SOC_BOOKING:
            st.info(f"💡 Chính sách an toàn: Hệ thống tự động áp dụng ngưỡng tối thiểu **{MIN_SOC_BOOKING}%** pin.")

    # Lọc xe tại Hub xuất phát
    available_vehicles = [
        v for v in orig_hub["current_vehicles"]
        if v.get("status") == VehicleStatus.AVAILABLE.value
        and v.get("ownership", "SHARED") == "SHARED"
        and v.get("type") in type_filter
        and v.get("battery_soc", 0) >= effective_soc
    ]

    if not available_vehicles:
        st.warning("⚠️ Hiện không có phương tiện nào thỏa mãn điều kiện lọc tại Hub này.")
        # Gợi ý Hub lân cận
        alts = find_alternative_hubs(hubs, orig_hub["hub_id"], need_slots=False, limit=2)
        if alts:
            st.info("💡 Bạn có thể tham khảo các Hub lân cận còn xe:")
            for a in alts:
                st.write(f"- **{a['name']}** (~{a['distance_km']} km): Còn {a['available_slots']} chỗ.")
        return

    # Hiển thị bảng xe
    df_disp = pd.DataFrame([{
        "Mã xe": v["vehicle_id"],
        "Loại xe": v["type"].upper(),
        "Mức pin": f"{v['battery_soc']}%",
        "Trạng thái": v["status"]
    } for v in available_vehicles])
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("📝 Bước 3 — Đặt giữ xe & Khóa cọc")
    veh_opts = [
        f"{v['vehicle_id']} – {v['type'].upper()} ({v['battery_soc']}% Pin)"
        for v in available_vehicles
    ]
    chosen_str = st.selectbox("Chọn xe cần đặt:", veh_opts, key="sb_chosen_veh")
    chosen_id = chosen_str.split(" – ")[0]

    voucher_input = st.text_input("🎟️ Mã giảm giá / Voucher SV (SVBK50, VNU2026):", value="SVBK50", key="sb_voucher")
    voucher_code = voucher_input.strip().upper() if voucher_input.strip() else None
    if voucher_code and voucher_code in SHARED_VOUCHERS:
        st.success(f"✅ Voucher `{voucher_code}` hợp lệ! Giảm {SHARED_VOUCHERS[voucher_code]:,.0f}₫ trên phí thuê.")

    with st.expander("📊 Bảng giá thuê xe dùng chung (Chính sách ĐHQG-HCM)", expanded=True):
        st.markdown(f"""
| Hạng mục | Chi tiết chính sách |
|:---|:---|
| **Miễn phí** | **{SHARED_FREE_MINUTES} phút** đầu tiên cho SV ĐHQG-HCM |
| **Đơn giá thuê** | **{SHARED_RATE_PER_MINUTE:,.0f} ₫/phút** sau {SHARED_FREE_MINUTES} phút |
| **Tiền cọc giữ chỗ** | **{SHARED_DEPOSIT_VND:,.0f} ₫** (Khóa tạm trong ví, hoàn 100% khi nhận xe/hủy đúng hạn) |
| **Thời hạn giữ chỗ** | **{SHARED_EXPIRY_MINUTES} phút** (Quá hạn phạt no-show {SHARED_NOSHOW_PENALTY_VND:,.0f}₫, hoàn lại {SHARED_DEPOSIT_VND - SHARED_NOSHOW_PENALTY_VND:,.0f}₫) |
        """)

    if st.button("✅ Xác nhận Đặt giữ xe (Khóa cọc 50,000₫)", type="primary", key="sb_btn_confirm"):
        ok, booking_data, msg = create_shared_booking(
            state=st.session_state,
            student_id=user["user_id"],
            hub_id=orig_hub["hub_id"],
            vehicle_id=chosen_id,
            voucher_code=voucher_code,
            destination_hub_id=dest_hub_id
        )
        if ok:
            st.success(
                f"🎉 {msg}\n\n"
                f"- **Mã đặt chỗ:** `{booking_data['booking_id']}`\n"
                f"- **Mã PIN nhận xe:** `{booking_data['pin_code']}` (Dùng mã này tại trạm để mở khóa xe)\n"
                f"- **Hạn chót nhận xe:** `{booking_data['expires_at']}`\n"
                f"- **Xe:** `{booking_data['vehicle_id']}` tại `{booking_data['hub_name']}`"
            )
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ {msg}")

def _tab_pickup():
    """Luồng nhận xe: Xác thực PIN/QR → Mở khóa IoT → Xe IN_USE & Giải phóng slot xuất phát."""
    user = st.session_state["current_user"]
    process_expired_bookings(st.session_state)

    active_b = get_active_student_booking(st.session_state, user["user_id"])
    if not active_b or active_b.get("status") != ReservationStatus.RESERVED.value:
        st.info("📭 Hiện bạn không có lệnh đặt xe nào đang chờ nhận. Vui lòng đặt xe ở tab **🚲 Đặt xe** trước.")
        return

    st.subheader("📱 Xác thực Nhận xe (Mô phỏng IoT Lock / PIN)")
    st.info(
        f"**Thông tin đặt xe:**\n\n"
        f"- Mã đặt chỗ: `{active_b['booking_id']}`\n"
        f"- Phương tiện: **{active_b['vehicle_id']}** ({active_b.get('vehicle_type', '').upper()})\n"
        f"- Hub xuất phát: **{active_b['hub_name']}**\n"
        f"- Hạn nhận xe: **{active_b['expires_at']}**"
    )

    pin_in = st.text_input("🔐 Nhập mã PIN mở khóa xe (4-6 chữ số):", value=active_b.get("pin_code", ""), key="sb_pickup_pin")
    
    if st.button("🔓 Xác nhận mở khóa xe", type="primary", key="sb_btn_pickup"):
        ok, msg = pickup_shared_vehicle(
            state=st.session_state,
            booking_id=active_b["booking_id"],
            entered_pin=pin_in
        )
        if ok:
            st.success(f"🎉 {msg}")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ {msg}")

def _render_shared_invoice(invoice):
    fee = invoice.get("total_fee", invoice.get("final_cost", 0))
    deposit = invoice["deposit_released"]
    debt = invoice["debt_incurred"]
    refund = invoice.get("refund_amount", max(0, deposit - fee))
    deducted = invoice.get("deducted_from_available", max(0, fee - deposit - debt))
    free_minutes = invoice.get("free_minutes", invoice.get("free_minutes_applied", 0))
    base_fee = invoice.get("base_fee", invoice.get("gross_rental_fee", 0))
    discount = invoice.get("discount", invoice.get("voucher_discount", 0))
    st.subheader("🧾 Hóa đơn chuyến đi gần nhất")
    st.markdown(f"""
| Trường thông tin | Giá trị chi tiết |
|:---|:---|
| **Mã hóa đơn** | `{invoice['invoice_id']}` |
| **Mã chuyến đi** | `{invoice['booking_id']}` |
| **Quãng đường mô phỏng** | {invoice.get("distance_km", "Chưa có")} km · {invoice.get("distance_source", "")} |
| **Tổng thời lượng** | {invoice['duration_minutes']} phút (Miễn phí: {free_minutes} phút) |
| **Thời gian tính phí** | {invoice['billable_minutes']} phút × {SHARED_RATE_PER_MINUTE:,.0f}₫ |
| **Phí thuê gộp** | {base_fee:,.0f} ₫ |
| **Giảm giá voucher** | -{discount:,.0f} ₫ |
| **Chi phí thực tế** | **{fee:,.0f} ₫** |
| **Tiền cọc đã giải phóng** | {deposit:,.0f} ₫ |
| **Số tiền hoàn về ví** | **+{refund:,.0f} ₫** |
| **Số tiền trừ thêm từ ví** | -{deducted:,.0f} ₫ |
| **Công nợ ghi nhận** | {debt:,.0f} ₫ |
    """)
    if debt > 0:
        st.warning(f"Số dư không đủ. Hệ thống ghi nhận công nợ **{debt:,.0f} ₫**.")

def _tab_return():
    """Luồng trả xe One-way: Chọn Hub đích → Quyết toán → E-Invoice bền vững."""
    user = st.session_state["current_user"]
    hubs = st.session_state.get("hubs", [])

    active_b = get_active_student_booking(st.session_state, user["user_id"])
    if not active_b or active_b.get("status") != VehicleStatus.IN_USE.value:
        st.info("📭 Không có chuyến đi đang hoạt động. Vui lòng nhận xe ở tab **📱 Nhận xe** trước.")
        
        # Nếu có invoice gần nhất, vẫn hiển thị để SV xem lại
        last_inv = st.session_state.get("last_invoice")
        if last_inv:
            st.divider()
            _render_shared_invoice(last_inv)
        return

    st.subheader("🔄 Trả xe One-Way & Quyết toán chi phí")
    st.info(
        f"**Chuyến đi đang diễn ra:**\n\n"
        f"- Mã đặt chỗ: `{active_b['booking_id']}` | Xe: **{active_b['vehicle_id']}**\n"
        f"- Xuất phát từ: **{active_b['hub_name']}** lúc `{active_b.get('pickup_time')}`\n"
        f"- Điểm đến đã giữ trước: **{active_b.get('destination_hub_id') or 'Chưa đăng ký trước'}**\n"
        f"- Phút miễn phí bổ sung (do điều hướng): **+{active_b.get('extra_free_minutes', 0)} phút**"
    )

    # Chọn Hub đích
    hub_names = [h["name"] for h in hubs]
    default_dest_idx = 0
    if active_b.get("destination_hub_id"):
        for idx, h in enumerate(hubs):
            if h["hub_id"] == active_b["destination_hub_id"]:
                default_dest_idx = idx
                break

    dest_choice = st.selectbox("📍 Chọn Hub trả xe thực tế:", hub_names, index=default_dest_idx, key="sb_return_dest")
    dest_hub = next(h for h in hubs if h["name"] == dest_choice)

    # Kiểm tra chỗ đỗ tại đích (nếu không phải là slot đã được hold từ trước)
    is_pre_held = (active_b.get("destination_hub_id") == dest_hub["hub_id"] and active_b.get("destination_held"))
    
    if not is_pre_held and dest_hub["available_slots"] <= 0:
        st.error(f"🚫 **Hub {dest_choice} hiện đã đầy chỗ đỗ!** (available_slots == 0)")
        alts = find_alternative_hubs(hubs, dest_hub["hub_id"], need_slots=True, limit=2)
        if alts:
            st.warning("🔄 **Gợi ý điều hướng tự động (FR-15c / UC_SS7_02):**")
            for a in alts:
                col_info, col_act = st.columns([3, 1])
                with col_info:
                    st.write(f"- 📍 **{a['name']}** (~{a['distance_km']} km) — Còn **{a['available_slots']}** chỗ đỗ")
                with col_act:
                    if st.button("Chuyển tới đây (+15p)", key=f"reroute_to_{a['hub_id']}"):
                        ok_r, msg_r = apply_rerouting_to_booking(st.session_state, active_b["booking_id"], a["hub_id"])
                        if ok_r:
                            st.success(msg_r)
                            st.rerun()
                        else:
                            st.error(msg_r)
        return

    st.success(f"✅ Hub **{dest_choice}** sẵn sàng tiếp nhận xe.")

    # Mô phỏng thời gian chuyến đi
    override_dur = st.number_input(
        "⏱️ Thời gian di chuyển thực tế (phút) [Mô phỏng]:",
        min_value=1, max_value=300, value=25, key="sb_sim_trip_duration"
    )

    if st.button("✅ Hoàn tất trả xe & Thanh toán", type="primary", key="sb_btn_return"):
        ok, invoice, msg = return_shared_vehicle(
            state=st.session_state,
            booking_id=active_b["booking_id"],
            return_hub_id=dest_hub["hub_id"],
            override_duration_minutes=override_dur
        )
        if ok and invoice:
            st.session_state["last_invoice"] = invoice
            st.session_state["shared_checkout_message"] = msg
            st.rerun()
        else:
            st.error(f"❌ {msg}")

def _tab_cancel():
    """Luồng hủy đặt xe: Xác nhận hủy → Hoàn 100% cọc nếu trước 30p → AVAILABLE."""
    user = st.session_state["current_user"]
    process_expired_bookings(st.session_state)

    active_b = get_active_student_booking(st.session_state, user["user_id"])
    if not active_b or active_b.get("status") != ReservationStatus.RESERVED.value:
        st.info("📭 Không có lệnh đặt xe nào đang ở trạng thái `RESERVED` để hủy.")
        return

    st.subheader("❌ Hủy lệnh đặt giữ xe")
    st.warning(
        f"**Chi tiết lệnh đặt:**\n\n"
        f"- Xe: **{active_b['vehicle_id']}** tại **{active_b['hub_name']}**\n"
        f"- Thời điểm đặt: `{active_b['created_at']}`\n"
        f"- Hạn nhận xe: `{active_b['expires_at']}`\n"
        f"- Tiền cọc đang khóa: **{SHARED_DEPOSIT_VND:,.0f} ₫**"
    )

    st.info(f"💡 Hủy trước thời hạn {SHARED_EXPIRY_MINUTES} phút: **Hoàn 100% tiền cọc ({SHARED_DEPOSIT_VND:,.0f}₫)** về ví điện tử ngay lập tức.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Đồng ý hủy — Hoàn 100% cọc", type="primary", key="sb_btn_cancel"):
            ok, msg = cancel_shared_booking(st.session_state, active_b["booking_id"])
            if ok:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.warning(f"⚠️ {msg}")
                st.rerun()

def render():
    """Render giao diện Subsystem 1 – Student EV Booking & Shared Services."""
    _ensure_active_user()

    st.header("🚲 Quản lý & Đặt xe điện dùng chung cho Sinh viên")
    st.caption("Phân hệ SS1 — Student EV Booking & Shared Services | Đặt xe → Nhận xe → Trả xe → Hủy đặt xe")

    _wallet_card()
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🚲 Đặt xe",
        "📱 Nhận xe (Pick-up)",
        "🔄 Trả xe & Quyết toán",
        "❌ Hủy đặt xe",
    ])

    with tab1:
        _tab_book()
    with tab2:
        _tab_pickup()
    with tab3:
        checkout_message = st.session_state.pop("shared_checkout_message", None)
        if checkout_message:
            st.success(f"🎉 {checkout_message}")
        _tab_return()
    with tab4:
        _tab_cancel()

    # Bảng lịch sử đặt xe
    bookings = st.session_state.get("bookings", [])
    if bookings:
        st.divider()
        st.subheader("📋 Lịch sử đặt xe & Chuyến đi của sinh viên")
        hist_rows = []
        for b in reversed(bookings):
            inv = b.get("invoice") or {}
            fee = inv.get("total_fee", inv.get("final_cost"))
            cost_str = f"{fee:,.0f}₫" if fee is not None else "—"
            hist_rows.append({
                "Mã đặt chỗ": b.get("booking_id"),
                "Mã xe": b.get("vehicle_id"),
                "Hub xuất phát": b.get("hub_name"),
                "Hub trả xe": b.get("return_hub_name", "—"),
                "Trạng thái": b.get("status"),
                "Thời gian đặt": b.get("created_at"),
                "Thời gian nhận": b.get("pickup_time", "—"),
                "Thời gian trả": b.get("return_time", "—"),
                "Chi phí": cost_str
            })
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)
