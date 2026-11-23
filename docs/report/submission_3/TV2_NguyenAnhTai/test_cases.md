# Test case bonus — Nguyễn Anh Tài — SS2

**MSSV:** 2413035  
**Phân hệ:** SS2 — Xe cá nhân, chỗ đỗ và check-in/out  
**Trạng thái:** Đã thiết kế đủ 8 ca kiểm thử (`TC-SS2-01` → `TC-SS2-08`) bao phủ 4 Use Case của SS2 (mỗi UC có ít nhất 1 ca luồng chính và 1 ca lỗi/ngoại lệ/biên). Các ca đã có trong `tests/test_personal_ev.py`, `tests/test_reservation_30_minutes.py` và `tests/test_submission_2_acceptance.py` ghi nhận kết quả thực tế; các ca mới thiết kế mở rộng ghi trạng thái `DESIGNED`.

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
| **Kết quả thực tế** | Test tự động `test_register_personal_ev_success_and_duplicate` (`tests/test_personal_ev.py`, dòng 21–34) kiểm tra `ok`, `plate` và `ownership`. Các kỳ vọng còn lại (`status == "REGISTERED"`, `battery_kwh == 3.5`, `state_version` tăng 1, số chỗ Hub không đổi) đã đối chiếu bằng chạy lại kịch bản ngày 23/11/2026: khớp. |
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
| **Kết quả thực tế** | Test tự động `test_reserve_and_checkin_checkout_lifecycle` (`tests/test_personal_ev.py`, dòng 65–77) kiểm tra `destination_holds`, `available_slots`, `held_deposit == 50.000` và `arrival_deadline == "2026-10-21 08:30:00"`. Số dư `balance == 100.000` và `status == "RESERVED"` đã đối chiếu bằng chạy lại kịch bản ngày 23/11/2026: khớp. |
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
| **Kết quả thực tế** | Chưa có test tự động. Nhánh xe đang có đơn hoạt động (dòng 121–125 trong `src/core/personal_ev.py`) đã chạy thử thủ công ngày 23/11/2026: trả `ok == False`, không khóa thêm cọc (`held_deposit` giữ `50.000`). Nhánh Hub hết chỗ (dòng 133–134) và ví có nợ (`hold_deposit` trong `src/core/billing.py`) chưa chạy riêng. |
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

### `TC-SS2-07` — Check-out có sạc giờ cao điểm: phí đỗ theo giờ + điện năng đo từ SS5, thu một lần (Luồng chính)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-07` / `UC_SS2_04` / `SS2-MTH-10` (`PersonalEVService.check_out_personal_ev`), `SS2-MTH-06` (`ParkingSession.build_parking_charge_line`) |
| **Tiền điều kiện** | Biểu phí đỗ mặc định `5.000 VNĐ/giờ bắt đầu`, tối thiểu 1 giờ (`EMOBILITY_PARKING_HOURLY_VND` không đặt). Xe đã đặt chỗ có `request_charging = True` tại `HUB-001` lúc `2026-10-21 08:00:00` (cao điểm `06:00–09:00`, `7.000 VNĐ/kWh`); sau khi khóa cọc ví có `balance = 100.000 VNĐ`, `held_deposit = 50.000 VNĐ`. |
| **Dữ liệu vào** | **(a) Có sạc thật:** `current_soc = 98` (`%`); check-in, SS5 mô phỏng +15 phút sạc, rút sạc ở SS5; check-out với `duration_hours = 1`.<br>**(b) Chưa nạp kWh nào:** check-out ngay sau check-in với `duration_hours = 2.0`, nhập tay `kwh_charged = 4.0` (`kWh`), `overstay_minutes = 20` (`phút`). |
| **Các bước** | **(a)** 1. `check_in_personal_ev` → SS5 cấp phiên sạc.<br>2. SS5 bấm "Mô phỏng +15 phút sạc" rồi "Rút sạc".<br>3. Gọi `check_out_personal_ev(..., duration_hours=1, ...)`; kiểm tra hóa đơn SS5, hóa đơn SS2, ví và cổng sạc.<br>**(b)** 1. `check_in_personal_ev`.<br>2. Gọi ngay `check_out_personal_ev(..., duration_hours=2.0, kwh_charged=4.0, overstay_minutes=20)`; kiểm tra hóa đơn và chỗ đỗ. |
| **Kết quả mong đợi** | **(a)** Hóa đơn SS5 khi rút sạc `total_due == 0` và ghi chú quyết toán một lần tại SS2. Hóa đơn SS2: `parking_fee == 5.000 VNĐ` (1 giờ), `kwh_charged == 0,07` (`(100 − 98)% × 3,5 kWh`), `energy_fee == 490 VNĐ` (`0,07 × 7.000`), `overstay_fee == 0`, `total_amount == 5.490 VNĐ`. Ví `balance == 144.510 VNĐ` (`100.000 + 50.000 − 5.490`), `held_deposit == 0`; cổng sạc của Hub trả lại đủ (`available == 4`).<br>**(b)** `parking_fee == 10.000 VNĐ` (2 giờ bắt đầu), `is_peak_tariff == True`, `energy_fee == 0` và `overstay_fee == 0` vì phiên sạc chưa nạp kWh nào (số nhập tay không ghi đè số đo), `total_amount == 10.000 VNĐ`; xe rời Hub, `available_slots` trở về giá trị ban đầu. |
| **Kết quả thực tế** | **(a)** Khớp với `test_personal_charging_is_billed_once_on_consolidated_checkout` trong `tests/test_submission_2_acceptance.py` (test kiểm tra `energy_fee == round(kwh × 7.000)`, số dư ví, cọc và cổng sạc); các con số cụ thể ở trên đo lại bằng cùng kịch bản ngày 23/11/2026.<br>**(b)** Khớp với `test_reserve_and_checkin_checkout_lifecycle` trong `tests/test_personal_ev.py` (dòng 87–104). |
| **Trạng thái** | `PASS` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — chạy lại pytest ngày 23/11/2026 (60/60 PASS). |

