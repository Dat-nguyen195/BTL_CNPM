# Bảng ma trận truy vết cá nhân — Hoàng Văn Tấn — SS6
**Môn học:** Công nghệ Phần mềm (CO3001) — Học kỳ 261  
**Dự án:** Smart E-Mobility Hub — BEE BRAVE (Nhóm 7)  
**Phân hệ:** SS6 — Mô phỏng nhu cầu What-if & Dự báo 24 giờ  
**Thành viên:** Hoàng Văn Tấn — MSSV: 2213074 — Vai trò: TV6  
**Trạng thái:** HOÀN THIỆN THIẾT KẾ SUBMISSION 3 (Đối chiếu mã nguồn, sơ đồ và hợp đồng dùng chung).

---

## 1. Nguyên tắc truy vết
Chuỗi truy vết chuẩn hóa xuyên suốt dự án:  
`Yêu cầu (US / FR) → Use Case Sub 2 → Thông điệp Sequence / Nhánh Activity → Lớp thiết kế Sub 3 → Phương thức (Method ID) → Mã nguồn triển khai / Đề xuất → Test case liên quan`.

*Lưu ý:* Toàn bộ liên kết trong tài liệu sử dụng đường dẫn tương đối (relative path) để đảm bảo khả năng chuyển đổi và truy cập nhất quán trên mọi môi trường và hệ điều hành.

---

## 2. Bảng truy vết chi tiết theo Use Case

### 2.1. UC_SS6_01 — Mô phỏng tăng đột biến nhu cầu khách Metro (What-if Metro Surge)

| Yêu cầu gốc (SRS) | Use Case & Sơ đồ Sub 2 | Thông điệp Sequence / Nhánh Activity | Lớp Sub 3 | Method ID & Chữ ký phương thức Sub 3 | Mã nguồn hiện có / Đề xuất | Test Case ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **US-21** (Mô phỏng nhu cầu What-if Metro),<br>**FR-12** (What-if scenario engine) | `UC_SS6_01`<br>[Sequence](<../../../diagrams/Use-case detail-scenario/SS6/Sequence diagrams/UC_SS6_01_HoangVanTan_sequence.puml>)<br>[Activity](<../../../diagrams/Use-case detail-scenario/SS6/Activity diagrams/UC_SS6_01_HoangVanTan_activity.puml>) | Bước 1.1–1.3: Cấu hình tham số Metro Surge (chọn Hub, số SV) | `SimDemandUI` | `SS6-MTH-08`: `render_metro_surge_tab(): void` | [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) (Đã triển khai UI) | `TC-SS6-SRG-01` |
| **US-21**, **FR-12** | `UC_SS6_01` | Bước 2.1: Khởi tạo bản sao cách ly (Deepcopy isolation) | `DemandSimulationService` | `SS6-MTH-01`: `preview_demand(hub_id, num_students, seed): OperationResult[SimulationPreview]` | [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) bọc logic service | `TC-SS6-SRG-03` |
| **US-21**, **FR-12** | `UC_SS6_01` | Bước 2.2–2.3: Thực thi thuật toán Metro Surge, trừ chỗ đỗ, sinh xe pin thấp, theo dõi unserved arrivals | `HubEventSimulatorAdapter` / `HubEventSimulator` | `SS6-MTH-05`: `simulate_metro_surge(target_hub_id, num_students, seed): Tuple` | [src/core/simulator.py](<../../../../src/core/simulator.py>) (Đã triển khai Core) | `TC-SS6-SRG-01`,<br>`TC-SS6-SRG-02` |
| **US-21**, **FR-12** | `UC_SS6_01` | Bước 2.4: Đóng gói và lưu bản xem trước độc lập | `SimulationPreview`, `DemandScenario` | Khởi tạo DTO `SimulationPreview` với `scenario_type=DEMAND` | [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) lưu `st.session_state["sim_preview_ss6"]` | `TC-SS6-SRG-03` |
| **US-21**, **FR-12** | `UC_SS6_01` | Bước 3.1: So sánh Hiện trạng trước / Dự kiến sau mô phỏng | `SimDemandUI` | `SS6-MTH-08`: `render_preview_comparison(preview)` | [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) (Đã triển khai UI) | `TC-SS6-SRG-01` |
| **US-21**, **FR-12** | `UC_SS6_01` | Bước 3.2: Áp dụng kết quả vào vận hành (Kiểm tra version, commit, tăng state_version) | `SimulationCoordinator` | `SS6-MTH-03`: `apply_preview(preview_id, expected_version): OperationResult[ApplyResult]` | [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) & [src/core/state.py](<../../../../src/core/state.py>) | `TC-SS6-APL-01`,<br>`TC-SS6-APL-02`,<br>`TC-SS6-APL-03` |
| **US-21**, **FR-12** | `UC_SS6_01` | Bước 3.3: Hủy bỏ bản xem trước mô phỏng | `SimulationCoordinator` | `SS6-MTH-04`: `discard_preview(preview_id): OperationResult[bool]` | [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) | `TC-SS6-APL-04` |

