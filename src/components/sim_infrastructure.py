"""
sim_infrastructure.py – Subsystem 7: Mô phỏng kịch bản What-if (Sự cố Hạ tầng)
Smart E-Mobility Hub – ĐHQG-HCM

Chức năng chuẩn hóa:
  • Console quản lý bật/tắt cổng sạc (Toggle) bảo toàn sức chứa (FR-13, FR-14)
  • Mô phỏng Port Failure phân biệt cổng rảnh vs cổng đang sạc (ngắt phiên sạc) (FR-15)
  • Tách biệt Preview và Nút Áp dụng (Khắc phục hoàn toàn lỗi lồng nút)
  • Tự động đề xuất điều phối sang 2 Hub lân cận qua core/routing.py (FR-15c / UC_SS7_02)

FR Covered: FR-14, FR-15, FR-15c
US Covered: US-23, US-24, US-24b
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

from core.simulator import HubEventSimulator
from core.routing import find_alternative_hubs
from core.state import bump_state_version

def _init_ss7():
    if "port_overrides" not in st.session_state:
        st.session_state["port_overrides"] = {}
    if "infra_log" not in st.session_state:
        st.session_state["infra_log"] = []

def render():
    """Render giao diện Subsystem 7 – Mô phỏng Sự cố Hạ tầng."""
    _init_ss7()

    st.header("🔧 Mô phỏng Sự cố Hạ tầng – Infrastructure Failure")
    st.caption("Mô phỏng sự cố cổng sạc, mất điện lưới và kích hoạt điều hướng tự động (FR-14, FR-15, FR-15c).")

    hubs = st.session_state.get("hubs", [])
    if not hubs:
        st.error("Không có dữ liệu Hub.")
        return

    sim_time = st.session_state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    tab_console, tab_fail_sim, tab_overview, tab_log = st.tabs([
        "🔌 1. Console bật/tắt cổng sạc",
        "💥 2. Mô phỏng sự cố trạm (Failure Preview)",
        "📊 3. Tổng quan hạ tầng mạng lưới",
        "📋 4. Nhật ký thay đổi hạ tầng",
    ])

    # ═══════════════════════════════════════════════
    # TAB 1: CONSOLE BẬT/TẮT CỔNG SẠC
    # ═══════════════════════════════════════════════
    with tab_console:
        st.subheader("🔌 Console quản trị bật/tắt cổng sạc theo Hub")
        st.caption("Mô phỏng ngắt kết nối cục bộ bảo trì hoặc sự cố lưới điện.")

        for hub in hubs:
            hid = hub["hub_id"]
            total_p = hub["charging_ports"]["total"]
            avail_p = hub["charging_ports"]["available"]
            current_down = st.session_state["port_overrides"].get(hid, 0)

            c_name, c_input, c_stat = st.columns([3, 2, 2])
            with c_name:
                st.markdown(f"**{hub['name']}**")
                st.caption(f"Tổng cổng: {total_p} | Đang khả dụng: {avail_p}")
            with c_input:
                new_down = st.number_input(
                    f"Số cổng ngắt ({hid}):",
                    min_value=0, max_value=total_p, value=current_down,
                    key=f"toggle_port_{hid}"
                )
            with c_stat:
                if new_down == total_p:
                    st.error("⛔ Toàn bộ trạm offline")
                elif new_down > 0:
                    st.warning(f"⚠️ {new_down} cổng offline")
                else:
                    st.success("✅ Hoạt động bình thường")

        if st.button("⚡ Áp dụng trạng thái bật/tắt cổng sạc", type="primary", key="btn_apply_port_toggles"):
            import copy
            from core.scheduler import apply_hub_snapshot
            updated = copy.deepcopy(hubs)
            for hub in updated:
                ports = hub["charging_ports"]
                new_d = int(st.session_state.get(f"toggle_port_{hub['hub_id']}", 0))
                busy = ports["total"] - ports.get("offline", 0) - ports["available"]
                increase = new_d - ports.get("offline", 0)
                ports["available"] = max(0, ports["available"] - max(0, increase - busy)) if increase > 0 else ports["available"] - increase
                ports["offline"] = new_d
                st.session_state["port_overrides"][hub["hub_id"]] = new_d
            apply_hub_snapshot(st.session_state, updated)
            bump_state_version(st.session_state)
            st.success("✅ Đã cập nhật trạng thái cổng sạc thành công (Bảo toàn sức chứa)!")
            st.rerun()

    # ═══════════════════════════════════════════════
    # TAB 2: MÔ PHỎNG SỰ CỐ TRẠM & ĐỀ XUẤT ĐIỀU PHỐI
    # ═══════════════════════════════════════════════
    with tab_fail_sim:
        st.subheader("💥 Mô phỏng sự cố hỏng cổng sạc & Điều hướng thay thế")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            hub_opts = [f"{h['hub_id']} – {h['name']}" for h in hubs]
            fail_hub_str = st.selectbox("Hub xảy ra sự cố:", hub_opts, index=3, key="ss7_fail_hub")
            fail_hub_id = fail_hub_str.split(" – ")[0]
        with f_col2:
            num_fail = st.number_input("Số cổng bị hỏng đột ngột:", min_value=1, max_value=15, value=4, key="ss7_fail_num")

        if st.button("🔧 Chạy mô phỏng Port Failure (Tạo Preview)", type="primary", key="btn_run_port_failure"):
            sim = HubEventSimulator(st.session_state["hubs"])
            mod_hubs, log, metrics = sim.simulate_port_failure(
                target_hub_id=fail_hub_id,
                num_ports_down=num_fail,
                seed=42
            )
            st.session_state["sim_preview_ss7"] = {
                "preview_id": f"PREV-SS7-{uuid.uuid4().hex[:6].upper()}",
                "baseline_version": st.session_state.get("state_version", 1),
                "target_hub_id": fail_hub_id,
                "modified_hubs": mod_hubs,
                "event_log": log,
                "metrics": metrics
            }
            st.success("✅ Đã chạy xong mô phỏng sự cố hạ tầng! Xem Preview ở phía dưới.")
            st.rerun()

        # Render Preview & Apply độc lập
        prev7 = st.session_state.get("sim_preview_ss7")
        if prev7:
            st.divider()
            st.subheader("🔍 Bản xem trước Sự cố Hạ tầng (Preview)")
            st.info(f"Mã Preview: `{prev7['preview_id']}` | Baseline State Version: `{prev7['baseline_version']}`")

            with st.expander("📋 Nhật ký chi tiết sự cố", expanded=True):
                for e in prev7["event_log"]:
                    if "CẢNH BÁO" in e:
                        st.error(e)
                    elif "BẮT ĐẦU" in e:
                        st.warning(e)
                    else:
                        st.text(e)

            # Đề xuất điều hướng tự động sang Hub lân cận (FR-15c / UC_SS7_02)
            alts = find_alternative_hubs(
                hubs=prev7["modified_hubs"],
                target_hub_id=prev7["target_hub_id"],
                need_ports=True,
                need_slots=False,
                limit=2
            )
            if alts:
                st.warning("🔄 **Đề xuất điều phối tự động sang trạm sạc lân cận (FR-15c / UC_SS7_02):**")
                for a in alts:
                    st.write(f"- 📍 **{a['name']}** (~{a['distance_km']} km): Còn **{a['available_ports']}** cổng sạc trống | **{a['available_slots']}** chỗ đỗ")

            # Nút Áp dụng & Hủy bỏ độc lập
            ca1, ca2 = st.columns(2)
            with ca1:
                if st.button("✅ Áp dụng sự cố vào hệ thống vận hành", type="primary", key="btn_apply_ss7"):
                    cur_v = st.session_state.get("state_version", 1)
                    if prev7["baseline_version"] != cur_v:
                        st.error("❌ Dữ liệu trạm đã thay đổi trong phiên. Vui lòng chạy lại mô phỏng trước khi áp dụng!")
                    else:
                        from core.scheduler import apply_hub_snapshot
                        apply_hub_snapshot(st.session_state, prev7["modified_hubs"])
                        bump_state_version(st.session_state)
                        del st.session_state["sim_preview_ss7"]
                        st.success("🎉 Đã áp dụng thành công sự cố hạ tầng vào dữ liệu hệ thống!")
                        st.rerun()

            with ca2:
                if st.button("❌ Hủy bỏ bản xem trước sự cố", key="btn_discard_ss7"):
                    del st.session_state["sim_preview_ss7"]
                    st.info("Đã hủy bản xem trước sự cố.")
                    st.rerun()

    # ═══════════════════════════════════════════════
    # TAB 3: TỔNG QUAN HẠ TẦNG
    # ═══════════════════════════════════════════════
    with tab_overview:
        st.subheader("📊 Tình trạng cổng sạc theo Hub")
        infra_data = []
        for h in hubs:
            tot = h["charging_ports"]["total"]
            av = h["charging_ports"]["available"]
            offline = h["charging_ports"].get("offline", 0)
            infra_data.append({
                "Hub": h["name"].replace("Hub ", ""),
                "Đang sạc / Bận": max(0, tot - av - offline),
                "Khả dụng": av,
                "Offline": offline,
            })
        fig = px.bar(
            pd.DataFrame(infra_data),
            x="Hub",
            y=["Đang sạc / Bận", "Khả dụng", "Offline"],
            title="Phân bổ trạng thái cổng sạc theo Hub",
            barmode="stack",
            color_discrete_sequence=["#ff6b6b", "#51cf66", "#777777"]
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # ═══════════════════════════════════════════════
    # TAB 4: NHẬT KÝ THAY ĐỔI
    # ═══════════════════════════════════════════════
    with tab_log:
        st.subheader("📋 Nhật ký lịch sử thay đổi hạ tầng trạm")
        if st.session_state["infra_log"]:
            st.dataframe(pd.DataFrame(st.session_state["infra_log"]), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có sự kiện thay đổi hạ tầng.")
