# NHẬT KÝ SỬA ĐỔI BÁO CÁO BTL SUBMISSION #2 (CHANGELOG_FIX.md)

**Dự án:** Smart E-Mobility Hub – Hệ thống Trạm xe điện Đa phương thức Thông minh ĐHQG-HCM  
**Nhóm thực hiện:** BEE BRAVE  
**Ngày hoàn thành:** 20/10/2026  
**Tài liệu áp dụng:** `docs/report/submission_2/REPORT_SUBMISSION_2.tex` và hệ thống sơ đồ UML (`docs/diagrams/`)

---

## 1. Tổng quan Đợt Sửa đổi

Đợt cập nhật này thực hiện toàn diện theo Kế hoạch Tối ưu và Đồng bộ Báo cáo Submission #2 (`PLAN_FIX_SUBMISSION_2.md`), nhằm xử lý triệt để:
1. Mâu thuẫn nghiệp vụ và số liệu giữa các phân hệ (Chính sách cọc D1, công thức sạc D2, trạng thái D3, ngưỡng cảnh báo D6).
2. Sự sai lệch giữa sơ đồ UML và bảng mô tả đặc tả (Lifelines, Messages, Alternate branches).
3. Độ phóng đại và khả năng đọc của các sơ đồ lớn (xoay khổ ngang `landscape`, phóng to sơ đồ hoạt động).
4. Tính trung thực học thuật giữa năng lực Prototype thực tế (`src/app.py`) và thiết kế mục tiêu mở rộng.
5. Ngôn ngữ, font chữ, dấu tiếng Việt và chuẩn hóa danh xưng tác nhân (`Operator` vs `Admin`).

---

## 2. Bảng Danh mục Chi tiết Sửa đổi (Theo từng Hạng mục)

