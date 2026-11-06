# Khai báo sử dụng AI — Nguyễn Trung Nguyên — SS7

**Trạng thái:** TV7 đã xem và xác nhận chấp nhận nội dung deployment view và class_diagram. TV7 tự tạo implementation view riêng để đối chiếu ánh xạ, không ảnh hưởng đến phần của TV3.

## Công cụ và phạm vi

- **Công cụ:** AI assistant using Copilot SDK in VS Code.
- **Model:** phiên làm việc không cung cấp tên model cụ thể.
- **Phạm vi AI hỗ trợ:** đọc hướng dẫn Sub3, hợp đồng dùng chung, code SS7, sơ đồ Sub2 và test; tổng hợp ánh xạ prototype; soạn/chỉnh báo cáo, deployment view, implementation view SS7, class diagram SS7, truy vết, test case, self-check và tài liệu này; render/kiểm tra sơ đồ và xuất PDF.
- **Mức đóng góp:** AI thực hiện việc tổng hợp và soạn thảo tài liệu/sơ đồ trong lượt hỗ trợ. Không sửa code triển khai. Không coi các lớp/service đề xuất, tích hợp IoT/SSO/payment hoặc các test case bonus chưa chạy là chức năng đã triển khai.

## Đóng góp và xác nhận của TV7

- TV7 phụ trách SS7 và Deployment view chung theo phân công.
- TV7 chịu trách nhiệm cuối cùng về tính đúng, sửa đổi theo nhận xét của nhóm/giảng viên, ký/xác nhận cá nhân và nộp bài.
- `SimulationPreview`/`SimulationCoordinator` thuộc TV6; `ChargingService` thuộc TV5; `BookingService` và nghiệp vụ chuyển booking thuộc TV1. Phần TV7 chỉ mô tả giao tiếp và cách SS7 tích hợp.
- Các lựa chọn thiết kế được giữ lại vì phản ánh chính xác mức prototype hoặc được đánh dấu là hợp đồng mục tiêu; không tuyên bố hệ thống đang tích hợp IoT, SSO, payment gateway hay database.

## Prompt history

[Bản ghi prompt Sub3](<../../../prompt-history/TV7_NguyenTrungNguyen/prompt_history_NguyenTrungNguyen_sub3.txt>) lưu các prompt thực tế nhìn thấy trong phiên hỗ trợ cùng phần tóm tắt công việc. Đây là bản ghi bổ sung, không phải transcript toàn bộ hội thoại hoặc bản export từ một nền tảng bên ngoài.


## Bổ sung khi tổng hợp 06/11/2026

Codex (AI assistant trong phiên làm việc của trưởng nhóm) đọc đề giảng viên, SRS, code và bài bàn giao; hỗ trợ review, sửa/bổ sung Markdown/PlantUML, danh mục phương thức/truy vết, kiểm tra kỹ thuật và tạo PDF. Mức đóng góp AI trong đợt này là trực tiếp soạn/chỉnh nội dung và tự động hóa kiểm tra; không phải chỉ sửa chính tả. Trưởng nhóm yêu cầu công việc; chủ sở hữu chưa xác nhận đã đọc/hiểu mọi bản sửa. Lịch sử prompt trước giữ nguyên; bản ghi revision ở docs/prompt-history/submission_3_integration_20261106.md, không giả lập hội thoại cá nhân bị thiếu.
