# Danh mục mọi phương thức SS2 - revision 06/11/2026

Chữ ký dưới đây khớp class diagram. Mô tả bổ sung cho bản bàn giao; kiểu dữ liệu/đơn vị và class descriptions đọc cùng REPORT_SUB3.md. Không suy ra service đề xuất đã tồn tại từ test của hàm core.

## `PersonalVehicle.normalize_plate`

**Chữ ký:** `normalize_plate(raw_plate: str) -> str`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Thuần đọc: nhận raw_plate không rỗng, bỏ dấu cách/dấu gạch ngang và viết hoa để kiểm tra trùng. Trả chuỗi chuẩn hóa; không đăng ký thêm xe hoặc đổi số chỗ. Lớp đề xuất ánh xạ đoạn chuẩn hóa trong register_personal_ev, không có method class thực tế.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalVehicle.is_owned_by`

**Chữ ký:** `is_owned_by(user_id: str) -> bool`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** So sánh user_id với owner_id của xe; trả bool, không đổi dữ liệu. Caller phải kiểm tra quyền trước đặt chỗ/check-in/out, không coi bool này là xác thực tài khoản thật.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ParkingReservation.is_expired`

**Chữ ký:** `is_expired(sim_now: datetime) -> bool`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Trả status=RESERVED và sim_now>=expires_at; chỉ đọc và không tự phạt. Hạn là booking_start_time+30 phút, tại đúng hạn là hết hạn.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ParkingReservation.can_check_in`

**Chữ ký:** `can_check_in(sim_now: datetime) -> bool`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Trả True khi RESERVED và booking_start_time<=sim_now<expires_at. Đến sớm/trạng thái khác/đúng hạn đều False; không tự thay đổi ví/chỗ đỗ.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ParkingSession.attach_charging_ref`

**Chữ ký:** `attach_charging_ref(request_id: str, session_id: str | None = None) -> None`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Chỉ sau check-in hợp lệ. Ghi request_id, session_id tùy chọn; không gán request đang chờ thành đang sạc. Cùng tham chiếu lặp không tạo request khác; tham chiếu xung đột phải INVALID_STATE/CONFLICTING_OPERATION.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ParkingSession.build_parking_charge_line`

**Chữ ký:** `build_parking_charge_line() -> ChargeLine`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Trả ChargeLine có charge_id ổn định theo parking session, kind PARKING và amount_vnd=5.000 VNĐ/lượt của prototype; không trừ ví. SRS theo giờ là chênh lệch chưa giải quyết, không suy ra đã có hourly policy.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVService.register_personal_ev`

**Chữ ký:** `register_personal_ev(owner_id: str, owner_name: str, plate_number: str, vehicle_type: str, brand: str, battery_kwh: float) -> OperationResult[PersonalVehicle]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Kiểm tra owner/biển số/loại xe/dung lượng pin hợp lệ; chuẩn hóa biển số, từ chối trùng, thêm hồ sơ ownership PERSONAL, tăng version. Không đổi Hub/slot. Service thiết kế trả OperationResult, core trả tuple(ok,record,msg), ev_id ánh xạ vehicle_id. Mô tả chi tiết và giới hạn UI/prototype xem mục6 báo cáo.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVService.reserve_personal_ev_slot`

**Chữ ký:** `reserve_personal_ev_slot(owner_id: str, vehicle_id: str, hub_id: str, booking_start_time: datetime, request_charging: bool = False, current_soc: float = 50.0, operation_key: str = "") -> OperationResult[ParkingReservation]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Xác nhận xe thuộc owner và chưa có lượt hoạt động, Hub còn chỗ, booking_start_time không trước sim_now, SoC hợp lệ. Khóa cọc50.000, giảm available_slots và tăng destination_holds đúng một lần; deadline=start+30 phút. Thiếu tiền/nợ/Hub đầy/đầu vào sai giữ nguyên. Service thiết kế thêm operation_key để chống lặp; core chưa có key. Trả reservation trong OperationResult hoặc tuple prototype.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVService.check_in_personal_ev`

**Chữ ký:** `check_in_personal_ev(owner_id: str, reservation_id: str, operation_key: str = "") -> OperationResult[ParkingSession]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Quét hết hạn, yêu cầu RESERVED và start<=now<deadline. Chuyển destination_holds sang hiện diện PERSONAL mà không giảm available lần hai, ghi CHECKED_IN/check_in_time. Service gọi INT-01 nếu request_charging, không tự cấp trùng. Core hiện giảm số cổng nếu có và có thể gán xe CHARGING khi chưa được cấp; phải nêu là giới hạn. Không thực sự mở barie/scan QR vật lý. Lặp từ chối INVALID_STATE, quá hạn EXPIRED.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVService.check_out_personal_ev`

