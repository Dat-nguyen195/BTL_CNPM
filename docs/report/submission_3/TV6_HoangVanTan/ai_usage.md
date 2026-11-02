# Khai báo sử dụng Trí tuệ Nhân tạo (AI Usage Statement)
**Học phần:** Công nghệ Phần mềm CO3001 — HK261  
**Sinh viên:** Hoàng Văn Tấn — MSSV: 2213074 — Phân hệ SS6 (TV6)  
**Submission:** 3 — Software Architecture & Detailed Design  

---

## 1. Công cụ AI sử dụng
- **Công cụ:** Antigravity AI Coding Assistant (mô hình Gemini 3.8 Flash).
- **Mục đích:** Hỗ trợ rà soát yêu cầu thiết kế, định dạng cấu trúc tài liệu Markdown theo mẫu hướng dẫn, sinh mã nguồn PlantUML cho Class Diagram SS6 và tự động hóa render ảnh qua Kroki API.

---

## 2. Phạm vi và Mức độ hỗ trợ của AI
1. **Sinh cấu trúc và rà soát tài liệu (Scaffolding & Review):**
   - AI hỗ trợ sinh khung định dạng theo đúng các mẫu bảng biểu tại Mục 6 của [GUIDANCE_FOR_SUB_3.md](../../../../GUIDANCE_FOR_SUB_3.md).
   - Rà soát các liên kết truy vết giữa Sequence Diagram từ Sub 2 và các Method ID trong Sub 3.
2. **Hỗ trợ tạo Class Diagram PlantUML:**
   - Dựa trên phân công lớp dùng chung tại Mục 2.2 và giao tiếp `INT-04`, `INT-08`, `INT-10`, AI hỗ trợ chuyển đổi các thực thể và chữ ký thành cú pháp PlantUML trực quan.
   - Hỗ trợ gọi script Python render mã nguồn PlantUML ra định dạng PNG/SVG sắc nét.
3. **Thiết kế kịch bản kiểm thử (Test Automation Scripting):**
   - Hỗ trợ viết script kiểm thử tự động 7 ca test case bonus để đối chiếu assert trực tiếp trên mã nguồn `src/core/simulator.py` và `src/core/state.py`.

---

## 3. Phần công việc sinh viên tự tay thực hiện và kiểm chứng
- **Đọc hiểu và đối chiếu mã nguồn:** Trực tiếp phân tích và hiểu rõ từng dòng lệnh trong [`src/components/sim_demand.py`](../../../../src/components/sim_demand.py), [`src/core/simulator.py`](../../../../src/core/simulator.py) và cơ chế `state_version` trong [`src/core/state.py`](../../../../src/core/state.py).
- **Quyết định kiến trúc & biên giới:** Trực tiếp quyết định việc tách bạch giữa bản xem trước `SimulationPreview` và trạng thái trạm gốc, chỉ rõ giới hạn của mô hình doanh thu US-21 trong nguyên mẫu hiện tại.
- **Xác minh kết quả kiểm thử:** Tự chạy kiểm thử, đọc log assert và xác nhận tính đúng đắn của toàn bộ 7 ca test case.
- **Tổng hợp truy vết cấp nhóm:** Chịu trách nhiệm trực tiếp thu thập dữ liệu từ các thành viên khác để hoàn thiện file ma trận 17 Use Case toàn hệ thống [`docs/traceability/submission_3.md`](../../../traceability/submission_3.md).
- **Kiểm tra trực quan tài liệu:** Rà soát định dạng bảng, mục lục, căn lề và xuất file PDF cá nhân cuối cùng.
