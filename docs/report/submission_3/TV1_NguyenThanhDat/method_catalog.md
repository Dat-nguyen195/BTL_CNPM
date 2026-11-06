# Danh mục phương thức SS1 - revision 06/11/2026

Mọi kiểu/đơn vị như class diagram. `OperationResult` là hợp đồng đề xuất; các tuple/dict hiện có được nêu ở ánh xạ. UC chi tiết và test được liên kết trong traceability.md.

## SS1-MTH-01: `BookingService.create_booking`

**Chữ ký:** `create_booking(student_id: str, hub_id: str, vehicle_id: str, destination_hub_id: Optional[str] = None, voucher_code: Optional[str] = None) -> OperationResult[Booking]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Sinh viên chưa có lượt RESERVED/IN_USE; xe SHARED, AVAILABLE và SoC >=20%; Hub đích nếu chọn phải còn chỗ. Quét hết hạn trước, giữ cọc 50.000 VNĐ qua BillingService, giữ xe và chỗ đích, tạo expires_at=created_at+30 phút. Không đổi trạng thái khi kiểm tra thất bại; NOT_FOUND/INVALID_STATE/NO_CAPACITY/INSUFFICIENT_FUNDS/DEBT_BLOCKED. Prototype chưa kiểm tra ownership tại core; UI có lọc. Thiết kế bắt buộc kiểm tra ở service.

**Ánh xạ:** `src/core/booking.py:create_shared_booking`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-02: `BookingService.pickup`

**Chữ ký:** `pickup(booking_id: str, pin: str) -> OperationResult[Booking]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Yêu cầu đúng chủ booking (thiết kế), PIN và trạng thái RESERVED. Khi now >= expires_at phải xử lý no-show trước khi xét nhận xe. Nhận trong hạn chuyển IN_USE, ghi pickup_time, giải phóng chỗ nguồn; giữ chỗ đích còn hiệu lực. PIN sai trả FORBIDDEN, hết hạn EXPIRED, gọi lại INVALID_STATE; không trừ thêm cọc. Prototype dùng PIN 4 chữ số, QR/khóa vật lý là mô phỏng.

**Ánh xạ:** `src/core/booking.py:pickup_shared_vehicle`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-03: `BookingService.cancel`

**Chữ ký:** `cancel(booking_id: str) -> OperationResult[Booking]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Chỉ chủ booking RESERVED trong hạn được hủy. Hoàn đúng cọc reference 50.000 VNĐ một lần, giải phóng xe/giữ chỗ đích, chuyển CANCELLED. Nếu tới hạn, xử lý EXPIRED và no-show thay vì hoàn toàn phần cọc. Gọi lại không hoàn thêm. NOT_FOUND/INVALID_STATE/EXPIRED.

**Ánh xạ:** `src/core/booking.py:cancel_shared_booking`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-04: `BookingService.return_vehicle`

**Chữ ký:** `return_vehicle(booking_id: str, return_hub_id: str) -> OperationResult[SettlementResult]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Booking IN_USE, xe có trong active trip, Hub trả tồn tại và có chỗ hoặc giữ chỗ của lượt đó. Chốt thời lượng từ pickup_time, miễn phí 30 phút + ưu đãi reroute nếu có; 1.000 VNĐ/phút sau miễn phí, voucher hợp lệ giảm 5.000 VNĐ và tổng không âm. Chuyển giữ chỗ cũ sang hiện diện Hub trả, COMPLETED, quyết toán/ghi nợ nếu thiếu. Gọi lại không thu thêm; NOT_FOUND/INVALID_STATE/NO_CAPACITY. Không tự bịa số km.

**Ánh xạ:** `src/core/booking.py:return_shared_vehicle`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-05: `BookingService.expire_reservations`

