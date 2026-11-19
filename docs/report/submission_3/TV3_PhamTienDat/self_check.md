# Bản tự kiểm tra chất lượng cá nhân — Phạm Tiến Đạt — SS3
**Phân hệ:** SS3 — Giám sát mạng lưới Hub, KPI, Doanh thu & Cảnh báo  
**Thành viên:** Phạm Tiến Đạt — MSSV: 2410724 — Vai trò: TV3  
**Phiên bản sản phẩm:** 1.1 (Submission 3 Final)  
**Ngày tự kiểm tra:** 06/11/2026  
**Trạng thái xác nhận:** ĐÃ TỰ KIỂM TRA & XÁC NHẬN CHỊU TRÁCH NHIỆM NỘI DUNG.

---

## 1. Tiến độ hoàn thành 12 nhiệm vụ cá nhân (Checklist TV3)

- [x] `TV3-01` — Lập danh sách lớp SS3 (`Hub`, `OccupancySnapshot`, `RevenueReport`, `Alert`, `NetworkSnapshot`, `MonitoringService`, `HubMonitorUI`) và các nguồn dữ liệu dùng cho KPI/cảnh báo.
- [x] `TV3-02` — Mô tả kiến trúc module/tầng hiện tại dựa trên code (`hub_monitor.py`, `state.py`, `policies.py`, `billing.py`) và quyết định mục 2.2–2.3 của GUIDANCE.
- [x] `TV3-03` — **[Nhiệm vụ cá nhân & nhóm]** Tạo Class Diagram SS3 (`docs/diagrams/submission_3/SS3/class_diagram.puml`) và tổng hợp Development/Implementation View chung (`docs/diagrams/submission_3/shared/implementation.puml`), đủ nguồn `.puml` + ảnh `.png`/`.svg`.
- [x] `TV3-04` — Mô tả đầy đủ lớp chuẩn `Hub`, các snapshot, `Alert`, đơn vị KPI (`%`, `kW`, `VNĐ`, `chỗ`, `cổng`) và các phụ thuộc theo định nghĩa đã chốt.
- [x] `TV3-05` — Hoàn thành mô tả chi tiết toàn bộ lớp và 13 phương thức của SS3 (`SS3-MTH-01` đến `SS3-MTH-13`), giải thích rõ nguồn tính KPI và doanh thu thực thu.
- [x] `TV3-06` — **[Nhiệm vụ nhóm]** Tổng hợp System-level Class Diagram (`docs/diagrams/submission_3/shared/system_classes.puml`) liên kết cả 7 phân hệ từ sản phẩm của các chủ sở hữu và quy ước chung.
- [x] `TV3-07` — Hoàn thành báo cáo `REPORT_SUB3.md`, bảng truy vết `traceability.md`, 5 ca test case bonus `test_cases.md` và khai báo `ai_usage.md`.
- [x] `TV3-08` — Tự kiểm tra SS3 và các sơ đồ chung do TV3 tổng hợp; ghi nhận bằng chứng vào `self_check.md`.
- [x] `TV3-09` — Tự sửa lỗi bố cục PlantUML, kiểm tra lại và kết xuất sơ đồ Implementation View cùng System-level Class Diagram hoàn chỉnh, rõ nét.
- [x] `TV3-10` — Cung cấp nguồn, ảnh, thuyết minh và phiên bản kiến trúc chung cho cả nhóm tham chiếu.
- [x] `TV3-11` — Kết xuất báo cáo PDF/Word cá nhân hoàn chỉnh tại `output/submission_3/REPORT_SUB3_PhamTienDat_2410724.pdf`, kiểm tra hình ảnh và ánh xạ mã nguồn trước khi bàn giao.
- [x] `TV3-12` — Xác nhận đúng bộ file bàn giao trên kho lưu trữ Git và hoàn tất trách nhiệm chuẩn bị nộp theo LMS.

---

## 2. Đối chiếu 12 tiêu chí chất lượng nghiêm ngặt (Mục 8.1 GUIDANCE)

