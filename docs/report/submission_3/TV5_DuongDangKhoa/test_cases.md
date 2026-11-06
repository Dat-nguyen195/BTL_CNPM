# TEST CASE BONUS — DƯƠNG ĐĂNG KHOA — SS5

**Trạng thái:** Đã thiết kế test case (DESIGNED); chưa chạy kiểm thử Sub3 (NOT_RUN). Không có kết quả PASS mặc định.

## UC_SS5_01 — Lập lịch sạc tự động theo điểm ưu tiên và giới hạn công suất lưới

### TC-SS5-B01 — Luồng chính: Tính điểm ưu tiên và phân bổ cổng sạc

- **Test ID:** TC-SS5-B01
- **Method ID:** `SmartChargingScheduler.calculate_priority()`, `SmartChargingScheduler.get_sorted_queue()`, `SmartChargingScheduler.allocate_ports()`
- **Tiền điều kiện:**
  - Scheduler được khởi tạo với giới hạn công suất 20 kW.
  - Hub H1 có 3 cổng sạc khả dụng.
  - Không có phiên sạc nào đang hoạt động.
- **Dữ liệu đầu vào:**

| Vehicle ID | SoC | Student Booking | Port Power |
|---|---:|---|---:|
| EV-01 | 5% | No | 7.4 kW |
| EV-02 | 30% | Yes | 7.4 kW |
| EV-03 | 30% | No | 7.4 kW |

- **Các bước thực hiện:**
  1. Khởi tạo `SmartChargingScheduler(cap_kw=20.0)`.
  2. Tạo ba `ChargingRequest` tương ứng với dữ liệu đầu vào.
  3. Gọi `add_request()` cho từng request.
  4. Gọi `get_sorted_queue()` để kiểm tra thứ tự ưu tiên.
  5. Gọi `allocate_ports(hub_id="H1", available_port_count=3)`.
  6. Kiểm tra số phiên sạc được tạo và số request còn lại trong queue.

- **Kết quả mong đợi:**
  - EV-01 có Priority Score = 177.5.
  - EV-02 có Priority Score = 125.0.
  - EV-03 có Priority Score = 65.0.
  - Thứ tự ưu tiên: EV-01 → EV-02 → EV-03.
  - Chỉ hai phương tiện đầu tiên được phân bổ cổng vì tổng công suất là 14.8 kW; nếu phân bổ thêm EV-03 thì tổng công suất là 22.2 kW, vượt giới hạn 20 kW.
  - Hai phiên sạc được tạo; một request còn lại trong queue.

- **Kết quả thực tế / bằng chứng:** CHƯA CHẠY.
- **Trạng thái:** DESIGNED / NOT_RUN.

### TC-SS5-B02 — Ngoại lệ: Tổng công suất vượt giới hạn hub

- **Test ID:** TC-SS5-B02
- **Method ID:** `SmartChargingScheduler.add_request()`, `SmartChargingScheduler.allocate_ports()`
- **Tiền điều kiện:**
  - Scheduler được khởi tạo với giới hạn công suất 20 kW.
  - Hub H1 có 3 cổng khả dụng.
  - Không có phiên sạc đang hoạt động.
- **Dữ liệu đầu vào:**

| Vehicle ID | SoC | Port Power |
|---|---:|---:|
| EV-04 | 10% | 11 kW |
| EV-05 | 15% | 11 kW |

- **Các bước thực hiện:**
  1. Khởi tạo `SmartChargingScheduler(cap_kw=20.0)`.
  2. Tạo hai `ChargingRequest` cho EV-04 và EV-05.
  3. Thêm hai request vào hàng đợi.
  4. Gọi `allocate_ports(hub_id="H1", available_port_count=3)`.
  5. Kiểm tra kết quả phân bổ và hàng đợi sau khi xử lý.

- **Kết quả mong đợi:**
  - EV-04 được ưu tiên phân bổ trước.
  - Công suất sau khi phân bổ EV-04 là 11 kW.
  - Không thể phân bổ EV-05 vì tổng công suất dự kiến là 22 kW, vượt giới hạn 20 kW.
  - Chỉ một phiên sạc được tạo.
  - EV-05 tiếp tục ở trạng thái chờ trong queue.
  - Không có phiên sạc nào làm tổng công suất vượt 20 kW.

- **Kết quả thực tế / bằng chứng:** CHƯA CHẠY.
- **Trạng thái:** DESIGNED / NOT_RUN.

## UC_SS5_02 — Giám sát hàng chờ sạc, hoàn thành, ân hạn và tính phí quá giờ

### TC-SS5-B03 — Luồng chính: Sạc hoàn tất, hết ân hạn và phát sinh phí Overstay

- **Test ID:** TC-SS5-B03
- **Method ID:** `SmartChargingScheduler.advance_simulation_tick()`, `SmartChargingScheduler.unplug_vehicle()`
- **Tiền điều kiện:**
  - Scheduler được khởi tạo với giới hạn công suất 150 kW.
  - Hub H1 có ít nhất một cổng sạc khả dụng.
  - Không có phiên sạc đang hoạt động.
- **Dữ liệu đầu vào:**
  - Vehicle ID: EV-06.
  - Initial SoC: 98%.
  - Port Power: 7.4 kW.
  - Target SoC: 100%.
  - Grace Period: 15 phút.
  - Overstay Rate: 10,000 VND / 15 phút.

