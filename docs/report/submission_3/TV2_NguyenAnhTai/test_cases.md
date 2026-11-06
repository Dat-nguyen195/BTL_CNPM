# Test case bonus — Nguyễn Anh Tài — SS2

**MSSV:** 2413035  
**Phân hệ:** SS2 — Xe cá nhân, chỗ đỗ và check-in/out  
**Trạng thái:** Đã thiết kế đủ 8 ca kiểm thử (`TC-SS2-01` → `TC-SS2-08`) bao phủ 4 Use Case của SS2 (mỗi UC có ít nhất 1 ca luồng chính và 1 ca lỗi/ngoại lệ/biên). Các ca đã có trong `tests/test_personal_ev.py` và `tests/test_reservation_30_minutes.py` ghi nhận kết quả thực tế; các ca mới thiết kế mở rộng ghi trạng thái `DESIGNED`.

---

## 1. `UC_SS2_01` — Đăng ký xe EV cá nhân lên hệ thống

### `TC-SS2-01` — Đăng ký xe EV cá nhân hợp lệ (Luồng chính)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-01` / `UC_SS2_01` / `SS2-MTH-07` (`PersonalEVService.register_personal_ev`), `SS2-MTH-01` (`PersonalVehicle.normalize_plate`) |
| **Tiền điều kiện** | Trạng thái phiên khởi tạo từ `get_initial_session_state()`, `current_sim_time = "2026-10-21 08:00:00"`, biển số `"59-X1 77777"` chưa tồn tại trong `state["personal_evs"]`. |
| **Dữ liệu vào** | `owner_id = "SV-2211234"`, `owner_name = "Nguyễn Văn A"`, `plate_number = "59-X1 77777"`, `ev_type = "scooter"`, `brand = "VinFast Klara"`, `battery_kwh = 3.5` (`kWh`). |
| **Các bước** | 1. Khởi tạo `clean_state`.<br>2. Gọi `register_personal_ev(state=clean_state, owner_id="SV-2211234", owner_name="Nguyễn Văn A", plate_number="59-X1 77777", ev_type="scooter", brand="VinFast Klara", battery_kwh=3.5)`.<br>3. Kiểm tra giá trị trả về và danh sách `clean_state["personal_evs"]`. |
| **Kết quả mong đợi** | • Trả về `ok == True`, `ev["plate"] == "59-X1 77777"`, `ev["ownership"] == "PERSONAL"`, `ev["status"] == "REGISTERED"`, `ev["battery_kwh"] == 3.5`.<br>• `state_version` tăng thêm 1; số chỗ của các Hub không bị ảnh hưởng. |
| **Kết quả thực tế** | Khớp hoàn toàn với kiểm thử tự động `test_register_personal_ev_success_and_duplicate` trong `tests/test_personal_ev.py` (dòng 21–34). |
| **Trạng thái** | `PASS` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — đối chiếu bộ test `tests/test_personal_ev.py`. |

### `TC-SS2-02` — Từ chối đăng ký xe cá nhân trùng biển số khác định dạng (Luồng lỗi)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-02` / `UC_SS2_01` / `SS2-MTH-07` (`PersonalEVService.register_personal_ev`), `SS2-MTH-01` (`PersonalVehicle.normalize_plate`) |
| **Tiền điều kiện** | Trong `state["personal_evs"]` đã có xe mang biển số `"59-X1 77777"` (chuẩn hóa thành `"59X177777"`). |
| **Dữ liệu vào** | `owner_id = "SV-9999999"`, `owner_name = "Trần Văn B"`, `plate_number = "59X1-77777"` (khác vị trí dấu gạch ngang và khoảng trắng), `ev_type = "scooter"`, `brand = "VinFast"`, `battery_kwh = 3.0` (`kWh`). |
| **Các bước** | 1. Sau khi đăng ký biển số `"59-X1 77777"`, gọi tiếp `register_personal_ev` với `plate_number = "59X1-77777"`.<br>2. Kiểm tra cờ kết quả `ok2`, thông báo `msg2` và số lượng phần tử trong `state["personal_evs"]`. |
| **Kết quả mong đợi** | • `normalize_plate("59X1-77777")` trả về `"59X177777"` trùng với hồ sơ đã có.<br>• Trả về `ok2 == False`, `ev2 is None`, thông báo chứa chuỗi `"đã được đăng ký"`.<br>• Không thêm bản ghi trùng vào `personal_evs`. |
| **Kết quả thực tế** | Khớp hoàn toàn với kiểm thử tự động `test_register_personal_ev_success_and_duplicate` trong `tests/test_personal_ev.py` (dòng 36–47). |
| **Trạng thái** | `PASS` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — đối chiếu bộ test `tests/test_personal_ev.py`. |

