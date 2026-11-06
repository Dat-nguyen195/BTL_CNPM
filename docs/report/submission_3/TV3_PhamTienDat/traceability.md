# Bảng ma trận truy vết cá nhân — Phạm Tiến Đạt — SS3
**Môn học:** Công nghệ Phần mềm (CO3001) — Học kỳ 261  
**Dự án:** Smart E-Mobility Hub — BEE BRAVE (Nhóm 7)  
**Phân hệ:** SS3 — Giám sát mạng lưới Hub, KPI, Doanh thu & Cảnh báo  
**Thành viên:** Phạm Tiến Đạt — MSSV: 2410724 — Vai trò: TV3  
**Trạng thái:** HOÀN THIỆN THIẾT KẾ SUBMISSION 3 (Đối chiếu mã nguồn, sơ đồ và hợp đồng dùng chung).

---

## 1. Nguyên tắc truy vết
Chuỗi truy vết chuẩn hóa xuyên suốt dự án:  
`Yêu cầu (US / FR) → Use Case Sub 2 → Thông điệp Sequence / Nhánh Activity → Lớp thiết kế Sub 3 → Phương thức (Method ID) → Mã nguồn triển khai / Đề xuất → Test case liên quan`.

*Lưu ý:* Toàn bộ liên kết trong tài liệu sử dụng đường dẫn tương đối (relative path) để đảm bảo khả năng chuyển đổi và truy cập nhất quán trên mọi môi trường và hệ điều hành.

---

## 2. Bảng truy vết chi tiết theo Use Case

### 2.1. UC_SS3_01 — Giám sát mạng lưới Hub, KPI & Doanh thu thời gian thực

| Yêu cầu gốc (SRS) | Use Case & Sơ đồ Sub 2 | Thông điệp Sequence / Nhánh Activity | Lớp Sub 3 | Method ID & Chữ ký phương thức Sub 3 | Mã nguồn hiện có / Đề xuất | Test Case ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **US-13**, **US-14** (Giám sát trạng thái xe & chỗ đỗ),<br>**FR-05**, **FR-06** | `UC_SS3_01`<br>[Scenario](<../../../diagrams/Use-case detail-scenario/SS3/Usecase scenario/UC_SS3_PhamTienDat.md>)<br>[Sequence](<../../../diagrams/Use-case detail-scenario/SS3/Sequence diagrams/UC_SS3_01_PhamTienDat_sequence.puml>)<br>[Activity](<../../../diagrams/Use-case detail-scenario/SS3/Activity diagrams/UC_SS3_01_PhamTienDat_activity.puml>) | Bước 1–2: Truy cập Dashboard Giám sát Hub & yêu cầu tải dữ liệu toàn mạng lưới | `HubMonitorUI`,<br>`MonitoringService` | `SS3-MTH-13`: `render(): void`<br>`SS3-MTH-05`: `get_network_snapshot(): OperationResult[NetworkSnapshot]` (`INT-03`) | [src/components/hub_monitor.py](<../../../../src/components/hub_monitor.py>) (Đã triển khai UI; đề xuất tách tầng Service) | `TC-SS3-INV-01`,<br>`TC-SS3-IOT-01` |
| **US-12** (Giám sát phụ tải trạm sạc),<br>**US-13**, **FR-05** | `UC_SS3_01` | Bước 3–4: Kiểm tra bất biến sức chứa, tính tỷ lệ lấp đầy chỗ đỗ, tỷ lệ bận cổng sạc và công suất tiêu thụ so với trần $150.0\text{ kW}$ | `Hub`,<br>`OccupancySnapshot`,<br>`MonitoringService` | `SS3-MTH-03`: `validate_capacity_invariant(): bool`<br>`SS3-MTH-06`: `calculate_hub_occupancy(hub_id): OperationResult[OccupancySnapshot]` | [src/core/state.py](<../../../../src/core/state.py>) (`validate_hub_capacity`) & [src/components/hub_monitor.py](<../../../../src/components/hub_monitor.py>) (dòng 45–64, 152–166) | `TC-SS3-INV-01` |
| **US-07** (Báo cáo doanh thu vận hành),<br>**FR-05**, **FR-15b** | `UC_SS3_01` | Khung `opt [Tài khoản Admin]`: Tổng hợp doanh thu thực thu từ sổ cái, tách biệt tiền cọc đang tạm giữ (`HOLD_DEPOSIT`) và dư nợ (`debt`) | `RevenueReport`,<br>`MonitoringService` | `SS3-MTH-07`: `generate_revenue_report(hub_id=None): OperationResult[RevenueReport]` | [src/components/hub_monitor.py](<../../../../src/components/hub_monitor.py>) (dòng 129–150) & [src/core/billing.py](<../../../../src/core/billing.py>) | `TC-SS3-REV-01` |
| **US-13b** (Cấu hình ngưỡng cảnh báo) | `UC_SS3_01` | Khung `opt [Tài khoản Admin]`: Cập nhật ngưỡng cảnh báo sớm và ngưỡng quá tải | `MonitoringService` | `SS3-MTH-11`: `update_alert_thresholds(admin_id, warning_pct, critical_pct): OperationResult[bool]` | [src/core/policies.py](<../../../../src/core/policies.py>) (Hằng số ngưỡng; đề xuất hàm cập nhật động) | `TC-SS3-IOT-01` |
| **US-13**, **FR-06** | `UC_SS3_01` | Nhánh `Alt 1 [Phát hiện lỗi cảm biến IoT]` (Bước 5–7): Kỹ thuật viên xem danh sách lỗi IoT và ghi nhận phương án bảo trì | `Alert`,<br>`MonitoringService` | `SS3-MTH-12`: `get_iot_error_logs(hub_id=None)` & `record_iot_maintenance_plan(tech_id, alert_id, plan_note)` | [src/components/hub_monitor.py](<../../../../src/components/hub_monitor.py>) (dòng 33–36 quét cổng offline; đề xuất log bảo trì) | `TC-SS3-IOT-01` |
| **US-13**, **FR-05** | `UC_SS3_01` | Nhánh `Exception 1 [Mất kết nối cảm biến IoT]`: Hiển thị dữ liệu từ bộ nhớ đệm (Cache) kèm cảnh báo gián đoạn | `NetworkSnapshot`,<br>`Alert`,<br>`MonitoringService` | `SS3-MTH-05`: `get_network_snapshot()` trả về `is_using_cached_data = True` và `AlertType.IOT_SENSOR_TIMEOUT` | Thiết kế đề xuất trong `MonitoringService` (đã kiểm thử tự động) | `TC-SS3-IOT-01` |

