# 🚲 Smart E-Mobility Hub

## Hệ thống Điều phối Phương tiện Điện trong Khu đô thị ĐHQG-HCM

> **Môn học:** Công nghệ Phần mềm (Software Engineering) – HK1/2026-2027  
> **Trường:** Đại học Bách Khoa – ĐHQG TP.HCM (HCMUT – VNU-HCM)  
> **Loại dự án:** Evolutionary Prototype (Agile/Scrum)

---

## 📋 Mô tả Dự án

**Smart E-Mobility Hub** là hệ thống quản lý và điều phối phương tiện điện (EV) thông minh tại Khu đô thị Đại học Quốc gia TP.HCM. Hệ thống giúp:

- 🎓 **Sinh viên** dễ dàng tìm và đặt xe điện / chỗ đỗ xe tại các Hub
- 🔌 **Quản lý sạc thông minh** dựa trên ưu tiên pin & booking
- 📊 **Giám sát** tình trạng toàn bộ mạng lưới Hub theo thời gian thực
- 🚨 **Xử lý sự cố** và điều phối phương tiện giữa các Hub
- 📈 **Mô phỏng What-if** để dự đoán nhu cầu và kiểm tra khả năng chịu tải

---

## 👥 Thành viên Nhóm & Phân công

| STT | Họ và Tên | MSSV | Email | Vai trò | Subsystem |
|:---:|-----------|:----:|-------|---------|-----------|
| 1 | Nguyễn Thành Đạt | 2410709 | dat.nguyen19052006@hcmut.edu.vn | **Project Manager** | SS1: Quản lý & Đặt xe cho SV |
| 2 | Nguyễn Anh Tài | 2413035 | tai.nguyenanh1906@hcmut.edu.vn | Developer | SS2: Đăng ký dịch vụ Xe cá nhân |
| 3 | Phạm Tiến Đạt | 2410724 | dat.phamkhmtk24@hcmut.edu.vn | Developer | SS3: Giám sát mạng lưới Hub |
| 4 | Đặng Hoàng Quý Nhân | 2412401 | nhan.dangcs06@hcmut.edu.vn | Developer | SS4: Điều phối & Xử lý sự cố |
| 5 | Dương Đăng Khoa | 2411589 | khoa.duong272dk@hcmut.edu.vn | Developer | SS5: Lập lịch sạc thông minh |
| 6 | Hoàng Văn Tấn | 2213074 | tan.hoang0815@hcmut.edu.vn | Developer | SS6: Mô phỏng nhu cầu SV |
| 7 | Nguyễn Trung Nguyên | 2011710 | nguyen.nguyen1111@hcmut.edu.vn | Developer | SS7: Mô phỏng sự cố hạ tầng |

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Ngôn ngữ | Python 3.10+ |
| Framework UI | Streamlit |
| Xử lý dữ liệu | Pandas |
| Trực quan hoá | Plotly, Matplotlib |
| Dữ liệu | In-memory JSON (st.session_state) |
| Quản lý mã nguồn | Git + GitHub |

---

## 📁 Cấu trúc Thư mục

```
smart-emobility-hub/
├── .github/
│   └── pull_request_template.md
├── docs/
│   ├── meeting-minutes/
│   │   ├── Meeting_01_20260908.md
│   │   └── README.md
│   ├── tasks-assignment.md
│   └── README.md
├── src/
│   ├── app.py                     # Entry point chính
│   ├── components/
│   │   ├── student_booking.py     # SS1: Đặt xe & chỗ đỗ
│   │   ├── personal_ev.py         # SS2: Xe cá nhân
│   │   ├── hub_monitor.py         # SS3: Dashboard giám sát
│   │   ├── dispatch_incident.py   # SS4: Điều phối & sự cố
│   │   ├── smart_charging.py      # SS5: Sạc thông minh
│   │   ├── sim_demand.py          # SS6: Mô phỏng nhu cầu
│   │   └── sim_infrastructure.py  # SS7: Mô phỏng hạ tầng
│   ├── core/
│   │   ├── scheduler.py           # Logic hàng đợi sạc
│   │   └── simulator.py           # Logic mô phỏng sự kiện
│   └── data/
│       └── mock_hubs.json         # Dữ liệu mock 6 Hub
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔧 Quy trình Phát triển

**Software Process Model:** Incremental Development (Agile/Scrum)

- **Sprint Duration:** 2 tuần
- **Ceremonies:** Sprint Planning, Daily Standup, Sprint Review, Retrospective
- **Branching Strategy:** Feature Branch → Pull Request → Code Review → Merge to `main`
- **Naming Convention:** `feature/<mssv>-<tên-tính-năng>` (ví dụ: `feature/2211234-booking-ui`)

---

## 🚀 Cài đặt & Chạy ứng dụng

### Yêu cầu
- Python 3.10 trở lên
- pip (Python package manager)

### Cài đặt

```bash
# Clone repository
git clone https://github.com/Dat-nguyen195/BTL_1_CNPM.git
cd smart-emobility-hub