| STT | Vị trí (Mục / Hình / Bảng) | Nội dung Trước khi sửa | Nội dung Sau khi sửa | Lý do sửa đổi & Ghi chú |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Mục 2.1.3 & Hình 2.3** | Mô tả mâu thuẫn: hoàn cọc 100% trong mọi trường hợp nhưng hình lại phạt mất 50k sau 30p | **Quyết định D1 thống nhất:** Hủy chủ động trong 30p: hoàn 100% (50.000 VNĐ). Quá hạn 30p (No-show): phạt 10.000 VNĐ phí giữ chỗ, hoàn lại 40.000 VNĐ vào ví | Đồng bộ với logic xử lý trong `src/components/student_booking.py` và chính sách công bằng dịch vụ |
| **2** | **Bảng 3.1 & Bảng 4.1 (D1)** | Ghi "hoàn cọc 100% nếu trễ" hoặc "phạt toàn bộ cọc" | Cập nhật chính sách phạt No-show: trừ 10.000 VNĐ phí giữ chỗ, hoàn 40.000 VNĐ | Đồng bộ toàn diện D1 trong bảng ma trận hoạt động và bảng trạng thái phương tiện |
| **3** | **Sơ đồ PUML SS1 (Seq 03, Act 03)** | Nhánh timeout phạt mất 50.000 VNĐ cọc | Cập nhật nhánh timeout: Trừ 10k phí giữ chỗ, hoàn 40k về ví sinh viên | Khớp chuẩn xác với bảng mô tả và mã nguồn |
| **4** | **Mục 1.5.3 (Phương trình 1.1)** | Công thức tính điểm sạc giả định dạng tổng trọng số $w_1 \text{SoC} + w_2 \text{Wait} + \dots$ không khớp code | Công thức chuẩn từ `src/core/scheduler.py`: $\text{Score} = (100 - \text{SoC}) \times 0.5 + 100 \times \mathbb{I}(\text{SoC} < 20\%) + 60 \times \mathbb{I}(\text{HasBooking}) + 30 \times \mathbb{I}(\text{SoC} < 50\%)$ | Đồng bộ toán học với code triển khai; có tính toán ví dụ cụ thể cho `EV-B009` (177.5) và `EV-A008` (65.0) |
| **5** | **Hình 4.1 & Bảng 4.1** | Thiếu đồng bộ trạng thái xe; bảng dùng `MAINTENANCE_OFFLINE`, hình dùng `INCIDENT` | Thống nhất bộ 7 trạng thái: `AVAILABLE`, `RESERVED`, `IN_USE`, `CHARGING`, `DISPATCHED`, `INCIDENT`, `MAINTENANCE_OFFLINE` | Bổ sung đầy đủ các chuyển trạng thái (như SoC $\ge 80\%$, xe gặp sự cố) |
| **6** | **Hình 4.2 & Bảng 4.2** | Chuỗi trạng thái phiên sạc không khớp giữa sơ đồ và bảng | Thống nhất bộ 8 trạng thái: `WAITING`, `SCHEDULED`, `CHARGING`, `CHARGE_COMPLETED`, `GRACE_PERIOD`, `OVERSTAY`, `ERROR`, `AVAILABLE` | Chuẩn hóa quy trình sạc xe điện thông minh và tính phí chiếm dụng cổng |
| **7** | **Hình 4.3 & Bảng 4.3** | Hình dùng `NORMAL_OPERATION`, bảng dùng `NORMAL`; thiếu trạng thái `GRID_OFFLINE` | Thống nhất 5 trạng thái vận hành Hub: `NORMAL_OPERATION`, `HIGH_DEMAND`, `CRITICAL_OVERLOAD`, `GRIDLOCK_DEPLETED`, `GRID_OFFLINE` | Bổ sung trạng thái mất điện lưới (`GRID_OFFLINE`) cho SS7 và gắn ngưỡng D6 ($<70\%, 70-85\%, >85\%$) |
| **8** | **Bảng 2.2** | Liệt kê các lớp kiến trúc backend không xuất hiện trên Sequence Diagram 2.1 (`BookingController`, `WalletService`) | Viết lại hoàn toàn theo đúng 5 Lifelines trên Hình 2.1: `student_booking.py (UI)`, `Cổng VNU-SSO`, `st.session_state`, `Ví điện tử`, `Khóa IoT` | Bổ sung Group 1 (SSO), Group 2 (Đặt cọc), Group 3 (Nhận xe & Alternative No-show) |
| **9** | **Hình 2.5, 2.7, 3.5, 3.9** | Sơ đồ tuần tự và hoạt động SS2/SS3 bị cắt cụt lề, co rút font chữ cực nhỏ, không đọc được | Bổ sung `\usepackage{pdflscape}`, chuyển các trang sơ đồ sang môi trường `\begin{landscape}` và mở rộng scale tối đa | Đảm bảo 100% chữ, nhãn mũi tên và điều kiện rẽ nhánh đọc rõ nét ở zoom 100% |
| **10** | **Hình 3.14 đến 3.17** | Sơ đồ hoạt động SS6 và SS7 bị thu nhỏ quá mức | Tăng tỉ lệ hiển thị lên `0.98\textwidth` và `0.75\textheight` | Tối ưu hóa tính công thái học và khả năng tra cứu tài liệu |
| **11** | **Hình 1.8 & Mục 1.6.2** | Ảnh màn hình SS7 chụp ở trạng thái chưa kích hoạt sự cố; văn bản mô tả kết quả | Chạy trực tiếp prototype, kích hoạt mô phỏng Port Failure (-3 cổng tại ĐH Bách Khoa) và chụp ảnh thực tế đầy đủ: Console log, Bảng rerouting sang ĐH KHXH&NV và nút Áp dụng | Khớp 100% giữa ảnh chụp prototype thực tế và bài viết |
| **12** | **Hình 1.1 & Bảng 1.3** | Luồng màn hình tạo cảm giác toàn bộ chức năng SSO và Barie đã hoàn thiện trên mobile app | Ghi chú rõ ràng trên Caption Hình 1.1 và Bảng 1.3: Đăng nhập VNU-SSO và Barie Check-in là Thiết kế mục tiêu (Target Design); prototype điều hướng qua Sidebar | Đảm bảo tính trung thực kỹ thuật và phân định rõ phạm vi đã cài đặt |
| **13** | **Mục 1.4.1 & Mục 1.5.2** | Số xe tại Hub KTX Khu A mâu thuẫn giữa 5 xe và 8 xe | Chuẩn hóa: Hub KTX Khu A có tổng cộng **8 xe** ($5\text{ xe AVAILABLE}$, $2\text{ xe CHARGING}$, $1\text{ xe RESERVED}$) | Khớp chuẩn xác với cơ sở dữ liệu `src/data/mock_hubs.json` |
| **14** | **Mục 1.5.1, 1.5.2, 2.3.2** | Mâu thuẫn màu cảnh báo: Yellow Alert vs Red Overload; dot màu KTX Khu A | Chuẩn hóa ngưỡng D6: $<70\%$ Bình thường (xanh), $70-85\%$ Mức cao (vàng), $>85\%$ Quá tải (đỏ). Hub KTX Khu A ($62.5\%$) gắn mác Bình thường/Mức cao theo code | Xóa bỏ mâu thuẫn cảnh báo quá tải trên giao diện giám sát |
| **15** | **Mục 1.2 & Dòng Tổng MoSCoW** | Tỷ lệ cam kết MoSCoW không rõ ràng | Chuẩn hóa: Must ($50\%$) + Should ($25\%$) = $75\%$ cam kết nền tảng; tích hợp thêm Could ($15\%$) đạt tổng $90\%$ chức năng prototype | Thể hiện kế hoạch phát triển phần mềm chặt chẽ |
| **16** | **Mục 1.6.1 & UC_SS6_01** | Gọi nhầm tên ga Metro Suối Tiên | Chuẩn hóa toàn bộ thành "ga Metro ĐHQG-HCM" (tuyến Metro số 1 Bến Thành -- Suối Tiên) | Thống nhất tên địa danh học đường thực tế |
| **17** | **Hình 1.7 (SS6 Demand)** | Trục biểu đồ đạt mốc 150 nhưng bài viết ghi "vượt mốc 170" | Sửa văn bản bài viết khớp với biểu đồ: "vượt mốc 150 người" | Đảm bảo số liệu minh họa khớp 100% với đồ thị Plotly |
| **18** | **Mục 2 & Bảng 2.8, Hình 2.8** | Tác nhân ghi gộp "Operator / Admin" | Tách biệt chuẩn mực: vai trò chính tương tác là `Operator`; `Admin` chỉ can thiệp cấu hình hệ thống | Tuân thủ nghiêm ngặt chuẩn UML 2.5 và phản hồi chuyên môn |
| **19** | **Bảng 0.1 & Danh mục bảng** | Tên nhóm ghi là "Nhóm 1" | Sửa thành tên chính thức: **"Nhóm BEE BRAVE"** | Chuẩn hóa nhận diện nhóm tác giả |
| **20** | **Toàn bộ sơ đồ SS5** | Sơ đồ PUML viết bằng tiếng Việt không dấu | Bổ sung đầy đủ dấu tiếng Việt có thanh điệu chuẩn mực cho toàn bộ Sequence, Activity và State-chart của SS5 | Nâng cao chất lượng trình bày đồ án học thuật |
| **21** | **Toàn bộ sơ đồ SS3** | Sử dụng theme riêng màu cam `!theme aws-orange` | Chuyển đổi toàn bộ sang `!theme plain` đồng bộ với các phân hệ SS1, SS2, SS4, SS5, SS6, SS7 | Tạo tính đồng nhất mỹ thuật xuyên suốt toàn bộ báo cáo |
| **22** | **Mục 1.4, 1.5, 2.1, 2.2** | Tuyên bố quá mức: OAuth 2.0 thực tế, barie tự động ngoài hiện trường, loại bỏ hoàn toàn cảm tính, phục vụ hơn 60.000 người dùng | Chuyển sang văn phong học thuật trung thực: "mô phỏng định danh VNU-SSO (thiết kế mục tiêu OAuth 2.0)", "mô phỏng tín hiệu barie/IoT", "thuật toán tối ưu hóa đa mục tiêu", "thiết kế phục vụ quy mô ĐHQG-HCM" | Đảm bảo tính trung thực học thuật và phân định rõ ranh giới nghiên cứu |