---

### 2.2. UC_SS3_02 — Cảnh báo phân cấp chiếm dụng Hub & Sự cố IoT

| Yêu cầu gốc (SRS) | Use Case & Sơ đồ Sub 2 | Thông điệp Sequence / Nhánh Activity | Lớp Sub 3 | Method ID & Chữ ký phương thức Sub 3 | Mã nguồn hiện có / Đề xuất | Test Case ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **US-13b** (Cảnh báo sớm chiếm dụng cao),<br>**FR-05c** | `UC_SS3_02`<br>[Scenario](<../../../diagrams/Use-case detail-scenario/SS3/Usecase scenario/UC_SS3_PhamTienDat.md>)<br>[Sequence](<../../../diagrams/Use-case detail-scenario/SS3/Sequence diagrams/UC_SS3_02_PhamTienDat_sequence.puml>)<br>[Activity](<../../../diagrams/Use-case detail-scenario/SS3/Activity diagrams/UC_SS3_02_PhamTienDat_activity.puml>) | Bước 1–3 (Normal Flow): Tính tỷ lệ chiếm dụng; $< 70\%$ hiển thị bình thường; $70\% \le \text{occ} < 85\%$ phát cảnh báo sớm (Màu vàng) | `Hub`,<br>`Alert`,<br>`MonitoringService` | `SS3-MTH-01`: `calculate_occupancy_rate(): float`<br>`SS3-MTH-02`: `get_occupancy_level(): OccupancyLevel`<br>`SS3-MTH-08`: `evaluate_hub_alerts(hub_id)` | [src/core/policies.py](<../../../../src/core/policies.py>) (`get_occupancy_level`) & [src/components/hub_monitor.py](<../../../../src/components/hub_monitor.py>) (`yellow_hubs`, dòng 71–87) | `TC-SS3-BND-01` |
| **US-13b**, **FR-05c** | `UC_SS3_02` | Nhánh `Alt 1 [Chiếm dụng chạm ngưỡng 85% đến dưới 100%]`: Phát cảnh báo nguy cơ quá tải (Màu đỏ) và đề xuất điều phối xe sang SS4 (`UC_SS4_01`) | `Alert`,<br>`MonitoringService` | `SS3-MTH-08`: `evaluate_hub_alerts(hub_id)` sinh `AlertSeverity.CRITICAL` kèm cờ `dispatch_suggested`<br>`SS3-MTH-04`: `Alert.acknowledge(user_id, now)` | [src/components/hub_monitor.py](<../../../../src/components/hub_monitor.py>) (`red_hubs`, dòng 72, 89–94) | `TC-SS3-BND-01` |
| **US-13b**, **FR-05c** | `UC_SS3_02` | Nhánh `Alt 2 [Chiếm dụng đạt 100% sức chứa]`: Phát cảnh báo Khóa Đỏ và đồng bộ khóa tiếp nhận đặt chỗ mới với SS1/SS2 | `Hub`,<br>`MonitoringService` | `SS3-MTH-09`: `sync_hub_booking_lock(hub_id, lock_state=True, operation_key): OperationResult[bool]` | [src/components/hub_monitor.py](<../../../../src/components/hub_monitor.py>) (`full_hubs`, dòng 73, 96–101); chặn đặt chỗ tại [src/core/booking.py](<../../../../src/core/booking.py>) & [src/core/personal_ev.py](<../../../../src/core/personal_ev.py>) | `TC-SS3-BND-01`,<br>`TC-SS3-LCK-01` |
| **US-13b**, **FR-05c** | `UC_SS3_02` | Nhánh `Exception 1 [Lỗi đồng bộ khóa đặt chỗ khi Hub đạt 100%]`: Phát cảnh báo khẩn cấp và cho phép Operator khóa Hub thủ công | `Alert`,<br>`MonitoringService` | `SS3-MTH-10`: `manual_lock_hub(operator_id, hub_id, lock_state): OperationResult[bool]` | Thiết kế đề xuất chuẩn hóa xử lý ngoại lệ trong `MonitoringService` | `TC-SS3-LCK-01` |

