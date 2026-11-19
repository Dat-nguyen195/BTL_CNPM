# ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH
# TRƯỜNG ĐẠI HỌC BÁCH KHOA
## KHOA KHOA HỌC VÀ KỸ THUẬT MÁY TÍNH

---

# BÁO CÁO THIẾT KẾ KIẾN TRÚC VÀ CHI TIẾT HỆ THỐNG PHẦN MỀM
## SUBMISSION #3: SOFTWARE ARCHITECTURE & DETAILED DESIGN

- **Môn học:** Công nghệ Phần mềm (CO3001) — Học kỳ HK261
- **Đề tài:** SMART E-MOBILITY HUB — Hệ thống Điều phối Phương tiện Điện trong Khu đô thị ĐHQG-HCM
- **Phân hệ phụ trách:** **PHÂN HỆ SS3: GIÁM SÁT MẠNG LƯỚI HUB, KPI, DOANH THU & CẢNH BÁO**
- **Giảng viên hướng dẫn:** TS. Trần Thị Ngọc Trâm
- **Lớp học phần:** L02 — **Nhóm báo cáo:** BEE BRAVE (Nhóm 7)
- **Sinh viên thực hiện:** Phạm Tiến Đạt
- **Mã số sinh viên (MSSV):** 2410724
- **Vai trò nhóm:** TV3 — Tổng hợp Development / Implementation View & System-level Class Diagram toàn hệ thống
- **Phiên bản tài liệu:** 1.1 (Hoàn thiện Submission 3)
- **Ngày hoàn thành:** 06/11/2026

---

## DANH SÁCH THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ

| STT | Họ và Tên | MSSV | Phân hệ phụ trách | Vai trò / Phần chung | Đóng góp |
| :-: | :--- | :-: | :--- | :--- | :-: |
| 1 | Nguyễn Thành Đạt | 2410709 | SS1: Đặt & Quản lý Xe dùng chung | Leader/PM — Chốt kiến trúc & hợp đồng tài chính | 100% |
| 2 | Nguyễn Anh Tài | 2413035 | SS2: Đăng ký Sạc & Đỗ xe cá nhân | Dev/Analyst — Hợp đồng tài chính & sạc liên phân hệ | 100% |
| **3** | **Phạm Tiến Đạt** | **2410724** | **SS3: Giám sát Mạng lưới Hub & Cảnh báo** | **TV3 — Tổng hợp Implementation View & System Class Diagram** | **100%** |
| 4 | Đặng Hoàng Quý Nhân | 2412401 | SS4: Điều phối & Xử lý Sự cố xe | TV4 — Tổng hợp danh sách vấn đề mở (`open_issues.md`) | 100% |
| 5 | Dương Đăng Khoa | 2411589 | SS5: Lập lịch Sạc Thông minh | TV5 — Chính sách sạc, công suất 150kW & hợp đồng phiên sạc | 100% |
| 6 | Hoàng Văn Tấn | 2213074 | SS6: Mô phỏng What-if Nhu cầu | TV6 — Tổng hợp Ma trận Truy vết 17 Use Case & Danh mục Test | 100% |
| 7 | Nguyễn Trung Nguyên | 2011710 | SS7: Mô phỏng What-if Hạ tầng | TV7 — Tổng hợp Deployment View hiện tại | 100% |

---

## DANH MỤC HÌNH ẢNH VÀ SƠ ĐỒ THIẾT KẾ

| Ký hiệu | Tên hình ảnh / Sơ đồ | File nguồn & Ảnh xuất | Vị trí |
| :--- | :--- | :--- | :--- |
| **Hình 2.1** | Sơ đồ Triển khai Hệ thống hiện tại (Deployment View — do TV7 tổng hợp) | `docs/diagrams/submission_3/shared/deployment.puml` (`.png` / `.svg`) | Mục 2 |
| **Hình 3.1** | Sơ đồ Cấu trúc Tầng & Module Hệ thống (Implementation View — do TV3 tổng hợp) | `docs/diagrams/submission_3/shared/implementation.puml` (`.png` / `.svg`) | Mục 3 |
| **Hình 4.1** | Sơ đồ Lớp Cấp Hệ thống (System-level Class Diagram — do TV3 tổng hợp) | `docs/diagrams/submission_3/shared/system_classes.puml` (`.png` / `.svg`) | Mục 4.1 |
| **Hình 4.2** | Sơ đồ Lớp Chi tiết Phân hệ SS3 (SS3 Class Diagram — do TV3 thiết kế) | `docs/diagrams/submission_3/SS3/class_diagram.puml` (`.png` / `.svg`) | Mục 4.2 |

---

## MỤC LỤC BÁO CÁO

- **Mục 1:** Phạm vi và đóng góp cá nhân
- **Mục 2:** Deployment View (Góc nhìn Triển khai)
- **Mục 3:** Development / Implementation View (Góc nhìn Cấu trúc Module)
- **Mục 4:** Class Diagram Cấp Hệ thống và Phân hệ SS3
- **Mục 5:** Mô tả chi tiết Lớp (Class Descriptions)
- **Mục 6:** Mô tả chi tiết Phương thức (Method Descriptions)
- **Mục 7:** Bảng ma trận truy vết (Traceability Matrix)
- **Mục 8:** Danh mục Test Case Bonus & Kết quả Kiểm thử thực tế
- **Mục 9:** Giới hạn và Quyết định Thiết kế
- **Mục 10:** Tự kiểm tra và Khai báo sử dụng AI
- **Mục 11:** Đầu ra bàn giao Submission 3

---

## 1. Phạm vi và đóng góp cá nhân

### 1.1. Phạm vi Use Case phụ trách
Phân hệ SS3 chịu trách nhiệm kế thừa và đặc tả thiết kế hướng đối tượng cho 2 Use Case cốt lõi từ Submission 2:
1. **`UC_SS3_01` — Giám sát mạng lưới Hub, KPI & Doanh thu thời gian thực (Real-time Hub Network, KPI & Revenue Monitoring):**
   - *Yêu cầu truy vết:* **US-07** (Thống kê doanh thu & phân tích vận hành), **US-12** (Giám sát phụ tải trạm sạc & biểu phí), **US-13**, **US-14** (Giám sát trạng thái xe & chỗ đỗ toàn mạng lưới), **FR-05**, **FR-06**, **FR-15b**.
   - *Mục tiêu:* Cung cấp Dashboard trung tâm cho Nhân viên vận hành (Operator), Quản trị viên (Admin) và Kỹ thuật viên (Technician) theo dõi tức thời số lượng xe hiện hữu, tỷ lệ lấp đầy mạng lưới, số chỗ đỗ trống, số trụ sạc đang hoạt động, công suất tiêu thụ so với trần an toàn $150.0\text{ kW}$, bản đồ tọa độ 6 Hub và báo cáo doanh thu thực thu từ sổ cái (`wallet["ledger"]`), tách biệt minh bạch giữa doanh thu đã quyết toán, tiền cọc đang tạm giữ và công nợ chưa thu.
