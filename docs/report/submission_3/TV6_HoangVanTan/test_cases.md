# Danh mục Test Case Bonus — Hoàng Văn Tấn — SS6
**Phân hệ:** SS6 — Mô phỏng nhu cầu What-if & Dự báo 24 giờ  
**Tác giả:** Hoàng Văn Tấn — MSSV: 2213074 — TV6  
**Trạng thái:** ĐÃ THỰC THI & VERIFIED (Có log kiểm thử tự động đính kèm).

---

## 1. Nguyên tắc kiểm thử Submission 3
- Tuân thủ quy định mục 6.4 và 7 của [GUIDANCE_FOR_SUB_3.md](../../../../GUIDANCE_FOR_SUB_3.md): Mỗi UC có ít nhất một ca luồng chính, một ca ngoại lệ/lỗi và các ca kiểm tra biên quan trọng.
- Trạng thái `PASS` chỉ được gán khi ca kiểm thử đã được chạy thực tế trên môi trường Python của dự án và có bằng chứng assert/log đi kèm.

---

## 2. Chi tiết các Test Case

### 2.1. UC_SS6_01 — Mô phỏng tăng đột biến nhu cầu khách Metro (What-if Metro Surge)

#### TC-SS6-SRG-01: Chạy mô phỏng Metro Surge trong ngưỡng sức chứa trạm (Luồng chính)
- **Method ID:** `SS6-MTH-01` (`DemandSimulationService.preview_demand`), `SS6-MTH-05` (`HubEventSimulator.simulate_metro_surge`).
- **Tiền điều kiện:** Hub KTX Khu B (`HUB-002`) có `available_slots = 8`, `total_slots = 20`.
- **Dữ liệu vào:** `target_hub_id = "HUB-002"`, `num_new_students = 5`, `seed = 42`.
- **Các bước thực hiện:**
  1. Khởi tạo `HubEventSimulator` với bản sao sâu (`deepcopy`) của danh sách Hubs.
  2. Thực thi `simulate_metro_surge("HUB-002", 5, seed=42)`.
  3. Kiểm tra các trường metrics trả về và cập nhật số chỗ đỗ.
- **Kết quả mong đợi:**
  - `metrics["admitted_students"] == 5`.
  - `metrics["unserved_students"] == 0`.
  - `available_slots` của Hub đích giảm từ 8 xuống 3.
  - Sinh đúng 5 xe mới (`EV-SURGE-xxxx`) có pin từ 15% đến 45%.
- **Kết quả thực tế:**
  - `admitted_students = 5`, `unserved_students = 0`, chỗ đỗ sau mô phỏng: 3.
  - Log xác nhận: `TC-SS6-SRG-01: PASS (Admitted 5, Unserved 0, Slot reduced by 5)`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 02/11/2026).

---

#### TC-SS6-SRG-02: Mô phỏng quá tải khi lượng sinh viên vượt quá sức chứa (Ngoại lệ & Boundary)
- **Method ID:** `SS6-MTH-01`, `SS6-MTH-05`.
- **Tiền điều kiện:** Hub KTX Khu B (`HUB-002`) có `available_slots = 8`.
- **Dữ liệu vào:** `target_hub_id = "HUB-002"`, `num_new_students = 50` (vượt xa sức chứa 8 chỗ), `seed = 42`.
- **Các bước thực hiện:**
  1. Chạy `simulate_metro_surge("HUB-002", 50, seed=42)`.
  2. Kiểm tra việc bảo toàn sức chứa và theo dõi số lượng bị từ chối (`unserved_students`).
- **Kết quả mong đợi:**
  - `metrics["admitted_students"] == 8` (toàn bộ chỗ trống hiện có).
  - `metrics["unserved_students"] == 42` (`50 - 8`).
  - `available_slots == 0` (hết sạch chỗ đỗ).
  - `metrics["final_occupancy_pct"] == 100.0%`.
  - Log chứa cảnh báo quá tải trạm và sinh viên bị từ chối.
