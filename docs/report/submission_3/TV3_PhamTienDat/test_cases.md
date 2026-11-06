# Danh mục Test Case Bonus — Phạm Tiến Đạt — SS3
**Phân hệ:** SS3 — Giám sát mạng lưới Hub, KPI, Doanh thu & Cảnh báo  
**Tác giả:** Phạm Tiến Đạt — MSSV: 2410724 — TV3  
**Trạng thái:** ĐÃ THỰC THI & VERIFIED (Chạy tự động qua `pytest` tại [`tests/test_ss3_monitoring_bonus.py`](../../../../tests/test_ss3_monitoring_bonus.py)).

---

## 1. Nguyên tắc kiểm thử Submission 3
- Tuân thủ quy định mục 6.4 và 7 của [GUIDANCE_FOR_SUB_3.md](../../../../GUIDANCE_FOR_SUB_3.md): Mỗi Use Case có đầy đủ ca kiểm thử luồng chính, ca kiểm thử ngoại lệ/lỗi và ca kiểm tra giá trị biên/bất biến quan trọng.
- Trạng thái `PASS` chỉ được ghi nhận sau khi đã chạy thực tế bằng lệnh `PYTHONPATH=src python -m pytest -v tests/test_ss3_monitoring_bonus.py` trên môi trường Python của dự án.

---

## 2. Chi tiết các Test Case Bonus SS3

### 2.1. UC_SS3_01 — Giám sát mạng lưới Hub, KPI & Doanh thu thời gian thực

#### TC-SS3-INV-01: Kiểm tra bất biến bảo toàn sức chứa chỗ đỗ Hub & phát hiện lỗi cộng trùng xe (Luồng chính & Invariant)
- **Method ID:** `SS3-MTH-03` (`Hub.validate_capacity_invariant`), `SS3-MTH-06` (`MonitoringService.calculate_hub_occupancy`).
- **Tiền điều kiện:** Khởi tạo `MonitoringService` với trạm `HUB_01` có tổng sức chứa `capacity = 40` chỗ, `total_ports = 10` cổng sạc, công suất trần `max_power_kw = 150.0` $\text{kW}$.
- **Dữ liệu vào:**
  - *Trường hợp 1 (Hợp lệ):* `present_vehicles_count = 20`, `incoming_reserved_count = 5`, `background_load_count = 5`, `available_slots = 10` (tổng $= 40$); `active_ports_count = 8`, `current_load_kw = 88.0`.
  - *Trường hợp 2 (Vi phạm bất biến do cộng trùng 1 xe vừa ở `present` vừa ở `incoming_reserved`):* `present_vehicles_count = 21`, các trường khác giữ nguyên (tổng $= 41 \ne 40$).
- **Các bước thực hiện:**
  1. Gọi `calculate_hub_occupancy("HUB_01")` trên bộ dữ liệu Trường hợp 1 và kiểm tra các chỉ số trả về.
  2. Giả lập hỏng 2 cổng sạc (`active_ports_count` giảm từ 8 xuống 6) và kiểm tra `available_slots` đỗ xe.
  3. Gán bộ dữ liệu Trường hợp 2 (cộng trùng xe) và gọi lại `calculate_hub_occupancy("HUB_01")`.
- **Kết quả mong đợi:**
  - Trường hợp 1: Trả về `ok = True`, `occupancy_rate_pct == 75.0%`, `occupancy_level == OccupancyLevel.WARNING`, `port_utilization_pct == 80.0%`.
  - Khi cổng sạc giảm từ 8 xuống 6: `available_slots` vẫn giữ nguyên là `10` chỗ (sự cố cổng sạc không làm thay đổi chỗ đỗ xe).
  - Trường hợp 2: `validate_capacity_invariant()` trả về `False`; dịch vụ trả về `OperationResult(ok=False, error_code="INVALID_STATE")`.
- **Kết quả thực tế:**
  - Khớp $100\%$ kỳ vọng; phát hiện chính xác lỗi cộng trùng xe và bảo toàn độc lập giữa cổng sạc với chỗ đỗ.
  - Log pytest: `tests/test_ss3_monitoring_bonus.py::test_tc_ss3_inv_01_hub_capacity_conservation_and_no_double_counting PASSED`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 06/11/2026).

---

