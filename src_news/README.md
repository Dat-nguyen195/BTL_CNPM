# 🚲 Smart E-Mobility Hub – ĐHQG-HCM

Hệ thống quản lý, đặt xe điện dùng chung, đặt lịch sạc xe điện cá nhân, giám sát mật độ trạm Hub và lập lịch sạc thông minh tại khu đô thị ĐHQG-HCM.

## 📁 Cấu trúc thư mục

```text
.
├── backend/          # REST API (Python FastAPI + Supabase)
├── frontend/         # Giao diện người dùng (React + TypeScript + Vite + Tailwind CSS)
└── README.md
```

## 🛠️ Yêu cầu hệ thống

* **Git**
* **Python** `3.10+`
* **Node.js** `18+` & **npm**
* Tài khoản **Supabase** (PostgreSQL)

---

## 🚀 Hướng dẫn tải về và chạy dự án

### 1. Clone mã nguồn

```bash
git clone https://github.com/Dat-nguyen195/BTL_CNPM.git
cd BTL_CNPM/src_news
```

---

### 2. Cài đặt & Chạy Backend (Port `8000`)

Mở **Terminal 1**, di chuyển vào thư mục `backend` và cài đặt môi trường:

```bash
cd backend

# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows (CMD/PowerShell)

# Cài đặt thư viện
pip install -r requirements.txt
```

Tạo file `.env` trong thư mục `backend/` (có thể copy từ `.env.example` nếu có) và điền thông tin kết nối Supabase của bạn:

```env
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_KEY=<your-service-role-secret-key>
JWT_SECRET=thay-doi-chuoi-bi-mat-cua-ban
```

> **Lưu ý Database:** Trên **Supabase → SQL Editor**, đảm bảo đã cấp quyền cho `service_role`:
> ```sql
> GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
> GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres, service_role;
> GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres, service_role;
> ```

Khởi động server Backend:

```bash
uvicorn app.main:app --reload --port 8000
```

* API chạy tại: `http://localhost:8000`
* Tài liệu API (Swagger UI): `http://localhost:8000/docs`

---

### 3. Cài đặt & Chạy Frontend (Port `5173`)

Mở **Terminal 2** (giữ nguyên Terminal 1 đang chạy Backend), di chuyển vào thư mục `frontend`:

```bash
cd frontend

# Cài đặt dependencies
npm install
```

*(Tùy chọn)* Nếu Backend không chạy ở `http://localhost:8000`, tạo file `frontend/.env` để cấu hình địa chỉ API:

```env
VITE_API_URL=http://localhost:8000
```

Khởi động server Frontend:

```bash
npm run dev
```

* Truy cập ứng dụng trên trình duyệt tại: **`http://localhost:5173`**

---

## 💡 Hướng dẫn sử dụng nhanh

1. **Tạo tài khoản**: Vào tab **Đăng ký tài khoản**, nhập MSSV, Họ tên, Email và Mật khẩu ($\ge 8$ ký tự). Tài khoản mới mặc định có vai trò `STUDENT` và nhận sẵn **`150,000₫`** trong ví.
2. **Đặt & Trả xe (SS1)**:
   * Chọn **Hub xuất phát** $\rightarrow$ chọn xe có pin $\ge 20\%$ $\rightarrow$ nhấn **Xác nhận đặt giữ xe** (tạm khóa cọc `50,000₫` và nhận mã PIN 4 số).
   * Nhập mã PIN để **Mở khóa & Nhận xe**.
   * Khi kết thúc, chọn Hub trả xe và thời gian đi để **Trả xe & Quyết toán** (miễn phí 30 phút đầu; sau 30 phút tính `500₫/phút`, hỗ trợ mã `SVBK50` giảm 50% và `VNU2026` giảm 30%).
3. **Xe điện cá nhân (SS2)**: Đăng ký biển số xe cá nhân và đặt khung giờ sạc tại các trạm Hub.
4. **Giám sát & Lập lịch sạc (SS3 & SS5)**: Theo dõi tình trạng lấp đầy từng trạm và danh sách ưu tiên sạc. *(Để dùng quyền điều phối viên `OPERATOR`, chỉnh cột `role` của user thành `OPERATOR` trực tiếp trong bảng `users` trên Supabase).*