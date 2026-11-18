"""
sim_demand.py – Subsystem 6: Mô phỏng kịch bản What-if (Nhu cầu Sinh viên)
Smart E-Mobility Hub – ĐHQG-HCM

Chức năng chuẩn hóa:
  • Dự đoán nhu cầu What-if theo giờ (Hàng đợi & thời gian chờ)
  • Mô phỏng Metro Surge độc lập với Deepcopy isolation
  • Khắc phục triệt để lỗi lồng nút: Xem Preview độc lập và nút 'Áp dụng' hoạt động bền vững qua các lần rerun
  • Kiểm tra state_version để tránh áp dụng dữ liệu cũ (stale apply)

FR Covered: FR-12, FR-13
US Covered: US-21, US-22
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid

from core.simulator import HubEventSimulator
from core.state import bump_state_version

def render():
    """Render giao diện Subsystem 6 – Mô phỏng kịch bản Nhu cầu What-if."""
    st.header("📈 Mô phỏng Kịch bản What-if – Nhu cầu Sinh viên")
    st.caption("Mô phỏng đợt tăng đột biến nhu cầu sinh viên (Metro Surge) và dự báo hệ quả (FR-12, FR-13).")

    hubs = st.session_state.get("hubs", [])
    if not hubs:
        st.error("Không có dữ liệu Hub.")
        return

    # ═══════════════════════════════════════════════
    # PHẦN 1: DỰ ĐOÁN NHU CẦU THEO GIỜ (BIỂU ĐỒ)
    # ═══════════════════════════════════════════════
    st.subheader("📊 1. Dự đoán nhu cầu theo giờ (Forecasting Engine)")
    st.markdown("Điều chỉnh tham số để dự đoán lưu lượng sinh viên, hàng đợi tích lũy và thời gian chờ trung bình.")

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        base_rate = st.slider("Tỉ lệ đến cơ bản (SV/giờ):", min_value=5, max_value=50, value=15, key="ss6_base_rate")
    with pc2:
        surge_mult = st.slider("Hệ số tăng đột biến (Multiplier):", min_value=1.0, max_value=5.0, value=1.5, step=0.5, key="ss6_surge_mult")
    with pc3:
        sim_hours = st.slider("Số giờ dự báo:", min_value=6, max_value=24, value=24, key="ss6_sim_hours")

    forecast = HubEventSimulator.generate_demand_forecast(
        base_arrival_rate=base_rate,
        surge_multiplier=surge_mult,
        hours=sim_hours,
        seed=42
    )
    forecast_df = pd.DataFrame(forecast)
    price = st.number_input("Giả định doanh thu mỗi lượt phục vụ (VNĐ)", min_value=0, value=5000, step=1000)
    served = sum(min(row["arrivals"] + (forecast[i-1]["queue_length"] if i else 0), 8)
                 for i, row in enumerate(forecast))
    st.metric("Doanh thu dự báo theo giả định", f"{served * price:,.0f} VNĐ")
    st.caption("Giả định phục vụ tối đa 8 lượt/giờ, thu đủ đơn giá mỗi lượt. Doanh thu thực ở SS3.")


    # Biểu đồ cột & đường
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=forecast_df["hour"],
        y=forecast_df["arrivals"],
        name="Lượng SV đến",
        marker_color="#748ffc"
    ))
    fig1.add_trace(go.Scatter(
        x=forecast_df["hour"],
        y=forecast_df["queue_length"],
        name="Hàng đợi tích lũy",
        line=dict(color="#ff6b6b", width=3),
        yaxis="y2"
    ))
    fig1.update_layout(
        title="Dự báo: Lượng sinh viên đến & Hàng đợi tích lũy theo giờ",
        xaxis_title="Thời gian (Giờ)",
        yaxis_title="Số SV đến",
        yaxis2=dict(title="Hàng đợi (người)", overlaying="y", side="right"),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # ═══════════════════════════════════════════════
    # PHẦN 2: MÔ PHỎNG METRO SURGE & XỬ LÝ PREVIEW ĐỘC LẬP
    # ═══════════════════════════════════════════════
    st.subheader("🚇 2. Chạy mô phỏng Metro Surge trực tiếp")
    st.caption("Mô phỏng sinh viên từ tuyến Metro Bến Thành - Suối Tiên đổ về Hub KTX Khu B.")

    col_target, col_students = st.columns(2)
    with col_target:
        hub_opts = [f"{h['hub_id']} – {h['name']}" for h in hubs]
        chosen_hub_str = st.selectbox("Chọn Hub chịu tải Metro:", hub_opts, index=1, key="ss6_target_hub")
        chosen_hub_id = chosen_hub_str.split(" – ")[0]
    with col_students:
        num_students = st.number_input("Số lượng sinh viên đến đột biến:", min_value=5, max_value=100, value=25, key="ss6_num_students")

    # Nút CHẠY MÔ PHỎNG (Lưu kết quả vào session_state độc lập)
    if st.button("🚀 Chạy mô phỏng Metro Surge (Tạo Preview)", type="primary", key="btn_run_metro_surge"):
        sim = HubEventSimulator(st.session_state["hubs"])
        mod_hubs, log, metrics = sim.simulate_metro_surge(
            target_hub_id=chosen_hub_id,
            num_new_students=num_students,
            seed=42
        )
        st.session_state["sim_preview_ss6"] = {
            "preview_id": f"PREV-SS6-{uuid.uuid4().hex[:6].upper()}",
            "baseline_version": st.session_state.get("state_version", 1),
            "target_hub_id": chosen_hub_id,
            "modified_hubs": mod_hubs,
            "event_log": log,
            "metrics": metrics
        }
        st.success("✅ Đã chạy xong mô phỏng! Xem bản xem trước (Preview) ở phía dưới.")
        st.rerun()

    # ═══════════════════════════════════════════════
    # RENDER BẢN XEM TRƯỚC (PREVIEW) & NÚT ÁP DỤNG ĐỘC LẬP
    # ═══════════════════════════════════════════════
    preview = st.session_state.get("sim_preview_ss6")
    if preview:
        st.divider()
        st.subheader("🔍 Bản xem trước kết quả mô phỏng (Preview)")
        st.info(f"Mã Preview: `{preview['preview_id']}` | Baseline State Version: `{preview['baseline_version']}`")

        # Hiển thị nhật ký sự kiện
        with st.expander("📋 Nhật ký sự kiện mô phỏng", expanded=True):
            for entry in preview["event_log"]:
                if "CẢNH BÁO" in entry:
                    st.error(entry)
                elif "BẮT ĐẦU" in entry:
                    st.info(entry)
                else:
                    st.text(entry)

        # So sánh Trước / Sau
        before_h = next(h for h in st.session_state["hubs"] if h["hub_id"] == preview["target_hub_id"])
        after_h = next(h for h in preview["modified_hubs"] if h["hub_id"] == preview["target_hub_id"])

        c_bef, c_aft = st.columns(2)
        with c_bef:
            st.markdown("##### 🔵 Hiện trạng trước mô phỏng")
            st.metric("Chỗ đỗ trống", f"{before_h['available_slots']}/{before_h['total_slots']}")
            st.metric("Cổng sạc trống", f"{before_h['charging_ports']['available']}/{before_h['charging_ports']['total']}")
            st.metric("Tổng số xe hiện hữu", len(before_h["current_vehicles"]))

        with c_aft:
            st.markdown("##### 🔴 Dự kiến sau mô phỏng")
            st.metric(
                "Chỗ đỗ trống",
                f"{after_h['available_slots']}/{after_h['total_slots']}",
                delta=after_h['available_slots'] - before_h['available_slots']
            )
            st.metric(
                "Cổng sạc trống",
                f"{after_h['charging_ports']['available']}/{after_h['charging_ports']['total']}",
                delta=after_h['charging_ports']['available'] - before_h['charging_ports']['available']
            )
            st.metric(
                "Tổng số xe hiện hữu",
                len(after_h["current_vehicles"]),
                delta=len(after_h["current_vehicles"]) - len(before_h["current_vehicles"])
            )

        # NÚT ÁP DỤNG & HỦY BỎ ĐỘC LẬP (Đã fix hoàn toàn lỗi nested button)
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("✅ Áp dụng kết quả vào vận hành trạm", type="primary", key="btn_apply_ss6"):
                current_ver = st.session_state.get("state_version", 1)
                if preview["baseline_version"] != current_ver:
                    st.error(f"❌ Dữ liệu trạm đã thay đổi (Phiên bản {current_ver} khác {preview['baseline_version']}). Vui lòng chạy lại mô phỏng trước khi áp dụng!")
                else:
                    st.session_state["hubs"] = preview["modified_hubs"]
                    bump_state_version(st.session_state)
                    del st.session_state["sim_preview_ss6"]
                    st.success("🎉 Đã áp dụng thành công kết quả mô phỏng vào dữ liệu vận hành hệ thống!")
                    st.rerun()

        with col_act2:
            if st.button("❌ Hủy bỏ bản xem trước", key="btn_discard_ss6"):
                del st.session_state["sim_preview_ss6"]
                st.info("Đã xóa bản xem trước mô phỏng. Dữ liệu trạm được giữ nguyên.")
                st.rerun()
