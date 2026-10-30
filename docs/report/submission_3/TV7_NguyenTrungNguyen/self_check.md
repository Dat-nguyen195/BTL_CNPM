# Tự kiểm tra — Nguyễn Trung Nguyên — SS7

**Phiên bản sản phẩm:** 1.0 (báo cáo TV7 và PDF ngày 30/10/2026).  
**Trạng thái xác nhận:** 30/10/2026.  
**Nguyên tắc:** tác giả tự kiểm tra, tự sửa và tự chịu trách nhiệm; không có kiểm tra chéo.

## Task cá nhân kế thừa từ hướng dẫn

- [x] `TV7-01` — Lập danh sách lớp SS7 và thông tin thực tế cho Deployment view.
- [x] `TV7-02` — Mô tả triển khai hiện tại và sử dụng schema preview/Apply đã chốt ở mục 2.3.
- [x] `TV7-03` — Tạo class diagram SS7 và Deployment view, đủ nguồn + ảnh.
- [ ] `TV7-04` — Mô tả tác động sự cố, gợi ý Hub và cách gọi giao tiếp `INT-05` đến `INT-10` trong phần SS7.
- [x] `TV7-05` — Mô tả đủ phương thức, điều kiện Apply/điều hướng và giới hạn tích hợp ngoài.
- [x] `TV7-06` — Hoàn thành báo cáo nháp, truy vết, test case bonus nếu thực hiện và khai báo AI.
- [x] `TV7-07` — Tự kiểm tra SS7, sự cố, điều hướng và Deployment view; ghi `self_check.md`.
- [x] `TV7-08` — Tự đối chiếu ánh xạ dữ liệu vào ChargingService/SimulationCoordinator; kiểm tra hướng dẫn chạy và vòng đời session.
- [x] `TV7-09` — Tự sửa lỗi, kiểm tra lại; xuất Deployment view hoàn chỉnh có chú giải/thuyết minh.
- [x] `TV7-10` — Cung cấp nguồn, ảnh, phiên bản và thuyết minh triển khai chung cho cả nhóm.
- [x] `TV7-11` — Xuất PDF cá nhân hoàn chỉnh, kiểm tra hình deployment và bàn giao cùng nguồn.
- [ ] `TV7-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

> **Chú thích bổ sung:** Báo cáo SS7 nêu INT-05/06/07/09/10; chưa mô tả INT-08, nên `TV7-04` chưa được đánh dấu hoàn tất. INT-08 thuộc `DemandSimulationService` của TV6; cần xác nhận với hướng dẫn/chủ sở hữu nếu yêu cầu mục này phải bao gồm cả INT-08.

## Tiêu chí chất lượng trước khi bàn giao

- [x] Có đủ Deployment view và Development/Implementation view; phân biệt đúng vai trò hai view.
- [ ] Phạm vi UC cá nhân đầy đủ: SS1 có 3, SS2 có 4, SS3–SS7 mỗi SS có 2.
- [x] Class diagram thể hiện trách nhiệm, kiểu dữ liệu, quan hệ và bội số hợp lý.
- [x] Mọi phương thức được vẽ có mô tả tương ứng; tên và chữ ký khớp nhau.
- [x] Có điều kiện trước/sau, lỗi, tác động dữ liệu và quy tắc xử lý lặp khi cần.
- [x] Truy vết đến đúng UC và thông điệp/nhánh từ Sub2; không dùng ID tự đặt thay ID chuẩn.
- [ ] Lớp và giao tiếp dùng chung khớp bản đã chốt; không có bảy định nghĩa Hub khác nhau.
- [x] Mốc 30 phút đúng phạm vi; các quy tắc 15 phút khác không bị thay theo.
- [x] Trạng thái và đơn vị đúng; bảo toàn sức chứa, công suất và tài chính được giải thích.
- [x] Phân biệt code hiện tại với thiết kế đề xuất, mock và mở rộng tương lai.
- [x] Test có đầu vào/kết quả cụ thể; trạng thái PASS có bằng chứng thực thi.
- [x] PDF đọc được, không cắt hình/bảng; đóng góp cá nhân và AI được khai báo đúng.

> **Chú thích bổ sung:** Các ô được đánh dấu phản ánh phần SS7 và bằng chứng trong bộ file TV7. Chưa đánh dấu tiêu chí phạm vi UC toàn nhóm và xác nhận bảy định nghĩa Hub dùng chung vì cần đối chiếu sản phẩm của toàn nhóm, không thể xác nhận chỉ từ phần TV7. PDF đã được xuất và kiểm tra bố cục trong phiên hỗ trợ; TV7 cần mở lại bản cuối trước khi nộp.

## Kết quả tự kiểm tra thực tế

- **Đã kiểm tra file/phiên bản nào:** `REPORT_SUB3.md` phiên bản 1.0; `traceability.md`; `test_cases.md`; `ai_usage.md`; nguồn và ảnh Deployment view, class diagram SS7, Implementation view SS7; PDF `output/submission_3/REPORT_SUB3_NguyenTrungNguyen_2011710.pdf`.
- **Kết quả và bằng chứng:** PlantUML syntax check và xuất PNG/SVG đạt cho ba sơ đồ TV7; PDF cá nhân 13 trang đã được mở kiểm tra bố cục trong phiên hỗ trợ. Test prototype hiện có: PowerShell `$env:PYTHONPATH = (Resolve-Path .\src).Path; python -m pytest -q tests/test_simulations.py` — PASS, 2 passed; PowerShell `$env:PYTHONPATH = (Resolve-Path .\src).Path; python -m pytest -q tests/test_submission_2_acceptance.py -k rerouting` — PASS, 1 passed, 12 deselected. Sáu test bonus `SS7-TC-01`–`SS7-TC-06` được thiết kế, chưa chạy riêng; xem `test_cases.md`.
- **Vấn đề còn mở:** báo cáo TV7 chưa mô tả INT-08; prototype chưa tích hợp `ChargingService`/INT-05 hoặc `SimulationCoordinator`/INT-10; chưa có port ID, tích hợp IoT hay phát hiện mất điện thật; routing chưa lọc Hub theo trạng thái OFFLINE chuẩn. Việc nộp LMS và tiêu chí xác nhận dùng chung cấp nhóm chưa được xác nhận.
- **Xác nhận của tác giả:** TV7 đã kiểm tra phần của mình  ngày 30/10/2026.

> **Chú thích bổ sung:** Ô `TV7-12` để trống vì chưa có bằng chứng xác nhận tải bộ file lên LMS hoặc biên nhận/trạng thái nộp. Việc đánh dấu phản ánh bằng chứng có trong repository và kiểm tra kỹ thuật đã thực hiện; TV7 tự chịu trách nhiệm xác nhận cuối cùng theo nguyên tắc ở đầu checklist.