---

## 2. `UC_SS2_02` — Đặt trước chỗ đỗ và nhu cầu sạc xe EV cá nhân

### `TC-SS2-03` — Đặt chỗ đỗ kèm nhu cầu sạc hợp lệ và khóa cọc 50.000 VNĐ (Luồng chính)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-03` / `UC_SS2_02` / `SS2-MTH-08` (`PersonalEVService.reserve_personal_ev_slot`) |
| **Tiền điều kiện** | Xe `ev_id` đã đăng ký thuộc `"SV-2211234"`; `current_sim_time = "2026-10-21 08:00:00"`; ví sinh viên có `balance = 150.000 VNĐ`, `held_deposit = 0 VNĐ`, `debt = 0 VNĐ`; Hub đích còn chỗ trống (`available_slots > 0`) và cổng sạc trống (`charging_ports.available > 0`). |
| **Dữ liệu vào** | `owner_id = "SV-2211234"`, `ev_id = ev["ev_id"]`, `hub_id = hub["hub_id"]`, `request_charging = True`, `current_soc = 30.0` (`%`), `booking_start_time = "2026-10-21 08:00:00"`. |
| **Các bước** | 1. Gọi `reserve_personal_ev_slot(...)`.<br>2. Đối chiếu `hub["destination_holds"]`, `hub["available_slots"]`, `wallet["balance"]`, `wallet["held_deposit"]` và `res["arrival_deadline"]`. |
| **Kết quả mong đợi** | • Trả về `ok_res == True`, `res["status"] == "RESERVED"`.<br>• `hub["destination_holds"] == initial_holds + 1`, `hub["available_slots"] == initial_avail - 1`.<br>• `wallet["balance"] == 100.000 VNĐ`, `wallet["held_deposit"] == 50.000 VNĐ`.<br>• Hạn check-in đúng 30 phút từ giờ đến đã chọn: `res["arrival_deadline"] == "2026-10-21 08:30:00"`. |
| **Kết quả thực tế** | Khớp hoàn toàn với kiểm thử tự động `test_reserve_and_checkin_checkout_lifecycle` trong `tests/test_personal_ev.py` (dòng 63–76). |
| **Trạng thái** | `PASS` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — đối chiếu bộ test `tests/test_personal_ev.py`. |

### `TC-SS2-04` — Từ chối đặt chỗ khi xe đang có đơn hoạt động, Hub hết chỗ hoặc ví đang có nợ (Luồng lỗi)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-04` / `UC_SS2_02` / `SS2-MTH-08` (`PersonalEVService.reserve_personal_ev_slot`), `SS2-MTH-02` (`PersonalVehicle.is_owned_by`) |
| **Tiền điều kiện** | Xe `ev_id` đang có 1 đơn ở trạng thái `RESERVED` (hoặc đặt vào Hub có `available_slots = 0`, hoặc ví có `debt = 20.000 VNĐ`). |
| **Dữ liệu vào** | Gọi `reserve_personal_ev_slot` lần thứ 2 cho cùng `ev_id` khi đơn thứ nhất chưa hoàn tất. |
| **Các bước** | 1. Tạo đơn đặt chỗ thứ nhất thành công cho `ev_id`.<br>2. Gọi tiếp `reserve_personal_ev_slot` lần thứ hai cho cùng `ev_id`.<br>3. Kiểm tra số dư ví, `held_deposit` và `available_slots` của Hub. |
| **Kết quả mong đợi** | • Trả về `ok == False`, `res is None`, thông báo `"Phương tiện ... đang có lượt đặt chỗ ... chưa hoàn tất."` (mã lỗi thiết kế `CONFLICTING_OPERATION`).<br>• Không khóa thêm `50.000 VNĐ` tiền cọc lần hai; không giảm thêm `available_slots` của Hub. |
| **Kết quả thực tế** | CHƯA CHẠY RIÊNG (Đã có nhánh kiểm tra tại dòng 106–111 trong `src/core/personal_ev.py`). |
| **Trạng thái** | `DESIGNED` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — thiết kế ngày 30/10/2026. |

---

## 3. `UC_SS2_03` — Check-in xe EV cá nhân tại cổng Hub (QR/Biển số)