2. **`UC_SS3_02` — Cảnh báo phân cấp chiếm dụng Hub & Sự cố IoT (Multi-level Hub Occupancy & IoT Fault Alerts):**
   - *Yêu cầu truy vết:* **US-13b** (Cảnh báo sớm chiếm dụng cao & cấu hình ngưỡng), **FR-05c** (Phân cấp cảnh báo tự động & khóa nhận đặt chỗ).
   - *Mục tiêu:* Tự động đánh giá tỷ lệ chiếm dụng chỗ đỗ của từng Hub theo 4 ngưỡng chuẩn hóa (`NORMAL` $< 70\%$, `WARNING` $70\% \le \text{occ} < 85\%$, `CRITICAL` $85\% \le \text{occ} < 100\%$, `FULL` $= 100\%$); phát cảnh báo điều phối xe sang phân hệ SS4 khi chạm ngưỡng $85\%$; tự động khóa tiếp nhận đặt chỗ mới ở SS1/SS2 khi chạm $100\%$ và hỗ trợ cơ chế khóa thủ công / ghi nhận bảo trì khi cảm biến IoT báo lỗi.

### 1.2. Đóng góp cá nhân và vai trò trong nhóm
- **Thiết kế chi tiết SS3:** Xây dựng mô hình lớp hướng đối tượng, phân định rõ ranh giới giữa tầng giao diện (`HubMonitorUI`), tầng dịch vụ nghiệp vụ (`MonitoringService`), các thực thể miền (`Hub`, `Alert`) và các Value Object bất biến (`NetworkSnapshot`, `OccupancySnapshot`, `RevenueReport`).
- **Chủ trì Mô hình & Hợp đồng dùng chung liên phân hệ:**
  - Thiết kế và chuẩn hóa lớp thực thể **`Hub`** dùng chung cho toàn bộ 7 phân hệ, chốt công thức bất biến bảo toàn sức chứa chỗ đỗ (`validate_capacity_invariant`).
  - Thiết kế cấu trúc `RevenueReport` bảo đảm nguyên tắc tài chính: chỉ ghi nhận các khoản phí đã thực thu (`SETTLE_RENTAL_FEE`, `SETTLE_RENTAL_DEBT`, phí đỗ/sạc SS2/SS5, `PENALTY_NOSHOW`), không cộng tiền cọc đang giữ (`HOLD_DEPOSIT`) hay dư nợ (`debt`) vào doanh thu.
  - Chuẩn hóa chữ ký hợp đồng **`INT-03`** (`MonitoringService.get_network_snapshot() -> OperationResult[NetworkSnapshot]`) theo [GUIDANCE_FOR_SUB_3.md](../../../../GUIDANCE_FOR_SUB_3.md).
- **Trách nhiệm nhóm chung (TV3):**
  - Trực tiếp thiết kế và tổng hợp **Development / Implementation View** cấp hệ thống tại [`docs/diagrams/submission_3/shared/implementation.puml`](../../../diagrams/submission_3/shared/implementation.puml).
  - Trực tiếp tổng hợp **System-level Class Diagram** liên kết toàn bộ 7 phân hệ (SS1–SS7) tại [`docs/diagrams/submission_3/shared/system_classes.puml`](../../../diagrams/submission_3/shared/system_classes.puml).

---

## 2. Deployment View (Góc nhìn Triển khai)

Sơ đồ triển khai chung của hệ thống nguyên mẫu trong mối quan hệ giữa trình duyệt máy trạm và tiến trình máy chủ ứng dụng Python/Streamlit:

![Deployment View Shared](../../../diagrams/submission_3/shared/deployment.png)

*(File nguồn PlantUML dùng chung do TV7 tổng hợp: [docs/diagrams/submission_3/shared/deployment.puml](../../../diagrams/submission_3/shared/deployment.puml))*

### 2.1. Vị trí phân hệ SS3 trong kiến trúc triển khai
- **Môi trường chạy:** Ứng dụng nguyên mẫu đơn tiến trình (In-Process Modular Monolith) chạy trên nền tảng **Python 3.12+ / Streamlit Framework**. Người vận hành, Quản trị viên và Kỹ thuật viên tương tác qua trình duyệt web hiện đại (`HTTP / WebSocket`).
- **Thành phần thực thi SS3:**
  - Module [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py) chạy trực tiếp trong tiến trình Streamlit Server Worker khi mục `"3️⃣ Giám sát Hub (Operator)"` trên thanh điều hướng của [`src/app.py`](../../../../src/app.py) được chọn.
  - Toàn bộ phép tính KPI toàn mạng, kiểm tra ngưỡng cảnh báo 4 cấp, tổng hợp sổ cái doanh thu và dựng biểu đồ/bản đồ chạy in-memory trên cùng tiến trình CPU, không phụ thuộc vào cơ sở dữ liệu ngoài hay message broker.

```text
+-------------------------------------------------------------------------+
| Client Tier (Web Browser: Operator / Admin / Technician)                |
| - Chrome / Edge / Firefox (HTML5 / Streamlit Metrics / Map / Tables)    |
+-------------------------------------------------------------------------+
                                   │ HTTP / WebSocket (Port 8501)
                                   ▼
+-------------------------------------------------------------------------+
| Application Server (Python / Streamlit Single Process)                  |
| +---------------------------------------------------------------------+ |
| | Entry Point: src/app.py (init_session_state, sweep expired holds)   | |
| +---------------------------------------------------------------------+ |
| | Presentation Layer: src/components/hub_monitor.py (HubMonitorUI)    | |
| +---------------------------------------------------------------------+ |
| | Service Layer (Sub3 Design): MonitoringService (INT-03)             | |
| +---------------------------------------------------------------------+ |
| | Core Domain & Policy Layer:                                         | |
| | - src/core/policies.py (OCCUPANCY_WARNING=70, CRITICAL=85, FULL=100)| |
| | - src/core/state.py (validate_hub_capacity, load_and_normalize_hubs)| |
| | - src/core/billing.py (Wallet Ledger & Realized Revenue rules)      | |
| +---------------------------------------------------------------------+ |
| | In-Memory Session State (st.session_state)                          | |
| | - hubs (Dữ liệu 6 Hub vận hành hiện hành)                           | |
| | - wallet (balance, held_deposit, debt, ledger[])                    | |
| | - bookings[], personal_reservations[], state_version                | |
| +---------------------------------------------------------------------+ |
+-------------------------------------------------------------------------+
```

### 2.2. Vòng đời dữ liệu và Ranh giới triển khai Telemetry
- **Đồng bộ tức thời theo phiên (`st.session_state`):** Khi các phân hệ SS1/SS2 thực hiện đặt/nhận/trả xe, SS4 điều chuyển xe/báo hỏng, SS5 cấp phát công suất sạc hoặc SS6/SS7 cam kết (`Apply`) kịch bản mô phỏng vào `st.session_state["hubs"]` và tăng `state_version`, Dashboard của SS3 tự động phản ánh trạng thái mới ngay ở chu kỳ `st.rerun()` tiếp theo hoặc khi Operator nhấn nút `"🔄 Cập nhật Telemetry"`.
- **Giới hạn hiện tại của nguyên mẫu:** Chưa kết nối phần cứng cảm biến IoT vật lý qua MQTT; trạng thái lỗi IoT trên UI hiện được suy dẫn từ bộ đếm cổng sạc bị ngắt (`charging_ports["offline"] > 0`) và được chuẩn hóa thành cơ chế `cached_network_snapshot` trong tầng `MonitoringService`.

---

## 3. Development / Implementation View (Góc nhìn Cấu trúc Module)

Sơ đồ cấu trúc phân tầng và phụ thuộc module cấp hệ thống (do TV3 chủ trì tổng hợp):

![Implementation View Shared](../../../diagrams/submission_3/shared/implementation.png)

