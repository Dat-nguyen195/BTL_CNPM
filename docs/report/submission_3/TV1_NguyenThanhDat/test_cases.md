# Test cases SS1 - revision 06/11/2026

Các test prototype hiện có đã chạy trong bộ49 test baseline; log chung ở docs/audit/submission_3/review_20261106/pytest-baseline.txt. Không có class service đề xuất đang chạy; không ghi PASS thay cho contract test.

## UC_SS1_01

- **PASS (prototype):** `tests/test_core_state_and_billing.py::test_booking_pickup_return_capacity_conservation`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
- **PASS (prototype):** `tests/test_submission_2_acceptance.py::test_student_ui_filters_available_vehicles_and_books_voucher`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
## UC_SS1_02

- **PASS (prototype):** `tests/test_core_state_and_billing.py::test_booking_pickup_return_capacity_conservation`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
- **PASS (prototype):** `tests/test_core_state_and_billing.py::test_no_silent_debt_loss`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
- **PASS (prototype):** `tests/test_submission_2_readiness_fixes.py::test_r08_alternate_hub_return_releases_destination_hold`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
## UC_SS1_03

- **PASS (prototype):** `tests/test_core_state_and_billing.py::test_noshow_expiry_and_penalty`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
- **PASS (prototype):** `tests/test_core_state_and_billing.py::test_early_cancellation_full_refund`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
- **PASS (prototype):** `tests/test_reservation_30_minutes.py::test_reservation_30_minute_boundary_and_single_settlement`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.

## Các ca thiết kế chưa thực thi (DESIGNED)

### SS1-D01 - Lặp settle_invoice cùng charge_id

**Đầu vào/thao tác:** reference A đã có charge_id C đã thu10.000; gọi cùng key rồi đổi key nhưng cùng C.

**Mong đợi:** Trả kết quả cũ, không trừ lần hai; C đổi amount phải CONFLICTING_CHARGE, ví không đổi.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.

### SS1-D02 - Authorization và ownership ở service

**Đầu vào/thao tác:** xe PERSONAL/owner khác; gọi create_booking trực tiếp.

**Mong đợi:** Từ chối FORBIDDEN/INVALID_STATE, không giữ cọc/chỗ; core hiện chưa chặn ownership đầy đủ.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.

### SS1-D03 - Reroute nhiều Hub

**Đầu vào/thao tác:** booking đổi Hub B rồi C bằng hai key.

**Mong đợi:** Ưu đãi tổng15 phút, không cộng30; TTL không đổi.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.
