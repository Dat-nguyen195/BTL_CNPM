# 📐 Danh mục Sơ đồ Thiết kế (Diagrams Hub)

## Smart E-Mobility Hub (ĐHQG-HCM)

Thư mục này quản lý toàn bộ các sơ đồ thiết kế hệ thống và sơ đồ phân tích nghiệp vụ của 7 phân hệ.

---

## 1. Cấu trúc Thư mục

```
docs/diagrams/
├── system/
│   ├── generate_system_usecase.py      # Script sinh sơ đồ tổng thể tự động
│   ├── parse_drawio.py                 # Script phân tích cấu trúc Draw.io
│   ├── smartEhub.drawio                # File thiết kế Draw.io gốc (17 Canonical UCs)
│   ├── smartEhub.svg                   # Vector SVG phân giải cao
│   ├── smartEhub.png                   # Render PNG dùng cho tài liệu
│   └── smartEhub.pdf                   # Bản xuất PDF khổ lớn
└── Use-case detail-scenario/
    ├── SS1/  # Nguyễn Thành Đạt (3 UCs)
    │   ├── Activity diagrams/
    │   ├── Sequence diagrams/
    │   ├── State-chart diagrams/
    │   └── Usecase scenario/
    ├── SS2/  # Nguyễn Anh Tài (4 UCs)
    │   ├── Activity diagrams/
    │   ├── Sequence diagrams/
    │   ├── State-chart diagrams/
    │   └── Usecase scenario/
    ├── SS3/  # Phạm Tiến Đạt (2 UCs)
    │   ├── Activity diagrams/
    │   ├── Sequence diagrams/
    │   ├── State-chart diagrams/
    │   └── Usecase scenario/
    ├── SS4/  # Đặng Hoàng Quý Nhân (2 UCs)
    │   ├── Activity diagrams/
    │   ├── Sequence diagrams/
    │   ├── State-chart diagrams/
    │   └── Usecase scenario/
    ├── SS5/  # Dương Đăng Khoa (2 UCs)
    │   ├── Activity diagrams/
    │   ├── Sequence diagrams/
    │   ├── State-chart diagrams/
    │   └── Usecase scenario/
    ├── SS6/  # Hoàng Văn Tấn (2 UCs)
    │   ├── Activity diagrams/
    │   ├── Sequence diagrams/
    │   ├── State-chart diagrams/
    │   └── Usecase scenario/
    └── SS7/  # Nguyễn Trung Nguyên (2 UCs)
        ├── Activity diagrams/
        ├── Sequence diagrams/
        ├── State-chart diagrams/
        └── Usecase scenario/
```

---

## 2. Quy chuẩn Kỹ thuật
- **Định dạng nguồn:** PlantUML (`.puml`) mã hóa UTF-8.
- **Biên dịch hình ảnh:** PNG và SVG tương ứng được render tự động qua `plantuml.jar` với layout engine Smetana.
- **Chuẩn giao tiếp:**
  - Các sơ đồ activity, sequence và state-chart của Submission 2 dùng `!include ../../../common.puml`; không ghi đè màu ký hiệu bằng cấu hình riêng.
  - Sequence diagrams: phân chia lifeline theo trách nhiệm; mũi tên liền cho lời gọi, mũi tên nét đứt cho phản hồi, `alt` cho các nhánh lựa chọn.
  - Activity diagrams: nút đầu là chấm đặc; nút cuối là vòng tròn kép; hành động là hình chữ nhật bo góc; decision/merge là hình thoi; fork/join là thanh đậm. Điều kiện nhánh ghi trong `[ ]`; vòng lặp dùng `while` hoặc `repeat` với điều kiện rõ ràng.
  - Swimlane biểu diễn bên chịu trách nhiệm, không bắt buộc đủ 5 làn khi nghiệp vụ không sử dụng. SS1 dùng các tên ngắn: Sinh viên, Giao diện SS1, Trạng thái phiên, Ví điện tử, IoT (mô phỏng).
  - State-chart diagrams: Chuẩn hóa định danh trạng thái `UPPER_CASE`.
  - Phân biệt trạng thái **xe** (`AVAILABLE`, `RESERVED`, `IN_USE`, `CHARGING`, `OFFLINE`) và **booking** (`RESERVED`, `IN_USE`, `COMPLETED`, `CANCELLED`, `EXPIRED`). `PARKED` và `MAINTENANCE_OFFLINE` là tên cũ, không dùng thay trạng thái xe hiện tại.

Các ảnh `.png` được dựng lại từ nguồn trước khi biên dịch báo cáo. Sơ đồ SS1_02 đầy đủ nằm cạnh nguồn; bản trong báo cáo được chia thành hai phần tiếp nối bằng connector `A` để giữ khả năng đọc.

## Sơ đồ Submission 3

Xem [cây sơ đồ Sub3](submission_3/README.md): ba nguồn dùng chung và class diagram SS1–SS7. Các nguồn khởi tạo có nhãn DRAFT; hoàn thiện rồi xuất PNG/SVG cạnh nguồn. Cây use case cũ được giữ nguyên.
