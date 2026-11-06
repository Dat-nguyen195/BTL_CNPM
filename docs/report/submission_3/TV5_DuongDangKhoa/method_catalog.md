# Danh mục mọi phương thức SS5 - revision 06/11/2026

Chữ ký dưới đây khớp class diagram. Mô tả bổ sung cho bản bàn giao; kiểu dữ liệu/đơn vị và class descriptions đọc cùng REPORT_SUB3.md. Không suy ra service đề xuất đã tồn tại từ test của hàm core.

## `ChargingRequest.__post_init__`

**Chữ ký:** `__post_init__() -> None`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** ChargingRequest đã có. Sau khởi tạo dataclass, nếu priority_score==0 thì tính từ calculate_priority; score khác0 được giữ. Cần battery_soc hữu hạn0–100 từ caller; core chưa validation đầy đủ. Không thêm queue hoặc thu phí.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ChargingRequest.__repr__`

**Chữ ký:** `__repr__() -> str`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** ChargingRequest đã có. Tạo chuỗi vehicle/SoC/priority để debug, không cập nhật request/queue. Gọi lặp cho cùng dữ liệu trả cùng chuỗi.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.__init__`

**Chữ ký:** `__init__(cap_kw: float = HUB_POWER_CAP_KW) -> None`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Scheduler đã có. Nhận cap_kw mặc định150 kW, tạo queue và active_sessions rỗng. Thiết kế ràng buộc cap_kw>0/hữu hạn; khởi tạo không đặt cổng/thu phí.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.calculate_priority`

**Chữ ký:** `calculate_priority(request: ChargingRequest) -> float`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Static đã có. Score=0.5*(100-SoC)+100*I(SoC<20)+60*I(has_booking)+30*I(SoC<50). Trả float; ví dụ SoC5 không booking177.5, SoC30 không booking65, có booking125. Thuần đọc; chưa có thành phần giá điện hoặc thời gian chờ tăng điểm theo SRS, requested_at chỉ dùng phá hòa.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.add_request`

**Chữ ký:** `add_request(request: ChargingRequest) -> None`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Đã có: bỏ request cũ cùng vehicle_id khỏi queue, tính lại score rồi append request mới. Không tự allocate hoặc kiểm tra trùng xe trong active_sessions; yêu cầu active-dedup do service thiết kế kiểm tra. Không đổi wallet/cổng.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.remove_request`

**Chữ ký:** `remove_request(vehicle_id: str) -> Optional[ChargingRequest]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Đã có: tìm vehicle_id trong queue, xóa và trả ChargingRequest hoặc None nếu không có. Gọi lặp trả None và không tác động session đang sạc.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.get_sorted_queue`

**Chữ ký:** `get_sorted_queue() -> List[ChargingRequest]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Đã có: trả bản sắp xếp theo (-priority_score,requested_at,vehicle_id), không sửa thứ tự lưu của queue hay allocate. Bảo đảm tie deterministic khi requested_at/ID đã cố định.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.allocate_ports`

**Chữ ký:** `allocate_ports(hub_id: str, available_port_count: int, current_active_kw: float = 0.0) -> List[Dict]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Đã có: theo Hub và số cổng available, ưu tiên queue, kiểm tra active power đang có và current_active_kw trước thêm port_kw; trả danh sách allocation, xóa request được nhận và tạo session CHARGING. Không vượt cap khi gọi liên tiếp; không tự giảm charging_ports của Hub ngoài scheduler, UI/service chịu đồng bộ. Caller loại cổng offline. Không đảm bảo port ID vật lý hoặc giao dịch SS2/SS7.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.advance_simulation_tick`

**Chữ ký:** `advance_simulation_tick(minutes: int = 15) -> List[Dict]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Đã có: tăng mức pin/energy theo minutes, phát ngưỡng90%, đạt target ghi completed và GRACE_PERIOD. Sau15 phút grace, mỗi khối15 phút bắt đầu tính10.000 VNĐ; cập nhật session, trả sự kiện. Mỗi lời gọi là một bước thời gian mới, không idempotent; retry phải do service/key kiểm soát. Không tự thu ví; core dùng giờ session thực khi tạo, cần adapter đồng hồ mô phỏng.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.unplug_vehicle`

**Chữ ký:** `unplug_vehicle(session_id: str) -> Optional[ChargingSession]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Đã có: pop session_id khỏi active_sessions, trả ChargingSession hoặc None. Lặp không tháo phiên hai lần. UI/service trả port/count và chuyển trạng thái xe, đối soát phí; hàm scheduler không tự thay Hub/wallet.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SmartChargingScheduler.get_queue_as_dicts`

**Chữ ký:** `get_queue_as_dicts() -> list`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Đã có: trả danh sách dictionary biểu diễn queue cho UI, không tạo request hay quyết toán. Không coi returned list là dữ liệu giao dịch có khóa hoặc snapshot toàn hệ thống.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ChargingService.request_charging`

**Chữ ký:** `request_charging(owner_id: str, vehicle_id: str, hub_id: str, current_soc: float, target_soc: float = 100.0, reservation_id: Optional[str] = None) -> OperationResult[ChargingRequestResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** INT-01 (thiết kế TV5). Xe/owner/Hub hợp lệ, check-in đã thành công, SoC0–100 và target>=current. Tạo request có ID ổn định, chưa có session/cổng khi còn chờ; thêm queue, cấp theo power/cổng thực khi có khả năng. Không cấp trùng cùng lượt/xe; NOT_FOUND/FORBIDDEN/INVALID_STATE/INVALID_INPUT không commit. Prototype SS2 giảm cổng tổng hợp trực tiếp, chưa gọi service này.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ChargingService.get_bill`