| STT | Tiêu chí chất lượng | Kết quả đối chiếu thực tế | Đánh giá |
| :---: | :--- | :--- | :---: |
| 1 | Có đủ Deployment view và Development/Implementation view; phân biệt đúng vai trò 2 view | Đã phân tích rõ trong mục 2 & 3 của `REPORT_SUB3.md`; dẫn chiếu Deployment view chung của TV7 và trực tiếp tổng hợp Implementation view chung của toàn hệ thống | **ĐẠT** |
| 2 | Phạm vi UC cá nhân đầy đủ: SS3 có đủ 2 UC (`UC_SS3_01`, `UC_SS3_02`) | Bao phủ trọn vẹn cả 2 UC, bao gồm cả các nhánh Alternative ($85\text{–}<100\%$, $100\%$, lỗi cảm biến IoT) và Exception (mất kết nối IoT, lỗi đồng bộ khóa) từ Sub 2 | **ĐẠT** |
| 3 | Class diagram thể hiện trách nhiệm, kiểu dữ liệu, quan hệ và bội số hợp lý | Cả `SS3/class_diagram.puml` và `shared/system_classes.puml` đều có đủ stereotype, kiểu dữ liệu, bội số quan hệ và ghi chú bất biến | **ĐẠT** |
| 4 | Mọi phương thức được vẽ có mô tả tương ứng; tên và chữ ký khớp nhau | Toàn bộ phương thức trên sơ đồ lớp SS3 đều được đặc tả chi tiết từ `SS3-MTH-01` đến `SS3-MTH-13` tại Mục 6 | **ĐẠT** |
| 5 | Có điều kiện trước/sau, lỗi, tác động dữ liệu và quy tắc xử lý lặp khi cần | Mục 6 mô tả rõ precondition, postcondition, mã lỗi (`NOT_FOUND`, `INVALID_STATE`, `FORBIDDEN`, `STALE_STATE`) và tính lũy đẳng (`operation_key`) khi khóa Hub | **ĐẠT** |
| 6 | Truy vết đến đúng UC và thông điệp/nhánh từ Sub 2; không dùng ID tự đặt | Bảng `traceability.md` dẫn đúng đường dẫn tương đối tới các file `.puml` Sequence/Activity của Sub 2 và khớp mã `US`/`FR` chuẩn | **ĐẠT** |
| 7 | Lớp và giao tiếp dùng chung khớp bản đã chốt; không có 7 định nghĩa Hub khác nhau | TV3 định nghĩa duy nhất lớp `Hub` chuẩn dùng chung toàn hệ thống và chữ ký `INT-03` (`get_network_snapshot`); tham chiếu đúng `BillingService` (TV1) và `ChargingService` (TV5) | **ĐẠT** |
| 8 | Mốc 30 phút đúng phạm vi; các quy tắc 15 phút khác không bị thay theo | Giữ nguyên quy tắc phạt no-show $10.000\text{ VNĐ}$ sau 30 phút giữ chỗ xe; không làm sai lệch ân hạn 15 phút sạc của SS5 hay thưởng 15 phút rerouting của SS1/SS7 | **ĐẠT** |
| 9 | Trạng thái và đơn vị đúng; bảo toàn sức chứa, công suất và tài chính được giải thích | Giải thích và kiểm chứng công thức `avail + present + holds + bg == total`, trần công suất $150.0\text{ kW}$ và việc tách biệt tiền cọc $50.000\text{ VNĐ}$/nợ khỏi doanh thu thực thu | **ĐẠT** |
| 10 | Phân biệt code hiện tại với thiết kế đề xuất, mock và mở rộng tương lai | Mục 3.1 và Mục 9 chỉ rõ phần nào đang chạy trong `hub_monitor.py`, phần nào là tầng `MonitoringService` đề xuất và chênh lệch hệ số ước tính $7.4\text{ kW}$ vs $11.0\text{ kW}$ | **ĐẠT** |
| 11 | Test có đầu vào/kết quả cụ thể; trạng thái PASS có bằng chứng thực thi | Thực thi tự động `tests/test_ss3_monitoring_bonus.py` bằng `pytest` đạt `5 passed` ($100\%$ PASS) cùng các test tích hợp core/acceptance | **ĐẠT** |
| 12 | PDF đọc được, không cắt hình/bảng; đóng góp cá nhân và AI được khai báo đúng | Sơ đồ PlantUML đã được căn chỉnh bố cục thoáng, xuất ảnh `.png`/`.svg` đầy đủ; khai báo AI và prompt history trung thực | **ĐẠT** |

---

## 3. Xác nhận trách nhiệm của tác giả
- **Tác giả cam đoan:** Toàn bộ nội dung trong hồ sơ thiết kế phân hệ SS3 cũng như 2 sơ đồ kiến trúc chung cấp hệ thống (`implementation.puml` và `system_classes.puml`) do tôi phụ trách đã được tự kiểm tra kỹ lưỡng, đối chiếu trực tiếp với mã nguồn dự án và chạy kiểm thử `pytest` thực tế.
- **Ký tên xác nhận:** Phạm Tiến Đạt (06/11/2026).