#### TC-SS3-REV-01: Tổng hợp Doanh thu thực thu tách biệt hoàn toàn với Tiền cọc đang giữ, Tiền hoàn và Công nợ (Luồng chính & Financial Invariant)
- **Method ID:** `SS3-MTH-07` (`MonitoringService.generate_revenue_report`), `SS3-MTH-05` (`MonitoringService.get_network_snapshot`).
- **Tiền điều kiện:** Hệ thống có 2 người dùng `SV_01` (số dư $200.000\text{ VNĐ}$) và `SV_02` (số dư $60.000\text{ VNĐ}$).
- **Dữ liệu vào (Chuỗi 4 nghiệp vụ tài chính):**
  1. `SV_01` đặt xe `BK_ACTIVE_01`: Tạm giữ cọc $50.000\text{ VNĐ}$ (đang ở trạng thái giữ chỗ, chưa kết thúc chuyến).
  2. `SV_01` có một lượt đặt khác `BK_NOSHOW_02` quá hạn 30 phút không nhận xe: Thu phí phạt no-show $10.000\text{ VNĐ}$ và hoàn lại $40.000\text{ VNĐ}$ về ví.
  3. `SV_02` hoàn tất phiên đỗ xe cá nhân kèm sạc điện `SESS_PEV_01` với phí đỗ $5.000\text{ VNĐ}$ + phí sạc $10.000\text{ VNĐ} = 15.000\text{ VNĐ}$ (đã thanh toán hết).
  4. `SV_02` phát sinh một hóa đơn thuê xe vượt số dư ví, ghi nhận khoản công nợ chưa trả `debt = 15.000 VNĐ`.
- **Các bước thực hiện:**
  1. Thực thi 4 nghiệp vụ trên sổ cái và gọi `MonitoringService.generate_revenue_report()`.
  2. Kiểm tra từng trường phân rã doanh thu, tiền cọc, tiền hoàn và công nợ trong `RevenueReport`.
- **Kết quả mong đợi:**
  - `settled_penalty_fee_vnd == 10_000` VNĐ.
  - `settled_parking_fee_vnd == 5_000` VNĐ; `settled_charging_fee_vnd == 10_000` VNĐ.
  - **`total_realized_revenue_vnd == 25_000` VNĐ** ($10.000 + 5.000 + 10.000$; tuyệt đối **không** cộng $50.000\text{ VNĐ}$ cọc đang giữ hay $15.000\text{ VNĐ}$ công nợ chưa thu).
  - `held_deposit_vnd == 50_000` VNĐ; `refunded_amount_vnd == 40_000` VNĐ; `outstanding_debt_vnd == 15_000` VNĐ.
- **Kết quả thực tế:**
  - Báo cáo trả về đúng `total_realized_revenue_vnd = 25000`, `held_deposit_vnd = 50000`, `refunded_amount_vnd = 40000`, `outstanding_debt_vnd = 15000`.
  - Log pytest: `tests/test_ss3_monitoring_bonus.py::test_tc_ss3_rev_01_realized_revenue_strictly_excludes_deposits_and_debt PASSED`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 06/11/2026).

---

#### TC-SS3-IOT-01: Xử lý mất kết nối cảm biến IoT (Cache Fallback), ghi nhận kế hoạch bảo trì của Kỹ thuật viên & cấu hình ngưỡng của Admin (Ngoại lệ & Nhánh thay thế)
- **Method ID:** `SS3-MTH-05` (`get_network_snapshot`), `SS3-MTH-11` (`update_alert_thresholds`), `SS3-MTH-12` (`get_iot_error_logs`, `record_iot_maintenance_plan`).
- **Tiền điều kiện:** Hệ thống đã chụp thành công 1 bản `NetworkSnapshot` hợp lệ ở `state_version = 1`.
- **Dữ liệu vào:**
  1. Cảm biến IoT tại `HUB_03` bị mất kết nối (`iot_online = False`) kèm 1 lỗi phần cứng cảm biến `IOT_HARDWARE_FAULT`.
  2. Kỹ thuật viên `TECH_01` gọi `record_iot_maintenance_plan` với ghi chú `"Thay thế cảm biến từ tại ô đỗ số 04 - HUB_03"`.
  3. Quản trị viên `ADMIN_01` cập nhật ngưỡng cảnh báo thành $(65.0\%, 88.0\%)$ và thử cập nhật ngưỡng sai $(90.0\%, 80.0\%)$.
