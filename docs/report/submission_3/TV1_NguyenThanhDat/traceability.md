# Truy vết SS1 - revision 06/11/2026

ID US/FR lấy từ SRS, UC và đường dẫn scenario/sequence/activity kế thừa manifest Sub2. Các tên alias cũ trong trường functions của Sub2 không chứng minh code có method tương ứng; bảng này dùng tên hiện tại.

## UC_SS1_01 - Tra cứu, Đặt xe & Nhận xe qua QR/PIN

- **Yêu cầu:** US-01, US-02, US-03, US-03b, US-04, FR-01, FR-01b, FR-01c.
- **Scenario:** [UC_SS1_NguyenThanhDat.md](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Usecase scenario/UC_SS1_NguyenThanhDat.md>).
- **Sequence:** [UC_SS1_01_NguyenThanhDat_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Sequence diagrams/UC_SS1_01_NguyenThanhDat_sequence.puml>).
- **Activity:** [UC_SS1_01_NguyenThanhDat_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Activity diagrams/UC_SS1_01_NguyenThanhDat_activity.puml>).
- **Thiết kế:** `BookingService.create_booking`, `BookingService.pickup`. Class diagram SS1, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_core_state_and_billing.py::test_booking_pickup_return_capacity_conservation`, `tests/test_submission_2_acceptance.py::test_student_ui_filters_available_vehicles_and_books_voucher`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS1_02 - Trả xe, Cập nhật vị trí & Quyết toán ví điện tử

- **Yêu cầu:** US-05b, US-06, FR-01c, FR-15b.
- **Scenario:** [UC_SS1_NguyenThanhDat.md](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Usecase scenario/UC_SS1_NguyenThanhDat.md>).
- **Sequence:** [UC_SS1_02_NguyenThanhDat_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Sequence diagrams/UC_SS1_02_NguyenThanhDat_sequence.puml>).
- **Activity:** [UC_SS1_02_NguyenThanhDat_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Activity diagrams/UC_SS1_02_NguyenThanhDat_activity.puml>).
- **Thiết kế:** `BookingService.return_vehicle`, `BillingService.settle_invoice`. Class diagram SS1, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_core_state_and_billing.py::test_booking_pickup_return_capacity_conservation`, `tests/test_core_state_and_billing.py::test_no_silent_debt_loss`, `tests/test_submission_2_readiness_fixes.py::test_r08_alternate_hub_return_releases_destination_hold`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS1_03 - Hủy đặt chỗ & Hoàn cọc / Phạt quá giờ

- **Yêu cầu:** US-05, FR-02.
- **Scenario:** [UC_SS1_NguyenThanhDat.md](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Usecase scenario/UC_SS1_NguyenThanhDat.md>).
- **Sequence:** [UC_SS1_03_NguyenThanhDat_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Sequence diagrams/UC_SS1_03_NguyenThanhDat_sequence.puml>).
- **Activity:** [UC_SS1_03_NguyenThanhDat_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS1/Activity diagrams/UC_SS1_03_NguyenThanhDat_activity.puml>).
- **Thiết kế:** `BookingService.cancel`, `BookingService.expire_reservations`, `BillingService.release_deposit`, `BillingService.settle_no_show`. Class diagram SS1, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_core_state_and_billing.py::test_noshow_expiry_and_penalty`, `tests/test_core_state_and_billing.py::test_early_cancellation_full_refund`, `tests/test_reservation_30_minutes.py::test_reservation_30_minute_boundary_and_single_settlement`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.