- **Các bước thực hiện:**
  1. Khởi tạo `SmartChargingScheduler(cap_kw=150.0)`.
  2. Tạo request cho EV-06 với SoC 98% và công suất cổng 7.4 kW.
  3. Thêm request vào queue và gọi `allocate_ports()`.
  4. Lấy phiên sạc vừa tạo từ `_active_sessions`.
  5. Gọi `advance_simulation_tick(minutes=15)` để mô phỏng quá trình sạc.
  6. Kiểm tra trạng thái phiên sạc sau khi đạt SoC 100%.
  7. Gọi `advance_simulation_tick(minutes=15)` để mô phỏng thời gian ân hạn.
  8. Gọi `advance_simulation_tick(minutes=5)` để mô phỏng xe tiếp tục chiếm cổng sau thời gian ân hạn.
  9. Kiểm tra trạng thái Overstay và phí phát sinh.
  10. Gọi `unplug_vehicle(session_id)` để giải phóng phiên sạc.

- **Kết quả mong đợi:**
  - Phiên sạc chuyển sang `GRACE_PERIOD` sau khi đạt SoC 100%.
  - Trong 15 phút ân hạn, phiên vẫn ở trạng thái `GRACE_PERIOD`.
  - Sau khi vượt quá thời gian ân hạn, phiên chuyển sang `OVERSTAY`.
  - Phí Overstay được tính là 10,000 VND.
  - Gọi `unplug_vehicle()` trả về phiên sạc đã kết thúc.
  - Phiên sạc được loại khỏi `_active_sessions`.

- **Kết quả thực tế / bằng chứng:** CHƯA CHẠY.
- **Trạng thái:** DESIGNED / NOT_RUN.

### TC-SS5-B04 — Ngoại lệ: Xe rời cổng trong thời gian ân hạn

- **Test ID:** TC-SS5-B04
- **Method ID:** `SmartChargingScheduler.advance_simulation_tick()`, `SmartChargingScheduler.unplug_vehicle()`
- **Tiền điều kiện:**
  - Scheduler được khởi tạo với giới hạn công suất 150 kW.
  - Hub H1 có ít nhất một cổng sạc khả dụng.
  - Không có phiên sạc đang hoạt động.
- **Dữ liệu đầu vào:**
  - Vehicle ID: EV-07.
  - Initial SoC: 98%.
  - Port Power: 7.4 kW.
  - Target SoC: 100%.
  - Grace Period: 15 phút.

- **Các bước thực hiện:**
  1. Khởi tạo `SmartChargingScheduler(cap_kw=150.0)`.
  2. Tạo request cho EV-07 với SoC 98%.
  3. Thêm request vào queue và phân bổ cổng sạc.
  4. Lấy phiên sạc từ `_active_sessions`.
  5. Gọi `advance_simulation_tick(minutes=15)` để đưa phiên sạc đến trạng thái hoàn tất.
  6. Kiểm tra phiên sạc chuyển sang `GRACE_PERIOD`.
  7. Trong thời gian ân hạn, gọi `unplug_vehicle(session_id)`.
  8. Kiểm tra phiên sạc đã được giải phóng và không phát sinh phí Overstay.

- **Kết quả mong đợi:**
  - Phiên sạc đạt trạng thái `GRACE_PERIOD`.
  - Khi xe rời cổng trong thời gian ân hạn, phiên sạc được kết thúc.
  - Phiên sạc được loại khỏi `_active_sessions`.
  - Không phát sinh phí Overstay.
  - Cổng sạc có thể được sử dụng cho request tiếp theo.

- **Kết quả thực tế / bằng chứng:** CHƯA CHẠY.
- **Trạng thái:** DESIGNED / NOT_RUN.

## Test Execution Summary

| Test ID | Use Case | Test Type | Status |
|---|---|---|---|
| TC-SS5-B01 | UC_SS5_01 | Main Flow | DESIGNED / NOT_RUN |
| TC-SS5-B02 | UC_SS5_01 | Exception Flow | DESIGNED / NOT_RUN |
| TC-SS5-B03 | UC_SS5_02 | Main Flow | DESIGNED / NOT_RUN |
| TC-SS5-B04 | UC_SS5_02 | Exception Flow | DESIGNED / NOT_RUN |

**Test File:** `tests/test_scheduler_and_charging.py` (unit tests hiện có); bốn bonus test case ở trên là thiết kế bổ sung, chưa được xác nhận đã viết thành test function.

**Execution Command:**

```bash
pytest -v tests/test_scheduler_and_charging.py
```

**Important:** Chỉ cập nhật trạng thái thành PASS hoặc FAIL sau khi thực thi test và lưu lại bằng chứng tương ứng.

## Đối chiếu thực thi 06/11/2026

Bộ49 test hiện có đã chạy PASS (log baseline chung). Các tên test dẫn trong traceability.md được đối chiếu với nguồn. Nhãn PASS của bản bàn giao chỉ có hiệu lực trong phạm vi các assert thực sự có trong test đó; các điều kiện mở rộng/operation_key/service đề xuất vẫn DESIGNED. Không dùng test của core để xác nhận service chưa tồn tại.
