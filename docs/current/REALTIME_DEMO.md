# Chạy và kiểm chứng bản demo hiện tại

Từ thư mục gốc repo, cài Python 3.12 và dependencies.

~~~bash
python3 -m venv venv
venv/bin/pip install -r requirements-tested.txt -r requirements-dev.txt
EMOBILITY_IOT_ENABLED=1 venv/bin/python -m streamlit run src/app.py
~~~

Ở terminal thứ hai, chạy bộ phát. Dừng bằng Ctrl+C.

~~~bash
venv/bin/python scripts/iot_producer.py --hub HUB-001 --port 1 --interval 5
~~~

Mở SS3 trong hai cửa sổ. Bảng sự kiện ở cuối trang hiện event_id, occurred_at, received_at, displayed_at và kết quả APPLIED/STALE/REJECTED. Bộ phát luân phiên OFFLINE/ONLINE. Mỗi hai giây giao diện đọc feed SQLite. Hai phiên quan sát cùng các bản tin. Bản tin được lưu tại tmp/telemetry.sqlite3, có thể cấu hình đường dẫn tuyệt đối bằng EMOBILITY_IOT_DB cho cả hai tiến trình. Restart bộ phát tạo ID mới. Restart ứng dụng đọc lại feed. Reset phiên nạp seed rồi tái phát các sự kiện.

Nghiệp vụ booking, ví và phiên sạc vẫn thuộc từng phiên demo. Feed chia sẻ sự kiện ngoại vi, mỗi phiên áp dụng cùng thay đổi trên trạng thái local của nó. Vì thế hai phiên có thể khác số xe/cổng đang dùng nếu người dùng thực hiện nghiệp vụ khác nhau. Đây là giới hạn của prototype; chưa có transaction nghiệp vụ dùng chung đa người dùng.

Các hub seed cũ chỉ lưu tổng số cổng. Adapter dùng chỉ số cổng 1..total cho bản tin, và giữ số offline tổng hợp; khi cổng chuyển offline, phiên đang chiếm tài nguyên tại hub bị ngắt theo thứ tự tạo. Ánh xạ cảm biến đến đúng ổ cắm vật lý cần model cổng đầy đủ trong phiên bản tiếp theo. Năng lượng và phí quá hạn đã phát sinh được giữ trong reservation, khi check-out chỉ thu một lần.

Biểu phí đỗ mặc định là **giả định demo 5.000đ cho mỗi giờ bắt đầu**. Nhóm chưa cung cấp đơn giá chính thức. Thay EMOBILITY_PARKING_HOURLY_VND khi chốt. Điện năng lấy từ phiên sạc mô phỏng, pin giả định 3,5 kWh. Phí điện tích lũy theo từng phút mô phỏng và khung giá trong bước tick. Quãng đường hóa đơn thuê xe giả lập theo thời lượng × 15 km/h. Dự báo doanh thu dùng giả định công suất phục vụ 8 lượt/giờ và giá nhập trên SS6, tách khỏi khoản thu trên SS3.

Để kiểm tra What-if, tạo preview SS7 rồi chờ một sự kiện mới. Khi Apply, preview cũ bị từ chối. Tạo preview mới để tiếp tục. Với UI mô phỏng sạc SS5, bước tick có thể làm xe đầy; rút sạc bảo toàn phí quá hạn cho hóa đơn SS2.

## Chạy bằng container hoặc server

~~~bash
docker compose up --build -d
docker compose logs --tail=30 app producer
docker compose down
~~~

Volume telemetry giữ feed qua restart. Cần cài Docker và cấp quyền truy cập Docker cho tài khoản thực thi. Khi có server đích, dùng cùng repo/cấu hình, mở cổng 8501 theo cấu hình server và kiểm tra từ máy khác. Mục tiêu điểm cộng server còn chờ đích triển khai và xác minh truy cập ngoài máy.

## Kiểm tra

~~~bash
PYTHONPATH=src venv/bin/python -m pytest -q tests/
JAVA_TOOL_OPTIONS=-Djava.awt.headless=true venv/bin/python scripts/validate_submission_2.py
venv/bin/python scripts/validate_submission_3.py --technical-only
~~~
