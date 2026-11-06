# Truy vết SS4 - revision 06/11/2026

ID US/FR lấy từ SRS, UC và đường dẫn scenario/sequence/activity kế thừa manifest Sub2. Các tên alias cũ trong trường functions của Sub2 không chứng minh code có method tương ứng; bảng này dùng tên hiện tại.

## UC_SS4_01 - Lập lệnh điều chuyển phương tiện cân bằng phụ tải

- **Yêu cầu:** US-15, FR-07.
- **Scenario:** [UC_SS4_DangHoangQuyNhan.md](<../../../../docs/diagrams/Use-case detail-scenario/SS4/Usecase scenario/UC_SS4_DangHoangQuyNhan.md>).
- **Sequence:** [UC_SS4_01_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS4/Sequence diagrams/UC_SS4_01_sequence.puml>).
- **Activity:** [UC_SS4_01_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS4/Activity diagrams/UC_SS4_01_activity.puml>).
- **Thiết kế:** `DispatchService.create_order`, `DispatchService.complete_order`. Class diagram SS4, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_submission_2_acceptance.py::test_dispatch_ui_moves_vehicle_and_conserves_capacity`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS4_02 - Báo cáo, tiếp nhận xử lý và khắc phục sự cố phương tiện

- **Yêu cầu:** US-16, US-17, FR-08.
- **Scenario:** [UC_SS4_DangHoangQuyNhan.md](<../../../../docs/diagrams/Use-case detail-scenario/SS4/Usecase scenario/UC_SS4_DangHoangQuyNhan.md>).
- **Sequence:** [UC_SS4_02_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS4/Sequence diagrams/UC_SS4_02_sequence.puml>).
- **Activity:** [UC_SS4_02_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS4/Activity diagrams/UC_SS4_02_activity.puml>).
- **Thiết kế:** `IncidentService.report_vehicle_incident`, `IncidentService.acknowledge`, `IncidentService.resolve`. Class diagram SS4, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_submission_2_acceptance.py::test_incident_ui_report_acknowledge_resolve_and_history`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.