---

## 3. Tổng hợp ánh xạ Mã nguồn & Kiểm thử

- **Mã nguồn đã triển khai:**
  * UI Component: [src/components/hub_monitor.py](<../../../../src/components/hub_monitor.py>) (166 dòng code Streamlit hoàn chỉnh, hiển thị KPI, cảnh báo 3 cột, bản đồ, sổ cái doanh thu và phụ tải năng lượng).
  * Chính sách ngưỡng & Công suất: [src/core/policies.py](<../../../../src/core/policies.py>) (`OCCUPANCY_WARNING_MIN = 70.0`, `OCCUPANCY_CRITICAL_MIN = 85.0`, `OCCUPANCY_FULL_MIN = 100.0`, `HUB_POWER_CAP_KW = 150.0`, hàm `get_occupancy_level`).
  * Quản lý trạng thái & Bảo toàn sức chứa: [src/core/state.py](<../../../../src/core/state.py>) (`load_and_normalize_hubs`, `validate_hub_capacity`, `validate_state_invariants`).
  * Sổ cái tài chính: [src/core/billing.py](<../../../../src/core/billing.py>) (quản lý `wallet["ledger"]`, tách biệt `HOLD_DEPOSIT` và các khoản `SETTLE_*`).
- **Mã nguồn kiểm thử tự động:**
  * Suite kiểm thử mở rộng Sub 3 của SS3: [tests/test_ss3_monitoring_bonus.py](<../../../../tests/test_ss3_monitoring_bonus.py>) (5 ca test tự động kiểm tra 6 mốc biên thập phân, bất biến sức chứa, doanh thu thực thu, khóa lũy đẳng và cache IoT — đạt `5/5 PASS`).
  * Test tích hợp hệ thống: [tests/test_core_state_and_billing.py](<../../../../tests/test_core_state_and_billing.py>) (`test_occupancy_threshold_levels`, `test_state_initialization_and_invariants`) và [tests/test_submission_2_acceptance.py](<../../../../tests/test_submission_2_acceptance.py>) (`test_dashboard_shows_actual_booking_ledger_and_revenue`).