- **Các bước thực hiện:**
  1. Gọi `get_network_snapshot()` khi `HUB_03.iot_online = False`.
  2. Gọi `calculate_hub_occupancy("HUB_999")` với mã Hub không tồn tại.
  3. Thực thi ghi nhận bảo trì của `TECH_01` và cập nhật ngưỡng của `ADMIN_01`.
- **Kết quả mong đợi:**
  - Khi IoT mất kết nối: `get_network_snapshot()` trả về `ok = True` với bản chụp cache có `is_using_cached_data == True` và sinh cảnh báo `IOT_SENSOR_TIMEOUT` chứa chuỗi `"Dữ liệu thời gian thực đang bị gián đoạn"`.
  - Mã `HUB_999` không tồn tại trả về `ok = False, error_code = "NOT_FOUND"`.
  - Bản ghi lỗi IoT cập nhật đúng `acknowledged_by == "TECH_01"` và lưu phương án bảo trì.
  - Ngưỡng $(65.0\%, 88.0\%)$ được áp dụng thành công; ngưỡng ngược $(90.0\%, 80.0\%)$ bị từ chối với mã lỗi `"INVALID_INPUT"`.
- **Kết quả thực tế:**
  - Toàn bộ các nhánh ngoại lệ và kiểm tra quyền/tham số đều xử lý chính xác.
  - Log pytest: `tests/test_ss3_monitoring_bonus.py::test_tc_ss3_iot_01_sensor_timeout_cache_fallback_and_tech_maintenance PASSED`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 06/11/2026).

---

### 2.2. UC_SS3_02 — Cảnh báo phân cấp chiếm dụng Hub & Sự cố IoT

#### TC-SS3-BND-01: Kiểm tra phân loại cảnh báo tại đúng 6 mốc giá trị biên thập phân (`69.99%`, `70.00%`, `84.99%`, `85.00%`, `99.99%`, `100.00%`)
- **Method ID:** `SS3-MTH-01` (`Hub.calculate_occupancy_rate`), `SS3-MTH-02` (`Hub.get_occupancy_level`), `SS3-MTH-08` (`MonitoringService.evaluate_hub_alerts`).
- **Tiền điều kiện:** Khởi tạo trạm kiểm thử có `capacity = 10000` chỗ để kiểm tra độ chính xác tuyệt đối tới 2 chữ số thập phân.
- **Dữ liệu vào & Kết quả mong đợi theo từng mốc biên:**
  1. `occupied = 6999` (`available_slots = 3001` $\rightarrow 69.99\%$): `OccupancyLevel.NORMAL`, danh sách cảnh báo rỗng (`len == 0`), `is_locked == False`.
  2. `occupied = 7000` (`available_slots = 3000` $\rightarrow 70.00\%$): `OccupancyLevel.WARNING`, sinh 1 `Alert` mức `WARNING` (Màu vàng), `is_locked == False`.
  3. `occupied = 8499` (`available_slots = 1501` $\rightarrow 84.99\%$): `OccupancyLevel.WARNING`, sinh 1 `Alert` mức `WARNING`, `is_locked == False`.
  4. `occupied = 8500` (`available_slots = 1500` $\rightarrow 85.00\%$): `OccupancyLevel.CRITICAL`, sinh 1 `Alert` mức `CRITICAL` (Màu đỏ nhấp nháy, đề xuất điều phối SS4), `is_locked == False`.
  5. `occupied = 9999` (`available_slots = 1` $\rightarrow 99.99\%$): `OccupancyLevel.CRITICAL`, sinh 1 `Alert` mức `CRITICAL`, `is_locked == False`.
  6. `occupied = 10000` (`available_slots = 0` $\rightarrow 100.00\%$): `OccupancyLevel.FULL`, sinh 1 `Alert` mức `CRITICAL`/`FULL` (Khóa Đỏ) và tự động đặt `hub.is_locked == True`.
- **Kết quả thực tế:**
  - Cả 6 mốc biên đều trả về đúng `OccupancyLevel`, đúng loại `Alert` và đúng trạng thái khóa `is_locked`.
  - Log pytest: `tests/test_ss3_monitoring_bonus.py::test_tc_ss3_bnd_01_exact_occupancy_threshold_boundaries PASSED`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 06/11/2026).

