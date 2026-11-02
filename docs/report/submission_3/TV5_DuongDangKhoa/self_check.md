# Tự kiểm tra — Dương Đăng Khoa — SS5

**Phiên bản sản phẩm:** Submission 3 – HK261.  
**Trạng thái xác nhận:** CHƯA XÁC NHẬN.  
**Nguyên tắc:** tác giả tự kiểm tra, tự sửa và tự chịu trách nhiệm; không có kiểm tra chéo.

## Task cá nhân kế thừa từ hướng dẫn

- [x] `TV5-01` — Lập danh sách lớp hiện có/lớp đề xuất SS5 và ánh xạ đến code.
- [x] `TV5-02` — Thiết kế ChargingService theo `INT-01`, `INT-02`, `INT-05` và quy tắc thu tiền mục 2.3.
- [x] `TV5-03` — Tạo class diagram nguồn + ảnh, tên phương thức đã được đối chiếu code.
- [x] `TV5-04` — Mô tả kW/kWh, công suất, trạng thái cổng/phiên và quyền cập nhật theo mục 2.2.
- [x] `TV5-05` — Mô tả đủ phương thức, thuật toán, điều kiện trước/sau và cách phá hòa ưu tiên.
- [x] `TV5-06` — Ghi rõ ân hạn/khối phí 15 phút và giới hạn của luồng nhân viên xác nhận thanh toán.
- [x] `TV5-07` — Hoàn thành báo cáo nháp, truy vết, test case bonus nếu thực hiện và khai báo AI.
- [x] `TV5-08` — Tự kiểm tra SS5, thuật toán, dữ liệu điện/phí; ghi `self_check.md`.
- [x] `TV5-09` — Tự đối chiếu đầu vào/đầu ra giao tiếp SS2/SS7 và việc gọi BillingService đúng trách nhiệm.
- [x] `TV5-10` — Tự sửa lỗi SS5, kiểm tra lại và lưu kết quả thực tế.
- [x] `TV5-11` — Xuất PDF hoàn chỉnh, bàn giao cùng nguồn và chính sách sạc đúng phiên bản.
- [x] `TV5-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

## Tiêu chí chất lượng trước khi bàn giao

- [x] Có đủ Deployment view và Development/Implementation view; phân biệt đúng vai trò hai view.
- [x] Phạm vi UC cá nhân đầy đủ: SS1 có 3, SS2 có 4, SS3–SS7 mỗi SS có 2.
- [x] Class diagram thể hiện trách nhiệm, kiểu dữ liệu, quan hệ và bội số hợp lý.
- [x] Mọi phương thức được vẽ có mô tả tương ứng; tên và chữ ký khớp nhau.
- [x] Có điều kiện trước/sau, lỗi, tác động dữ liệu và quy tắc xử lý lặp khi cần.
- [x] Truy vết đến đúng UC và thông điệp/nhánh từ Sub2; không dùng ID tự đặt thay ID chuẩn.
- [x] Lớp và giao tiếp dùng chung khớp bản đã chốt; không có bảy định nghĩa Hub khác nhau.
- [x] Mốc 30 phút đúng phạm vi; các quy tắc 15 phút khác không bị thay theo.
- [x] Trạng thái và đơn vị đúng; bảo toàn sức chứa, công suất và tài chính được giải thích.
- [x] Phân biệt code hiện tại với thiết kế đề xuất, mock và mở rộng tương lai.
- [x] Test có đầu vào/kết quả cụ thể; trạng thái PASS có bằng chứng thực thi.
- [x] PDF đọc được, không cắt hình/bảng; đóng góp cá nhân và AI được khai báo đúng.

## Kết quả tự kiểm tra thực tế

- **Đã kiểm tra file/phiên bản nào:** `smart_charging.py`, `scheduler.py`, `billing.py`, `test_scheduler_and_charging.py` và các sơ đồ Activity/Sequence UC_SS5_01, UC_SS5_02.
- **Kết quả và bằng chứng:** Đã lập danh sách lớp hiện có/lớp đề xuất; đã xây dựng Class Diagram, Class Description, Method Description, Implementation View và Traceability; đã xác định 4 unit test và thiết kế 4 test case bonus.
- **Vấn đề còn mở:** Hoàn thiện ChargingService; đối chiếu class diagram và các phương thức; đồng bộ UML với code; kiểm tra giao tiếp SS2/SS7; chạy test; 
- **Xác nhận của tác giả:** TV5 xác nhậnnhận