### `TC-SS2-08` — Check-out khi ví thiếu số dư (ghi nhận nợ minh bạch) và chống gọi Check-out lặp (Luồng ngoại lệ)

| Trường | Nội dung chi tiết |
| :--- | :--- |
| **Test ID / UC / Method ID** | `TC-SS2-08` / `UC_SS2_04` / `SS2-MTH-10` (`PersonalEVService.check_out_personal_ev`) |
| **Tiền điều kiện** | Đơn `reservation_id` đang ở trạng thái `CHECKED_IN`; trước khi Check-out, số dư khả dụng của ví sau khi hoàn cọc nhỏ hơn tổng phí hóa đơn (ví dụ tổng số dư khả dụng sau hoàn cọc là `30.000 VNĐ`, trong khi `total_amount = 43.000 VNĐ`, chẳng hạn đỗ 2 giờ `10.000 VNĐ` cộng điện năng và phí quá giờ đo từ SS5 `33.000 VNĐ`). |
| **Dữ liệu vào** | Gọi `check_out_personal_ev` lần 1 với `total_amount = 43.000 VNĐ` khi ví chỉ có `30.000 VNĐ`; sau đó gọi lại `check_out_personal_ev` lần 2 trên cùng `reservation_id`. |
| **Các bước** | 1. Thiết lập số dư khả dụng của ví sao cho sau khi giải phóng cọc đạt `30.000 VNĐ`.<br>2. Gọi `check_out_personal_ev` lần 1 (`total_amount = 43.000 VNĐ`).<br>3. Kiểm tra `wallet["balance"]`, `wallet["debt"]`, `inv["debt_incurred"]` và `hub["available_slots"]`.<br>4. Gọi tiếp `check_out_personal_ev` lần 2 trên cùng `reservation_id`. |
| **Kết quả mong đợi** | • Lần 1: Trả về `ok == True`; `inv["deducted_from_wallet"] == 30.000 VNĐ`, `inv["debt_incurred"] == 13.000 VNĐ`; `wallet["balance"] == 0`, `wallet["debt"] == 13.000 VNĐ`; xe vẫn được giải phóng khỏi Hub (`available_slots` tăng +1) và `res["status"] == "COMPLETED"`.<br>• Lần 2: Trả về `ok == False` do `res["status"] != "CHECKED_IN"`; không cộng thêm `available_slots` và không ghi nợ lặp lần hai. |
| **Kết quả thực tế** | CHƯA CHẠY RIÊNG (Đã triển khai tại dòng 309–310 (chặn check-out lặp) và 369–380 (trừ ví, ghi nợ) trong `src/core/personal_ev.py`). |
| **Trạng thái** | `DESIGNED` |
| **Người / ngày kiểm tra** | Nguyễn Anh Tài (`2413035`) — thiết kế ngày 30/10/2026. |


## Đối chiếu thực thi 06/11/2026

Bộ49 test hiện có đã chạy PASS (log baseline chung). Các tên test dẫn trong traceability.md được đối chiếu với nguồn. Nhãn PASS của bản bàn giao chỉ có hiệu lực trong phạm vi các assert thực sự có trong test đó; các điều kiện mở rộng/operation_key/service đề xuất vẫn DESIGNED. Không dùng test của core để xác nhận service chưa tồn tại.

Test đăng ký hiện tại có kiểm tra duplicate khác dấu gạch/khoảng trắng (59-X1 77777 và 59X1-77777); đã đối chiếu đúng nguồn, không cần suy rộng ngoài các assert có sẵn.

## Đối chiếu thực thi 23/11/2026

Chạy lại toàn bộ `pytest`: 60/60 PASS. Code SS2 đã thay đổi sau Sub3: phí đỗ tính theo giờ bắt đầu, tối thiểu 1 giờ (`5.000 VNĐ/giờ`, giá demo, cấu hình qua `EMOBILITY_PARKING_HOURLY_VND`) và điện năng/phí quá giờ lấy từ phiên sạc SS5. Vì vậy `TC-SS2-07` được viết lại theo hai test tự động hiện có; số dòng code trong `TC-SS2-04`, `TC-SS2-08` được cập nhật. `TC-SS2-04` và `TC-SS2-08` vẫn ở trạng thái `DESIGNED`.
