# Truy vết SS6 - revision 06/11/2026

ID US/FR lấy từ SRS, UC và đường dẫn scenario/sequence/activity kế thừa manifest Sub2. Các tên alias cũ trong trường functions của Sub2 không chứng minh code có method tương ứng; bảng này dùng tên hiện tại.

## UC_SS6_01 - Mô phỏng tăng đột biến nhu cầu khách Metro (What-if Metro Surge)

- **Yêu cầu:** US-21, FR-12.
- **Scenario:** [UC_SS6_HoangVanTan.md](<../../../../docs/diagrams/Use-case detail-scenario/SS6/Usecase scenario/UC_SS6_HoangVanTan.md>).
- **Sequence:** [UC_SS6_01_HoangVanTan_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS6/Sequence diagrams/UC_SS6_01_HoangVanTan_sequence.puml>).
- **Activity:** [UC_SS6_01_HoangVanTan_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS6/Activity diagrams/UC_SS6_01_HoangVanTan_activity.puml>).
- **Thiết kế:** `DemandSimulationService.preview_demand`, `SimulationCoordinator.apply_preview`, `HubEventSimulator.simulate_metro_surge`. Class diagram SS6, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_simulations.py::test_metro_surge_deepcopy_isolation_and_unserved_students`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS6_02 - Dự báo phụ tải nhu cầu và phân tích hàng đợi 24h

- **Yêu cầu:** US-22, FR-13.
- **Scenario:** [UC_SS6_HoangVanTan.md](<../../../../docs/diagrams/Use-case detail-scenario/SS6/Usecase scenario/UC_SS6_HoangVanTan.md>).
- **Sequence:** [UC_SS6_02_HoangVanTan_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS6/Sequence diagrams/UC_SS6_02_HoangVanTan_sequence.puml>).
- **Activity:** [UC_SS6_02_HoangVanTan_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS6/Activity diagrams/UC_SS6_02_HoangVanTan_activity.puml>).
- **Thiết kế:** `ForecastService.forecast`, `HubEventSimulator.generate_demand_forecast`. Class diagram SS6, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_submission_2_acceptance.py::test_forecast_24h_queue_wait_and_reproducibility`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.