---

#### TC-SS3-LCK-01: Tính lũy đẳng khi đồng bộ khóa tự động, xử lý lỗi đồng bộ khóa (Exception 1) & phân quyền khóa thủ công (Manual Lock)
- **Method ID:** `SS3-MTH-09` (`sync_hub_booking_lock`), `SS3-MTH-10` (`manual_lock_hub`), `SS3-MTH-04` (`Alert.acknowledge`).
- **Tiền điều kiện:** Trạm `HUB_02` chạm mức lấp đầy $100\%$ (`available_slots = 0`), `state_version` ban đầu $= 1$.
- **Dữ liệu vào & Các bước thực hiện:**
  1. Gọi `sync_hub_booking_lock("HUB_02", True, operation_key="LOCK-OP-001")` 2 lần liên tiếp với cùng `operation_key`.
  2. Gọi lại với cùng key `"LOCK-OP-001"` nhưng truyền `lock_state = False` (xung đột tham số).
  3. Giả lập cờ lỗi đồng bộ `simulate_lock_sync_failure = True` rồi gọi `evaluate_hub_alerts("HUB_02")`.
  4. Thử gọi `manual_lock_hub` bằng tài khoản sinh viên `"SV_01"` (vai trò `STUDENT`), sau đó gọi bằng tài khoản nhân viên vận hành `"OP_01"` (vai trò `OPERATOR`).
- **Kết quả mong đợi:**
  - Bước 1: Lần gọi đầu khóa trạm và tăng `state_version` lên `2`; lần gọi lặp thứ hai trả về `ok = True` nhưng giữ nguyên `state_version == 2` (Idempotent).
  - Bước 2: Trả về `ok = False, error_code = "CONFLICTING_OPERATION"`.
  - Bước 3: Khi lỗi đồng bộ xảy ra, trạm chưa thể khóa tự động và hệ thống phát sinh `Alert` loại `LOCK_SYNC_FAILURE` mức `EMERGENCY`.
  - Bước 4: Tài khoản `STUDENT` bị từ chối với mã lỗi `"FORBIDDEN"`; tài khoản `OPERATOR` khóa thủ công thành công (`hub.is_locked == True`) và tự động đánh dấu `is_resolved == True` cho cảnh báo `LOCK_SYNC_FAILURE`.
- **Kết quả thực tế:**
  - Khớp hoàn toàn mọi điều kiện kiểm tra lũy đẳng, xung đột và phân quyền.
  - Log pytest: `tests/test_ss3_monitoring_bonus.py::test_tc_ss3_lck_01_auto_lock_sync_failure_and_manual_lock_idempotency PASSED`.
- **Trạng thái:** `PASS` (Đã chạy kiểm thử tự động ngày 06/11/2026).

---

## 3. Bảng tổng hợp kết quả kiểm thử SS3

| Test ID | Tên ca kiểm thử | Loại kiểm thử | Đối tượng kiểm tra | Kết quả | Ngày thực thi |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `TC-SS3-BND-01` | Phân loại cảnh báo tại 6 mốc biên thập phân ($69.99\%$–$100\%$) | Giá trị biên & Luồng chính | `Hub`, `MonitoringService` | **PASS** | 06/11/2026 |
| `TC-SS3-INV-01` | Bảo toàn sức chứa chỗ đỗ & chống cộng trùng xe | Invariant & Ngoại lệ | `Hub`, `MonitoringService` | **PASS** | 06/11/2026 |
| `TC-SS3-REV-01` | Doanh thu thực thu tách biệt tiền cọc giữ và công nợ | Luồng chính & Tài chính | `RevenueReport`, `MonitoringService` | **PASS** | 06/11/2026 |
| `TC-SS3-LCK-01` | Khóa tự động lũy đẳng, lỗi đồng bộ & khóa thủ công | Ngoại lệ, Lặp & Phân quyền | `MonitoringService`, `Alert` | **PASS** | 06/11/2026 |
| `TC-SS3-IOT-01` | Cache fallback khi IoT mất kết nối & bảo trì/cấu hình ngưỡng | Ngoại lệ & Nhánh thay thế | `MonitoringService`, `NetworkSnapshot` | **PASS** | 06/11/2026 |