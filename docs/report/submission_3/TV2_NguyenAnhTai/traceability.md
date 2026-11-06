# Truy vết cá nhân — Nguyễn Anh Tài — SS2

**MSSV:** 2413035  
**Phân hệ:** SS2 — Xe cá nhân, chỗ đỗ và check-in/out  
**Trạng thái:** HOÀN THIỆN (`SELF_CHECKED` — 31/10/2026).  

[Manifest Sub2](<../../../traceability/submission_2.json>) · [Báo cáo thiết kế SS2](<REPORT_SUB3.md>) · [Sơ đồ lớp SS2 (.puml)](<../../../diagrams/submission_3/SS2/class_diagram.puml>) · [Sơ đồ lớp SS2 (.svg)](<../../../diagrams/submission_3/SS2/class_diagram.svg>) · [Sơ đồ lớp SS2 (.png)](<../../../diagrams/submission_3/SS2/class_diagram.png>)

---

## 1. Bảng tổng hợp truy vết Sub1 → Sub2 → Sub3 (Phân hệ SS2)

| US / FR (SRS Sub1) | Use Case (Sub2) | File & Thông điệp Sequence / Nhánh Activity (Sub2) | Lớp thiết kế (Sub3) | Method ID & Chữ ký phương thức (Sub3) | Code hiện tại (`src/`) | Test ID & Kiểm thử |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `US-08`<br>`FR-03` | `UC_SS2_01`<br>Đăng ký xe EV cá nhân lên hệ thống | • Sequence: `UC_SS2_01_NguyenAnhTai_sequence.puml` — Nhóm 2 (`Nhập và kiểm tra thông tin đăng ký`), Nhóm 3 (`3.1 Tra cứu biển số và tài khoản sở hữu`, `3.2 Cấp mã xe, liên kết tài khoản; ghi thời điểm đăng ký và trạng thái REGISTERED`)<br>• Activity: `UC_SS2_01_NguyenAnhTai_activity.puml` — Nhánh kiểm tra thông tin bắt buộc, đối chiếu trùng biển số chuẩn hóa và lưu hồ sơ `personal_evs` | `PersonalVehicle`<br>(`SS2-CLS-01`)<br>`PersonalEVService`<br>(`SS2-CLS-04`)<br>`core.personal_ev`<br>(`SS2-CLS-06`)<br>`personal_ev.render`<br>(`SS2-CLS-05`) | • `SS2-MTH-01`: `PersonalVehicle.normalize_plate(raw_plate: str): str`<br>• `SS2-MTH-07`: `PersonalEVService.register_personal_ev(owner_id: str, owner_name: str, plate_number: str, vehicle_type: str, brand: str, battery_kwh: float): OperationResult[PersonalVehicle]`<br>• `SS2-IMP-02`: `personal_ev.render()` (Tab 1) | `src/core/personal_ev.py`:<br>`register_personal_ev()`<br>`src/components/personal_ev.py`:<br>Tab 1 (`pev_reg_form`) | • `test_register_personal_ev_success_and_duplicate` (`tests/test_personal_ev.py`)<br>• `TC-SS2-01` (`PASS`)<br>• `TC-SS2-02` (`PASS`) |
| `US-09`<br>`US-10`<br>`US-12`<br>`FR-04`<br>`FR-05b` | `UC_SS2_02`<br>Đặt trước chỗ đỗ và nhu cầu sạc xe EV cá nhân | • Sequence: `UC_SS2_02_NguyenAnhTai_sequence.puml` — Nhóm 2 (`Kiểm tra thời gian, lịch trùng và vị trí AVAILABLE`), Nhóm 3 (`Kiểm tra số dư khả dụng >= 50.000 VNĐ`, `Tạm giữ 50.000 VNĐ tiền cọc`, `Đặt hạn Check-in = booking_start_time + 30 phút`), Nhóm 4 (`Đến booking_start_time + 30 phút và chưa Check-in -> EXPIRED`)<br>• Activity: `UC_SS2_02_NguyenAnhTai_activity.puml` — Nhánh kiểm tra sở hữu xe, sức chứa Hub, khóa cọc và quét quá hạn 30 phút | `PersonalVehicle`<br>(`SS2-CLS-01`)<br>`ParkingReservation`<br>(`SS2-CLS-02`)<br>`PersonalEVService`<br>(`SS2-CLS-04`)<br>`BillingService` *(TV1)*<br>`Hub` *(TV3)* | • `SS2-MTH-02`: `PersonalVehicle.is_owned_by(user_id: str): bool`<br>• `SS2-MTH-03`: `ParkingReservation.is_expired(sim_now: datetime): bool`<br>• `SS2-MTH-08`: `PersonalEVService.reserve_personal_ev_slot(owner_id: str, vehicle_id: str, hub_id: str, booking_start_time: datetime, request_charging: bool = False, current_soc: float = 50.0, operation_key: str = ""): OperationResult[ParkingReservation]`<br>• `SS2-MTH-11`: `PersonalEVService.sweep_expired_personal_reservations(sim_now: datetime): OperationResult[list[str]]`<br>• Hợp đồng TV1: `BillingService.hold_deposit()`, `BillingService.settle_no_show()` | `src/core/personal_ev.py`:<br>`reserve_personal_ev_slot()`<br>`sweep_expired_personal_reservations()`<br>`src/core/billing.py`:<br>`hold_deposit()`<br>`settle_pev_noshow_penalty()`<br>`src/components/personal_ev.py`:<br>Tab 2 (`pev_res_form`) | • `test_reserve_and_checkin_checkout_lifecycle` (`tests/test_personal_ev.py`)<br>• `test_reservation_30_minute_boundary_and_single_settlement` (`tests/test_reservation_30_minutes.py`)<br>• `TC-SS2-03` (`PASS`)<br>• `TC-SS2-04` (`DESIGNED`)<br>• `TC-SS2-06` (`PASS`) |
| `US-11b`<br>`FR-03b` | `UC_SS2_03`<br>Check-in xe EV cá nhân tại cổng Hub (QR/Biển số) | • Sequence: `UC_SS2_03_NguyenAnhTai_sequence.puml` — Nhóm 1 (`1.1 Đối chiếu QR/PIN, xe, quyền sử dụng, đơn đặt chỗ, Hub và khung giờ`), Nhóm 2 (`Ghi thời điểm Check-in; đơn = CHECKED_IN; vị trí RESERVED -> OCCUPIED`), Nhóm 3 (`Kích hoạt phiên sạc`)<br>• Activity: `UC_SS2_03_NguyenAnhTai_activity.puml` — Nhánh quét hết hạn trước, kiểm tra `booking_start_time <= sim_now < expires_at`, giảm `destination_holds` mà không trừ `available_slots` lần hai | `ParkingReservation`<br>(`SS2-CLS-02`)<br>`ParkingSession`<br>(`SS2-CLS-03`)<br>`PersonalEVService`<br>(`SS2-CLS-04`)<br>`ChargingService` *(TV5)*<br>`Hub` *(TV3)* | • `SS2-MTH-04`: `ParkingReservation.can_check_in(sim_now: datetime): bool`<br>• `SS2-MTH-05`: `ParkingSession.attach_charging_ref(request_id: str, session_id: str \| None = None): None`<br>• `SS2-MTH-09`: `PersonalEVService.check_in_personal_ev(owner_id: str, reservation_id: str, operation_key: str = ""): OperationResult[ParkingSession]`<br>• `SS2-MTH-11`: `PersonalEVService.sweep_expired_personal_reservations(sim_now: datetime): OperationResult[list[str]]`<br>• Hợp đồng TV5 (`INT-01`): `ChargingService.request_charging()` | `src/core/personal_ev.py`:<br>`check_in_personal_ev()`<br>`sweep_expired_personal_reservations()`<br>`src/components/personal_ev.py`:<br>Tab 3 (`btn_checkin_...`) | • `test_reserve_and_checkin_checkout_lifecycle` (`tests/test_personal_ev.py`)<br>• `test_reservation_30_minute_boundary_and_single_settlement` (`tests/test_reservation_30_minutes.py`)<br>• `TC-SS2-05` (`PASS`)<br>• `TC-SS2-06` (`PASS`) |
| `US-09`<br>`US-10`<br>`US-11`<br>`US-11b`<br>`US-12`<br>`FR-03b`<br>`FR-04`<br>`FR-05b`<br>`FR-15b` | `UC_SS2_04`<br>Check-out và thanh toán tổng hợp dịch vụ xe EV cá nhân | • Sequence: `UC_SS2_04_NguyenAnhTai_sequence.puml` — Nhóm 1 (`Tra cứu phiên đỗ đã CHECKED_IN`), Nhóm 2 (`Kết thúc sạc và lập hóa đơn tổng hợp 5.000 VNĐ/lượt + phí sạc + overstay`), Nhóm 3 (`Quyết toán hóa đơn thực tế; đối soát khoản cọc 50.000 VNĐ; ghi nợ nếu thiếu số dư`), Nhóm 5 (`Kết thúc phiên; đơn = COMPLETED; giải phóng tài nguyên một lần`)<br>• Activity: `UC_SS2_04_NguyenAnhTai_activity.puml` — Nhánh tổng hợp phí, đối trừ cọc, xử lý thiếu tiền và trả chỗ đỗ | `ParkingSession`<br>(`SS2-CLS-03`)<br>`PersonalEVService`<br>(`SS2-CLS-04`)<br>`BillingService` *(TV1)*<br>`ChargingService` *(TV5)*<br>`Hub` *(TV3)* | • `SS2-MTH-06`: `ParkingSession.build_parking_charge_line(): ChargeLine`<br>• `SS2-MTH-10`: `PersonalEVService.check_out_personal_ev(owner_id: str, reservation_id: str, operation_key: str = ""): OperationResult[SettlementResult]`<br>• Hợp đồng TV5 (`INT-02`): `ChargingService.get_bill(session_id: str)`<br>• Hợp đồng TV1: `BillingService.settle_invoice()` | `src/core/personal_ev.py`:<br>`check_out_personal_ev()`<br>`src/core/billing.py`:<br>`release_held_deposit_full()`<br>`record_wallet_debt()`<br>`src/components/personal_ev.py`:<br>Tab 4 (`btn_checkout_...`) | • `test_reserve_and_checkin_checkout_lifecycle` (`tests/test_personal_ev.py`)<br>• `TC-SS2-07` (`PASS`)<br>• `TC-SS2-08` (`DESIGNED`) |

