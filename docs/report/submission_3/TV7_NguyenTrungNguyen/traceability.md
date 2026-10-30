# Truy vết cá nhân — Nguyễn Trung Nguyên — SS7

**Phạm vi:** `UC_SS7_01`, `UC_SS7_02`
**Trạng thái:** Bản truy vết đã hoàn thiện; TV7 xác nhận nội dung ngày 30/10/2026.

[Manifest Sub2](<../../../traceability/submission_2.json>) · [Báo cáo TV7](<REPORT_SUB3.md>) · [Hợp đồng dùng chung](<../shared/shared_contracts.md>)

| US | FR | UC / scenario | Sequence / activity | Lớp, method và giao tiếp Sub3 | Code prototype / test |
|---|---|---|---|---|---|
| `US-23`, `US-24` | `FR-14`, `FR-15` | `UC_SS7_01` — mô phỏng sự cố hạ tầng, lỗi cổng/mất điện | [Scenario](<../../../diagrams/Use-case detail-scenario/SS7/Usecase scenario/UC_SS7_NguyenTrungNguyen.md>); [sequence](<../../../diagrams/Use-case detail-scenario/SS7/Sequence diagrams/UC_SS7_01_NguyenTrungNguyen_sequence.puml>); [activity](<../../../diagrams/Use-case detail-scenario/SS7/Activity diagrams/UC_SS7_01_NguyenTrungNguyen_activity.puml>) | `InfrastructureFailure`; `InfrastructureSimulationService.preview_port_failure` — INT-09; `SimulationCoordinator.apply_preview` — INT-10 (TV6); `ChargingService.handle_port_failure` — INT-05 (TV5); `SS7-MTH-01/02` | `src/components/sim_infrastructure.py`; `src/core/simulator.py`; hiện có `test_port_failure_distinguishes_free_vs_busy_ports`; thiết kế bổ sung `SS7-TC-01`–`SS7-TC-03` |
| `US-24`, `US-24b` | `FR-15`, `FR-15c` | `UC_SS7_02` — gợi ý Hub thay thế và cảnh báo | [Scenario](<../../../diagrams/Use-case detail-scenario/SS7/Usecase scenario/UC_SS7_NguyenTrungNguyen.md>); [sequence](<../../../diagrams/Use-case detail-scenario/SS7/Sequence diagrams/UC_SS7_02_NguyenTrungNguyen_sequence.puml>); [activity](<../../../diagrams/Use-case detail-scenario/SS7/Activity diagrams/UC_SS7_02_NguyenTrungNguyen_activity.puml>) | `RouteSuggestion`; `ReroutingService.suggest_hubs` — INT-06; sau xác nhận, `BookingService.accept_rerouting` — INT-07 (TV1); `SS7-MTH-03` | `src/components/sim_infrastructure.py`; `src/core/routing.py`; `src/core/booking.py`; hiện có `test_rerouting_selects_two_hubs_and_transfers_hold_once`; thiết kế bổ sung `SS7-TC-04`–`SS7-TC-06` |

## Luồng gọi và trạng thái triển khai

### UC_SS7_01

1. UI lấy `hubs` và `state_version` của session.
2. Prototype tạo `HubEventSimulator` và gọi `simulate_port_failure(target_hub_id, num_ports_down, seed=42)`.
3. Kết quả trên bản sao sâu được giữ trong `sim_preview_ss7`; người dùng có thể xem hoặc hủy mà không thay Hub gốc.
4. Prototype chỉ Apply khi version nền bằng version hiện tại, sau đó gán snapshot Hub và tăng version. Giao tiếp đích của Sub3 là `SimulationCoordinator.apply_preview` (INT-10), tích hợp `ChargingService.handle_port_failure` (INT-05) và chống Apply trùng.

**Nhánh cần thể hiện rõ:** Hub không tồn tại; số cổng không hợp lệ; cổng lỗi ảnh hưởng cổng rảnh/đang bận; preview cũ; không có tích hợp nguồn điện/IoT thật. Cờ `seed` hiện không quyết định kết quả hàm mô phỏng cổng lỗi.

### UC_SS7_02

1. UI/SS7 gọi `ReroutingService.suggest_hubs` với nhu cầu thực tế. Hiện UI mô phỏng cổng lỗi yêu cầu cổng sạc (`need_ports=True`, `need_slots=False`); luồng trả xe phải yêu cầu slot.
2. Service trả danh sách snapshot xếp theo khoảng cách; danh sách rỗng là nhánh hợp lệ. Không coi gợi ý là đặt giữ chỗ.
3. Người dùng xác nhận lựa chọn; UI chuyển yêu cầu cho TV1 qua `BookingService.accept_rerouting` (INT-07). Service kiểm tra lại version, booking và capacity, chuyển giữ chỗ và cấp tối đa một lần ưu đãi 15 phút.

**Khác biệt lịch sử:** sequence/activity Sub2 có nội dung SSO/IoT, trạng thái `OFFLINE`, tự động Apply và Euclidean; các thành phần này chưa có trong prototype. Hàm routing hiện dùng Haversine, lọc capacity nhưng chưa loại Hub theo trạng thái hoạt động chuẩn. Cần kiểm tra và xin chủ sở hữu Sub2 xác nhận mọi chỉnh sửa trước khi sửa nguồn lịch sử.

## Ca kiểm thử

Chi tiết dữ liệu, bước chạy, kết quả mong đợi và trạng thái hiện tại ở [test_cases.md](<test_cases.md>). Các test cũ chỉ được dẫn như kiểm tra phần assertion tương ứng; không xem chúng là bằng chứng cho toàn bộ UC.