*(File nguồn PlantUML: [docs/diagrams/submission_3/shared/implementation.puml](../../../diagrams/submission_3/shared/implementation.puml))*

```text
[Presentation Layer]
   │  src/app.py ──> src/components/hub_monitor.py (render, KPI, Alerts, Revenue, Power, IoT)
   ▼
[Business Service & Coordination Layer]
   │  MonitoringService (get_network_snapshot [INT-03], evaluate_hub_alerts, generate_revenue_report)
   │    ├──> BillingService (Đọc sổ cái giao dịch đã quyết toán — TV1)
   │    ├──> ChargingService (Đối chiếu hóa đơn sạc INT-02 — TV5)
   │    └──> ForecastService (Tham chiếu dự báo nhu cầu 24h INT-04 — TV6)
   ▼
[Core Engine, Policies & State Management Layer]
   │  src/core/policies.py (get_occupancy_level, OCCUPANCY_* thresholds, HUB_POWER_CAP_KW = 150.0)
   │  src/core/state.py (validate_hub_capacity, validate_state_invariants, st.session_state["hubs"])
   │  src/core/billing.py (st.session_state["wallet"]["ledger"])
```

### 3.1. Ánh xạ mã nguồn thực tế
1. **Tầng Trình diễn (Presentation):**
   - File [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py): Đảm nhận vẽ toàn bộ Dashboard SS3 gồm: cảnh báo cổng sạc IoT offline (dòng 33–36), 4 thẻ KPI toàn mạng lưới (dòng 45–64), hệ thống cảnh báo sớm 3 cột Vàng / Đỏ / Đầy 100% (dòng 69–101), bản đồ tọa độ 6 Hub & bảng chi tiết sức chứa (dòng 105–127), cùng 2 tab Báo cáo Doanh thu & Sổ cái (dòng 129–150) và Giám sát Năng lượng Sạc (dòng 152–166).
2. **Tầng Nghiệp vụ & Điều phối (Business Service):**
   - Đề xuất chuẩn hóa thành lớp `MonitoringService` cung cấp hợp đồng `INT-03` (`get_network_snapshot`) và các phương thức nghiệp vụ độc lập với Streamlit UI. Trong prototype hiện tại, các phép tính này đang nằm trực tiếp trong hàm `render()` của `hub_monitor.py` và đã được tách thành lớp kiểm thử độc lập tại [`tests/test_ss3_monitoring_bonus.py`](../../../../tests/test_ss3_monitoring_bonus.py).
3. **Tầng Chính sách & Quản lý Trạng thái (Core Policies & State):**
   - File [`src/core/policies.py`](../../../../src/core/policies.py): Chứa các hằng số ngưỡng `OCCUPANCY_WARNING_MIN = 70.0`, `OCCUPANCY_CRITICAL_MIN = 85.0`, `OCCUPANCY_FULL_MIN = 100.0`, `HUB_POWER_CAP_KW = 150.0` và hàm `get_occupancy_level()` (dòng 24–38, 67–68).
   - File [`src/core/state.py`](../../../../src/core/state.py): Cung cấp hàm `load_and_normalize_hubs()` (dòng 53–75) và `validate_hub_capacity()` (dòng 78–89) bảo đảm công thức bảo toàn chỗ đỗ tại mọi Hub.
   - File [`src/core/billing.py`](../../../../src/core/billing.py): Quản lý sổ cái `wallet["ledger"]` với các loại giao dịch chuẩn (`HOLD_DEPOSIT`, `SETTLE_RENTAL_FEE`, `SETTLE_RENTAL_DEBT`, `PENALTY_NOSHOW`, `REFUND_DEPOSIT_FULL`).

---

## 4. Class Diagram Cấp Hệ thống và Phân hệ SS3

### 4.1. Sơ đồ Lớp Cấp Hệ thống (System-level Class Diagram — do TV3 tổng hợp)

![System-level Class Diagram](../../../diagrams/submission_3/shared/system_classes.png)

*(File nguồn PlantUML: [docs/diagrams/submission_3/shared/system_classes.puml](../../../diagrams/submission_3/shared/system_classes.puml))*

### 4.2. Sơ đồ Lớp Chi tiết Phân hệ SS3 (SS3 Class Diagram)

![Class Diagram SS3](../../../diagrams/submission_3/SS3/class_diagram.png)

*(File nguồn PlantUML: [docs/diagrams/submission_3/SS3/class_diagram.puml](../../../diagrams/submission_3/SS3/class_diagram.puml))*

### Phân tích kiến trúc sơ đồ SS3:
- **`HubMonitorUI`** là lớp ranh giới (Boundary) tiếp nhận thao tác từ Operator / Admin / Kỹ thuật viên và hiển thị các thành phần trực quan dựa trên dữ liệu chụp từ tầng dịch vụ.
- **`MonitoringService`** đóng vai trò dịch vụ trung tâm của SS3, thực thi hợp đồng `INT-03`, đánh giá cảnh báo 4 cấp, tổng hợp doanh thu thực thu từ sổ cái và đồng bộ cờ khóa đặt chỗ (`is_locked`).
- **`Hub`** là lớp thực thể cốt lõi dùng chung toàn hệ thống do TV3 sở hữu, đóng gói trạng thái vật lý và phương thức tự kiểm tra bất biến sức chứa (`validate_capacity_invariant`).
- Mô hình tách biệt rõ giữa **Entity có vòng đời** (`Hub`, `Alert`) và các **Value Object bất biến chỉ đọc** (`NetworkSnapshot`, `OccupancySnapshot`, `RevenueReport`), ngăn chặn việc giao diện vô tình làm đột biến dữ liệu vận hành gốc.

---

## 5. Mô tả chi tiết Lớp (Class Descriptions)

Tuân thủ quy chuẩn mẫu bảng Mục 6.1 của GUIDANCE:

### 5.1. `SS3-CLS-01`: `Hub`
- **Tên lớp:** `Hub` (Entity — Lớp chuẩn dùng chung toàn hệ thống do TV3 sở hữu)
- **Trách nhiệm:** Đại diện cho một trạm trung chuyển phương tiện điện trong khu đô thị ĐHQG-HCM; quản lý sức chứa chỗ đỗ, các thành phần chiếm dụng chỗ, trụ sạc, phụ tải điện năng và trạng thái khóa/cảm biến. Các phân hệ SS1, SS2, SS4, SS5, SS6, SS7 tham chiếu trực tiếp lớp `Hub` này.
- **Mức triển khai:** Đã có trong mã nguồn (ánh xạ từ cấu trúc từ điển `st.session_state["hubs"]` trong `src/data/mock_hubs.json` và `src/core/state.py`).
- **Thuộc tính:**
  - `hub_id` (`str`): Mã định danh duy nhất của trạm (ví dụ: `"HUB-001"` đến `"HUB-006"`).
  - `name` (`str`): Tên hiển thị của trạm (ví dụ: `"Hub KTX Khu A"`).
  - `latitude` (`float`), `longitude` (`float`): Tọa độ GPS của trạm (đơn vị: độ thập phân).
  - `capacity` (`int`): Tổng sức chứa chỗ đỗ tối đa của trạm (ánh xạ khóa `total_slots`, đơn vị: chỗ, $> 0$).
  - `available_slots` (`int`): Số chỗ đỗ đang trống có thể nhận đặt mới (đơn vị: chỗ, $\ge 0$).
  - `present_vehicles_count` (`int`): Số xe (cả xe dùng chung và xe cá nhân) đang đỗ thực tế tại trạm (`status != "IN_USE"`, đơn vị: xe).
  - `incoming_reserved_count` (`int`): Số chỗ đang phong tỏa cho xe đặt trước hướng tới trạm (ánh xạ khóa `destination_holds`, đơn vị: chỗ).
  - `background_load_count` (`int`): Tải nền chiếm dụng chỗ đỗ (ánh xạ khóa `background_occupied`, đơn vị: chỗ).
  - `total_ports` (`int`), `active_ports_count` (`int`): Tổng số cổng sạc và số cổng đang hoạt động/bận (đơn vị: cổng).
  - `max_power_kw` (`float`): Công suất điện trần an toàn của trạm (mặc định: $150.0\text{ kW}$).
  - `current_load_kw` (`float`): Tổng công suất điện năng đang tiêu thụ tại trạm (đơn vị: $\text{kW}$).
  - `is_locked` (`bool`): Cờ khóa tiếp nhận đặt chỗ mới khi trạm đầy $100\%$ hoặc bị khóa thủ công.
  - `iot_online` (`bool`): Trạng thái kết nối telemetry cảm biến IoT tại trạm.
