# Smart E-Mobility Hub — Phiên bản 2

Bản web đã đóng gói, dùng React, FastAPI và PostgreSQL. Người dùng thông thường
(`STUDENT`) tự đăng ký để đặt xe dùng chung và đăng ký, giữ chỗ cho xe cá nhân.
Điều phối viên (`OPERATOR`) đăng nhập bằng tài khoản đã được người quản trị
cấp quyền để điều phối xe, xử lý sự cố, cấp cổng sạc và chạy mô phỏng.
FastAPI đọc vai trò từ cơ sở dữ liệu và kiểm tra quyền cho các thao tác vận hành.

## Chạy bản đóng gói trên máy

Cài Docker với Docker Compose v2. Ở repo, mở terminal trong `src_news/`.
Nếu giải nén ZIP nộp bài, mở terminal trong `source/phien_ban_2/`.
Tạo tệp `.env` trong thư mục này. Lệnh sau in hai chuỗi ngẫu nhiên gồm 64 ký tự hex:

```sh
docker run --rm python:3.12-slim python -c "import secrets; print(secrets.token_hex(32)); print(secrets.token_hex(32))"
```

Sao chép `.env.example` thành `.env`, điền một chuỗi vào `JWT_SECRET_KEY` và
chuỗi còn lại vào `POSTGRES_PASSWORD`. Giữ các giá trị này trên những lần chạy lại
và giữ tệp `.env` trên máy.

```sh
docker compose up --build -d
docker compose ps
```

Mở <http://localhost:8080>. Kiểm tra API ở <http://localhost:8080/health>
(kết quả `{"status":"ok"}`). Đăng nhập và mở màn hình Hub để kiểm tra dữ liệu.
Lần đầu cần Internet để tải image và thư viện. PostgreSQL khởi tạo trạm, xe mẫu
khi volume còn trống. Dữ liệu giữ qua `docker compose down`.

### Thử hai vai trò

1. Tạo một tài khoản sinh viên ở trang đăng ký. Xác nhận có thể xem Hub, đặt xe
   còn pin hoặc đăng ký xe cá nhân và giữ chỗ. Các chức năng điều phối bị khóa.
2. Tạo tài khoản thứ hai, dùng email và mã số khác. Ví dụ email
   `operator@example.com`. Người chạy demo cấp vai trò qua PostgreSQL từ chính
   thư mục Compose. Thay email trong câu lệnh nếu đã đăng ký email khác.

   ```sh
   docker compose exec db psql -U emobility -d emobility -c "UPDATE public.users SET role = 'OPERATOR' WHERE email = 'operator@example.com';"
   ```

   Kiểm tra lệnh trả `UPDATE 1`, rồi đăng xuất và đăng nhập lại bằng tài khoản
   này. Mở điều phối trạm hoặc cấp cổng sạc và xác nhận thao tác được bật.
3. Dừng hai dịch vụ ứng dụng và các dịch vụ dữ liệu bằng `docker compose down`.

Các phiên đặt chỗ và ví ở bản web dùng PostgreSQL riêng. Thiết bị, điện năng
nhập ở luồng check-out và giao dịch thanh toán dùng dữ liệu mô phỏng. Phần
What-if của bản web hiển thị kết quả ước tính. Luồng IoT qua SQLite và kiểm
tra phiên bản preview khi Apply nằm ở bản Streamlit (phiên bản 1).

## Tùy chọn chạy từ mã nguồn với Supabase

Trong một dự án Supabase dành cho demo, chạy lần lượt `db/01-schema.sql` và
`db/02-seed.sql` qua SQL Editor trên cơ sở dữ liệu chưa có các bảng ứng dụng.
Tập lệnh `db/03-local-postgrest.sql` chỉ dành cho Docker Compose.
Nếu đã dùng một schema thử nghiệm cũ, dùng database demo riêng để tránh xung
đột tên bảng. Dùng SQL Editor để cấp vai trò `OPERATOR` như ví dụ trên.

1. Trong `backend/`, dùng Python 3.12 để tạo và kích hoạt môi trường ảo.
   Chạy `python -m pip install -r requirements.txt`, sao chép
   `backend/.env.example` thành `backend/.env`, điền URL, khóa service role và
   một khóa JWT ngẫu nhiên. Khóa service role chỉ dùng ở backend.
   Chạy `python -m uvicorn app.main:app --port 8000`.
2. Trong terminal thứ hai ở `frontend/`, dùng Node.js 22 và chạy
   `npm ci`, rồi `npm run dev`. Mở <http://localhost:5173>.
   Dùng `npm run build` để kiểm tra bản dựng frontend.
