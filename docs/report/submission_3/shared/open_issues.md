# Vấn đề còn mở - revision tích hợp 06/11/2026

Danh sách này ghi bằng chứng đối chiếu, không tự gắn trạng thái DONE cho công việc chưa làm. Các blocker về thiếu tài liệu đã xử lý trong review; dưới đây phân biệt việc chốt nộp và chênh lệch triển khai.

| ID | Mức / phạm vi | Vấn đề và bằng chứng | Chủ sở hữu | Trạng thái / tiêu chí xử lý |
| --- | --- | --- | --- | --- |
| O01 | Blocker nộp | Không có thông báo LMS/biên nhận, guidance chỉ ghi30/10 | TV1 | OPEN; xác minh còn nhận bài và lưu quy cách/biên nhận thật |
| O02 | Major xác nhận | Sau sửa/bổ sung nội dung, chưa có7 xác nhận tác giả | Mỗi TV; TV1 theo dõi | OPEN; đọc/hiểu nguồn sửa và PDF, khai báo AI/đóng góp đúng |
| O03 | Major code | BillingService/reference/operation_key/charge_id là thiết kế; core billing giữ tổng cọc và có nhiều hàm trừ ví | TV1/TV2/TV5 | DOCUMENTED_GAP; triển khai ledger/dedup và test tích hợp trước demo/final |
| O04 | Major SRS | US09 phí đỗ theo giờ nhưng personal_ev checkout tính5.000/lượt; phí điện dùng tariff tại checkout thay tích phân theo từng tick | TV2/TV5 | DOCUMENTED_GAP; cần chốt chiến lược, giữ khác biệt công khai trong Sub3 |
| O05 | Major code | SS2 chưa gọi ChargingService, có thể gán CHARGING trước có cổng; SS7 simulator chỉ đếm cổng, chưa đồng bộ scheduler | TV2/TV5/TV7 | DOCUMENTED_GAP; service+port/session adapter và integration tests |
| O06 | Major code | Apply riêng ở hai UI có version check nhưng chưa coordinator nguyên tử/invariant chung; SimulationPreview typed DTO chưa có | TV6/TV7 | DOCUMENTED_GAP; implement INT10/rollback/idempotency, giữ preview/booking/wallet không ghi đè |
| O07 | Major SRS | Dashboard doanh thu chỉ cộng một số giao dịch SS1; estimate power=(total-available)*7.4 gồm cả offline, scheduler mặc định11 | TV3/TV5 | DOCUMENTED_GAP; đọc active sessions và ledger khoản thu toàn hệ thống |
| O08 | Major code | Core create_shared_booking chưa kiểm ownership PERSONAL, authority tại UI/mock; reroute tới Hub khác có thể cộng ưu đãi nhiều lần | TV1 | DOCUMENTED_GAP; kiểm tra ownership/quyền/version tại core và marker bonus một lần |
| O09 | Major code | SS4 complete chưa kiểm tra lại đầy đủ capacity/hold, resolve xe gán AVAILABLE không xét binding | TV4 | DOCUMENTED_GAP; service validate/stage/atomic, previous_status/binding tests |
| O10 | Major SRS | Priority score chưa có giá điện/thời gian chờ tăng điểm; US12 xác nhận nhân viên chưa trọn luồng | TV5 | DOCUMENTED_GAP; chốt thuật toán và UI confirm, không nhận current score đáp ứng mọi tiêu chí |
| O11 | Minor prototype | Forecast core/UI mặc định12, chọn24 mới đúng horizon yêu cầu | TV6 | DOCUMENTED_GAP; thiết kế ForecastService dùng24 tường minh; cân nhắc đổi default trước demo |
| O12 | Major SRS | US21 chưa dự báo biến động doanh thu; US06 thiếu số đo km | TV6/TV1 | DOCUMENTED_GAP; cần nguồn đo/mô hình rõ, không tự dựng dữ liệu |
| O13 | Major deployment | Per-session memory, mock auth, không lưu bền/chia sẻ đa phiên; chưa benchmark NFR | TV1 điều phối | DOCUMENTED_GAP; thiết kế tương lai transaction/storage/auth và benchmark; database không bắt buộc Sub3 |

Danh mục mục tiêu/designed không có nghĩa đã triển khai hoặc đã test PASS. Nguồn review và kế hoạch ở thư mục report/review; cập nhật chủ sở hữu/kết quả khi có bằng chứng mới.
