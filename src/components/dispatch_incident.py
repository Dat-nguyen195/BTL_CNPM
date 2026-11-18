"""
dispatch_incident.py – Subsystem 4: Điều phối xe & Xử lý sự cố
Smart E-Mobility Hub – ĐHQG-HCM

Chức năng chuẩn hóa:
  • Điều phối xe cân bằng tải liên trạm (UC_SS4_01)
    - Kiểm tra sức chứa Hub đích nghiêm ngặt (từ chối nếu không đủ chỗ đỗ, không clamp).
    - Vòng đời điều phối rõ ràng: AVAILABLE (Hub nguồn) → DISPATCHED (Đang trung chuyển) → AVAILABLE (Hub đích khi nhận).
  • Báo cáo & Xử lý sự cố phương tiện / cổng sạc (UC_SS4_02)
    - Cách ly tài nguyên INCIDENT / OFFLINE.
    - Quy trình xác nhận (Acknowledge) → Sửa chữa (Repair) → Khôi phục (Recover).

FR Covered: FR-07, FR-08
US Covered: US-15, US-16, US-17
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

from core.state import VehicleStatus, PortStatus, bump_state_version

def _init_ss4_state():
    if "dispatch_log" not in st.session_state:
        st.session_state["dispatch_log"] = []
    if "active_dispatches" not in st.session_state:
        st.session_state["active_dispatches"] = []
    if "incident_log" not in st.session_state:
        st.session_state["incident_log"] = []

def render():
    """Render giao diện Subsystem 4 – Điều phối xe & Quản lý sự cố."""
    _init_ss4_state()

    st.header("🔄 Điều phối Xe & Quản lý Sự cố Trạm")
    st.caption("Phân hệ SS4 — Dispatch & Incident Management (FR-07, FR-08).")

    hubs = st.session_state.get("hubs", [])
    if not hubs:
        st.error("Không có dữ liệu Hub.")
        return

    sim_time = st.session_state.get("current_sim_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    tab_dispatch, tab_in_transit, tab_incident, tab_history = st.tabs([
        "🚚 1. Tạo lệnh điều phối (UC_SS4_01)",
        "📦 2. Tiếp nhận xe trung chuyển",
        "🚨 3. Báo cáo & Xử lý sự cố (UC_SS4_02)",
        "📋 4. Nhật ký điều phối & Sự cố",
    ])

    # ═══════════════════════════════════════════════
    # TAB 1: TẠO LỆNH ĐIỀU PHỐI (UC_SS4_01)
    # ═══════════════════════════════════════════════
    with tab_dispatch:
        st.subheader("🚚 Tạo lệnh điều phối cân bằng tải liên trạm")
        hub_names = [h["name"] for h in hubs]

        # Đặt selectbox bên ngoài form để UI cập nhật động danh sách xe
        col_src, col_dst = st.columns(2)
        with col_src:
            src_name = st.selectbox("Hub nguồn (Xuất xe):", hub_names, index=1, key="disp_src_name")
            src_hub = next(h for h in hubs if h["name"] == src_name)
        with col_dst:
            dst_name = st.selectbox("Hub đích (Tiếp nhận):", hub_names, index=3, key="disp_dst_name")
            dst_hub = next(h for h in hubs if h["name"] == dst_name)

        if src_name == dst_name:
            st.warning("⚠️ Hub nguồn và Hub đích phải khác nhau!")
        else:
            st.info(
                f"**Nguồn:** {src_name} (Xe đỗ sẵn sàng: {len([v for v in src_hub['current_vehicles'] if v['status'] == VehicleStatus.AVAILABLE.value and v.get('ownership', 'SHARED') == 'SHARED'])}) | "
                f"**Đích:** {dst_name} (Chỗ trống khả dụng: **{dst_hub['available_slots']}** chỗ)"
            )

        # Lọc danh sách xe shared available tại nguồn
        eligible_vehicles = [
            v for v in src_hub["current_vehicles"]
            if v["status"] == VehicleStatus.AVAILABLE.value
            and v.get("ownership", "SHARED") == "SHARED"
        ]

        if not eligible_vehicles:
            st.warning("⚠️ Hub nguồn không có xe dùng chung nào ở trạng thái AVAILABLE.")
        else:
            veh_opts = [f"{v['vehicle_id']} – {v['type'].upper()} (Pin: {v['battery_soc']}%)" for v in eligible_vehicles]
            selected_opts = st.multiselect("Chọn các xe cần điều phối:", veh_opts, key="disp_chosen_veh")
            reason = st.text_area("Lý do điều phối:", value="Cân bằng tải giờ cao điểm, bổ sung xe cho trạm thiếu hụt.", key="disp_reason")

            if st.button("🚀 Khởi tạo lệnh điều phối", type="primary", key="btn_create_dispatch"):
                if not selected_opts:
                    st.error("❌ Vui lòng chọn ít nhất một xe để điều phối.")
                elif src_name == dst_name:
                    st.error("❌ Hub nguồn và Hub đích phải khác nhau.")
                elif len(selected_opts) > dst_hub["available_slots"]:
                    st.error(
                        f"❌ Không thể thực hiện: Hub đích {dst_name} chỉ còn {dst_hub['available_slots']} chỗ trống, "
                        f"nhưng bạn đã chọn điều phối {len(selected_opts)} xe!"
                    )
                else:
                    # Chuyển xe: Nguồn giải phóng slot (+1/xe), xe sang DISPATCHED, Đích giữ slot (-1/xe)
                    chosen_ids = [s.split(" – ")[0] for s in selected_opts]
                    moved_records = []
                    
                    for vid in chosen_ids:
                        for i, v in enumerate(src_hub["current_vehicles"]):
                            if v["vehicle_id"] == vid:
                                veh = src_hub["current_vehicles"].pop(i)
                                veh["status"] = VehicleStatus.DISPATCHED.value
                                moved_records.append(veh)
                                src_hub["available_slots"] = min(src_hub["total_slots"], src_hub["available_slots"] + 1)
                                break

                    # Reserve slot at destination
                    dst_hub["available_slots"] = max(0, dst_hub["available_slots"] - len(moved_records))
                    dst_hub["destination_holds"] = dst_hub.get("destination_holds", 0) + len(moved_records)

                    dispatch_id = f"DISP-{uuid.uuid4().hex[:6].upper()}"
                    disp_record = {
                        "dispatch_id": dispatch_id,
                        "time": sim_time,
                        "source_hub_id": src_hub["hub_id"],
                        "source_name": src_name,
                        "destination_hub_id": dst_hub["hub_id"],
                        "destination_name": dst_name,
                        "vehicle_ids": chosen_ids,
                        "vehicles": moved_records,
                        "reason": reason,
                        "status": "IN_TRANSIT"
                    }
                    st.session_state["active_dispatches"].append(disp_record)
                    st.session_state["dispatch_log"].append(disp_record)
                    bump_state_version(st.session_state)

                    st.success(
                        f"🎉 Lệnh điều phối #{dispatch_id} đã được kích hoạt!\n\n"
                        f"- Đã chuyển **{len(chosen_ids)} xe** ({', '.join(chosen_ids)}) từ {src_name} sang trạng thái `DISPATCHED`.\n"
                        f"- Hub đích {dst_name} đã giữ chỗ tiếp nhận an toàn."
                    )
                    st.rerun()

    # ═══════════════════════════════════════════════
    # TAB 2: TIẾP NHẬN XE TRUNG CHUYỂN
    # ═══════════════════════════════════════════════
    with tab_in_transit:
        st.subheader("📦 Xác nhận Tiếp nhận Xe tại Hub đích")
        active_list = [d for d in st.session_state.get("active_dispatches", []) if d.get("status") == "IN_TRANSIT"]

        if not active_list:
            st.info("📭 Hiện không có chuyến điều phối nào đang trung chuyển trên đường.")
        else:
            for d in active_list:
                st.info(
                    f"**Lệnh #{d['dispatch_id']}** | Từ **{d['source_name']}** → Đến **{d['destination_name']}**\n\n"
                    f"- Xe trung chuyển: `{', '.join(d['vehicle_ids'])}`\n"
                    f"- Xuất phát lúc: `{d['time']}` | Lý do: {d['reason']}"
                )
                if st.button(f"📥 Xác nhận tiếp nhận tại {d['destination_name']} (#{d['dispatch_id']})", key=f"btn_recv_{d['dispatch_id']}"):
                    dst_h = next((h for h in hubs if h["hub_id"] == d["destination_hub_id"]), None)
                    if not dst_h or dst_h.get("destination_holds", 0) < len(d["vehicles"]):
                        st.error("Thiếu Hub hoặc chỗ giữ. Cần đối soát trước khi nhận xe.")
                        return
                    if dst_h:
                        # Restore destination_holds and insert vehicles as AVAILABLE
                        dst_h["destination_holds"] = max(0, dst_h.get("destination_holds", 0) - len(d["vehicles"]))
                        for v in d["vehicles"]:
                            v["status"] = VehicleStatus.AVAILABLE.value
                            v["hub_id"] = dst_h["hub_id"]
                            dst_h.setdefault("current_vehicles", []).append(v)

                    d["status"] = "COMPLETED"
                    d["completed_at"] = sim_time
                    bump_state_version(st.session_state)
                    st.success(f"✅ Đã tiếp nhận an toàn {len(d['vehicles'])} xe tại {d['destination_name']}. Các xe đã trở lại trạng thái AVAILABLE!")
                    st.rerun()

    # ═══════════════════════════════════════════════
    # TAB 3: BÁO CÁO & XỬ LÝ SỰ CỐ (UC_SS4_02)
    # ═══════════════════════════════════════════════
    with tab_incident:
        st.subheader("🚨 Báo cáo & Cách ly sự cố Phương tiện / Hạ tầng trạm")
        target_h_name = st.selectbox("Hub xảy ra sự cố:", hub_names, key="inc_hub_name")
        target_h = next(h for h in hubs if h["name"] == target_h_name)
        with st.form("incident_report_form"):
            i_col1, i_col2 = st.columns(2)
            with i_col1:
                inc_type = st.selectbox("Đối tượng sự cố:", ["Phương tiện (Xe điện)", "Cổng sạc (Charging Port)", "Hạ tầng trạm"], key="inc_type")
                available_ids = [v["vehicle_id"] for v in target_h["current_vehicles"] if v["status"] == "AVAILABLE"]
                incident_vehicle = st.selectbox("Xe cần cách ly (nếu là sự cố phương tiện):", available_ids or ["Không có xe AVAILABLE"], key="inc_vehicle")
            with i_col2:
                severity = st.selectbox("Mức độ nghiêm trọng:", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], index=2, key="inc_sev")
                desc = st.text_input("Mô tả chi tiết sự cố:", value="Hỏng phanh an toàn hoặc chập cáp sạc cổng số 2", key="inc_desc")

            if st.form_submit_button("🚨 Ghi nhận sự cố & Cách ly", type="primary"):
                inc_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
                inc_record = {
                    "incident_id": inc_id,
                    "hub_name": target_h_name,
                    "hub_id": target_h["hub_id"],
                    "type": inc_type,
                    "severity": severity,
                    "description": desc,
                    "reported_at": sim_time,
                    "status": "REPORTED"
                }
                if inc_type == "Phương tiện (Xe điện)" and incident_vehicle in available_ids:
                    vehicle = next(v for v in target_h["current_vehicles"] if v["vehicle_id"] == incident_vehicle)
                    vehicle["status"] = VehicleStatus.INCIDENT.value
                    inc_record["vehicle_id"] = incident_vehicle
                elif inc_type == "Cổng sạc (Charging Port)":
                    ports = target_h["charging_ports"]
                    if ports["available"] > 0:
                        ports["available"] -= 1
                        ports["offline"] = ports.get("offline", 0) + 1
                        inc_record["isolated_ports"] = 1
                st.session_state["incident_log"].append(inc_record)
                bump_state_version(st.session_state)
                st.error(f"🚨 Đã ghi nhận sự cố #{inc_id}! Hệ thống đã gắn nhãn cảnh báo và gửi thông báo tới kỹ thuật viên.")
                st.rerun()

        # Quản lý & Phục hồi sự cố
        active_inc = [i for i in st.session_state.get("incident_log", []) if i.get("status") in ["REPORTED", "ACKNOWLEDGED"]]
        if active_inc:
            st.divider()
            st.subheader("🔧 Xử lý & Phục hồi sự cố đang diễn ra")
            for inc in active_inc:
                c_desc, c_act = st.columns([3, 1])
                with c_desc:
                    st.write(f"- **#{inc['incident_id']}** [{inc['severity']}] tại **{inc['hub_name']}**: {inc['description']} (`{inc['reported_at']}`) — Trạng thái: **{inc['status']}**")
                with c_act:
                    if inc["status"] == "REPORTED":
                        if st.button("Xác nhận tiếp nhận", key=f"ack_{inc['incident_id']}"):
                            inc["status"] = "ACKNOWLEDGED"
                            bump_state_version(st.session_state)
                            st.rerun()
                    elif inc["status"] == "ACKNOWLEDGED":
                        if st.button("Hoàn tất sửa chữa", key=f"rec_{inc['incident_id']}"):
                            inc["status"] = "RESOLVED"
                            inc["resolved_at"] = sim_time
                            hub = next(h for h in hubs if h["hub_id"] == inc["hub_id"])
                            for vehicle in hub["current_vehicles"]:
                                if vehicle["vehicle_id"] == inc.get("vehicle_id"):
                                    vehicle["status"] = VehicleStatus.AVAILABLE.value
                            if inc.get("isolated_ports"):
                                hub["charging_ports"]["available"] += inc["isolated_ports"]
                                hub["charging_ports"]["offline"] -= inc["isolated_ports"]
                            bump_state_version(st.session_state)
                            st.success(f"Đã khôi phục tài nguyên #{inc['incident_id']}!")
                            st.rerun()

    # ═══════════════════════════════════════════════
    # TAB 4: NHẬT KÝ ĐIỀU PHỐI & SỰ CỐ
    # ═══════════════════════════════════════════════
    with tab_history:
        st.subheader("📋 Nhật ký lịch sử điều phối xe")
        if st.session_state["dispatch_log"]:
            st.dataframe(pd.DataFrame([{
                "Mã lệnh": d.get("dispatch_id", f"DISP-{d.get('time', '')}"),
                "Thời gian": d.get("time", "—"),
                "Hub xuất": d.get("source_name", d.get("from", "—")),
                "Hub nhận": d.get("destination_name", d.get("to", "—")),
                "Số lượng xe": len(d.get("vehicle_ids", d.get("vehicles", []))),
                "Trạng thái": d.get("status", "COMPLETED")
            } for d in st.session_state["dispatch_log"]]), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có lịch sử điều phối.")

        st.divider()
        st.subheader("📋 Nhật ký lịch sử sự cố trạm")
        if st.session_state["incident_log"]:
            st.dataframe(pd.DataFrame(st.session_state["incident_log"]), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có sự cố nào được ghi nhận.")