---

## 3. Kết luận
Toàn bộ 22 hạng mục sai lệch, mâu thuẫn và tồn đọng đã được giải quyết triệt để. Báo cáo `REPORT_SUBMISSION_2.tex` đã được biên dịch thành công qua `xelatex` tạo thành `REPORT_SUBMISSION_2.pdf` hoàn chỉnh, sắc nét và đạt chuẩn chất lượng đồ án Kỹ thuật Phần mềm.


## Đồng bộ ký hiệu UML ngày 26/10/2026

- Đưa 45 sơ đồ activity/sequence/state-chart Sub2 về `docs/diagrams/common.puml`; bỏ màu riêng ở SS4, thống nhất font, mũi tên, nút đầu/cuối và decision/merge hình thoi.
- Ghi điều kiện nhánh activity trong ngoặc vuông; bổ sung nhãn cho các nhánh bù trước đó để trống.
- Sửa activity SS1_02: vòng lặp kiểm tra lại Hub có nhãn rõ ràng, phân biệt chỗ đã giữ với chỗ mới, trạng thái xe với booking, ưu đãi điều hướng 15 phút một lần và dữ liệu hóa đơn trong phiên.
- Sửa tên xe cũ `PARKED` ở SS4 thành `AVAILABLE`, `MAINTENANCE_OFFLINE` ở SS1 thành `OFFLINE`; đồng bộ ngưỡng pin SS1 là >=20%, các tên `balance`/`held_deposit` và thời điểm hết hạn tại deadline.
- Đồng bộ số bước 3.3–3.13 của bảng thông điệp SS1_01 với autonumber trên hình; chuẩn hóa role STUDENT.
- Cập nhật sequence SS1_02 và thuyết minh tương ứng; thêm bảng chú giải UML, phân biệt Activity Final/Flow Final và connector A.
- Chia sơ đồ activity SS1_02 trong báo cáo thành hai phần nối A; giữ nguồn/ảnh đầy đủ cạnh use case. Dựng lại ảnh, các panel và PDF, đồng bộ danh mục hình theo tham chiếu LaTeX.
- Sửa đường dẫn include của panel sequence và phạm vi bộ kiểm tra Sub2 để không đếm nhầm các sơ đồ DRAFT Sub3. Bằng chứng của lần cập nhật này ở `docs/audit/submission_2/notation_sync_20261026/`; bằng chứng cũ trong `final/` được giữ như hồ sơ lịch sử.
