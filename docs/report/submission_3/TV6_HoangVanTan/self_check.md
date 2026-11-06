# Bản tự kiểm tra chất lượng cá nhân — Hoàng Văn Tấn — SS6
**Phân hệ:** SS6 — Mô phỏng nhu cầu What-if & Dự báo 24 giờ  
**Thành viên:** Hoàng Văn Tấn — MSSV: 2213074 — Vai trò: TV6  
**Phiên bản sản phẩm:** 1.0 (Submission 3 Final)  
**Ngày tự kiểm tra:** 02/11/2026  
**Trạng thái xác nhận:** ĐÃ TỰ KIỂM TRA & XÁC NHẬN CHỊU TRÁCH NHIỆM NỘI DUNG.

---

## 1. Tiến độ hoàn thành 12 nhiệm vụ cá nhân (Checklist TV6)

- [x] `TV6-01` — Lập danh sách lớp SS6 (`DemandScenario`, `ForecastPoint`, `ForecastResult`, `SimulationPreview`, `ApplyResult`, `DemandSimulationService`, `ForecastService`, `SimulationCoordinator`), đầu vào/đầu ra dự báo và ánh xạ đến mã nguồn thực tế.
- [x] `TV6-02` — Tạo Class Diagram nguồn PlantUML (`docs/diagrams/submission_3/SS6/class_diagram.puml`) và xuất ảnh (`.png`, `.svg`), phân định rõ Boundary, Service, Coordinator, Entity và Adapter.
- [x] `TV6-03` — Mô tả chi tiết các lớp dùng chung liên phân hệ: `ForecastResult`, `SimulationPreview` và `SimulationCoordinator` theo quyết định mục 2.2–2.3 của GUIDANCE.
- [x] `TV6-04` — Mô tả đầy đủ toàn bộ 8 phương thức trên class diagram, chuẩn hóa đơn vị, hạt giống seed, horizon 24 giờ và luồng preview/apply.
- [x] `TV6-05` — Ghi nhận trung thực các giả định và giới hạn của mô hình biến động doanh thu US-21, đề xuất công thức mở rộng, không nhận vơ số liệu doanh thu tĩnh từ SS3 Dashboard.
- [x] `TV6-06` — Hoàn thiện báo cáo cá nhân `REPORT_SUB3.md`, 7 ca test case bonus, bản khai báo AI và ma trận truy vết SS6.
- [x] `TV6-07` — **[Nhiệm vụ nhóm]** Tổng hợp Bảng ma trận truy vết toàn diện cho 17 Use Cases tại `docs/traceability/submission_3.md` từ dữ liệu của các thành viên.
- [x] `TV6-08` — Tự kiểm tra SS6 và cơ chế preview/apply thuộc sở hữu thông qua test suite tự động; ghi nhận vào `self_check.md`.
- [x] `TV6-09` — Tự sửa và rà soát tính nhất quán nội bộ SS6; cập nhật chỉ mục truy vết và trạng thái test theo bàn giao của từng tác giả.
- [x] `TV6-10` — **[Nhiệm vụ nhóm]** Phân định rõ ràng các ca kiểm thử đã chạy (PASS), chưa chạy (NOT_RUN) và mới thiết kế (DESIGNED) trong bảng test chung.
- [x] `TV6-11` — Kết xuất báo cáo PDF cá nhân hoàn chỉnh `output/submission_3/REPORT_SUB3_HoangVanTan_2213074.pdf`, sẵn sàng bàn giao nguồn và tài liệu.
- [x] `TV6-12` — Kiểm kê danh mục file, xác nhận đầy đủ bộ hồ sơ và chuẩn bị nộp bài theo hướng dẫn LMS.

---

## 2. Đối chiếu 12 tiêu chí chất lượng nghiêm ngặt (Mục 8.1 GUIDANCE)