**Chữ ký:** `check_out_personal_ev(owner_id: str, reservation_id: str, operation_key: str = "") -> OperationResult[SettlementResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Chỉ CHECKED_IN. Theo thiết kế lấy phí sạc INT-02 + phí đỗ, quyết toán BillingService bằng charge_id, trả slot/cổng thực sự đã cấp, COMPLETED và invoice. Thiếu số dư ghi nợ, không mất phần thiếu; gọi lại không thu thêm do vòng đời. Core nhận duration_hours/kwh/overstay từ mô phỏng và tự tính phí tại giờ checkout; chưa đo telemetry/thời gian biểu giá tích phân. Owner/key trong service chưa có ở core.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVService.sweep_expired_personal_reservations`

**Chữ ký:** `sweep_expired_personal_reservations(sim_now: datetime) -> OperationResult[list[str]]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Duyệt RESERVED khi sim_now>=arrival_deadline, chuyển EXPIRED, giảm hold/tăng available, phạt10.000 hoàn40.000 một lần. Không chạm CHECKED_IN; lặp không phạt lại. Service trả danh sách ID trong OperationResult, hàm core nhận state và trả số lượng int.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SS2UI._init_pev_state`

**Chữ ký:** `_init_pev_state() -> None`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Hàm UI hiện có; tạo các danh sách xe/đơn cá nhân chưa có trong session bằng mặc định. Không ghi đè danh sách đã tồn tại hoặc reset ví. Không tham số/trả None; gọi lặp chỉ khởi tạo thiếu.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `SS2UI.render`

**Chữ ký:** `render() -> None`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Hàm UI hiện có: hiển thị form đăng ký/đặt/check-in/out, gọi core theo thao tác Streamlit và rerun. Đọc/ghi session qua core, hiển thị tuple lỗi; không thay thế kiểm tra quyền phía service hoặc QR/barie thật. Không có giá trị trả về, render lặp không tự thu tiền nếu không có thao tác.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVModule.parse_time`

**Chữ ký:** `parse_time(t_str: str) -> datetime`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Adapter thuần đọc: nhận chuỗi thời gian YYYY-MM-DD HH:MM:SS; parse thành datetime naive. Theo quy ước tài liệu UTC+7 của đồng hồ mô phỏng, không tự chuyển timezone. Chuỗi lỗi: code fallback datetime.now, là giới hạn cần validation tại service trước khi tính hạn/phí.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVModule.format_time`

**Chữ ký:** `format_time(dt: datetime) -> str`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Adapter thuần đọc: datetime vào -> chuỗi YYYY-MM-DD HH:MM:SS, không ghi session. Đầu vào datetime hợp lệ; không kèm timezone offset trong chuỗi hiện tại.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVModule.register_personal_ev`

**Chữ ký:** `register_personal_ev(state: dict, owner_id: str, owner_name: str, plate_number: str, ev_type: str, brand: str, battery_kwh: float) -> tuple[bool, dict | None, str]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Kiểm tra owner/biển số/loại xe/dung lượng pin hợp lệ; chuẩn hóa biển số, từ chối trùng, thêm hồ sơ ownership PERSONAL, tăng version. Không đổi Hub/slot. Service thiết kế trả OperationResult, core trả tuple(ok,record,msg), ev_id ánh xạ vehicle_id. Mô tả chi tiết và giới hạn UI/prototype xem mục6 báo cáo.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVModule.reserve_personal_ev_slot`

**Chữ ký:** `reserve_personal_ev_slot(state: dict, owner_id: str, ev_id: str, hub_id: str, request_charging: bool = False, current_soc: float = 50.0, booking_start_time: str | None = None) -> tuple[bool, dict | None, str]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Xác nhận xe thuộc owner và chưa có lượt hoạt động, Hub còn chỗ, booking_start_time không trước sim_now, SoC hợp lệ. Khóa cọc50.000, giảm available_slots và tăng destination_holds đúng một lần; deadline=start+30 phút. Thiếu tiền/nợ/Hub đầy/đầu vào sai giữ nguyên. Service thiết kế thêm operation_key để chống lặp; core chưa có key. Trả reservation trong OperationResult hoặc tuple prototype.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVModule.sweep_expired_personal_reservations`

**Chữ ký:** `sweep_expired_personal_reservations(state: dict) -> int`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Duyệt RESERVED khi sim_now>=arrival_deadline, chuyển EXPIRED, giảm hold/tăng available, phạt10.000 hoàn40.000 một lần. Không chạm CHECKED_IN; lặp không phạt lại. Service trả danh sách ID trong OperationResult, hàm core nhận state và trả số lượng int.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVModule.check_in_personal_ev`