**Chữ ký:** `get_bill(session_id: str) -> OperationResult[ChargingBill]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** INT-02 (thiết kế TV5). Tìm session_id và đối soát energy_delivered_kwh, giá/phí, charge_id và khoản đã thu từ ledger. Trả ChargingBill chỉ đọc; gọi lặp không trừ ví hoặc tăng phí giả. Phiên không có trả NOT_FOUND. SS2 lấy dòng phí còn phải thu, không tính lại giá điện/quá giờ độc lập.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ChargingService.handle_port_failure`

**Chữ ký:** `handle_port_failure(hub_id: str, port_ids: list[str], operation_key: str) -> OperationResult[PortFailureResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** INT-05 (thiết kế TV5), chỉ trong coordinator Apply SS7. Kiểm tra Hub, port_ids duy nhất thuộc Hub và operation_key; ngắt các phiên liên quan, đưa về chờ hợp lệ, cập nhật port offline và công suất, trả PortFailureResult. Không thay capacity đỗ. Stage cùng preview, lỗi rollback toàn bộ. Lặp key/cùng nội dung không ngắt lần hai; CONFLICTING_OPERATION/NOT_FOUND/INVALID_STATE. Prototype chưa có adapter này và cổng chỉ là số đếm ở simulator.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingFunctions.settle_overstay_charging`

**Chữ ký:** `settle_overstay_charging(wallet: Dict[str, Any], session_id: str, vehicle_id: str, overstay_fee: int, energy_fee: int=0, kwh_charged: float=0.0, sim_time: Optional[str]=None) -> Dict[str, Any]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Hàm module billing hiện có. Nhận phí overstay/energy đã tính và session_id/vehicle_id; thu tối đa số dư, ghi nợ còn thiếu, append invoice/ledger. Không tự tái tính tariff. Không có operation_key/charge_id dedup toàn cục; caller chỉ gọi một lần theo vòng đời unplug. Phí tiền VNĐ nguyên không âm là điều kiện caller phải bảo vệ.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingFunctions.calculate_private_ev_bill`

**Chữ ký:** `calculate_private_ev_bill(parking_fee: int=PARKING_PER_VISIT_VND, kwh_consumed: float=0.0, checkin_time_str: Optional[str]=None, overstay_minutes: int=0) -> Dict[str, Any]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Hàm module billing hiện có, thuần tính toán phí đỗ/kWh theo khung giờ và phí overstay. Trả dictionary phân rã phí, không đổi ví/Hub. parking_fee mặc định5.000 VNĐ/lượt, tariff7.000 cao điểm/3.000 thấp điểm; không mô hình hourly parking hay tích phân biểu giá theo từng tick.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingFunctions.record_transaction`

**Chữ ký:** `record_transaction(wallet: Dict[str, Any], tx_type: str, amount: int, booking_id: Optional[str]=None, note: str='', sim_time: Optional[str]=None) -> Dict[str, Any]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Hàm module billing hiện có: append ledger entry mới với tx_id, time/type/amount và balance_after/held_after/debt_after, booking_id/note. Caller đã thực hiện thay đổi số dư; hàm không tự giữ/hoàn/thu và không kiểm tra dedup. Gọi hai lần tạo hai entry; đây không là một API idempotent.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingFunctions.record_wallet_debt`

**Chữ ký:** `record_wallet_debt(wallet: Dict[str, Any], amount: int, reason: str='', sim_time: Optional[str]=None) -> None`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Hàm module billing hiện có: cộng khoản thiếu vào debt và ghi ledger theo reason/sim_time; amount<=0 không phát sinh nợ. Gọi lại cùng amount vẫn có thể cộng thêm; caller kiểm soát vòng đời. Không coi ghi nợ là doanh thu thực thu.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingService.settle_invoice`

**Chữ ký:** `settle_invoice(owner_id: str, reference_id: str, charge_lines: list[ChargeLine], operation_key: str) -> OperationResult[SettlementResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Chỉ thu charge_id chưa thu, cùng ID khác tiền trả CONFLICTING_CHARGE. Đối trừ/hoàn cọc đúng reference rồi trừ số dư tối đa phần có thể thu và ghi nợ phần thiếu; paid/refunded/debt lấy từ ledger. Gọi lặp cùng key trả kết quả cũ, không thu lại phí SS5 ở SS2. Prototype có nhiều hàm thu trực tiếp, chưa có BillingService hay dedup charge_id. Thiết kế phải stage tất cả thay đổi trước commit.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## Class descriptions bổ sung

`BillingFunctions` là nhóm hàm ở core/billing.py, không phải class instance; mọi phương thức được vẽ đã mô tả ở trên. `BillingService`, `ChargeLine`, `OperationResult` là hợp đồng thuộc TV1, không định nghĩa lại thành lớp SS5. DTO ChargingRequestResult/ChargingBill/PortFailureResult và ChargingPort thuộc TV5, không có phương thức ngoài các thuộc tính; số liệu kWh/kW/VNĐ và quan hệ được ghi trong báo cáo. `queue_length` là property đọc int, không phải method bị bỏ mô tả; đọc len(_queue), không thay đổi dữ liệu.