| STT | Tiêu chí chất lượng | Kết quả đối chiếu thực tế | Đánh giá |
| :---: | :--- | :--- | :---: |
| 1 | Có đủ Deployment view và Development/Implementation view; phân biệt đúng vai trò 2 view | Đã phân tích rõ trong mục 2 & 3 của `REPORT_SUB3.md`; chỉ rõ vị trí module `sim_demand.py` và luồng tiến trình Streamlit | **ĐẠT** |
| 2 | Phạm vi UC cá nhân đầy đủ: SS6 có đủ 2 UC (`UC_SS6_01`, `UC_SS6_02`) | Bao phủ trọn vẹn cả 2 UC và liên kết đến sequence/activity diagrams từ Sub 2 | **ĐẠT** |
| 3 | Class diagram thể hiện trách nhiệm, kiểu dữ liệu, quan hệ và bội số hợp lý | Sơ đồ lớp chuẩn PlantUML, có đủ stereotype, kiểu trả về, bội số quan hệ và note giải thích | **ĐẠT** |
| 4 | Mọi phương thức được vẽ có mô tả tương ứng; tên và chữ ký khớp nhau | Toàn bộ 8 phương thức trên diagram đều có mục mô tả chi tiết từ `SS6-MTH-01` đến `SS6-MTH-08` | **ĐẠT** |
| 5 | Có điều kiện trước/sau, lỗi, tác động dữ liệu và quy tắc xử lý lặp khi cần | Mục 6 mô tả chi tiết precondition, postcondition, mã lỗi và cơ chế chống stale/duplicate apply | **ĐẠT** |
| 6 | Truy vết đến đúng UC và thông điệp/nhánh từ Sub 2; không dùng ID tự đặt | Bảng `traceability.md` dẫn đúng tên file `.puml` và từng bước trong kịch bản Sub 2 | **ĐẠT** |
| 7 | Lớp và giao tiếp dùng chung khớp bản đã chốt; không tự sinh định nghĩa Hub riêng | Sử dụng đúng schema `SimulationPreview`, `ApplyResult` và `OperationResult` đã chốt tại mục 2.2–2.3 | **ĐẠT** |
| 8 | Chân trời dự báo 24 giờ chuẩn hóa; các chính sách không bị thay đổi sai lệch | `ForecastService` bắt buộc `hours=24`; tốc độ phục vụ 8 xe/h giữ nguyên theo quy chuẩn | **ĐẠT** |
| 9 | Trạng thái và đơn vị đúng; bảo toàn sức chứa và cô lập dữ liệu được giải thích | Giải thích rõ `admitted` vs `unserved`, phần trăm lấp đầy trạm, deepcopy isolation và `bump_state_version` | **ĐẠT** |
| 10 | Phân biệt code hiện tại với thiết kế đề xuất, mock và mở rộng tương lai | Chỉ rõ hàm nào đã có trong `sim_demand.py`/`simulator.py`, lớp nào là DTO đề xuất, mô hình doanh thu là mở rộng | **ĐẠT** |
| 11 | Test có đầu vào/kết quả cụ thể; trạng thái PASS có bằng chứng thực thi | Chạy thực tế bộ test script với python 3.12, 7/7 test đạt PASS với log assert đầy đủ | **ĐẠT** |
| 12 | PDF đọc được, không cắt hình/bảng; đóng góp cá nhân và AI được khai báo đúng | PDF định dạng chuẩn A4, hình ảnh sắc nét, có khai báo AI và prompt history trung thực | **ĐẠT** |

---

## 3. Xác nhận trách nhiệm của tác giả
- **Tác giả cam đoan:** Toàn bộ nội dung trong hồ sơ thiết kế SS6 và bảng truy vết hệ thống do tôi phụ trách đã được tự kiểm tra kỹ lưỡng, đối chiếu trực tiếp với mã nguồn và tài liệu nhóm. Không có lỗi Blocker hoặc Major tồn đọng.
- **Ký tên xác nhận:** Hoàng Văn Tấn (02/11/2026).