**Chữ ký:** `check_in_personal_ev(state: dict, reservation_id: str) -> tuple[bool, str]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Quét hết hạn, yêu cầu RESERVED và start<=now<deadline. Chuyển destination_holds sang hiện diện PERSONAL mà không giảm available lần hai, ghi CHECKED_IN/check_in_time. Service gọi INT-01 nếu request_charging, không tự cấp trùng. Core hiện giảm số cổng nếu có và có thể gán xe CHARGING khi chưa được cấp; phải nêu là giới hạn. Không thực sự mở barie/scan QR vật lý. Lặp từ chối INVALID_STATE, quá hạn EXPIRED.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `PersonalEVModule.check_out_personal_ev`

**Chữ ký:** `check_out_personal_ev(state: dict, reservation_id: str, duration_hours: float = 2.0, kwh_charged: float = 3.5, overstay_minutes: int = 0) -> tuple[bool, dict | None, str]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Chỉ CHECKED_IN. Theo thiết kế lấy phí sạc INT-02 + phí đỗ, quyết toán BillingService bằng charge_id, trả slot/cổng thực sự đã cấp, COMPLETED và invoice. Thiếu số dư ghi nợ, không mất phần thiếu; gọi lại không thu thêm do vòng đời. Core nhận duration_hours/kwh/overstay từ mô phỏng và tự tính phí tại giờ checkout; chưa đo telemetry/thời gian biểu giá tích phân. Owner/key trong service chưa có ở core.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingService.hold_deposit`

**Chữ ký:** `hold_deposit(owner_id: str, reference_id: str, amount_vnd: int, operation_key: str) -> OperationResult[DepositResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Đúng owner/reference, amount_vnd >=0, ví không nợ và đủ số dư. Chuyển từ khả dụng sang held theo reference; ghi ledger với cùng operation_key. Lặp cùng nội dung không khóa thêm; CONFLICTING_OPERATION nếu key khác payload, INSUFFICIENT_FUNDS/DEBT_BLOCKED nếu không đủ điều kiện. Prototype giữ tổng cọc, chưa có sổ cọc theo reference.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingService.release_deposit`

**Chữ ký:** `release_deposit(owner_id: str, reference_id: str, operation_key: str) -> OperationResult[DepositResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Chỉ hoàn phần cọc chưa quyết toán của đúng reference, không lấy cọc booking khác. Tăng khả dụng, giảm held, ghi ledger; lặp trả kết quả cũ. NOT_FOUND/FORBIDDEN/CONFLICTING_OPERATION giữ nguyên dữ liệu. Prototype hàm thấp cấp chỉ bảo vệ tổng held, caller chịu kiểm tra vòng đời.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingService.settle_no_show`

**Chữ ký:** `settle_no_show(owner_id: str, reference_id: str, operation_key: str) -> OperationResult[SettlementResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Caller đã xác nhận EXPIRED. Với cọc 50.000 VNĐ, phạt 10.000 và hoàn 40.000; đóng cọc reference, ghi dòng tiền đúng một lần. Key/payload mâu thuẫn trả CONFLICTING_OPERATION; không áp dụng cho lượt IN_USE hoặc cọc đã quyết toán.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `BillingService.settle_invoice`

**Chữ ký:** `settle_invoice(owner_id: str, reference_id: str, charge_lines: list[ChargeLine], operation_key: str) -> OperationResult[SettlementResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** Chỉ thu charge_id chưa thu, cùng ID khác tiền trả CONFLICTING_CHARGE. Đối trừ/hoàn cọc đúng reference rồi trừ số dư tối đa phần có thể thu và ghi nợ phần thiếu; paid/refunded/debt lấy từ ledger. Gọi lặp cùng key trả kết quả cũ, không thu lại phí SS5 ở SS2. Prototype có nhiều hàm thu trực tiếp, chưa có BillingService hay dedup charge_id. Thiết kế phải stage tất cả thay đổi trước commit.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ChargingService.request_charging`

**Chữ ký:** `request_charging(owner_id: str, vehicle_id: str, hub_id: str, current_soc: float, target_soc: float = 100.0, reservation_id: str | None = None) -> OperationResult[ChargingRequestResult]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** INT-01 (thiết kế TV5). Xe/owner/Hub hợp lệ, check-in đã thành công, SoC0–100 và target>=current. Tạo request có ID ổn định, chưa có session/cổng khi còn chờ; thêm queue, cấp theo power/cổng thực khi có khả năng. Không cấp trùng cùng lượt/xe; NOT_FOUND/FORBIDDEN/INVALID_STATE/INVALID_INPUT không commit. Prototype SS2 giảm cổng tổng hợp trực tiếp, chưa gọi service này.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.

## `ChargingService.get_bill`

**Chữ ký:** `get_bill(session_id: str) -> OperationResult[ChargingBill]`.

**Điều kiện, hành vi, kết quả, lỗi và gọi lặp:** INT-02 (thiết kế TV5). Tìm session_id và đối soát energy_delivered_kwh, giá/phí, charge_id và khoản đã thu từ ledger. Trả ChargingBill chỉ đọc; gọi lặp không trừ ví hoặc tăng phí giả. Phiên không có trả NOT_FOUND. SS2 lấy dòng phí còn phải thu, không tính lại giá điện/quá giờ độc lập.

**Truy vết:** các UC/method liên quan được dẫn trong traceability.md; test và trạng thái thực thi ở test_cases.md.