# Tạo virtual environment (khuyến nghị)
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### Chạy ứng dụng

```bash
streamlit run src/app.py
```

Ứng dụng sẽ mở tại: `http://localhost:8501`

---

## 🤖 Tuyên bố Minh bạch về Sử dụng AI Tạo sinh (Generative AI Transparency Statement)

> **Bắt buộc theo quy định học thuật.**

### Mục đích sử dụng AI
Nhóm phát triển đã sử dụng công cụ AI tạo sinh (Generative AI – cụ thể: AI Coding Assistant) cho các mục đích sau:

1. **Scaffolding & Boilerplate:** AI được sử dụng để khởi tạo cấu trúc thư mục, tạo mã boilerplate ban đầu cho 7 subsystem, và thiết lập mock data. Điều này giúp tiết kiệm thời gian thiết lập ban đầu để nhóm tập trung vào logic nghiệp vụ.

2. **Code Generation:** AI hỗ trợ tạo giao diện Streamlit cơ bản, thuật toán lập lịch sạc, và logic mô phỏng sự kiện.

3. **Documentation:** AI hỗ trợ soạn thảo README, PR template, và inline comments.

### Xác minh của Con người (Human Verification)
- ✅ Toàn bộ mã nguồn do AI tạo ra đã được **mỗi thành viên nhóm đọc hiểu, kiểm tra**, và chỉnh sửa cho phù hợp với yêu cầu nghiệp vụ thực tế.
- ✅ Logic nghiệp vụ (thuật toán ưu tiên sạc, kịch bản mô phỏng) được **nhóm thiết kế** dựa trên phân tích yêu cầu, AI chỉ hỗ trợ hiện thực hoá.
- ✅ Mock data (toạ độ Hub, thông số xe) được **nhóm xác minh** dựa trên bản đồ thực tế ĐHQG-HCM.
- ✅ Giao diện người dùng được **nhóm tuỳ chỉnh** về UX/UI sau khi AI tạo khung cơ bản.

### Cam kết
> Nhóm cam kết rằng việc sử dụng AI là công cụ hỗ trợ, không thay thế quá trình học tập và tư duy thiết kế phần mềm. Mọi quyết định thiết kế, kiến trúc, và logic nghiệp vụ đều do nhóm chủ động đưa ra.

---

## 📝 Giấy phép

Dự án phục vụ mục đích học tập tại HCMUT – ĐHQG-HCM.  
© 2026 – Nhóm Sinh viên Công nghệ Phần mềm, Trường Đại học Bách Khoa TP.HCM.

## Bản nộp Submission #2 (21/10/2026)

- Báo cáo: `docs/report/submission_2/REPORT_SUBMISSION_2.pdf`.
- Truy vết đúng baseline SRS: `docs/traceability/submission_2.md`.
- Bằng chứng thực thi: `docs/audit/submission_2/final/`.
- Hướng dẫn demo và giới hạn: `SUBMISSION_2_HANDOFF.md`.

Môi trường đã kiểm thử dùng Python 3.12; các phiên bản thư viện được ghi trong `requirements-tested.txt`. Cài môi trường tái lập và kiểm thử:

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements-tested.txt -r requirements-dev.txt
PYTHONPATH=src venv/bin/python -m pytest -q tests
venv/bin/python -m streamlit run src/app.py
```

Dựng tài liệu từ thư mục gốc (cần Java, `tools/plantuml.jar`, XeLaTeX và latexmk):

```bash
venv/bin/python scripts/generate_traceability_json.py
venv/bin/python scripts/generate_traceability_md.py
venv/bin/python scripts/render_all_diagrams.py
venv/bin/python scripts/generate_sequence_panels.py
venv/bin/python scripts/generate_activity_panels.py
cd docs/report/submission_2
latexmk -xelatex -interaction=nonstopmode -halt-on-error REPORT_SUBMISSION_2.tex
```

Các test xác thực luồng prototype với dữ liệu trong phiên. SSO, IoT, barie và cổng thanh toán thật được mô phỏng; ba tiêu chí PARTIAL được công khai trong ma trận và báo cáo.

Chính sách giữ chỗ cập nhật ngày 21/10/2026: SS1 có hạn 30 phút kể từ khi đặt; SS2 có hạn Check-in 30 phút kể từ giờ đến đã chọn. Tại đúng deadline, lượt chưa nhận/Check-in hết hiệu lực. Cọc vẫn 50.000đ, phí no-show 10.000đ, hoàn 40.000đ. Ân hạn rút sạc và ưu đãi điều hướng vẫn 15 phút. Các booking đã lưu deadline trước đó giữ thông tin của thời điểm tạo; dùng phiên demo mới/Reset để kiểm tra chính sách mới.