### `TC-SS2-05` — Check-in hợp lệ ở mốc 29 phút 59 giây và bảo toàn sức chứa Hub (Luồng chính & Biên)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-05` / `UC_SS2_03` / `SS2-MTH-09` (`PersonalEVService.check_in_personal_ev`), `SS2-MTH-04` (`ParkingReservation.can_check_in`) |
| **Tiền điều kiện** | Đơn `reservation_id` được đặt với `booking_start_time = "2026-10-21 08:00:00"`, `arrival_deadline = "2026-10-21 08:30:00"`, `status = "RESERVED"`, `destination_holds = 1`, `held_deposit = 50.000 VNĐ`. |
| **Dữ liệu vào** | Đồng hồ mô phỏng tại `current_sim_time = "2026-10-21 08:29:59"` (`seconds = 30 * 60 - 1 = 1799`); gọi `check_in_personal_ev(state, reservation_id)`. |
| **Các bước** | 1. Đặt `state["current_sim_time"] = "2026-10-21 08:29:59"`.<br>2. Gọi `sweep_expired_personal_reservations(state)` và `check_in_personal_ev(state, reservation_id)`.<br>3. Kiểm tra `res["status"]`, `hub["destination_holds"]`, `hub["available_slots"]`, `hub["current_vehicles"]` và `validate_state_invariants(state)`. |
| **Kết quả mong đợi** | • Tại `08:29:59`, `sweep` trả về `0` (chưa hết hạn).<br>• `check_in_personal_ev` trả về `ok == True`; `res["status"] == "CHECKED_IN"`.<br>• `hub["destination_holds"]` giảm về `0`, `hub["available_slots"]` giữ nguyên (không bị trừ lần thứ hai), xe xuất hiện trong `hub["current_vehicles"]` với `ownership == "PERSONAL"`.<br>• `validate_state_invariants(state) == []`. |
| **Kết quả thực tế** | Khớp hoàn toàn với kiểm thử tự động `test_reservation_30_minute_boundary_and_single_settlement` (`service="personal"`, `seconds=1799`) trong `tests/test_reservation_30_minutes.py` và `test_reserve_and_checkin_checkout_lifecycle` trong `tests/test_personal_ev.py`. |
| **Trạng thái** | `PASS` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — đối chiếu bộ test `tests/test_reservation_30_minutes.py`. |

### `TC-SS2-06` — Quá hạn tại đúng 30 phút 00 giây, phạt no-show 10.000 VNĐ và từ chối Check-in / chống sweep lặp (Biên & Ngoại lệ)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-06` / `UC_SS2_02`, `UC_SS2_03` / `SS2-MTH-11` (`sweep_expired_personal_reservations`), `SS2-MTH-03` (`is_expired`), `SS2-MTH-09` (`check_in_personal_ev`) |
| **Tiền điều kiện** | Đơn `reservation_id` có `booking_start_time = "2026-10-21 08:00:00"`, `arrival_deadline = "2026-10-21 08:30:00"`, `status = "RESERVED"`, ví đã khóa cọc `50.000 VNĐ` (`balance = 100.000 VNĐ`, `held_deposit = 50.000 VNĐ`). |
| **Dữ liệu vào** | Đồng hồ mô phỏng chạm đúng mốc hạn chót `current_sim_time = "2026-10-21 08:30:00"` (`seconds = 30 * 60 = 1800`). |
| **Các bước** | 1. Đặt `state["current_sim_time"] = "2026-10-21 08:30:00"`.<br>2. Gọi `sweep_expired_personal_reservations(state)` lần 1.<br>3. Gọi `sweep_expired_personal_reservations(state)` lần 2 và gọi `check_in_personal_ev(state, reservation_id)`.<br>4. Kiểm tra trạng thái đơn, số chỗ trống của Hub, số dư ví và nhật ký `wallet["ledger"]`. |
| **Kết quả mong đợi** | • Lần `sweep` 1 trả về `1`: `res["status"] == "EXPIRED"`, `destination_holds == 0`, `available_slots` tăng lại +1; ví giải phóng cọc `held_deposit == 0`, phạt `10.000 VNĐ`, hoàn `40.000 VNĐ` (`balance == 140.000 VNĐ`).<br>• Lần `sweep` 2 trả về `0`; gọi `check_in_personal_ev` trả về `False`; `wallet["ledger"]` không phát sinh giao dịch trùng lặp; `validate_state_invariants(state) == []`. |
| **Kết quả thực tế** | Khớp hoàn toàn với kiểm thử tự động `test_reservation_30_minute_boundary_and_single_settlement` (`service="personal"`, `seconds=1800` và `seconds=1801`) trong `tests/test_reservation_30_minutes.py`. |
| **Trạng thái** | `PASS` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — đối chiếu bộ test `tests/test_reservation_30_minutes.py`. |

---

## 4. `UC_SS2_04` — Check-out và thanh toán tổng hợp dịch vụ xe EV cá nhân