- **Quan hệ:** Liên kết `1 - 1..*` với `OccupancySnapshot`; `1 - 0..*` với `Alert`; kết tập `1 - 0..*` với `ChargingPort` (SS5); được tham chiếu bởi `Booking` (SS1), `ParkingReservation` (SS2), `DispatchOrder` (SS4), `RouteSuggestion` (SS7).
- **Ràng buộc (Invariants):**
  1. Bảo toàn sức chứa: $\text{available\_slots} + \text{present\_vehicles\_count} + \text{incoming\_reserved\_count} + \text{background\_load\_count} == \text{capacity}$ (Không cộng trùng một xe hai lần).
  2. Độc lập tài nguyên: Sự cố hỏng cổng sạc chỉ làm giảm số cổng khả dụng, **không** làm thay đổi `capacity` hay `available_slots` đỗ xe.

---

### 5.2. `SS3-CLS-02`: `OccupancySnapshot`
- **Tên lớp:** `OccupancySnapshot` (Value Object)
- **Trách nhiệm:** Bản ghi bất biến chụp lại các chỉ số chiếm dụng chỗ đỗ, tỷ lệ sử dụng cổng sạc và công suất tiêu thụ điện của một `Hub` tại một thời điểm xác định.
- **Mức triển khai:** Thiết kế đề xuất (chuẩn hóa từ cấu trúc `hub_table_data` và `power_data` trong `src/components/hub_monitor.py`).
- **Thuộc tính:**
  - `snapshot_id` (`str`): Mã định danh bản chụp.
  - `hub_id` (`str`): Mã Hub được chụp trạng thái.
  - `captured_at` (`datetime`): Thời điểm ghi nhận dữ liệu (UTC+7).
  - `capacity` (`int`), `present_vehicles` (`int`), `incoming_reserved` (`int`), `background_load` (`int`), `available_slots` (`int`): Các thông số chỗ đỗ (đơn vị: chỗ/xe).
  - `occupancy_rate_pct` (`float`): Tỷ lệ chiếm dụng chỗ đỗ ($0.0..100.0$, đơn vị: $\%$).
  - `occupancy_level` (`OccupancyLevel`): Phân cấp mức chiếm dụng (`NORMAL`, `WARNING`, `CRITICAL`, `FULL`).
  - `active_ports` (`int`), `total_ports` (`int`): Số cổng đang sạc và tổng số cổng (đơn vị: cổng).
  - `port_utilization_pct` (`float`): Tỷ lệ bận của cổng sạc ($0.0..100.0$, đơn vị: $\%$).
  - `current_power_kw` (`float`), `max_power_kw` (`float`): Công suất hiện tại và công suất trần (đơn vị: $\text{kW}$).
  - `is_locked` (`bool`): Trạng thái khóa tiếp nhận đặt chỗ tại thời điểm chụp.
- **Quan hệ:** Là thành phần cấu tạo (Composition `1..*`) bên trong `NetworkSnapshot`; tham chiếu `1` `Hub`.
- **Ràng buộc:** Phân biệt rõ 3 tỷ lệ độc lập: `occupancy_rate_pct` (chỗ đỗ), `port_utilization_pct` (cổng sạc) và tỷ lệ tải công suất điện ($\text{current\_power\_kw} / \text{max\_power\_kw}$).

---

### 5.3. `SS3-CLS-03`: `RevenueReport`
- **Tên lớp:** `RevenueReport` (Value Object do TV3 sở hữu theo Mục 5.3 GUIDANCE)
- **Trách nhiệm:** Tổng hợp và phân tách minh bạch giữa doanh thu thực thu từ các giao dịch đã quyết toán với tiền cọc đang tạm giữ, tiền hoàn trả và công nợ người dùng.
- **Mức triển khai:** Đã có một phần trong mã nguồn (ánh xạ từ logic lọc `wallet["ledger"]` tại tab `tab_rev` của `hub_monitor.py`) và mở rộng đề xuất để gộp đủ doanh thu SS2/SS5.
- **Thuộc tính:**
  - `report_id` (`str`): Mã báo cáo doanh thu.
  - `generated_at` (`datetime`): Thời điểm tổng hợp báo cáo.
  - `hub_id` (`Optional[str]`): Mã Hub cụ thể hoặc `None` nếu là báo cáo toàn mạng lưới.
  - `settled_rental_fee_vnd` (`int`): Phí thuê xe dùng chung SS1 đã thực thu (`SETTLE_RENTAL_FEE`, `SETTLE_RENTAL_DEBT`, đơn vị: VNĐ).
  - `settled_parking_fee_vnd` (`int`): Phí đỗ xe cá nhân SS2 đã thực thu (đơn vị: VNĐ).
  - `settled_charging_fee_vnd` (`int`): Phí điện năng sạc và phí quá giờ chiếm dụng trụ sạc SS5 đã thực thu (`CHARGING_FEE`, `OVERSTAY_FEE`, `OVERSTAY_PARTIAL`, đơn vị: VNĐ).
  - `settled_penalty_fee_vnd` (`int`): Phí phạt quá hạn 30 phút không nhận xe (`PENALTY_NOSHOW`, `PENALTY_PEV_NOSHOW`, đơn vị: VNĐ).
  - `total_realized_revenue_vnd` (`int`): Tổng doanh thu thực thu = tổng 4 khoản phí đã quyết toán ở trên (đơn vị: VNĐ).
  - `held_deposit_vnd` (`int`): Tổng tiền cọc đang tạm giữ ($50.000\text{ VNĐ/lượt}$ đang hoạt động, đơn vị: VNĐ).
  - `refunded_amount_vnd` (`int`): Tổng tiền cọc đã hoàn trả về ví người dùng (đơn vị: VNĐ).
  - `outstanding_debt_vnd` (`int`): Tổng dư nợ chưa thu của người dùng (`wallet["debt"]`, đơn vị: VNĐ).
- **Quan hệ:** Là thành phần cấu tạo (Composition `1..1`) bên trong `NetworkSnapshot`.
- **Ràng buộc:** Mọi trường tiền tệ là số nguyên không âm ($\ge 0$). Tuyệt đối **không** cộng `held_deposit_vnd` hoặc `outstanding_debt_vnd` vào `total_realized_revenue_vnd`.