---

## 2. Chi tiết truy vết theo từng Use Case của SS2

### 2.1. `UC_SS2_01` — Đăng ký xe EV cá nhân lên hệ thống

- **US:** `US-08`.
- **FR:** `FR-03`.
- **Scenario:** [Nguồn scenario](<../../../diagrams/Use-case detail-scenario/SS2/Usecase scenario/UC_SS2_NguyenAnhTai.md>).
- **Sequence:** [Nguồn sequence](<../../../diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_01_NguyenAnhTai_sequence.puml>).
- **Activity:** [Nguồn activity](<../../../diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_01_NguyenAnhTai_activity.puml>).
- **Component hiện tại:** [src/components/personal_ev.py](<../../../../src/components/personal_ev.py>) (Tab 1 — `pev_reg_form`), [src/core/personal_ev.py](<../../../../src/core/personal_ev.py>) (`register_personal_ev`).
- **Lớp / Method ID / chữ ký Sub3:**
  - `PersonalVehicle` (`SS2-CLS-01`) → `SS2-MTH-01`: `PersonalVehicle.normalize_plate(raw_plate: str): str`
  - `PersonalEVService` (`SS2-CLS-04`) → `SS2-MTH-07`: `PersonalEVService.register_personal_ev(owner_id: str, owner_name: str, plate_number: str, vehicle_type: str, brand: str, battery_kwh: float): OperationResult[PersonalVehicle]`
