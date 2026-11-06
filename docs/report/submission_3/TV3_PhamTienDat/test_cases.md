# Test cases SS3 - revision 06/11/2026

Các test prototype hiện có đã chạy trong bộ49 test baseline; log chung ở docs/audit/submission_3/review_20261106/pytest-baseline.txt. Không có class service đề xuất đang chạy; không ghi PASS thay cho contract test.

## UC_SS3_01

- **PASS (prototype):** `tests/test_submission_2_acceptance.py::test_dashboard_shows_actual_booking_ledger_and_revenue`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
## UC_SS3_02

- **PASS (prototype):** `tests/test_core_state_and_billing.py::test_occupancy_threshold_levels`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.

## Các ca thiết kế chưa thực thi (DESIGNED)

### SS3-D01 - Doanh thu toàn hệ thống

**Đầu vào/thao tác:** ledger có cọc50.000, hoàn40.000, thuSS1=10.000, SS2=5.000, SS5=7.000, debt3.000.

**Mong đợi:** Collected22.000, held/debt tách riêng, không lấy tổng tiền cọc.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.

### SS3-D02 - Power có offline

**Đầu vào/thao tác:** 10 cổng,3 available,2 offline; 5 phiên đang CHARGING*11 kW.

**Mong đợi:** Công suất55 kW, không (10-3)*7.4; snapshot không thay state.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.
