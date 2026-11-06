# Truy vết SS5 - revision 06/11/2026

ID US/FR lấy từ SRS, UC và đường dẫn scenario/sequence/activity kế thừa manifest Sub2. Các tên alias cũ trong trường functions của Sub2 không chứng minh code có method tương ứng; bảng này dùng tên hiện tại.

## UC_SS5_01 - Lập lịch sạc tự động theo điểm ưu tiên & Giới hạn công suất lưới

- **Yêu cầu:** US-10, US-12, US-18, US-20, FR-04, FR-09, FR-11.
- **Scenario:** [UC_SS5_DuongDangKhoa.md](<../../../../docs/diagrams/Use-case detail-scenario/SS5/Usecase scenario/UC_SS5_DuongDangKhoa.md>).
- **Sequence:** [UC_SS5_01_DuongDangKhoa_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS5/Sequence diagrams/UC_SS5_01_DuongDangKhoa_sequence.puml>).
- **Activity:** [UC_SS5_01_DuongDangKhoa_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS5/Activity diagrams/UC_SS5_01_DuongDangKhoa_activity.puml>).
- **Thiết kế:** `SmartChargingScheduler.calculate_priority`, `SmartChargingScheduler.allocate_ports`, `ChargingService.request_charging`. Class diagram SS5, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_scheduler_and_charging.py::test_priority_scores_matching_plan_specification`, `tests/test_scheduler_and_charging.py::test_deterministic_tie_breaking`, `tests/test_scheduler_and_charging.py::test_allocation_and_power_cap`, `tests/test_submission_2_readiness_fixes.py::test_r09_repeated_charging_allocation_obeys_power_cap`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS5_02 - Giám sát hàng chờ sạc, hoàn thành, ân hạn & Tính phí quá giờ

- **Yêu cầu:** US-12, US-19, US-19b, FR-05b, FR-10, FR-10b, FR-15b.
- **Scenario:** [UC_SS5_DuongDangKhoa.md](<../../../../docs/diagrams/Use-case detail-scenario/SS5/Usecase scenario/UC_SS5_DuongDangKhoa.md>).
- **Sequence:** [UC_SS5_02_DuongDangKhoa_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS5/Sequence diagrams/UC_SS5_02_DuongDangKhoa_sequence.puml>).
- **Activity:** [UC_SS5_02_DuongDangKhoa_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS5/Activity diagrams/UC_SS5_02_DuongDangKhoa_activity.puml>).
- **Thiết kế:** `SmartChargingScheduler.advance_simulation_tick`, `SmartChargingScheduler.unplug_vehicle`, `ChargingService.get_bill`. Class diagram SS5, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_scheduler_and_charging.py::test_simulation_tick_and_overstay`, `tests/test_submission_2_acceptance.py::test_charging_completion_notification_survives_rerun_and_receipt_is_recorded`, `tests/test_submission_2_readiness_fixes.py::test_r11_overstay_charging_settlement_and_debt`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.
