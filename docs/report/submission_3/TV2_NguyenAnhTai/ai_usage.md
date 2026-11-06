# Khai báo AI — Nguyễn Anh Tài — SS2

**Họ và tên:** Nguyễn Anh Tài  
**MSSV:** 2413035  
**Phân hệ phụ trách:** SS2 — Xe cá nhân, chỗ đỗ và check-in/out  
**Trạng thái:** Đã hoàn thiện khai báo thực tế (31/10/2026).

---

## 1. Phần hỗ trợ ở cấp nhóm đã biết

AI (Codex) đã hỗ trợ trưởng nhóm (TV1) rà soát cách tổ chức thư mục, tạo hướng dẫn `GUIDANCE_FOR_SUB_3.md`, tài liệu `shared_contracts.md` và bộ khung Markdown/PlantUML ban đầu cho 7 thành viên.

---

## 2. Khai báo chi tiết của tác giả (TV2 — Nguyễn Anh Tài)

- **Công cụ / Model thực tế đã dùng:** ChatGPT.
- **Phạm vi và mức đóng góp của AI:**
  - Hỗ trợ tóm tắt yêu cầu từ `GUIDANCE_FOR_SUB_3.md`, hợp đồng dùng chung, mã nguồn SS2 và đối chiếu mã nguồn hiện tại (`src/core/personal_ev.py`, `src/components/personal_ev.py`, `src/core/billing.py`, `src/core/policies.py`, `tests/test_personal_ev.py`, `tests/test_reservation_30_minutes.py`).
  - Hỗ trợ biên tập, chỉnh sửa và mã nguồn PlantUML cho sơ đồ lớp SS2 (`docs/diagrams/submission_3/SS2/class_diagram.puml`) theo đúng định dạng chuẩn của nhóm.
  - Hỗ trợ ánh xạ và biên tập cấu trúc bảng cho phần Mô tả Lớp (Class Descriptions), Mô tả Phương thức (Method Descriptions), Bảng Truy vết (`traceability.md`) và Bộ Test Case (`test_cases.md`) trong `REPORT_SUB3.md`.
- **Phần cá nhân tự phân tích, chỉnh sửa và kiểm tra:**
  - Tự rà soát quy tắc nghiệp vụ của phân hệ SS2, đặc biệt là mốc hạn chót `expires_at = booking_start_time + 30 phút`, phương trình bảo toàn sức chứa Hub khi giữ chỗ/check-in/check-out và quy tắc quyết toán cọc `50.000 VNĐ` (phạt no-show `10.000 VNĐ`, hoàn `40.000 VNĐ`).
  - Yêu cầu điều chỉnh phạm vi sơ đồ lớp: rút gọn các lớp dùng chung của TV1, TV3, TV5 thành các khối `<<shared contract>>`, đồng thời bổ sung đầy đủ ngăn phương thức (`--`) cho các lớp thực thể (`PersonalVehicle`, `ParkingReservation`, `ParkingSession`), lớp dịch vụ (`PersonalEVService`) và module thực thi (`core.personal_ev`, `personal_ev.render`).
  - Tự kết xuất, kiểm tra trực quan file ảnh `class_diagram.svg` và `class_diagram.png` trong thư mục `docs/diagrams/submission_3/SS2/` (Thống nhất chỉ dùng `.puml`, `.svg`, `.png`).
- **Gợi ý của AI đã giữ / bỏ và lý do:**
  - **Đã giữ:** Cấu trúc tách lớp đề xuất `ParkingReservation` (quản lý giữ chỗ trước) và `ParkingSession` (quản lý phiên đỗ vật lý từ Check-in đến Check-out), cách ánh xạ `ev_id` → `vehicle_id` và tích hợp hợp đồng `BillingService` (TV1) cùng `INT-01`/`INT-02` của `ChargingService` (TV5).
  - **Đã bỏ / điều chỉnh:** Loại bỏ phiên bản sơ đồ lớp thiếu ngăn phương thức trên các lớp thực thể và loại bỏ file `.drawio` để bám sát quy chuẩn PlantUML (`.puml`, `.svg`, `.png`) của nhóm.
- **Nội dung dùng chung và chủ sở hữu:**
  - Hợp đồng tài chính (`BillingService`, `OperationResult`, `ChargeLine`, `DepositResult`, `SettlementResult`) và mô hình `User / Vehicle`: **TV1 — Nguyễn Thành Đạt**.
  - Mô hình `Hub` và kiến trúc Implementation view: **TV3 — Phạm Tiến Đạt**.
  - Hợp đồng dịch vụ sạc (`ChargingService` — `INT-01`, `INT-02`): **TV5 — Dương Đăng Khoa**.
  - Kiến trúc Deployment view: **TV7 — Nguyễn Trung Nguyên**.
- **Prompt history:** [Tệp cá nhân Submission 3](<../../../prompt-history/TV2_NguyenAnhTai/prompt_history_NguyenAnhTai_sub3.txt>).


## Bổ sung khi tổng hợp 06/11/2026

Codex (AI assistant trong phiên làm việc của trưởng nhóm) đọc đề giảng viên, SRS, code và bài bàn giao; hỗ trợ review, sửa/bổ sung Markdown/PlantUML, danh mục phương thức/truy vết, kiểm tra kỹ thuật và tạo PDF. Mức đóng góp AI trong đợt này là trực tiếp soạn/chỉnh nội dung và tự động hóa kiểm tra; không phải chỉ sửa chính tả. Trưởng nhóm yêu cầu công việc; chủ sở hữu chưa xác nhận đã đọc/hiểu mọi bản sửa. Lịch sử prompt trước giữ nguyên; bản ghi revision ở docs/prompt-history/submission_3_integration_20261106.md, không giả lập hội thoại cá nhân bị thiếu.