- **Kết quả thực tế:**
  - `admitted_students = 8`, `unserved_students = 42`, chỗ đỗ còn lại: 0, lấp đầy 100.0%.
  - Log xác nhận: `TC-SS6-SRG-02: PASS (Admitted 8, Unserved 42, Remaining slots 0)`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 02/11/2026).

---

#### TC-SS6-SRG-03: Bảo đảm tính cách ly Deepcopy (Isolation Invariant)
- **Method ID:** `SS6-MTH-01`, `SS6-MTH-05`.
- **Tiền điều kiện:** Dữ liệu trạm ban đầu nằm trong `st.session_state["hubs"]`.
- **Dữ liệu vào:** Chạy mô phỏng tải nặng với 30 sinh viên.
- **Các bước thực hiện:**
  1. Lưu một bản clone của `state["hubs"]`.
  2. Chạy `simulate_metro_surge` để tạo preview.
  3. So sánh dữ liệu `state["hubs"]` gốc trước và sau khi sinh preview.
- **Kết quả mong đợi:**
  - Dữ liệu `state["hubs"]` gốc không bị thay đổi bất kỳ trường nào trước khi có thao tác Apply.
- **Kết quả thực tế:**
  - Hai bản dữ liệu khớp hoàn toàn từng thuộc tính.
  - Log xác nhận: `TC-SS6-SRG-03: PASS (Deepcopy isolation verified: original state completely untouched)`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 02/11/2026).

---

### 2.2. UC_SS6_02 — Dự báo phụ tải nhu cầu và phân tích hàng đợi 24h

#### TC-SS6-FC-01: Dự báo chuỗi thời gian phụ tải đủ 24 giờ (Luồng chính & Horizon 24h)
- **Method ID:** `SS6-MTH-02` (`ForecastService.forecast`), `SS6-MTH-06` (`HubEventSimulator.generate_demand_forecast`).
- **Tiền điều kiện:** Mạng lưới trạm hoạt động bình thường, tham số dự báo hợp lệ.
- **Dữ liệu vào:** `base_arrival_rate = 15.0`, `surge_multiplier = 1.5`, `hours = 24`, `seed = 42`.
- **Các bước thực hiện:**
  1. Gọi `HubEventSimulator.generate_demand_forecast(15.0, 1.5, hours=24, seed=42)`.
  2. Kiểm tra số lượng phần tử của danh sách kết quả và nhãn thời gian từng giờ.
- **Kết quả mong đợi:**
  - Danh sách trả về chính xác 24 phần tử (`len == 24`).
  - Điểm đầu tiên là `06:00`, điểm cuối cùng là `05:00` sáng hôm sau.
  - Các giờ cao điểm (`07:00, 08:00, 17:00, 18:00`) có `peak_factor = 2.5` phản ánh lượng đến cao vượt trội.
  - Độ dài hàng đợi `queue_length >= 0` và thời gian chờ `wait_time_min >= 0`.
- **Kết quả thực tế:**
  - Sinh đủ đúng 24 điểm từ 06:00 đến 05:00.
  - Log xác nhận: `TC-SS6-FC-01: PASS (Forecast 24h generated: exactly 24 points from 06:00 to 05:00)`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 02/11/2026).

---

#### TC-SS6-FC-02: Tính tái lập của mô hình dự báo ngẫu nhiên (Reproducibility with Seed)
- **Method ID:** `SS6-MTH-02`, `SS6-MTH-06`.
- **Tiền điều kiện:** Hàm có yếu tố ngẫu nhiên Gaussian noise `rng.gauss(0, 1.5)`.
- **Dữ liệu vào:** Chạy 2 lần độc lập với cùng bộ tham số: `base_rate = 15`, `surge_mult = 1.5`, `hours = 24`, `seed = 42`.
- **Các bước thực hiện:**
  1. Chạy lần 1 thu được `fc1`.
  2. Chạy lần 2 thu được `fc2`.
  3. So sánh cấu trúc và giá trị từng trường trong toàn bộ 24 giờ.
- **Kết quả mong đợi:**
  - `fc1 == fc2` (giá trị dự báo khớp 100% từng số nguyên/thực).