---

### 5.4. `SS3-CLS-04`: `Alert`
- **Tên lớp:** `Alert` (Entity)
- **Trách nhiệm:** Biểu diễn một sự kiện cảnh báo vận hành phát sinh tại Hub (ngưỡng chiếm dụng cao, mất kết nối cảm biến IoT, lỗi phần cứng trụ sạc hoặc lỗi đồng bộ khóa trạm).
- **Mức triển khai:** Thiết kế đề xuất (chuẩn hóa từ các danh sách cảnh báo `yellow_hubs`, `red_hubs`, `full_hubs` và `iot_offline_alerts` trong `src/components/hub_monitor.py`).
- **Thuộc tính:**
  - `alert_id` (`str`): Mã định danh cảnh báo.
  - `hub_id` (`str`): Mã Hub phát sinh cảnh báo.
  - `alert_type` (`AlertType`): Loại cảnh báo (`OCCUPANCY_THRESHOLD`, `IOT_SENSOR_TIMEOUT`, `IOT_HARDWARE_FAULT`, `LOCK_SYNC_FAILURE`).
  - `severity` (`AlertSeverity`): Mức độ nghiêm trọng (`INFO`, `WARNING`, `CRITICAL`, `EMERGENCY`).
  - `occupancy_level` (`Optional[OccupancyLevel]`): Mức chiếm dụng đi kèm (nếu là cảnh báo sức chứa).
  - `message` (`str`): Nội dung thông điệp cảnh báo hoặc ghi chú phương án bảo trì.
  - `created_at` (`datetime`): Thời điểm phát sinh cảnh báo.
  - `acknowledged_by` (`Optional[str]`), `acknowledged_at` (`Optional[datetime]`): Mã nhân sự và thời điểm xác nhận xử lý.
  - `is_resolved` (`bool`): Trạng thái đã khắc phục xong sự cố/cảnh báo.
- **Quan hệ:** Tham chiếu `1` `Hub`; được tập hợp (Aggregation `0..*`) bên trong `NetworkSnapshot`.
- **Ràng buộc:** Khi `acknowledged_by != None` thì `acknowledged_at != None`; không ghi đè người xác nhận đầu tiên khi có thao tác bấm xác nhận trùng lặp.

---

### 5.5. `SS3-CLS-05`: `NetworkSnapshot`
- **Tên lớp:** `NetworkSnapshot` (Value Object — Hợp đồng `INT-03`)
- **Trách nhiệm:** Đóng gói toàn bộ bức tranh vận hành mạng lưới Hub tại một phiên bản `state_version`, bao gồm KPI toàn mạng, cờ dữ liệu cache, danh sách `OccupancySnapshot` của 6 Hub, `RevenueReport` và danh sách `Alert` đang hoạt động.
- **Mức triển khai:** Thiết kế đề xuất chuẩn hóa theo hợp đồng mục 2.3 (`INT-03`).
- **Thuộc tính:**
  - `captured_at` (`datetime`): Thời điểm chụp trạng thái toàn mạng lưới.
  - `state_version` (`int`): Phiên bản trạng thái hệ thống tại thời điểm chụp ($\ge 1$).
  - `total_active_vehicles` (`int`): Tổng số phương tiện hiện có trên toàn hệ thống (đơn vị: xe).
  - `network_occupancy_pct` (`float`): Tỷ lệ chiếm dụng chỗ đỗ trung bình toàn mạng lưới ($0.0..100.0$, đơn vị: $\%$).
  - `is_using_cached_data` (`bool`): `True` nếu đang trả về bản chụp từ bộ nhớ đệm do mất kết nối cảm biến IoT.
  - `occupancy_snapshots` (`List[OccupancySnapshot]`): Danh sách bản chụp chi tiết của từng Hub.
  - `revenue_summary` (`RevenueReport`): Báo cáo tổng hợp doanh thu thực thu và sổ cái.
  - `active_alerts` (`List[Alert]`): Danh sách các cảnh báo chưa được giải quyết.
- **Quan hệ:** Chứa `1..*` `OccupancySnapshot`, `1` `RevenueReport` và `0..*` `Alert`. Được trả về bởi `MonitoringService.get_network_snapshot()`.

---

### 5.6. `SS3-CLS-06`: `MonitoringService` & `SS3-CLS-07`: `HubMonitorUI`
- **Tên lớp:** `MonitoringService` (Service) & `HubMonitorUI` (Boundary)
- **Trách nhiệm:**
  - `HubMonitorUI`: Lớp ranh giới giao diện Streamlit (`src/components/hub_monitor.py`), điều khiển việc hiển thị các thẻ KPI, bản đồ, bảng trạng thái, báo cáo doanh thu và nhật ký IoT.
  - `MonitoringService`: Dịch vụ nghiệp vụ điều phối toàn bộ hoạt động giám sát mạng lưới, tính toán chiếm dụng, tổng hợp doanh thu thực thu từ sổ cái, phát cảnh báo phân cấp, đồng bộ khóa đặt chỗ với SS1/SS2 và quản lý bảo trì IoT.
- **Mức triển khai:** `HubMonitorUI` đã triển khai trong `src/components/hub_monitor.py`; `MonitoringService` là thiết kế đề xuất tách tầng Service (đã hiện thực hóa và kiểm thử trong `tests/test_ss3_monitoring_bonus.py`).
- **Thuộc tính (`MonitoringService`):**
  - `warning_threshold_pct` (`float`): Ngưỡng cảnh báo sớm màu vàng (mặc định: $70.0\%$).
  - `critical_threshold_pct` (`float`): Ngưỡng cảnh báo nguy cơ quá tải màu đỏ (mặc định: $85.0\%$).
  - `full_threshold_pct` (`float`): Ngưỡng đầy trạm khóa nhận đặt chỗ mới (mặc định: $100.0\%$).
- **Ràng buộc:** $0.0 < \text{warning\_threshold\_pct} < \text{critical\_threshold\_pct} < \text{full\_threshold\_pct} \le 100.0$. `MonitoringService` chỉ đọc sổ cái tài chính, không tự ý sửa số dư ví hay thay đổi trạng thái `Booking`.

---

## 6. Mô tả chi tiết Phương thức (Method Descriptions)

Tuân thủ quy chuẩn mẫu bảng Mục 6.2 của GUIDANCE cho toàn bộ phương thức xuất hiện trên Class Diagram:

### 6.1. `SS3-MTH-01`: `Hub.calculate_occupancy_rate`
- **Chữ ký:**
  ```python
  calculate_occupancy_rate(self) -> float
  ```
- **Mục đích và bên gọi:** Tính tỷ lệ phần trăm chiếm dụng chỗ đỗ hiện tại của một Hub; được gọi bởi `Hub.get_occupancy_level()` và `MonitoringService.calculate_hub_occupancy()`.
- **Tham số:** Không có (đọc trực tiếp `self.capacity` và `self.available_slots`).
- **Kết quả trả về:** `float` trong khoảng $[0.0, 100.0]$ (đơn vị: $\%$).
- **Tiền điều kiện:** `self.capacity > 0` và bất biến sức chứa hợp lệ.
- **Các bước xử lý:** Tính số chỗ đang bị chiếm dụng `occupied = self.capacity - self.available_slots`, sau đó trả về `round((occupied / self.capacity) * 100.0, 4)`.
- **Hậu điều kiện:** Không làm thay đổi trạng thái của `Hub` (Read-only).
- **Lỗi / Ngoại lệ:** Ném `ValueError("INVALID_INPUT")` nếu `self.capacity <= 0`.
- **Truy vết:** `UC_SS3_01`, `UC_SS3_02`, Code: [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py) (dòng 55, 76).

