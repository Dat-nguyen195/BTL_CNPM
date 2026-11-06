# Test cases SS6 - revision 06/11/2026

Các test prototype hiện có đã chạy trong bộ49 test baseline; log chung ở docs/audit/submission_3/review_20261106/pytest-baseline.txt. Không có class service đề xuất đang chạy; không ghi PASS thay cho contract test.

## UC_SS6_01

- **PASS (prototype):** `tests/test_simulations.py::test_metro_surge_deepcopy_isolation_and_unserved_students`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.
## UC_SS6_02

- **PASS (prototype):** `tests/test_submission_2_acceptance.py::test_forecast_24h_queue_wait_and_reproducibility`; xem assert cụ thể trong nguồn và log baseline. Phạm vi là hành vi core/UI đang có, không phải lớp service OOP.

## Các ca thiết kế chưa thực thi (DESIGNED)

### SS6-D01 - Coordinator stale/duplicate/invalid

**Đầu vào/thao tác:** preview baseline1, current2; hoặc applied=True; hoặc candidate capacity âm.

**Mong đợi:** Stale/invalid từ chối giữ dữ liệu gốc, applied trả already_applied; không tăng version lần hai.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.

### SS6-D02 - INT05 thất bại trong Apply

**Đầu vào/thao tác:** preview PORT_FAILURE; ChargingService.handle_port_failure trả lỗi.

**Mong đợi:** Rollback Hub/port/session toàn bộ, wallet/booking nguyên trạng, version không đổi.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.

### SS6-D03 - DTO chung và validation

**Đầu vào/thao tác:** num_students âm, rate NaN hoặc hours12 tại ForecastService.

**Mong đợi:** INVALID_INPUT, không tạo preview/kết quả24h giả; DTO chứa charging_effects/summary/is_applied.

**Trạng thái:** DESIGNED; cần hiện thực service/adapter trước khi chạy.