---

### 2.2. UC_SS6_02 — Dự báo phụ tải nhu cầu và phân tích hàng đợi 24h

| Yêu cầu gốc (SRS) | Use Case & Sơ đồ Sub 2 | Thông điệp Sequence / Nhánh Activity | Lớp Sub 3 | Method ID & Chữ ký phương thức Sub 3 | Mã nguồn hiện có / Đề xuất | Test Case ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **US-21**, **US-22** (Dự báo nhu cầu chuỗi thời gian),<br>**FR-13** (Queue & wait time forecast) | `UC_SS6_02`<br>[Sequence](<../../../diagrams/Use-case detail-scenario/SS6/Sequence diagrams/UC_SS6_02_HoangVanTan_sequence.puml>)<br>[Activity](<../../../diagrams/Use-case detail-scenario/SS6/Activity diagrams/UC_SS6_02_HoangVanTan_activity.puml>) | Bước 1.1–1.2: Điều chỉnh tham số What-if (base_rate, surge_mult, sim_hours=24) | `SimDemandUI` | `SS6-MTH-07`: `render_demand_forecast_tab(): void` | [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) (Đã triển khai UI) | `TC-SS6-FC-01` |
| **US-21**, **US-22**, **FR-13** | `UC_SS6_02` | Bước 2.1–2.2: Gọi động cơ dự báo theo giờ với horizon 24h và seed tái lập | `ForecastService` | `SS6-MTH-02`: `forecast(hub_id, base_arrival_rate, surge_multiplier, hours=24, seed=42): OperationResult[ForecastResult]` | [src/core/simulator.py](<../../../../src/core/simulator.py>) bọc logic service (`INT-04`) | `TC-SS6-FC-01`,<br>`TC-SS6-FC-02` |
| **US-21**, **US-22**, **FR-13** | `UC_SS6_02` | Bước 2.3–2.4: Tính toán chuỗi thời gian, giờ cao điểm, hàng đợi tích lũy và thời gian chờ (service rate = 8) | `HubEventSimulatorAdapter` / `HubEventSimulator` | `SS6-MTH-06`: `generate_demand_forecast(base_rate, surge_mult, hours, seed): List[Dict]` | [src/core/simulator.py](<../../../../src/core/simulator.py>) (Đã triển khai Core) | `TC-SS6-FC-01` |
| **US-21**, **US-22**, **FR-13** | `UC_SS6_02` | Bước 2.5: Đóng gói tập 24 điểm dự báo thành đối tượng kết quả | `ForecastResult`, `ForecastPoint` | Khởi tạo cấu trúc `ForecastResult` chứa 24 `ForecastPoint` | Ánh xạ từ danh sách `dict` hiện có sang typed DTO | `TC-SS6-FC-01` |
| **US-21**, **US-22**, **FR-13** | `UC_SS6_02` | Bước 3.1–3.3: Vẽ đồ thị Plotly (Bar lượng đến, Line hàng đợi Y2) & hiển thị KPI | `SimDemandUI` | `SS6-MTH-07`: `plot_forecast_charts(forecast_df)` | [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) (Đã triển khai UI) | `TC-SS6-FC-01` |
| **US-21** (Mô hình doanh thu theo nhu cầu) | `UC_SS6_02` (Mở rộng) | Phân tích biến động doanh thu tiềm năng & tổn thất do unserved | `ForecastService` (Đề xuất mở rộng) | `calculate_potential_revenue_impact()` *(Thiết kế mở rộng, ghi nhận giới hạn)* | Chưa có trong prototype; đề xuất công thức trong báo cáo | `TC-SS6-REV-01` (Thiết kế đề xuất) |

---

## 3. Tổng hợp ánh xạ Mã nguồn & Kiểm thử

* **Mã nguồn đã triển khai:**
  * UI Component: [src/components/sim_demand.py](<../../../../src/components/sim_demand.py>) (182 dòng code Streamlit hoàn chỉnh, chạy thực tế).
  * Core Engine: [src/core/simulator.py](<../../../../src/core/simulator.py>) (`HubEventSimulator`, phương thức `simulate_metro_surge`, `generate_demand_forecast`).
  * Trạng thái và Versioning: [src/core/state.py](<../../../../src/core/state.py>) (`bump_state_version`, `get_initial_session_state`).
* **Mã nguồn kiểm thử tự động:**
  * File test: [tests/test_simulations.py](<../../../../tests/test_simulations.py>) kiểm tra tính cách ly deepcopy và unserved arrivals.
  * Suite kiểm thử mở rộng Sub 3: 7 ca test chi tiết trong [test_cases.md](test_cases.md) bao phủ toàn bộ các điều kiện biên và xung đột phiên bản.
