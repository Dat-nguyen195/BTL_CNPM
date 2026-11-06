# Danh mục phương thức SS6 - revision 06/11/2026

Mọi kiểu/đơn vị như class diagram. `OperationResult` là hợp đồng đề xuất; các tuple/dict hiện có được nêu ở ánh xạ. UC chi tiết và test được liên kết trong traceability.md.

## SS6-MTH-01: `DemandSimulationService.preview_demand`

**Chữ ký:** `preview_demand(hub_id: str, num_students: int, seed: int = 42) -> OperationResult[SimulationPreview]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** INT-08, service đề xuất. Hub tồn tại, num_students nguyên >=0. Deepcopy snapshot và lưu baseline_version; gọi engine, đóng gói scenario_type=DEMAND, summary=metrics, charging_effects dự kiến và is_applied=False. Không sửa hubs thật/ví/booking. admitted=min(demand,available_slots), unserved=demand-admitted. Invalid/NOT_FOUND không lưu preview hợp lệ; timestamp log thực không là tiêu chí tái lập.

**Ánh xạ:** `src/core/simulator.py:HubEventSimulator.simulate_metro_surge`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS6-MTH-02: `ForecastService.forecast`

**Chữ ký:** `forecast(hub_id: str, base_arrival_rate: float, surge_multiplier: float, hours: int = 24, seed: int = 42) -> OperationResult[ForecastResult]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** INT-04, service đề xuất. Xác nhận Hub tồn tại, rate/multiplier hữu hạn >=0 và hours=24 cho báo cáo Sub3. Gọi engine với hours tường minh, trả 24 mốc 06:00 đến 05:00, arrivals/queue theo người và wait_time_min theo phút. service_rate=8 xe/giờ là giả định mô hình, không phải số đo từng Hub. Cùng input/seed cùng dữ liệu; không sửa state. INVALID_INPUT/NOT_FOUND nếu không hợp lệ. Prototype UI vẫn mặc định 12, có thể chọn 24.

**Ánh xạ:** `src/core/simulator.py:HubEventSimulator.generate_demand_forecast`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS6-MTH-03: `SimulationCoordinator.apply_preview`

**Chữ ký:** `apply_preview(preview_id: str, expected_version: int) -> OperationResult[ApplyResult]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** INT-10, coordinator dùng chung đề xuất. Tìm preview, kiểm tra baseline_version=expected_version=current version và invariant capacity/tài chính/công suất. Nếu đã apply cùng preview trả already_applied=True trước kiểm tra stale, không tác động lại. Stage candidate và tác động SS5 (INT-05) nếu PORT_FAILURE; chỉ commit toàn bộ khi hợp lệ, tăng version một lần và ghi applied. Không chép ví/booking từ snapshot. NOT_FOUND/STALE_STATE/INVALID_STATE giữ nguyên state. Prototype chỉ có Apply riêng ở UI và version check, chưa có class/coordinator, kiểm tra toàn bộ invariant hoặc giao dịch SS5.

**Ánh xạ:** `src/components/sim_demand.py:render`, `src/components/sim_infrastructure.py:render`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS6-MTH-04: `HubEventSimulator.simulate_metro_surge`

**Chữ ký:** `simulate_metro_surge(target_hub_id: str = "HUB-002", num_new_students: int = 20, seed: Optional[int] = 42) -> tuple[list[dict],list[str],dict]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Đã có trong core. Sao chép _original, tìm Hub, tiếp nhận tối đa số chỗ trống, thêm xe mô phỏng, giảm slots và cấp số cổng tổng hợp cho xe pin thấp; trả hubs/log/metrics. Không sửa nguồn. Hub không tồn tại trả metrics rỗng kèm log. Core chưa validation đầy đủ số âm/kiểu; adapter đề xuất phải chặn. Log timestamp dùng đồng hồ thật; loại log khi so tính tái lập.

**Ánh xạ:** `src/core/simulator.py:HubEventSimulator.simulate_metro_surge`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS6-MTH-05: `HubEventSimulator.generate_demand_forecast`

**Chữ ký:** `generate_demand_forecast(base_arrival_rate: float = 10.0, surge_multiplier: float = 1.0, hours: int = 12, seed: Optional[int] = 42) -> list[dict]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Đã có, static, mặc định thực tế 12 giờ. Cao điểm 7/8/17/18 factor2.5; 9/16/19 factor1.5; còn lại1.0, Gaussian sigma1.5, arrivals=max(0,int(rate*factor*mult+noise)). queue=max(0,queue+arrivals-8), wait=round(queue/8*60,1). Trả list hour/arrivals/queue_length/wait_time_min, không sửa state. Để đáp ứng Sub3 gọi hours=24; không mô tả giá trị mặc định là 24 và không coi wait estimate là đo chờ thực.

**Ánh xạ:** `src/core/simulator.py:HubEventSimulator.generate_demand_forecast`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.
