# Kế hoạch chốt Submission 3 sau tích hợp - 06/11/2026

## Trạng thái dùng để lập kế hoạch

Đã tiếp nhận4 nhánh bàn giao; bổ sung7 bộ nguồn thiết kế/truy vết/test/AI,3 sơ đồ chung, danh mục mọi phương thức và bộ PDF revision. Đây là bản kỹ thuật để các chủ sở hữu đọc và hoàn thiện xác nhận. Hạn30/10 trong guidance đã qua; không tự thay bằng một hạn LMS mới. TV1 phải xác minh tình trạng nhận bài/định dạng với LMS hoặc thông báo giảng viên thực tế.

| Ưu tiên / thứ tự | Người phụ trách | Việc cần làm | Tiêu chí hoàn thành | Phụ thuộc |
| --- | --- | --- | --- | --- |
| P0 - ngay sau merge | TV1 | Xác minh LMS: còn nhận/sửa bài, giờ đóng, nộp cá nhân hay nhóm, giới hạn file | Ghi nguồn thông báo, ngày/giờ UTC+7 và quy cách thật; không chỉ dùng guidance cũ | Quyền truy cập LMS |
| P0 - đọc nguồn sửa | TV1, TV3, TV4 | Đọc/hiểu phần thiết kế được bổ sung thay khung, chỉnh theo hiểu biết cá nhân | Từng người xác nhận REPORT/catalog/trace/AI và biết giải thích quyết định thiết kế | Revision tích hợp |
| P0 - xác nhận bản mới | TV2, TV5, TV6, TV7 | Đọc review, đối chiếu bài cũ với bản đã sửa, chỉnh AI/đóng góp cá nhân | self_check revision mới có xác nhận thật; không giữ FINAL/SELF_CHECKED cũ làm bằng chứng | Revision tích hợp |
| P0 - đồng bộ kiến trúc | TV3 với TV1 điều phối | Xác nhận implementation/system class view và Hub chuẩn; TV7 xác nhận deployment; TV6 schema preview | Cùng một revision kiến trúc trong7 PDF, method/catalog đúng diagram | Chủ sở hữu đọc nguồn |
| P0 - QA PDF cuối | Mỗi tác giả tự kiểm; TV1 tập hợp | Mở đúng PDF của mình, kiểm tra font/ảnh/bảng/phụ lục, tên/MSSV | Không cắt/chồng chữ, ảnh đọc được, mọi method có mô tả; thay chữ CHỜ XÁC NHẬN khi đã xác nhận thật | Nội dung đã chốt |
| P0 - nộp và lưu | Người thực hiện theo LMS; TV1 theo dõi | Tải đúng bộ file, mở lại file đã tải, lưu xác nhận/biên nhận | Ghi commit/hash của bộ nộp và bằng chứng hệ thống nhận | LMS cho phép, tất cả P0 trước hoàn tất |
| P1 - trước demo/final | TV1/TV2/TV5 | Hiện thực BillingService/idempotency/reference ledger; ChargingService/bill; giải quyết hourly parking | Test tích hợp không thu hai lần, giữ cọc đúng owner/reference, chốt chính sách theo SRS | Thống nhất chính sách, không bắt buộc giả vờ đã xong trong Sub3 |
| P1 - trước demo/final | TV6/TV7/TV5 | Coordinator dùng chung, typed DTO, atomic Apply và port/session adapter | Stale/duplicate/rollback tests chạy trên service thật; preview không ghi đè ví/booking | API thiết kế đã chốt |
| P1 - trước demo/final | TV3/TV4/TV1 | Revenue/power snapshot, authorization/ownership ở core, incident binding và dispatch completion validation | Tests trên nguồn triển khai mới; invariant không bị phá; dashboard đúng mọi SS | Thiết kế và phần core mới |
| P2 - final | TV6/TV1 | Quyết định mô hình doanh thu US21 và nguồn km US06; kế hoạch hiệu năng/đa phiên | Có giả định/công thức/dữ liệu đo hoặc công khai chưa triển khai; không nhầm với code hiện có | Phạm vi final và dữ liệu |

## Cách đóng gói sau mọi thay đổi

1. Sửa nguồn Markdown/PlantUML, không sửa PDF riêng. Chủ sở hữu tự đối chiếu lớp/method/trace và cập nhật AI đúng phạm vi.
2. Kiểm tra PlantUML, render PNG/SVG cùng nguồn; chạy `python3 scripts/validate_submission_3.py`.
3. Nếu code thay đổi, chạy test liên quan rồi bộ test trước tích hợp. Nếu chỉ đổi câu chữ, không cần lặp toàn bộ test.
4. Build7 PDF bằng scripts/build_submission_3.py (dependencies trong scripts/requirements-submission3.txt), QA trực quan và `python3 scripts/validate_submission_3.py --pdfs`.
5. TV1 tập hợp PDF và SHA256SUMS ở output/submission_3; tuân theo quy cách LMS đã xác minh. ZIP/source không thay định dạng doc/docx/pdf bắt buộc.

Không lên lịch/hạn mới như thông báo giảng viên khi chưa có căn cứ. Thứ tự P0 là đường hoàn thiện Sub3; P1/P2 là công việc triển khai/demo/final, không là lý do tự ghi các service đề xuất đã chạy.