### `TC-SS2-07` — Check-out có sạc giờ cao điểm + quá giờ 20 phút và hoàn trả chỗ đỗ (Luồng chính)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-07` / `UC_SS2_04` / `SS2-MTH-10` (`PersonalEVService.check_out_personal_ev`), `SS2-MTH-06` (`ParkingSession.build_parking_charge_line`) |
| **Tiền điều kiện** | Đơn `reservation_id` đã `CHECKED_IN` tại `current_sim_time = "2026-10-21 08:00:00"` (khung giờ cao điểm `06:00–09:00`, đơn giá `7.000 VNĐ/kWh`), `request_charging = True`, ví có `balance = 100.000 VNĐ`, `held_deposit = 50.000 VNĐ`. |
| **Dữ liệu vào** | `reservation_id = res["reservation_id"]`, `duration_hours = 2.0` (`giờ`), `kwh_charged = 4.0` (`kWh`), `overstay_minutes = 20` (`phút` — vượt 15 phút ân hạn là 5 phút = 1 khối 15 phút). |
| **Các bước** | 1. Gọi `check_out_personal_ev(state=clean_state, reservation_id=res["reservation_id"], duration_hours=2.0, kwh_charged=4.0, overstay_minutes=20)`.<br>2. Kiểm tra hóa đơn `inv`, số dư ví và số chỗ trống của Hub sau Check-out. |
| **Kết quả mong đợi** | • Trả về `ok_out == True`; `res["status"] == "COMPLETED"`.<br>• Hóa đơn `inv`: `parking_fee == 5.000 VNĐ`, `is_peak_tariff == True`, `energy_fee == 28.000 VNĐ` (`4.0 * 7.000`), `overstay_fee == 10.000 VNĐ` (`1 khối * 10.000`), `total_amount == 43.000 VNĐ`, `debt_incurred == 0 VNĐ`.<br>• Giải phóng cọc `50.000 VNĐ` và trừ `43.000 VNĐ` (`wallet["balance"] == 107.000 VNĐ`, `wallet["held_deposit"] == 0`).<br>• Xe được rút khỏi `hub["current_vehicles"]`, `hub["available_slots"] == initial_avail`. |
| **Kết quả thực tế** | Khớp hoàn toàn với kiểm thử tự động `test_reserve_and_checkin_checkout_lifecycle` trong `tests/test_personal_ev.py` (dòng 88–103). |
| **Trạng thái** | `PASS` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — đối chiếu bộ test `tests/test_personal_ev.py`. |

### `TC-SS2-08` — Check-out khi ví thiếu số dư (ghi nhận nợ minh bạch) và chống gọi Check-out lặp (Luồng ngoại lệ)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-08` / `UC_SS2_04` / `SS2-MTH-10` (`PersonalEVService.check_out_personal_ev`) |
| **Tiền điều kiện** | Đơn `reservation_id` đang ở trạng thái `CHECKED_IN`; trước khi Check-out, số dư khả dụng của ví sau khi hoàn cọc nhỏ hơn tổng phí hóa đơn (ví dụ tổng số dư khả dụng sau hoàn cọc là `30.000 VNĐ`, trong khi `total_amount = 43.000 VNĐ`). |
| **Dữ liệu vào** | Gọi `check_out_personal_ev` lần 1 với `total_amount = 43.000 VNĐ` khi ví chỉ có `30.000 VNĐ`; sau đó gọi lại `check_out_personal_ev` lần 2 trên cùng `reservation_id`. |
| **Các bước** | 1. Thiết lập số dư khả dụng của ví sao cho sau khi giải phóng cọc đạt `30.000 VNĐ`.<br>2. Gọi `check_out_personal_ev` lần 1 (`total_amount = 43.000 VNĐ`).<br>3. Kiểm tra `wallet["balance"]`, `wallet["debt"]`, `inv["debt_incurred"]` và `hub["available_slots"]`.<br>4. Gọi tiếp `check_out_personal_ev` lần 2 trên cùng `reservation_id`. |
| **Kết quả mong đợi** | • Lần 1: Trả về `ok == True`; `inv["deducted_from_wallet"] == 30.000 VNĐ`, `inv["debt_incurred"] == 13.000 VNĐ`; `wallet["balance"] == 0`, `wallet["debt"] == 13.000 VNĐ`; xe vẫn được giải phóng khỏi Hub (`available_slots` tăng +1) và `res["status"] == "COMPLETED"`.<br>• Lần 2: Trả về `ok == False` do `res["status"] != "CHECKED_IN"`; không cộng thêm `available_slots` và không ghi nợ lặp lần hai. |
| **Kết quả thực tế** | CHƯA CHẠY RIÊNG (Đã triển khai tại dòng 275–276 và 311–321 trong `src/core/personal_ev.py`). |
| **Trạng thái** | `DESIGNED` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — thiết kế ngày 30/10/2026. |
