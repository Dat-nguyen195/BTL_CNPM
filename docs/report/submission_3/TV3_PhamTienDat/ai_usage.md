# Khai báo sử dụng Trí tuệ Nhân tạo (AI Usage Statement)
**Học phần:** Công nghệ Phần mềm CO3001 — HK261  
**Sinh viên:** Phạm Tiến Đạt — MSSV: 2410724 — Phân hệ SS3 (TV3)  
**Submission:** 3 — Software Architecture & Detailed Design  

---

## 1. Công cụ AI sử dụng
- **Công cụ:** Google Gemini (Advanced Coding Assistant) & Codex (khởi tạo khung thư mục nhóm).
- **Mục đích:** Hỗ trợ rà soát yêu cầu thiết kế hướng đối tượng, định dạng cấu trúc tài liệu Markdown theo mẫu hướng dẫn, chuẩn hóa mã nguồn PlantUML cho Development/Implementation View, System-level Class Diagram, Class Diagram SS3 và xây dựng bộ kiểm thử tự động `pytest`.

---

## 2. Phạm vi và Mức độ hỗ trợ của AI
1. **Sinh cấu trúc và rà soát tài liệu (Scaffolding & Review):**
   - AI hỗ trợ sinh khung định dạng theo đúng các mẫu bảng biểu tại Mục 6 của [GUIDANCE_FOR_SUB_3.md](../../../../GUIDANCE_FOR_SUB_3.md).
   - Hỗ trợ rà soát tính nhất quán giữa Sequence Diagram / Activity Diagram từ Submission 2 với các lớp (`SS3-CLS-01` đến `SS3-CLS-07`) và phương thức (`SS3-MTH-01` đến `SS3-MTH-13`) trong Submission 3.
2. **Hỗ trợ tạo sơ đồ PlantUML (Shared & Subsystem Views):**
   - Dựa trên phân công lớp dùng chung tại Mục 2.2 và hợp đồng giao tiếp `INT-02`, `INT-03`, `INT-04`, AI hỗ trợ chuyển đổi các thực thể, lớp dịch vụ và quan hệ liên phân hệ thành cú pháp PlantUML cho 3 sơ đồ: `shared/implementation.puml`, `shared/system_classes.puml` và `SS3/class_diagram.puml`.
   - Hỗ trợ tinh chỉnh bố cục (`ranksep`, `nodesep`, hướng phân tầng) để xuất ảnh `.png` / `.svg` rõ nét, không bị cắt chữ hay chồng đường nối.
3. **Thiết kế kịch bản kiểm thử (Test Automation Scripting):**
   - Hỗ trợ viết script kiểm thử tự động `tests/test_ss3_monitoring_bonus.py` gồm 5 ca test case bonus để kiểm chứng trực tiếp các ngưỡng biên chiếm dụng, bất biến sức chứa, báo cáo doanh thu thực thu và cơ chế khóa/cache IoT.

---

## 3. Phần công việc sinh viên tự tay thực hiện và kiểm chứng
- **Đọc hiểu và đối chiếu mã nguồn thực tế:** Trực tiếp phân tích và đối chiếu từng dòng lệnh trong [`src/components/hub_monitor.py`](../../../../src/components/hub_monitor.py), [`src/core/state.py`](../../../../src/core/state.py), [`src/core/policies.py`](../../../../src/core/policies.py) và [`src/core/billing.py`](../../../../src/core/billing.py).
- **Quyết định kiến trúc & biên giới:**
  - Trực tiếp chuẩn hóa định nghĩa lớp thực thể `Hub` dùng chung toàn hệ thống và bất biến bảo toàn sức chứa chỗ đỗ (`available_slots + present_vehicles_count + incoming_reserved_count + background_load_count == capacity`).
  - Xác định rõ nguyên tắc tài chính trong `RevenueReport`: tách biệt hoàn toàn doanh thu thực thu (`total_realized_revenue_vnd`) khỏi tiền cọc đang tạm giữ (`held_deposit_vnd`) và công nợ (`outstanding_debt_vnd`).
  - Chỉ rõ ranh giới giữa logic hiện có trong hàm `render()` của `hub_monitor.py` và tầng dịch vụ `MonitoringService` đề xuất.
- **Xác minh kết quả kiểm thử:** Tự thiết lập môi trường `PYTHONPATH=src`, chạy kiểm thử `pytest`, đọc log assert và xác nhận $100\%$ các ca test case bonus SS3 cùng test tích hợp đều đạt `PASS`.
- **Tổng hợp kiến trúc cấp nhóm (TV3):** Chịu trách nhiệm trực tiếp tổng hợp sơ đồ **Development / Implementation View** (`docs/diagrams/submission_3/shared/implementation.puml`) và **System-level Class Diagram** (`docs/diagrams/submission_3/shared/system_classes.puml`) cho toàn bộ 7 phân hệ.
- **Kiểm tra trực quan tài liệu:** Tự rà soát bảng biểu, đường dẫn tương đối, ảnh sơ đồ và xuất file báo cáo PDF/Word cá nhân cuối cùng.
- **Nhật ký Prompt:** Được lưu trữ đầy đủ tại [`docs/prompt-history/TV3_PhamTienDat/prompt_history_PhamTienDat_sub3.txt`](../../../prompt-history/TV3_PhamTienDat/prompt_history_PhamTienDat_sub3.txt).