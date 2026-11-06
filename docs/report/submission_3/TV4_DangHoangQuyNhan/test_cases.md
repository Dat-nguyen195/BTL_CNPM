# Test cases SS4 - revision 06/11/2026

Các test prototype hiện có đã chạy trong bộ49 test baseline; log chung ở docs/audit/submission_3/review_20261106/pytest-baseline.txt. Không có class service đề xuất đang chạy; không ghi PASS thay cho contract test.

## UC_SS4_01

- **PASS (prototype):** `tests/test_submission_2_acceptance.py::test_dispatch_ui_moves_vehicle_and_conserves_capacity`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
## UC_SS4_02

- **PASS (prototype):** `tests/test_submission_2_acceptance.py::test_incident_ui_report_acknowledge_resolve_and_history`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.

## Các ca thiết kế chưa thực thi (DESIGNED)

### SS4-D01 - Hub đích thay đổi trước nhận

**Đầu vào/thao tác:** lệnh giữ2 chỗ nhưng hold bị mất/Hub không còn hợp lệ.

**Mong đợi:** Reject/giữ nguyên lệnh và xe, không commit một phần.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.

### SS4-D02 - Resolve xe còn binding

**Đầu vào/thao tác:** xe INCIDENT đang có charging/booking binding.

**Mong đợi:** Không đưa AVAILABLE cho đến khi binding được xử lý; ghi lịch sử người/giờ.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.

### SS4-D03 - Tạo/hoàn tất lệnh lặp

**Đầu vào/thao tác:** cùng operation_key cho create hoặc complete gọi2 lần.

**Mong đợi:** Một lệnh, một bản xe tại Hub đích, không thay count lần hai.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.