- **Thông điệp/nhánh cụ thể:**
  - Nhóm 2 Sequence (`2.1–2.4`): Kiểm tra các trường bắt buộc và chuẩn hóa biển số.
  - Nhóm 3 Sequence (`3.1–3.2`): Tra cứu trùng biển số trong `state["personal_evs"]`; nếu chưa tồn tại thì sinh `PEV-XXXXXX`, gán `ownership = "PERSONAL"`, `status = "REGISTERED"`, lưu hồ sơ và gọi `bump_state_version()`.
- **Test ID / kết quả thực tế:** `test_register_personal_ev_success_and_duplicate` (`tests/test_personal_ev.py`) — `TC-SS2-01` (`PASS`), `TC-SS2-02` (`PASS`).
- **Trạng thái thiết kế Sub3:** ĐÃ HOÀN THIỆN.

### 2.2. `UC_SS2_02` — Đặt trước chỗ đỗ và nhu cầu sạc xe EV cá nhân

- **US:** `US-09`, `US-10`, `US-12`.
- **FR:** `FR-04`, `FR-05b`.
- **Scenario:** [Nguồn scenario](<../../../diagrams/Use-case detail-scenario/SS2/Usecase scenario/UC_SS2_NguyenAnhTai.md>).
- **Sequence:** [Nguồn sequence](<../../../diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_02_NguyenAnhTai_sequence.puml>).
- **Activity:** [Nguồn activity](<../../../diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_02_NguyenAnhTai_activity.puml>).
- **Component hiện tại:** [src/components/personal_ev.py](<../../../../src/components/personal_ev.py>) (Tab 2 — `pev_res_form`), [src/core/personal_ev.py](<../../../../src/core/personal_ev.py>) (`reserve_personal_ev_slot`, `sweep_expired_personal_reservations`), [src/core/billing.py](<../../../../src/core/billing.py>) (`hold_deposit`, `settle_pev_noshow_penalty`).
- **Lớp / Method ID / chữ ký Sub3:**
  - `PersonalVehicle` (`SS2-CLS-01`) → `SS2-MTH-02`: `PersonalVehicle.is_owned_by(user_id: str): bool`
  - `ParkingReservation` (`SS2-CLS-02`) → `SS2-MTH-03`: `ParkingReservation.is_expired(sim_now: datetime): bool`
  - `PersonalEVService` (`SS2-CLS-04`) → `SS2-MTH-08`: `PersonalEVService.reserve_personal_ev_slot(...)` và `SS2-MTH-11`: `PersonalEVService.sweep_expired_personal_reservations(sim_now: datetime)`
  - Hợp đồng dùng chung TV1: `BillingService.hold_deposit()`, `BillingService.release_deposit()`, `BillingService.settle_no_show()`
