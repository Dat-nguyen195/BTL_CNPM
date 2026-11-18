# Bổ sung thiết kế chung S1–S3 cho runtime hiện tại

Nguồn dùng để đối chiếu mã hiện hành cùng với SRS và baseline 17 UC. Những catalog OOP cũ vẫn mô tả thiết kế mục tiêu. Các module dưới đây ánh xạ trực tiếp đến Python đang chạy.

## S1 — yêu cầu dữ liệu giả lập

Actor ngoại vi là Bộ mô phỏng cảm biến. Hệ thống nhận trạng thái cổng theo hub và chỉ số, xử lý sự kiện trùng/cũ, cập nhật năng lực cấp sạc và cảnh báo. Nhân viên quan sát mã sự kiện/thời điểm/trạng thái trên SS3. Đặc tả chức năng có trong [usecase](../diagrams/telemetry/usecase.puml). Bảng chung S1 đã đồng bộ mã SS2 với baseline.

## S2 — tương tác và lỗi

[Sequence xử lý sự kiện](../diagrams/telemetry/flow.puml) mô tả publish → feed → kiểm tra → snapshot → dashboard. Bộ phát độc lập thao tác UI. Một ID được ghi một lần. Khi cùng cổng có bản tin cũ hơn hoặc bằng timestamp đã nhận, giữ nguyên trạng thái; lưu STALE. Sai hub/cổng lưu REJECTED. Sai schema/múi giờ bị từ chối trước ghi feed. Nếu feed tạm dừng, UI giữ trạng thái cuối. Restart UI đọc lại feed từ đầu trên seed.

## S3 — lớp/module, triển khai và mô tả phương thức

[Class diagram](../diagrams/telemetry/classes.puml) và [deployment](../diagrams/telemetry/deployment.puml) dùng chung cho bản demo. File state và SQLite feed giữ vai trò khác nhau, chi tiết tại [hướng dẫn demo](REALTIME_DEMO.md).

| Phương thức | Điều kiện, đầu ra và tác động |
|---|---|
| feed_path() | Đọc EMOBILITY_IOT_DB, mặc định tmp/telemetry.sqlite3. Trả Path. Không thay state. |
| connect_feed(path) | Tạo thư mục và bảng events nếu thiếu. Trả SQLite connection; lỗi filesystem/SQLite được truyền cho caller. Dùng timeout 10 giây và transaction trong publish. |
| publish_event(event, path) | Kiểm tra trường, type ONLINE/OFFLINE và thời gian có timezone. Thiếu/sai sinh ValueError. INSERT OR IGNORE bởi UNIQUE event_id, thêm received_at. True nếu ghi mới, False nếu lặp. |
| consume_events(state, path) | Đọc sau cursor của session theo seq. Kiểm hub/chỉ số và thời gian từng cổng. Gọi apply_hub_snapshot khi hợp lệ, ghi before/after/displayed_at. Cập nhật cursor cả khi loại sự kiện. Trả số APPLIED. Feed được replay trên session mới. |
| apply_hub_snapshot(state, hubs) | Hubs là snapshot đã qua kiểm tra. Ngắt các phiên bị ảnh hưởng bởi tăng offline, lưu năng lượng/phí và đưa xe về chờ; commit hubs và tăng version. Caller kiểm tra baseline_version trước Apply preview. |
| release_charging_session(state, session_id) | Pop phiên đúng một lần. Phiên không tồn tại trả None. Tích lũy kWh, phí điện, overstay vào reservation, xóa binding cổng và hoàn chỗ cổng theo giới hạn offline. Trả phiên đã kết thúc. |
| allocate_hub_ports(state, hub_id) | Kiểm hub và scheduler. Cấp theo hàng chờ/trần kW và số cổng rảnh; cập nhật xe, reservation/session_id và version. Trả allocations hoặc list rỗng. |

## Quy tắc tài chính và phạm vi

SS2 thu điện từ phiên mô phỏng đã ghi nhận; điện và overstay được giữ sau rút cổng hoặc ngắt phiên. Checkout lặp bị từ chối. Overstay tính sau 15 phút ân hạn, mỗi khối bắt đầu 15 phút là 10.000đ. Phí điện tích lũy theo phút và khung giá trong tick. Bộ pin sạc giả định 3,5 kWh, nên năng lượng dừng ở mức pin đầy. Giá đỗ 5.000đ/giờ bắt đầu là giả định cấu hình được, chờ nhóm xác nhận.

US-06 có quãng đường mô phỏng 15 km/h × thời lượng. US-12 có nút xác nhận đối soát hóa đơn đã thanh toán SS2; xác nhận là hành động kiểm tra, không trừ tiền lần nữa. US-21 có forecast 24 giờ và doanh thu dự kiến theo đơn giá giả định. SS3 cộng các khoản thu thực SS1, SS2, SS5; công suất cộng các phiên CHARGING.

## Giới hạn đã xác định

Booking/ví/scheduler còn theo session; chưa có transaction vận hành đa người dùng. Seed cũ chỉ đếm cổng tổng hợp nên sự cố ngắt phiên theo thứ tự tạo, chưa mô phỏng vị trí ổ cắm chính xác. Bản tin cùng cổng replay đúng timestamp nhưng thao tác override thủ công có thể thay đổi tổng số offline độc lập; khi demo dùng một nguồn điều khiển cổng tại một thời điểm. Container/server cần kiểm chứng trên môi trường có Docker và quyền mạng. NFR tải lớn/availability chưa có benchmark.
