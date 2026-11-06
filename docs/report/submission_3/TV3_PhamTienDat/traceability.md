# Truy vết SS3 - revision 06/11/2026

ID US/FR lấy từ SRS, UC và đường dẫn scenario/sequence/activity kế thừa manifest Sub2. Các tên alias cũ trong trường functions của Sub2 không chứng minh code có method tương ứng; bảng này dùng tên hiện tại.

## UC_SS3_01 - Giám sát mạng lưới Hub, KPI & Doanh thu thời gian thực

- **Yêu cầu:** US-07, US-13, FR-05, FR-15b.
- **Scenario:** [UC_SS3_PhamTienDat.md](<../../../../docs/diagrams/Use-case detail-scenario/SS3/Usecase scenario/UC_SS3_PhamTienDat.md>).
- **Sequence:** [UC_SS3_01_PhamTienDat_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS3/Sequence diagrams/UC_SS3_01_PhamTienDat_sequence.puml>).
- **Activity:** [UC_SS3_01_PhamTienDat_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS3/Activity diagrams/UC_SS3_01_PhamTienDat_activity.puml>).
- **Thiết kế:** `MonitoringService.get_network_snapshot`. Class diagram SS3, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_submission_2_acceptance.py::test_dashboard_shows_actual_booking_ledger_and_revenue`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS3_02 - Cảnh báo phân cấp chiếm dụng Hub & Sự cố IoT

- **Yêu cầu:** US-13b, US-14, FR-05c, FR-06.
- **Scenario:** [UC_SS3_PhamTienDat.md](<../../../../docs/diagrams/Use-case detail-scenario/SS3/Usecase scenario/UC_SS3_PhamTienDat.md>).
- **Sequence:** [UC_SS3_02_PhamTienDat_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS3/Sequence diagrams/UC_SS3_02_PhamTienDat_sequence.puml>).
- **Activity:** [UC_SS3_02_PhamTienDat_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS3/Activity diagrams/UC_SS3_02_PhamTienDat_activity.puml>).
- **Thiết kế:** `MonitoringService.get_network_snapshot`, `MonitoringService.classify_occupancy`. Class diagram SS3, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_core_state_and_billing.py::test_occupancy_threshold_levels`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.