- **Thông điệp/nhánh cụ thể:**
  - Nhóm 2 Sequence: Kiểm tra quyền sở hữu xe, kiểm tra không có đơn `RESERVED`/`CHECKED_IN` trùng, kiểm tra `available_slots > 0` và `charging_ports.available > 0`.
  - Nhóm 3 Sequence: Tạm giữ cọc `50.000 VNĐ`, cập nhật `destination_holds += 1`, `available_slots -= 1`, thiết lập `expires_at = booking_start_time + 30 phút`.
  - Nhóm 4 Sequence: Khi `sim_now >= expires_at` mà chưa Check-in, chuyển `status = EXPIRED`, hoàn trả `destination_holds -= 1`, `available_slots += 1`, phạt no-show `10.000 VNĐ` và hoàn `40.000 VNĐ` đúng một lần.
- **Test ID / kết quả thực tế:** `test_reserve_and_checkin_checkout_lifecycle` (`tests/test_personal_ev.py`), `test_reservation_30_minute_boundary_and_single_settlement` (`tests/test_reservation_30_minutes.py`) — `TC-SS2-03` (`PASS`), `TC-SS2-04` (`DESIGNED`), `TC-SS2-06` (`PASS`).
- **Trạng thái thiết kế Sub3:** ĐÃ HOÀN THIỆN.

### 2.3. `UC_SS2_03` — Check-in xe EV cá nhân tại cổng Hub (QR/Biển số)

- **US:** `US-11b`.
- **FR:** `FR-03b`.
- **Scenario:** [Nguồn scenario](<../../../diagrams/Use-case detail-scenario/SS2/Usecase scenario/UC_SS2_NguyenAnhTai.md>).
- **Sequence:** [Nguồn sequence](<../../../diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_03_NguyenAnhTai_sequence.puml>).
- **Activity:** [Nguồn activity](<../../../diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_03_NguyenAnhTai_activity.puml>).
- **Component hiện tại:** [src/components/personal_ev.py](<../../../../src/components/personal_ev.py>) (Tab 3), [src/core/personal_ev.py](<../../../../src/core/personal_ev.py>) (`check_in_personal_ev`).
- **Lớp / Method ID / chữ ký Sub3:**
  - `ParkingReservation` (`SS2-CLS-02`) → `SS2-MTH-04`: `ParkingReservation.can_check_in(sim_now: datetime): bool`
  - `ParkingSession` (`SS2-CLS-03`) → `SS2-MTH-05`: `ParkingSession.attach_charging_ref(request_id: str, session_id: str | None = None): None`
  - `PersonalEVService` (`SS2-CLS-04`) → `SS2-MTH-09`: `PersonalEVService.check_in_personal_ev(owner_id: str, reservation_id: str, operation_key: str = ""): OperationResult[ParkingSession]`
  - Hợp đồng dùng chung TV5 (`INT-01`): `ChargingService.request_charging(...)`