**Chữ ký:** `expire_reservations(sim_now: datetime) -> OperationResult[list[str]]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Duyệt booking RESERVED và sim_now >= expires_at. Chuyển EXPIRED, trả xe AVAILABLE và giải phóng hold đích, settle_no_show phạt 10.000 và hoàn 40.000 VNĐ. Trả danh sách booking vừa hết hạn; sweep lặp trả danh sách rỗng, không tác động IN_USE. Đồng hồ service phải là đồng hồ mô phỏng.

**Ánh xạ:** `src/core/booking.py:process_expired_bookings`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-06: `BookingService.accept_rerouting`

**Chữ ký:** `accept_rerouting(booking_id: str, new_hub_id: str, expected_version: int, operation_key: str) -> OperationResult[Booking]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** INT-07, chỉ sau xác nhận của người dùng. Kiểm tra chủ booking, RESERVED/IN_USE, version và capacity Hub mới. Chuyển hold cũ/mới trong một commit, ưu đãi thêm 15 phút miễn phí tối đa một lần; không kéo TTL giữ xe. Cùng key/cùng dữ liệu trả kết quả cũ, key khác dữ liệu CONFLICTING_OPERATION; STALE_STATE/NO_CAPACITY không commit. Prototype chưa có expected_version/operation_key và vẫn có thể cộng ưu đãi khi đổi sang Hub khác nhiều lần; đây là hợp đồng đề xuất.

**Ánh xạ:** `src/core/booking.py:apply_rerouting_to_booking`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-07: `BillingService.hold_deposit`

**Chữ ký:** `hold_deposit(owner_id: str, reference_id: str, amount_vnd: int, operation_key: str) -> OperationResult[DepositResult]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Đúng owner/reference, amount_vnd >=0, ví không nợ và đủ số dư. Chuyển từ khả dụng sang held theo reference; ghi ledger với cùng operation_key. Lặp cùng nội dung không khóa thêm; CONFLICTING_OPERATION nếu key khác payload, INSUFFICIENT_FUNDS/DEBT_BLOCKED nếu không đủ điều kiện. Prototype giữ tổng cọc, chưa có sổ cọc theo reference.

**Ánh xạ:** `src/core/billing.py:hold_deposit`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-08: `BillingService.release_deposit`

**Chữ ký:** `release_deposit(owner_id: str, reference_id: str, operation_key: str) -> OperationResult[DepositResult]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Chỉ hoàn phần cọc chưa quyết toán của đúng reference, không lấy cọc booking khác. Tăng khả dụng, giảm held, ghi ledger; lặp trả kết quả cũ. NOT_FOUND/FORBIDDEN/CONFLICTING_OPERATION giữ nguyên dữ liệu. Prototype hàm thấp cấp chỉ bảo vệ tổng held, caller chịu kiểm tra vòng đời.

**Ánh xạ:** `src/core/billing.py:release_held_deposit_full`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-09: `BillingService.settle_no_show`

**Chữ ký:** `settle_no_show(owner_id: str, reference_id: str, operation_key: str) -> OperationResult[SettlementResult]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Caller đã xác nhận EXPIRED. Với cọc 50.000 VNĐ, phạt 10.000 và hoàn 40.000; đóng cọc reference, ghi dòng tiền đúng một lần. Key/payload mâu thuẫn trả CONFLICTING_OPERATION; không áp dụng cho lượt IN_USE hoặc cọc đã quyết toán.

**Ánh xạ:** `src/core/billing.py:settle_noshow_penalty`, `src/core/billing.py:settle_pev_noshow_penalty`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS1-MTH-10: `BillingService.settle_invoice`

**Chữ ký:** `settle_invoice(owner_id: str, reference_id: str, charge_lines: list[ChargeLine], operation_key: str) -> OperationResult[SettlementResult]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Chỉ thu charge_id chưa thu, cùng ID khác tiền trả CONFLICTING_CHARGE. Đối trừ/hoàn cọc đúng reference rồi trừ số dư tối đa phần có thể thu và ghi nợ phần thiếu; paid/refunded/debt lấy từ ledger. Gọi lặp cùng key trả kết quả cũ, không thu lại phí SS5 ở SS2. Prototype có nhiều hàm thu trực tiếp, chưa có BillingService hay dedup charge_id. Thiết kế phải stage tất cả thay đổi trước commit.

**Ánh xạ:** `src/core/billing.py:settle_shared_rental`, `src/core/personal_ev.py:check_out_personal_ev`, `src/core/billing.py:settle_overstay_charging`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.
