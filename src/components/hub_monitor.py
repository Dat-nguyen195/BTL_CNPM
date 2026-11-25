"""
hub_monitor.py – Subsystem 3: Giám sát mạng lưới Hub (Operator Dashboard)
Smart E-Mobility Hub – ĐHQG-HCM

Chức năng chuẩn hóa:
  • KPI cards thời gian thực: Tỉ lệ lấp đầy, xe sẵn sàng, cổng sạc, công suất lưới
  • Cảnh báo phân cấp ngưỡng: Vàng (70% <= occ < 85%), Đỏ (85% <= occ < 100%), Đầy (100%)
  • Doanh thu & Dòng tiền ví điện tử (US-07 / FR-05, FR-15b)
  • Giám sát nạp năng lượng & Biểu phí sạc (US-12 / FR-04, FR-05b)
  • Bản đồ vị trí Hub & Nhật ký cảm biến IoT
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from core.policies import (
    ALERT_YELLOW_THRESHOLD_PCT,
    ALERT_RED_THRESHOLD_PCT,
    ALERT_FULL_THRESHOLD_PCT,
    HUB_POWER_CAP_KW
)
from core.state import VehicleStatus

def render():
    """Render giao diện Subsystem 3 – Dashboard Giám sát Mạng lưới Hub."""
    st.header("📊 Giám sát Mạng lưới Hub – Operator Dashboard")
    st.caption("Tổng quan vận hành mạng lưới trạm sạc & xe điện ĐHQG-HCM theo thời gian thực (FR-05, FR-15b).")

    hubs = st.session_state.get("hubs", [])
    if not hubs:
        st.error("Không có dữ liệu Hub.")
        return

    sim_time = st.session_state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    offline_total = 0
    for hub in hubs:
        offline = hub.get("charging_ports", {}).get("offline", 0)
        offline_total += offline
        if offline:
            st.warning(f"Cảnh báo IoT mô phỏng: {hub['name']} có {offline} cổng sạc OFFLINE. Chuyển SS4/SS7 để xử lý.")

    # Thanh điều khiển & Refresh Telemetry
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        port_summary = f"{offline_total} cổng OFFLINE" if offline_total else "Không có cổng OFFLINE"
        st.info(f"🕒 **Đồng hồ mô phỏng:** `{sim_time}` · **{port_summary}**")
        latest = next((event for event in reversed(st.session_state.get("telemetry_log", []))
                       if event["result"] == "APPLIED"), None)
        if latest:
            st.caption(f"Bản tin đã áp dụng: {latest['event_id']} · {latest['hub_id']} · "
                       f"Cổng {latest['port_id']} · {latest['event_type']}")
    with top_col2:
        if st.button("🔄 Cập nhật Telemetry", key="btn_refresh_telemetry"):
            st.rerun()

    # ═══════════════════════════════════════════════
    # 1. KPI CARDS TOÀN HỆ THỐNG
    # ═══════════════════════════════════════════════
    total_slots = sum(h["total_slots"] for h in hubs)
    total_avail_slots = sum(h["available_slots"] for h in hubs)
    total_held_slots = sum(h.get("destination_holds", 0) for h in hubs)
    total_vehicles = sum(len(h["current_vehicles"]) for h in hubs)
    total_ports = sum(h["charging_ports"]["total"] for h in hubs)
    total_avail_ports = sum(h["charging_ports"]["available"] for h in hubs)

    system_occ_pct = ((total_slots - total_avail_slots) / total_slots * 100) if total_slots > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🚗 Xe hiện hữu tại trạm", f"{total_vehicles} xe")
    k2.metric("📈 Tỉ lệ lấp đầy toàn mạng", f"{system_occ_pct:.1f}%")
    k3.metric("🅿️ Chỗ đỗ khả dụng", f"{total_avail_slots}/{total_slots}")
    k4.metric("🔌 Cổng sạc khả dụng", f"{total_avail_ports}/{total_ports}")

    st.divider()

    # ═══════════════════════════════════════════════
    # 2. CẢNH BÁO QUÁ TẢI PHÂN CẤP (70% / 85% / 100%)
    # ═══════════════════════════════════════════════
    st.subheader("🚨 Cảnh báo Tình trạng Trọng tải & Nguy cơ Quá tải")
    alert_cols = st.columns(3)

    yellow_hubs = []
    red_hubs = []
    full_hubs = []

    for h in hubs:
        occ = ((h["total_slots"] - h["available_slots"]) / h["total_slots"] * 100) if h["total_slots"] > 0 else 0
        h_info = {"name": h["name"], "occ": occ, "avail": h["available_slots"], "total": h["total_slots"]}
        if occ >= ALERT_FULL_THRESHOLD_PCT:
            full_hubs.append(h_info)
        elif occ >= ALERT_RED_THRESHOLD_PCT:
            red_hubs.append(h_info)
        elif occ >= ALERT_YELLOW_THRESHOLD_PCT:
            yellow_hubs.append(h_info)

    with alert_cols[0]:
        st.markdown(f"**🟡 Cảnh báo tải cao (70% - 85%):** {len(yellow_hubs)}")
        for y in yellow_hubs:
            st.warning(f"📍 **{y['name']}**: {y['occ']:.1f}% ({y['avail']} chỗ trống)")

    with alert_cols[1]:
        st.markdown(f"**🔴 Quá tải nghiêm trọng (85% - 100%):** {len(red_hubs)}")
        for r in red_hubs:
            st.error(f"🚨 **{r['name']}**: {r['occ']:.1f}% (Cần điều phối SS4!)")

    with alert_cols[2]:
        st.markdown(f"**⛔ Trạm đã đầy 100% (Khóa tiếp nhận):** {len(full_hubs)}")
        for f in full_hubs:
            st.error(f"⛔ **{f['name']}**: 100% (Đã kích hoạt Rerouting)")

    if not (yellow_hubs or red_hubs or full_hubs):
        st.success("✅ Mọi Hub trong hệ thống đang hoạt động trong ngưỡng an toàn (< 70% tải).")

    st.divider()

    # ═══════════════════════════════════════════════
    # 3. TABS CHI TIẾT: VỊ TRÍ, NĂNG LƯỢNG, DOANH THU (US-07 & US-12)
    # ═══════════════════════════════════════════════
    tab_map, tab_rev, tab_power = st.tabs([
        "🗺️ Bản đồ & Trạng thái Hub",
        "💰 Doanh thu & Giao dịch ví (US-07)",
        "⚡ Năng lượng sạc & Biểu phí (US-12)",
    ])

    with tab_map:
        st.subheader("🗺️ Bản đồ & Chi tiết từng Hub")
        map_data = pd.DataFrame([{
            "lat": h["latitude"],
            "lon": h["longitude"],
            "Hub": h["name"],
        } for h in hubs])
        st.map(map_data, latitude="lat", longitude="lon", zoom=14)

        hub_table_data = []
        for h in hubs:
            occ = ((h["total_slots"] - h["available_slots"]) / h["total_slots"] * 100) if h["total_slots"] > 0 else 0
            hub_table_data.append({
                "Mã Hub": h["hub_id"],
                "Tên Hub": h["name"],
                "Tổng chỗ": h["total_slots"],
                "Chỗ trống": h["available_slots"],
                "Đang giữ chỗ": h.get("destination_holds", 0),
                "Tỉ lệ lấp đầy": f"{occ:.1f}%",
                "Cổng sạc trống": f"{h['charging_ports']['available']}/{h['charging_ports']['total']}",
                "Trạng thái": "QUÁ TẢI" if occ >= 85 else ("CẢNH BÁO" if occ >= 70 else "HOẠT ĐỘNG")
            })
        st.dataframe(pd.DataFrame(hub_table_data), use_container_width=True, hide_index=True)

    with tab_rev:
        st.subheader("💰 Báo cáo Doanh thu & Sổ cái Giao dịch Ví (US-07)")
        payment_confirmation()
        wallet = st.session_state.get("wallet", {})
        txs = wallet.get("ledger", [])
        
        # Thống kê giao dịch
        rev_shared = -sum(t.get("amount", 0) for t in txs if t.get("type") in ["SETTLE_RENTAL_FEE", "SETTLE_RENTAL_DEBT", "PENALTY_NOSHOW", "PENALTY_PEV_NOSHOW"])
        rev_shared += sum(r["invoice"].get("deducted_from_wallet", 0) for r in st.session_state.get("personal_reservations", []) if r.get("invoice"))
        rev_shared += sum(i.get("deducted", 0) for i in st.session_state.get("charging_invoices", []))
        total_tx = len(txs)
        debt = wallet.get("debt", 0)

        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("💵 Tổng doanh thu thu về", f"{rev_shared:,.0f} ₫")
        rc2.metric("📋 Tổng số giao dịch ledger", f"{total_tx}")
        rc3.metric("⚠️ Dư nợ người dùng ghi nhận", f"{debt:,.0f} ₫")

        st.markdown("##### Danh sách đặt chỗ hiện tại")
        bookings = st.session_state.get("bookings", [])
        if bookings:
            st.dataframe(pd.DataFrame(bookings), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có đặt chỗ trong phiên.")

        if txs:
            st.markdown("##### 📜 Lịch sử biến động số dư / Ledger:")
            st.dataframe(pd.DataFrame(txs), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có giao dịch phát sinh trên sổ cái.")

    with tab_power:
        st.subheader("⚡ Giám sát Năng lượng Sạc & Biểu phí Điện (US-12)")
        st.caption(f"Công suất trần (Power Cap) áp dụng: **{HUB_POWER_CAP_KW} kW/trạm** (FR-04, FR-05b).")

        power_data = []
        for h in hubs:
            offline_ports = h["charging_ports"].get("offline", 0)
            busy_ports = h["charging_ports"]["total"] - h["charging_ports"]["available"] - offline_ports
            est_kw = sum(s.port_kw for s in getattr(st.session_state.get("charging_scheduler"), "_active_sessions", {}).values() if s.hub_id == h["hub_id"] and s.status == "CHARGING")
            power_data.append({
                "Hub": h["name"].replace("Hub ", ""),
                "Cổng đang chiếm dụng": busy_ports,
                "Cổng offline": offline_ports,
                "Cổng trống": h["charging_ports"]["available"],
                "Công suất ước tính (kW)": round(est_kw, 1),
                "Tải so với trần 150kW (%)": f"{(est_kw / HUB_POWER_CAP_KW * 100):.1f}%"
            })
        st.dataframe(pd.DataFrame(power_data), use_container_width=True, hide_index=True)


def payment_confirmation():
    """Operator confirmation is an audit action after consolidated settlement."""
    invoices = [r["invoice"] for r in st.session_state.get("personal_reservations", []) if r.get("invoice")]
    for invoice in invoices:
        st.write(f"Hóa đơn {invoice['invoice_id']} · Đã thu {invoice['deducted_from_wallet']:,}đ · Nợ {invoice['debt_incurred']:,}đ")
        if invoice.get("operator_confirmed_at"):
            st.caption("Đã xác nhận bởi nhân viên")
        elif st.button("Xác nhận đối soát " + invoice["invoice_id"], key="confirm_" + invoice["invoice_id"]):
            invoice["operator_confirmed_at"] = st.session_state["current_sim_time"]
            invoice["operator_id"] = st.session_state.get("active_user", {}).get("user_id")
            st.rerun()