- **Thông điệp/nhánh cụ thể:**
  - Nhóm 1 Sequence: Quét hết hạn trước khi kiểm tra; đối chiếu `reservation_id`, trạng thái `RESERVED` và khung giờ `booking_start_time <= sim_now < expires_at`.
  - Nhóm 2 Sequence: Giảm `destination_holds -= 1`, giữ nguyên `available_slots`, thêm bản ghi xe cá nhân vào `hub.current_vehicles`, đổi trạng thái sang `CHECKED_IN`.
  - Nhóm 3 Sequence: Gửi yêu cầu sạc `INT-01` sang SS5 nếu `request_charging == True`.
- **Test ID / kết quả thực tế:** `test_reserve_and_checkin_checkout_lifecycle`, `test_reservation_30_minute_boundary_and_single_settlement` — `TC-SS2-05` (`PASS`), `TC-SS2-06` (`PASS`).
- **Trạng thái thiết kế Sub3:** ĐÃ HOÀN THIỆN.

### 2.4. `UC_SS2_04` — Check-out và thanh toán tổng hợp dịch vụ xe EV cá nhân

- **US:** `US-09`, `US-10`, `US-11`, `US-11b`, `US-12`.
- **FR:** `FR-03b`, `FR-04`, `FR-05b`, `FR-15b`.
- **Scenario:** [Nguồn scenario](<../../../diagrams/Use-case detail-scenario/SS2/Usecase scenario/UC_SS2_NguyenAnhTai.md>).
- **Sequence:** [Nguồn sequence](<../../../diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_04_NguyenAnhTai_sequence.puml>).
- **Activity:** [Nguồn activity](<../../../diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_04_NguyenAnhTai_activity.puml>).
- **Component hiện tại:** [src/components/personal_ev.py](<../../../../src/components/personal_ev.py>) (Tab 4), [src/core/personal_ev.py](<../../../../src/core/personal_ev.py>) (`check_out_personal_ev`), [src/core/billing.py](<../../../../src/core/billing.py>) (`release_held_deposit_full`, `record_wallet_debt`).
- **Lớp / Method ID / chữ ký Sub3:**
  - `ParkingSession` (`SS2-CLS-03`) → `SS2-MTH-06`: `ParkingSession.build_parking_charge_line(): ChargeLine`
  - `PersonalEVService` (`SS2-CLS-04`) → `SS2-MTH-10`: `PersonalEVService.check_out_personal_ev(owner_id: str, reservation_id: str, operation_key: str = ""): OperationResult[SettlementResult]`
  - Hợp đồng dùng chung TV5 (`INT-02`): `ChargingService.get_bill(session_id: str): OperationResult[ChargingBill]`
  - Hợp đồng dùng chung TV1: `BillingService.settle_invoice(owner_id: str, reference_id: str, charge_lines: list[ChargeLine], operation_key: str): OperationResult[SettlementResult]`
- **Thông điệp/nhánh cụ thể:**
  - Nhóm 2 Sequence: Lấy hóa đơn sạc từ SS5 (`INT-02`), ghép với phí đỗ xe mặc định `5.000 VNĐ/lượt` (ghi nhận chênh lệch với SRS tính theo giờ).
  - Nhóm 3 Sequence: Giải phóng cọc `50.000 VNĐ`, khấu trừ số dư ví khả dụng và ghi nhận nợ (`debt`) nếu thiếu tiền.
  - Nhóm 5 Sequence: Xóa xe khỏi `hub.current_vehicles`, tăng `hub.available_slots += 1`, đổi trạng thái đơn sang `COMPLETED` và xuất hóa đơn `PINV-XXXXXX`.
- **Test ID / kết quả thực tế:** `test_reserve_and_checkin_checkout_lifecycle` (`tests/test_personal_ev.py`) — `TC-SS2-07` (`PASS`), `TC-SS2-08` (`DESIGNED`).
- **Trạng thái thiết kế Sub3:** ĐÃ HOÀN THIỆN.