- **Kết quả thực tế:**
  - Khớp hoàn toàn 100%.
  - Log xác nhận: `TC-SS6-FC-02: PASS (Reproducibility verified: 2 runs with seed=42 produce identical points)`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 02/11/2026).

---

### 2.3. Kiểm thử cơ chế Apply & Điều phối phiên bản (SimulationCoordinator)

#### TC-SS6-APL-01: Áp dụng bản xem trước thành công khi phiên bản đồng bộ (Luồng chính)
- **Method ID:** `SS6-MTH-03` (`SimulationCoordinator.apply_preview`).
- **Tiền điều kiện:** `st.session_state["state_version"] = 1`, `preview.baseline_version = 1`.
- **Dữ liệu vào:** Lệnh `apply_preview(preview_id, expected_version=1)`.
- **Các bước thực hiện:**
  1. So sánh `baseline_version` với `state_version` hiện tại.
  2. Gán `state["hubs"] = preview["modified_hubs"]`.
  3. Tăng phiên bản `bump_state_version()`.
- **Kết quả mong đợi:**
  - `new_state_version == 2`.
  - Dữ liệu vận hành được cập nhật theo kết quả mô phỏng.
- **Kết quả thực tế:**
  - `new_state_version = 2`, `slots` trạm cập nhật đúng kết quả mô phỏng.
  - Log xác nhận: `TC-SS6-APL-01: PASS (Apply preview committed successfully, state_version bumped from 1 to 2)`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 02/11/2026).

---

#### TC-SS6-APL-02: Ngăn chặn xung đột phiên bản khi dữ liệu bị thay đổi giữa chừng (Stale Apply)
- **Method ID:** `SS6-MTH-03` (`SimulationCoordinator.apply_preview`).
- **Tiền điều kiện:** `preview.baseline_version = 1`, nhưng trạng thái hệ thống đã bị phân hệ khác cập nhật lên `state_version = 2`.
- **Dữ liệu vào:** Người dùng bấm nút Áp dụng với `expected_version = 1`.
- **Các bước thực hiện:**
  1. Kiểm tra điều kiện `baseline_version == current_version`.
  2. Phát hiện bất đồng bộ (`1 != 2`).
  3. Từ chối commit và giữ nguyên dữ liệu trạm hiện tại.
- **Kết quả mong đợi:**
  - Trả về lỗi xung đột phiên bản `STALE_STATE`.
  - `state["hubs"]` không bị ghi đè dữ liệu cũ.
- **Kết quả thực tế:**
  - Hệ thống phát hiện xung đột phiên bản và hủy commit.
  - Log xác nhận: `TC-SS6-APL-02: PASS (Stale state prevented: baseline_ver 1 != current_ver 2, commit aborted)`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 02/11/2026).

---

## 3. Bảng tổng hợp kết quả kiểm thử SS6

| Test ID | Tên ca kiểm thử | Loại kiểm thử | Đối tượng kiểm tra | Kết quả | Ngày thực thi |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `TC-SS6-SRG-01` | Metro Surge trong ngưỡng sức chứa | Luồng chính | `DemandSimulationService` | **PASS** | 02/11/2026 |
| `TC-SS6-SRG-02` | Metro Surge quá tải & unserved arrivals | Ngoại lệ & Biên | `HubEventSimulator` | **PASS** | 02/11/2026 |
| `TC-SS6-SRG-03` | Tính cách ly Deepcopy trạm gốc | Invariant | `DemandSimulationService` | **PASS** | 02/11/2026 |
| `TC-SS6-FC-01` | Dự báo chuỗi thời gian đủ 24 giờ | Luồng chính | `ForecastService` | **PASS** | 02/11/2026 |
| `TC-SS6-FC-02` | Tính tái lập kết quả theo Seed=42 | Invariant | `ForecastService` | **PASS** | 02/11/2026 |
| `TC-SS6-APL-01` | Áp dụng Preview thành công & Bump version | Luồng chính | `SimulationCoordinator` | **PASS** | 02/11/2026 |
| `TC-SS6-APL-02` | Ngăn chặn Stale version khi state thay đổi | Ngoại lệ & Xung đột | `SimulationCoordinator` | **PASS** | 02/11/2026 |