---

### 6.2. `SS3-MTH-02`: `Hub.get_occupancy_level`
- **Chữ ký:**
  ```python
  get_occupancy_level(self) -> OccupancyLevel
  ```
- **Mục đích và bên gọi:** Phân loại mức độ chiếm dụng chỗ đỗ của Hub theo 4 ngưỡng chính sách chuẩn; được gọi bởi `MonitoringService`.
- **Tham số:** Không có.
- **Kết quả trả về:** Enum `OccupancyLevel` (`NORMAL`, `WARNING`, `CRITICAL`, `FULL`).
- **Tiền điều kiện:** `self.capacity > 0`.
- **Các bước xử lý:**
  1. Gọi `rate = self.calculate_occupancy_rate()`.
  2. Đối chiếu với các ngưỡng chuẩn tại `src/core/policies.py`:
     - $\text{rate} < 70.0 \rightarrow$ `OccupancyLevel.NORMAL`.
     - $70.0 \le \text{rate} < 85.0 \rightarrow$ `OccupancyLevel.WARNING` (Màu vàng).
     - $85.0 \le \text{rate} < 100.0 \rightarrow$ `OccupancyLevel.CRITICAL` (Màu đỏ nhấp nháy).
     - $\text{rate} \ge 100.0$ hoặc $\text{self.available\_slots} == 0 \rightarrow$ `OccupancyLevel.FULL` (Khóa Đỏ).
- **Hậu điều kiện:** Trạng thái `Hub` giữ nguyên $100\%$.
- **Truy vết:** `UC_SS3_02`, Code: [`src/core/policies.py`](../../../../src/core/policies.py) (dòng 30–38).

---

### 6.3. `SS3-MTH-03`: `Hub.validate_capacity_invariant`
- **Chữ ký:**
  ```python
  validate_capacity_invariant(self) -> bool
  ```
- **Mục đích và bên gọi:** Kiểm tra tính bảo toàn sức chứa chỗ đỗ của Hub nhằm ngăn chặn lỗi cộng trùng xe; được gọi bởi `MonitoringService.calculate_hub_occupancy()`.
- **Kết quả trả về:** `bool` (`True` nếu hợp lệ, `False` nếu vi phạm bất biến).
- **Các bước xử lý:** Kiểm tra mọi bộ đếm không âm và `self.available_slots + self.present_vehicles_count + self.incoming_reserved_count + self.background_load_count == self.capacity`.
- **Truy vết:** `UC_SS3_01`, Code: [`src/core/state.py`](../../../../src/core/state.py) (`validate_hub_capacity`, dòng 78–89).

---

### 6.4. `SS3-MTH-04`: `Alert.acknowledge`
- **Chữ ký:**
  ```python
  acknowledge(
      self,
      user_id: str,
      now: datetime
  ) -> bool
  ```
- **Mục đích và bên gọi:** Ghi nhận nhân sự vận hành hoặc kỹ thuật viên đã tiếp nhận xử lý cảnh báo; được gọi bởi `MonitoringService`.
- **Tham số:** `user_id` (`str`), `now` (`datetime` theo giờ mô phỏng UTC+7).
- **Kết quả trả về:** `bool` (`True` nếu xác nhận lần đầu thành công, `False` nếu `user_id` rỗng hoặc cảnh báo đã được xác nhận trước đó).
- **Truy vết:** `UC_SS3_01` (Alt 1), `UC_SS3_02` (Alt 1).

---

### 6.5. `SS3-MTH-05`: `MonitoringService.get_network_snapshot`
- **Chữ ký:**
  ```python
  get_network_snapshot(self) -> OperationResult[NetworkSnapshot]
  ```
- **Mục đích và bên gọi:** Thu thập bức tranh tổng thể toàn mạng lưới Hub, các chỉ số KPI, báo cáo doanh thu thực thu và danh sách cảnh báo hiện hành; được gọi bởi `HubMonitorUI` hoặc các phân hệ khác theo hợp đồng giao tiếp **`INT-03`**.
- **Tham số:** Không có (ẩn `st.session_state` qua tầng adapter).
- **Kết quả trả về:** `OperationResult[NetworkSnapshot]`.
- **Tiền điều kiện:** Danh mục `hubs` trong `st.session_state` đã được khởi tạo.
- **Các bước xử lý:**
  1. Kiểm tra danh sách Hub; nếu rỗng trả về `OperationResult(ok=False, error_code="NOT_FOUND")`.
  2. Kiểm tra kết nối cảm biến `iot_online` của các trạm. Nếu phát hiện trạm mất kết nối (Exception 1 của `UC_SS3_01`), sinh cảnh báo `IOT_SENSOR_TIMEOUT` với thông điệp `"Cảnh báo: Dữ liệu thời gian thực đang bị gián đoạn"` và trả về bản `cached_network_snapshot` gần nhất kèm cờ `is_using_cached_data = True`.
  3. Duyệt qua toàn bộ 6 Hub, gọi `calculate_hub_occupancy(hub_id)` để kiểm tra bất biến sức chứa và tạo danh sách `OccupancySnapshot`.
  4. Gọi `generate_revenue_report()` để tổng hợp báo cáo tài chính thực thu.
  5. Đóng gói vào `NetworkSnapshot` kèm `state_version` hiện tại, cập nhật bộ nhớ đệm `cached_network_snapshot` và trả về kết quả thành công.
- **Hậu điều kiện:** Không làm thay đổi số dư ví, booking hay số chỗ đỗ của bất kỳ trạm nào.
- **Lỗi / Ngoại lệ:** `NOT_FOUND` (chưa khởi tạo trạm), `INVALID_STATE` (vi phạm bảo toàn sức chứa).
- **Truy vết:** Hợp đồng `INT-03`, `UC_SS3_01` (Bước 2–4 Normal Flow & Exception 1), Code: [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py).

---

### 6.6. `SS3-MTH-06`: `MonitoringService.calculate_hub_occupancy`
- **Chữ ký:**
  ```python
  calculate_hub_occupancy(
      self,
      hub_id: str
  ) -> OperationResult[OccupancySnapshot]
  ```
- **Mục đích và bên gọi:** Tính toán bộ chỉ số KPI chiếm dụng chỗ đỗ, tỷ lệ dùng cổng sạc và công suất điện của một Hub cụ thể; được gọi bởi `get_network_snapshot()`.
- **Tham số:** `hub_id` (`str`).
- **Kết quả trả về:** `OperationResult[OccupancySnapshot]`.
- **Các bước xử lý:** Tìm `Hub` theo `hub_id` (trả `NOT_FOUND` nếu không tồn tại); gọi `hub.validate_capacity_invariant()` (trả `INVALID_STATE` nếu sai lệch); tính `occupancy_rate_pct`, `occupancy_level`, `port_utilization_pct` và đóng gói vào `OccupancySnapshot`.
- **Truy vết:** `UC_SS3_01`, `UC_SS3_02`.

---

### 6.7. `SS3-MTH-07`: `MonitoringService.generate_revenue_report`
- **Chữ ký:**
  ```python
  generate_revenue_report(
      self,
      hub_id: Optional[str] = None
  ) -> OperationResult[RevenueReport]
  ```
