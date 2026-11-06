# Truy vết SS7 - revision 06/11/2026

ID US/FR lấy từ SRS, UC và đường dẫn scenario/sequence/activity kế thừa manifest Sub2. Các tên alias cũ trong trường functions của Sub2 không chứng minh code có method tương ứng; bảng này dùng tên hiện tại.

## UC_SS7_01 - Mô phỏng sự cố hạ tầng & Mất điện trạm sạc

- **Yêu cầu:** US-23, US-24, FR-14, FR-15.
- **Scenario:** [UC_SS7_NguyenTrungNguyen.md](<../../../../docs/diagrams/Use-case detail-scenario/SS7/Usecase scenario/UC_SS7_NguyenTrungNguyen.md>).
- **Sequence:** [UC_SS7_01_NguyenTrungNguyen_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS7/Sequence diagrams/UC_SS7_01_NguyenTrungNguyen_sequence.puml>).
- **Activity:** [UC_SS7_01_NguyenTrungNguyen_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS7/Activity diagrams/UC_SS7_01_NguyenTrungNguyen_activity.puml>).
- **Thiết kế:** `InfrastructureSimulationService.preview_port_failure`, `HubEventSimulator.simulate_port_failure`, `SimulationCoordinator.apply_preview`. Class diagram SS7, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_simulations.py::test_port_failure_distinguishes_free_vs_busy_ports`, `tests/test_submission_2_acceptance.py::test_infrastructure_preview_isolated_apply_and_stale_rejected`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.

## UC_SS7_02 - Đề xuất gợi ý điều hướng tự động sang Hub lân cận & Cảnh báo

- **Yêu cầu:** US-24, US-24b, FR-15, FR-15c.
- **Scenario:** [UC_SS7_NguyenTrungNguyen.md](<../../../../docs/diagrams/Use-case detail-scenario/SS7/Usecase scenario/UC_SS7_NguyenTrungNguyen.md>).
- **Sequence:** [UC_SS7_02_NguyenTrungNguyen_sequence.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS7/Sequence diagrams/UC_SS7_02_NguyenTrungNguyen_sequence.puml>).
- **Activity:** [UC_SS7_02_NguyenTrungNguyen_activity.puml](<../../../../docs/diagrams/Use-case detail-scenario/SS7/Activity diagrams/UC_SS7_02_NguyenTrungNguyen_activity.puml>).
- **Thiết kế:** `ReroutingService.suggest_hubs`, `BookingService.accept_rerouting`. Class diagram SS7, catalog cùng thư mục.
- **Luồng truy vết:** kiểm tra điều kiện/nhánh lỗi ở scenario và sequence/activity tương ứng -> phương thức phụ trách ở trên -> test prototype bên dưới; không tự đặt số bước nếu nguồn chưa có đánh số ổn định.
- **Test prototype:** `tests/test_submission_2_acceptance.py::test_rerouting_selects_two_hubs_and_transfers_hold_once`, `tests/test_core_state_and_billing.py::test_haversine_distance_accuracy`.
- **Trạng thái:** thiết kế đã rà soát kỹ thuật; chủ sở hữu chờ xác nhận. Test core/UI hiện có không xác nhận service đề xuất đã được tích hợp đầy đủ.
