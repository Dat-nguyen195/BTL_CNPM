# Truy vết SS2 - revision 06/11/2026

ID US/FR lấy từ SRS, UC và đường dẫn scenario/sequence/activity kế thừa manifest Sub2. Các tên alias cũ trong trường functions của Sub2 không chứng minh code có method tương ứng; bảng này dùng tên hiện tại.

## UC_SS2_01 - Đăng ký xe EV cá nhân lên hệ thống

- **Yêu cầu:** US-08, FR-03.
- **Scenario:** [UC_SS2_NguyenAnhTai.md](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Usecase scenario/UC_SS2_NguyenAnhTai.md>).
- **Sequence:** [UC_SS2_01_NguyenAnhTai_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_01_NguyenAnhTai_sequence.puml>).
- **Activity:** [UC_SS2_01_NguyenAnhTai_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_01_NguyenAnhTai_activity.puml>).
- **Thiết kế:** `PersonalEVService.register_personal_ev`, `PersonalVehicle.normalize_plate`. Class diagram SS2, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_personal_ev.py::test_register_personal_ev_success_and_duplicate`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS2_02 - Đặt trước chỗ đỗ và nhu cầu sạc xe EV cá nhân

- **Yêu cầu:** US-09, US-10, FR-04, FR-05b.
- **Scenario:** [UC_SS2_NguyenAnhTai.md](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Usecase scenario/UC_SS2_NguyenAnhTai.md>).
- **Sequence:** [UC_SS2_02_NguyenAnhTai_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_02_NguyenAnhTai_sequence.puml>).
- **Activity:** [UC_SS2_02_NguyenAnhTai_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_02_NguyenAnhTai_activity.puml>).
- **Thiết kế:** `PersonalEVService.reserve_personal_ev_slot`, `PersonalEVService.sweep_expired_personal_reservations`. Class diagram SS2, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_personal_ev.py::test_reserve_and_checkin_checkout_lifecycle`, `tests/test_submission_2_acceptance.py::test_personal_future_arrival_and_exact_expiry`, `tests/test_submission_2_acceptance.py::test_personal_invalid_reservation_has_no_financial_or_capacity_effect`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS2_03 - Check-in xe EV cá nhân tại cổng Hub (QR/Biển số)

- **Yêu cầu:** US-11b, US-10, FR-03b, FR-04.
- **Scenario:** [UC_SS2_NguyenAnhTai.md](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Usecase scenario/UC_SS2_NguyenAnhTai.md>).
- **Sequence:** [UC_SS2_03_NguyenAnhTai_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_03_NguyenAnhTai_sequence.puml>).
- **Activity:** [UC_SS2_03_NguyenAnhTai_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_03_NguyenAnhTai_activity.puml>).
- **Thiết kế:** `PersonalEVService.check_in_personal_ev`, `ParkingSession.attach_charging_ref`. Class diagram SS2, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_personal_ev.py::test_reserve_and_checkin_checkout_lifecycle`, `tests/test_reservation_30_minutes.py::test_reservation_30_minute_boundary_and_single_settlement`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS2_04 - Check-out và thanh toán tổng hợp dịch vụ xe EV cá nhân

- **Yêu cầu:** US-09, US-10, US-11, US-11b, FR-03b, FR-05b, FR-15b.
- **Scenario:** [UC_SS2_NguyenAnhTai.md](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Usecase scenario/UC_SS2_NguyenAnhTai.md>).
- **Sequence:** [UC_SS2_04_NguyenAnhTai_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_04_NguyenAnhTai_sequence.puml>).
- **Activity:** [UC_SS2_04_NguyenAnhTai_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_04_NguyenAnhTai_activity.puml>).
- **Thiết kế:** `PersonalEVService.check_out_personal_ev`, `BillingService.settle_invoice`. Class diagram SS2, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_personal_ev.py::test_reserve_and_checkin_checkout_lifecycle`, `tests/test_submission_2_acceptance.py::test_personal_charging_is_billed_once_on_consolidated_checkout`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.