- **Mục đích và bên gọi:** Tổng hợp báo cáo doanh thu thực thu từ sổ cái giao dịch (`wallet["ledger"]`), tách biệt rõ tiền cọc đang tạm giữ, tiền hoàn trả và công nợ; được gọi bởi `get_network_snapshot()` và tab Doanh thu (`US-07`).
- **Tham số:** `hub_id` (`Optional[str]`, mặc định `None` cho toàn mạng lưới).
- **Kết quả trả về:** `OperationResult[RevenueReport]`.
- **Các bước xử lý:**
  1. Đọc danh sách bút toán từ `wallet["ledger"]` (`BillingService`) và thông tin hóa đơn sạc (`ChargingService.get_bill` qua `INT-02`).
  2. Cộng dồn riêng 4 nhóm phí đã quyết toán thực thu: `settled_rental_fee_vnd`, `settled_parking_fee_vnd`, `settled_charging_fee_vnd`, `settled_penalty_fee_vnd` $\rightarrow$ tính `total_realized_revenue_vnd`.
  3. Tổng hợp độc lập `held_deposit_vnd` (tiền cọc đang tạm giữ), `refunded_amount_vnd` (tiền hoàn) và `outstanding_debt_vnd` (dư nợ).
- **Hậu điều kiện:** Chỉ đọc dữ liệu tài chính, tuyệt đối không ghi đè hay trừ tiền ví.
- **Truy vết:** `US-07`, `UC_SS3_01`, Code: [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py) (dòng 129–137), [`src/core/billing.py`](../../../../src/core/billing.py).

---

### 6.8. `SS3-MTH-08`: `MonitoringService.evaluate_hub_alerts`
- **Chữ ký:**
  ```python
  evaluate_hub_alerts(
      self,
      hub_id: str
  ) -> OperationResult[List[Alert]]
  ```
- **Mục đích và bên gọi:** Đánh giá tỷ lệ chiếm dụng của Hub, sinh cảnh báo đa cấp (`WARNING`, `CRITICAL`, `FULL`), gắn cờ đề xuất điều phối xe sang SS4 khi $\ge 85\%$ và kích hoạt khóa nhận đặt chỗ khi đạt $100\%$.
- **Các bước xử lý:**
  - Nếu `level == NORMAL` ($< 70\%$): Mở khóa tự động nếu trạm đang bị khóa do đầy trước đó.
  - Nếu `level == WARNING` ($70\% \le \text{occ} < 85\%$): Sinh `Alert` mức `WARNING` (Màu vàng).
  - Nếu `level == CRITICAL` ($85\% \le \text{occ} < 100\%$ — Alt 1 `UC_SS3_02`): Sinh `Alert` mức `CRITICAL` (Màu đỏ nhấp nháy) kèm đề xuất điều chuyển xe sang SS4.
  - Nếu `level == FULL` ($\ge 100\%$ — Alt 2 `UC_SS3_02`): Gọi `sync_hub_booking_lock(hub_id, True, operation_key)`. Nếu lỗi đồng bộ session (Exception 1 `UC_SS3_02`), sinh `Alert` loại `LOCK_SYNC_FAILURE` mức `EMERGENCY` yêu cầu Operator khóa thủ công.
- **Truy vết:** `UC_SS3_02`, Code: [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py) (dòng 69–101).

---

### 6.9. `SS3-MTH-09`: `MonitoringService.sync_hub_booking_lock`
- **Chữ ký:**
  ```python
  sync_hub_booking_lock(
      self,
      hub_id: str,
      lock_state: bool,
      operation_key: str
  ) -> OperationResult[bool]
  ```
- **Mục đích và bên gọi:** Đồng bộ cờ khóa nhận đặt chỗ mới (`hub.is_locked`) với phân hệ SS1 và SS2 khi trạm đạt $100\%$ sức chứa.
- **Xử lý lặp & xung đột:** Cùng `operation_key` và cùng `lock_state` trả về kết quả thành công đã lưu mà không tăng `state_version` lần hai (`Idempotent`). Cùng key nhưng khác `lock_state` trả lỗi `CONFLICTING_OPERATION`. Nếu phát hiện lỗi đồng bộ session, trả lỗi `STALE_STATE`.
- **Truy vết:** `UC_SS3_02` (Alt 2 & Exception 1).

---

### 6.10. `SS3-MTH-10`: `MonitoringService.manual_lock_hub`
- **Chữ ký:**
  ```python
  manual_lock_hub(
      self,
      operator_id: str,
      hub_id: str,
      lock_state: bool
  ) -> OperationResult[bool]
  ```
- **Mục đích và bên gọi:** Cho phép Nhân viên vận hành (`OPERATOR`) hoặc `ADMIN` khóa/mở khóa Hub thủ công trên giao diện khi cơ chế khóa tự động gặp sự cố đồng bộ (Exception 1 `UC_SS3_02`).
- **Tiền điều kiện:** Người gọi có quyền `OPERATOR` hoặc `ADMIN` (trả `FORBIDDEN` nếu là `STUDENT`).
- **Truy vết:** `UC_SS3_02` (Exception 1).

---

### 6.11. `SS3-MTH-11`: `MonitoringService.update_alert_thresholds`
- **Chữ ký:**
  ```python
  update_alert_thresholds(
      self,
      admin_id: str,
      warning_pct: float,
      critical_pct: float
  ) -> OperationResult[bool]
  ```
- **Mục đích và bên gọi:** Cho phép Quản trị viên (`ADMIN`) cấu hình ngưỡng cảnh báo sớm và cảnh báo nguy cơ quá tải theo `US-13b` và nhánh `opt [Tài khoản Admin]` của `UC_SS3_01`.
- **Tiền điều kiện:** Người gọi là `ADMIN` (`FORBIDDEN` nếu khác) và $0.0 < \text{warning\_pct} < \text{critical\_pct} < 100.0$ (`INVALID_INPUT` nếu sai khoảng).

---

### 6.12. `SS3-MTH-12`: `MonitoringService.get_iot_error_logs` & `record_iot_maintenance_plan`
- **Chữ ký:**
  ```python
  get_iot_error_logs(self, hub_id: Optional[str] = None) -> OperationResult[List[Alert]]
  record_iot_maintenance_plan(self, tech_id: str, alert_id: str, plan_note: str) -> OperationResult[Alert]
  ```
- **Mục đích và bên gọi:** Hỗ trợ Kỹ thuật viên (`TECHNICIAN`) tra cứu danh sách lỗi cảm biến/trụ sạc IoT và ghi nhận vị trí Hub, loại cảm biến cùng phương án bảo trì (`UC_SS3_01` Bước 5–7 & Alt 1).

---

### 6.13. `SS3-MTH-13`: `HubMonitorUI.render` (và các hàm hiển thị con)
- **Chữ ký:** `render() -> void`, `render_kpi_metrics() -> void`, `render_occupancy_alerts() -> void`, `render_revenue_reports() -> void`, `render_iot_logs() -> void`.
- **Mục đích:** Dựng toàn bộ giao diện giám sát, bản đồ, cảnh báo phân cấp, báo cáo doanh thu và công suất sạc theo mã nguồn dòng 23–166 của [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py).

---

## 7. Bảng ma trận truy vết (Traceability Matrix)

