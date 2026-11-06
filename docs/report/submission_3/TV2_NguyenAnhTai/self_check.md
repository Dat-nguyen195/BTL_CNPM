# Tự kiểm tra — Nguyễn Anh Tài — SS2

**Họ và tên:** Nguyễn Anh Tài  
**MSSV:** 2413035  
**Phạm vi chịu trách nhiệm:** Thành viên 2 (TV2) — Phân hệ SS2: Xe cá nhân, chỗ đỗ và check-in/out (`UC_SS2_01`, `UC_SS2_02`, `UC_SS2_03`, `UC_SS2_04`)  
**Phiên bản sản phẩm:** v1.0 (Ngày 31/10/2026)  
**Trạng thái xác nhận:** ĐÃ TỰ KIỂM TRA (`SELF_CHECKED`)  
**Nguyên tắc:** Tác giả tự kiểm tra, tự sửa và tự chịu trách nhiệm về nội dung, tiến độ, bằng chứng thực hiện của phần mình.

---

## 1. Task cá nhân kế thừa từ hướng dẫn (`TV2-01` → `TV2-12`)

- [x] `TV2-01` — Xác nhận đủ 4 UC SS2 (`UC_SS2_01` → `UC_SS2_04`), danh sách lớp (`PersonalVehicle`, `ParkingReservation`, `ParkingSession`, `PersonalEVService`) và ánh xạ đến code hiện có (`src/core/personal_ev.py`, `src/components/personal_ev.py`).
- [x] `TV2-02` — Áp dụng giao tiếp tài chính (`BillingService`: `hold_deposit`, `release_deposit`, `settle_no_show`, `settle_invoice`), `INT-01` (`ChargingService.request_charging`) và `INT-02` (`ChargingService.get_bill`) ở mục 2.3 trong thiết kế SS2.
- [x] `TV2-03` — Tạo class diagram nguồn + ảnh (`class_diagram.puml`, `class_diagram.svg`, `class_diagram.png`), có chủ xe (`User`), kế thừa `Vehicle`, trạm `Hub`, lượt đỗ (`ParkingReservation`, `ParkingSession`) và liên kết dịch vụ sạc (`ChargingService`).
- [x] `TV2-04` — Mô tả rõ `ownership = PERSONAL`, chỗ giữ trước (`destination_holds`) và hạn check-in 30 phút tính từ giờ đến đã chọn (`expires_at = booking_start_time + 30 phút`).
- [x] `TV2-05` — Mô tả toàn bộ phương thức xuất hiện trên sơ đồ lớp; mỗi UC của SS2 đều có lớp và phương thức chịu trách nhiệm rõ ràng.
- [x] `TV2-06` — Dùng phí đỗ mặc định `5.000 VNĐ/lượt` (`PEV_PARKING_FEE_PER_VISIT_VND`) và ghi rõ chênh lệch với yêu cầu tính theo giờ của SRS.
- [x] `TV2-07` — Hoàn thành báo cáo `REPORT_SUB3.md`, bảng truy vết `traceability.md`, bộ test case bonus `test_cases.md` và khai báo AI `ai_usage.md`.
- [x] `TV2-08` — Tự kiểm tra đủ 4 UC, tiền cọc `50.000 VNĐ` (phạt `10.000 VNĐ`, hoàn `40.000 VNĐ` khi no-show) và quyết toán hóa đơn tổng hợp; ghi `self_check.md`.
- [x] `TV2-09` — Tự đối chiếu ánh xạ dữ liệu SS2 (`ev_id` → `vehicle_id`, `ChargeLine`) vào giao tiếp `BillingService`/`ChargingService` đã chốt.
- [x] `TV2-10` — Tự rà soát, chuẩn hóa chữ ký phương thức trên sơ đồ lớp SS2 và ghi kết quả đối chiếu kiểm thử thực tế.
- [x] `TV2-11` — Xuất PDF hoàn chỉnh (`output/submission_3/REPORT_SUB3_NguyenAnhTai_2413035.pdf`), bàn giao cùng nguồn và bản kiến trúc chung đúng phiên bản khi TV3/TV7 xuất xong ảnh kiến trúc chung.
- [x] `TV2-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

---

## 2. Tiêu chí chất lượng trước khi bàn giao (Mục 8.1 Hướng dẫn)

- [x] Có đủ phần thuyết minh Deployment view và Development/Implementation view; phân biệt đúng vai trò hai view và vị trí của phân hệ SS2.
- [x] Phạm vi UC cá nhân đầy đủ: SS2 có đủ 4 UC (`UC_SS2_01`, `UC_SS2_02`, `UC_SS2_03`, `UC_SS2_04`).
- [x] Class diagram thể hiện trách nhiệm, kiểu dữ liệu, đơn vị, quan hệ và bội số hợp lý (`docs/diagrams/submission_3/SS2/class_diagram.puml`, `.svg`, `.png`).
- [x] Mọi phương thức được vẽ trên Class diagram đều có mô tả tương ứng trong Mục 6 của `REPORT_SUB3.md`; tên và chữ ký khớp nhau.
- [x] Có đầy đủ điều kiện trước/sau, mã lỗi, tác động dữ liệu và quy tắc xử lý lặp/xung đột.
- [x] Truy vết đến đúng UC và thông điệp Sequence / nhánh Activity từ Sub2; không dùng ID tự đặt thay ID chuẩn.
- [x] Lớp và giao tiếp dùng chung khớp bản đã chốt tại `shared_contracts.md` (`User / Vehicle`, `Hub`, `BillingService`, `ChargingService`).
- [x] Mốc 30 phút đúng phạm vi SS2 (`expires_at = booking_start_time + 30 phút`); các quy tắc 15 phút khác (ân hạn sạc `15 phút`, khối quá giờ `15 phút`) không bị thay theo.
- [x] Trạng thái (`ParkingReservationStatus`) và đơn vị (`VNĐ`, `kWh`, `%`, `UTC+7`) đúng; bảo toàn sức chứa Hub (`destination_holds`, `available_slots`, `current_vehicles`) và tài chính được giải thích nhất quán.
- [x] Phân biệt rõ code hiện tại (`<<implemented UI>>`, `<<implemented module>>`) với thiết kế đề xuất (`<<entity, proposed>>`, `<<proposed service>>`) và hợp đồng dùng chung (`<<shared contract>>`).
- [x] Test case có đầu vào/kết quả cụ thể; chỉ ghi `PASS` cho các ca đã có kiểm thử tự động trong `tests/test_personal_ev.py` và `tests/test_reservation_30_minutes.py`, các ca mở rộng chưa chạy ghi `DESIGNED`.
- [x] Đóng góp cá nhân và phạm vi sử dụng AI được khai báo trung thực tại `ai_usage.md`.

---

## 3. Kết quả tự kiểm tra thực tế

- **Đã kiểm tra file/phiên bản nào:**
  - Nguồn và ảnh sơ đồ lớp SS2: [class_diagram.puml](<../../../diagrams/submission_3/SS2/class_diagram.puml>), [class_diagram.svg](<../../../diagrams/submission_3/SS2/class_diagram.svg>), [class_diagram.png](<../../../diagrams/submission_3/SS2/class_diagram.png>) (v1.0 — 31/10/2026).
  - Báo cáo và tài liệu SS2: [REPORT_SUB3.md](<REPORT_SUB3.md>), [traceability.md](<traceability.md>), [test_cases.md](<test_cases.md>), [ai_usage.md](<ai_usage.md>).
  - Mã nguồn và kiểm thử đối chiếu: `src/core/personal_ev.py`, `src/components/personal_ev.py`, `src/core/billing.py`, `src/core/policies.py`, `tests/test_personal_ev.py`, `tests/test_reservation_30_minutes.py`.
- **Kết quả và bằng chứng:**
  - Sơ đồ lớp SS2 đã xuất thành công ra `.svg` và `.png` từ nguồn `.puml`, bao phủ đầy đủ 4 lớp của SS2, 2 module thực thi và 4 hợp đồng dùng chung.
  - Đối chiếu 100% chữ ký phương thức trên sơ đồ lớp với bảng Method Descriptions trong `REPORT_SUB3.md`.
- **Vấn đề còn mở (Công khai theo Mục 7 & Mục 9.2):**
  1. Biểu phí đỗ xe cá nhân trong prototype giữ mức cố định `5.000 VNĐ/lượt` (`PEV_PARKING_FEE_PER_VISIT_VND`), còn chênh lệch với yêu cầu tính theo giờ của SRS (đã ghi nhận rõ trong thiết kế).
  2. Trong prototype hiện tại, khi xe cá nhân Check-in có nhu cầu sạc mới chỉ giảm trực tiếp `charging_ports.available` và khi Check-out tự tính phí từ tham số mô phỏng; việc kết nối trực tiếp sang `SmartChargingScheduler` (SS5) qua `INT-01` và `INT-02` đang ở mức thiết kế hợp đồng Sub3.
  3. Luồng nhân viên vận hành (`OPERATOR`) xác nhận thanh toán ngoại tuyến (`US-12`) mới mô hình hóa ở mức thiết kế, chưa tách giao diện riêng trong prototype.
- **Xác nhận của tác giả:** **ĐÃ TỰ KIỂM TRA (`SELF_CHECKED`)** — Tôi (Nguyễn Anh Tài — 2413035) xác nhận đã tự kiểm tra và chịu trách nhiệm về nội dung, tiến độ và bằng chứng thực hiện của phân hệ SS2.
