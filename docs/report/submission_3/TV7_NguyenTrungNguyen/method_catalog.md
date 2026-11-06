# Danh mục mọi phương thức SS7 - revision 06/11/2026

Chữ ký dưới đây khớp class diagram. Mô tả bổ sung cho bản bàn giao; kiểu dữ liệu/đơn vị và class descriptions đọc cùng REPORT_SUB3.md. Không suy ra service đề xuất đã tồn tại từ test của hàm core.

## `InfrastructureSimulationService.preview_port_failure`

**Chữ ký:** `preview_port_failure(hub_id: str, num_ports_down: int, seed: int = 42) -> OperationResult[SimulationPreview]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** INT-09 đề xuất. Hub tồn tại, số cổng nguyên không âm và không vượt tập cổng hoạt động hợp lệ; snapshot baseline_version, gọi engine/adapter rồi đóng gói PORT_FAILURE với charging_effects/summary/is_applied. Không commit Hub/phiên/booking trước Apply. Invalid/NOT_FOUND không tạo preview hợp lệ; dùng DTO/INT-10 TV6, không tạo coordinator thứ hai.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ReroutingService.suggest_hubs`

**Chữ ký:** `suggest_hubs(target_hub_id: str, need_slots: bool = True, need_ports: bool = False, limit: int = 2) -> OperationResult[list[RouteSuggestion]]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** INT-06 đề xuất. Hub gốc tồn tại, limit>0; lọc nhu cầu chỗ/cổng và operational status, loại Hub gốc, xếp khoảng cách Haversine km rồi ID để phá hòa. Trả list RouteSuggestion (rỗng là hợp lệ), không đổi booking/cọc. Prototype mapping find_alternative_hubs/find_nearest_alternative_hubs chưa lọc OFFLINE chuẩn. Khi nhận gợi ý phải kiểm tra lại capacity/version ở INT-07 sau xác nhận.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `HubEventSimulator.simulate_port_failure`

**Chữ ký:** `simulate_port_failure(target_hub_id: str = "HUB-004", num_ports_down: int = 3, seed: Optional[int] = 42) -> tuple[list[dict],list[str],dict]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Engine hiện có: deepcopy _original, xác định Hub, phân chia busy/free bị ảnh hưởng bằng số đếm, chuyển xe CHARGING ảnh hưởng sang WAITING, cập nhật available/offline và trả hubs/log/metrics. Không đổi slot đỗ hoặc dữ liệu nguồn. Hub không tồn tại trả metrics rỗng; core chưa chặn đầy đủ số âm/lỗi lặp/offline đã có, không có port-ID/session adapter.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.