Chi tiết bảng truy vết 2 chiều từ Yêu cầu SRS, Kịch bản Sub 2, Thiết kế Sub 3 đến Mã nguồn và Test case được trình bày chi tiết trong tài liệu:  
👉 **[Bảng truy vết cá nhân SS3 — Phạm Tiến Đạt](traceability.md)**

### Bảng tóm tắt truy vết 2 Use Case cốt lõi:

| Mã UC | Yêu cầu gốc (SRS) | Lớp Sub 3 sở hữu | Phương thức Sub 3 cốt lõi | Mã nguồn hiện có | Test Case ID |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`UC_SS3_01`** | US-07, US-12, US-13, US-14,<br>FR-05, FR-06, FR-15b | `Hub`, `OccupancySnapshot`,<br>`RevenueReport`, `NetworkSnapshot`,<br>`MonitoringService`, `HubMonitorUI` | `get_network_snapshot()` (`SS3-MTH-05`),<br>`calculate_hub_occupancy()` (`SS3-MTH-06`),<br>`generate_revenue_report()` (`SS3-MTH-07`),<br>`validate_capacity_invariant()` (`SS3-MTH-03`) | `src/components/hub_monitor.py`<br>`src/core/state.py`<br>`src/core/billing.py` | `TC-SS3-INV-01`<br>`TC-SS3-REV-01`<br>`TC-SS3-IOT-01` |
| **`UC_SS3_02`** | US-13b, FR-05c | `Hub`, `Alert`,<br>`MonitoringService`, `HubMonitorUI` | `calculate_occupancy_rate()` (`SS3-MTH-01`),<br>`get_occupancy_level()` (`SS3-MTH-02`),<br>`evaluate_hub_alerts()` (`SS3-MTH-08`),<br>`sync_hub_booking_lock()` (`SS3-MTH-09`),<br>`manual_lock_hub()` (`SS3-MTH-10`) | `src/core/policies.py`<br>`src/components/hub_monitor.py`<br>`src/core/booking.py`<br>`src/core/personal_ev.py` | `TC-SS3-BND-01`<br>`TC-SS3-LCK-01` |

---

## 8. Danh mục Test Case Bonus & Kết quả Kiểm thử thực tế

Chi tiết các ca kiểm thử và log chạy tự động được ghi nhận tại:  
👉 **[Danh mục Test Case Bonus SS3](test_cases.md)**

Toàn bộ 5 ca kiểm thử bonus của SS3 (tại `tests/test_ss3_monitoring_bonus.py`) cùng các ca kiểm thử tích hợp liên quan đã được chạy tự động bằng `pytest` và đạt kết quả **100% PASS**:

```text
=== CHAY TEST SUITE SS3 SUBMISSION 3 (PYTHONPATH=src pytest -v) ===
tests/test_ss3_monitoring_bonus.py::test_tc_ss3_bnd_01_exact_occupancy_threshold_boundaries PASSED
tests/test_ss3_monitoring_bonus.py::test_tc_ss3_inv_01_hub_capacity_conservation_and_no_double_counting PASSED
tests/test_ss3_monitoring_bonus.py::test_tc_ss3_rev_01_realized_revenue_strictly_excludes_deposits_and_debt PASSED
tests/test_ss3_monitoring_bonus.py::test_tc_ss3_lck_01_auto_lock_sync_failure_and_manual_lock_idempotency PASSED
tests/test_ss3_monitoring_bonus.py::test_tc_ss3_iot_01_sensor_timeout_cache_fallback_and_tech_maintenance PASSED
5 passed in 0.18s
```

---

## 9. Giới hạn và Quyết định Thiết kế

### 9.1. Phân định giữa UI Prototype hiện tại và Tầng `MonitoringService` đề xuất (`S3-ISS-SS3-01`)
- **Thực trạng trong prototype:** Trong [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py), các phép tính tổng hợp KPI toàn mạng, lọc doanh thu từ `wallet["ledger"]` và phân loại 3 cột cảnh báo (`yellow_hubs`, `red_hubs`, `full_hubs`) đang được thực hiện trực tiếp bên trong hàm `render()`.
- **Quyết định thiết kế Sub 3:** Tách toàn bộ nghiệp vụ tính toán sang lớp `MonitoringService` và trả về các Value Object bất biến (`NetworkSnapshot`, `OccupancySnapshot`, `RevenueReport`), đáp ứng đúng chữ ký hợp đồng `INT-03`.

### 9.2. Quyết định về Minh bạch Doanh thu thực thu (`US-07`)
- Trong `hub_monitor.py` (dòng 133), hệ thống hiện tính `rev_shared` từ các bút toán `SETTLE_RENTAL_FEE`, `SETTLE_RENTAL_DEBT`, `PENALTY_NOSHOW` và đã tuân thủ đúng quy tắc **không cộng tiền cọc đang tạm giữ (`HOLD_DEPOSIT`) vào doanh thu**.
- Thiết kế lớp `RevenueReport` ở Mục 5.3 chuẩn hóa việc tách riêng 4 dòng doanh thu thực thu (thuê xe SS1, đỗ xe cá nhân SS2, sạc/quá giờ SS5, phạt no-show $10.000\text{ VNĐ}$) và đặt cạnh các chỉ số đối soát độc lập (`held_deposit_vnd`, `refunded_amount_vnd`, `outstanding_debt_vnd`).

### 9.3. Làm rõ hệ số công suất sạc ước tính ở Tab Năng lượng (`US-12`)
- Tại `hub_monitor.py` (dòng 158), công suất ước tính trên giao diện đang tính theo công thức `est_kw = busy_ports * 7.4`, trong khi hằng số tại `src/core/policies.py` (dòng 68) là `DEFAULT_PORT_KW = 11.0` $\text{kW}$ (trần trạm `HUB_POWER_CAP_KW = 150.0` $\text{kW}$). Thiết kế lớp `OccupancySnapshot` chốt quy ước đọc trực tiếp tổng công suất thực tế `current_power_kw` từ bộ lập lịch sạc của SS5.

---

## 10. Tự kiểm tra và Khai báo sử dụng AI

- **Checklist tự kiểm tra:** Đã hoàn thành tự đối chiếu 12 nhiệm vụ (`TV3-01` đến `TV3-12`) và 12 tiêu chí chất lượng nghiêm ngặt tại [`self_check.md`](self_check.md). Tác giả tự chịu trách nhiệm về tính đúng đắn của toàn bộ nội dung bàn giao.
- **Khai báo AI:** Được ghi nhận chi tiết tại [`ai_usage.md`](ai_usage.md).
- **Nhật ký Prompt:** Được lưu trữ đầy đủ tại [`docs/prompt-history/TV3_PhamTienDat/prompt_history_PhamTienDat_sub3.txt`](../../../prompt-history/TV3_PhamTienDat/prompt_history_PhamTienDat_sub3.txt).

---

## 11. Đầu ra bàn giao Submission 3

Báo cáo cá nhân hoàn chỉnh được kết xuất và bàn giao tại:
- `output/submission_3/REPORT_SUB3_PhamTienDat_2410724.docx`
- `output/submission_3/REPORT_SUB3_PhamTienDat_2410724.pdf`

Kèm theo toàn bộ mã nguồn sơ đồ PlantUML (`shared/implementation.puml`, `shared/system_classes.puml`, `SS3/class_diagram.puml`), file ảnh chất lượng cao (`.png`, `.svg`), bộ kiểm thử `tests/test_ss3_monitoring_bonus.py` và các tài liệu truy vết.