# Submission 3 — báo cáo và bộ khung làm việc

**Trạng thái:** TV7 đã hoàn thiện báo cáo, nguồn và ảnh các view cá nhân, đồng thời xuất PDF. Các phần cá nhân khác tiếp tục theo trạng thái trong file của từng thành viên.
**Bắt đầu:** 21/10/2026. **Kết thúc:** 30/10/2026.  
**Nguyên tắc:** mỗi thành viên tự làm, tự kiểm tra và tự chịu trách nhiệm; không có kiểm tra chéo hoặc deadline theo từng task.

## Vì sao dùng cấu trúc này?

Dự án đã có cây `docs/report/submission_3/` với `mau.png`. Cấu trúc mới tái sử dụng cây đó, tách nguồn sơ đồ sang `docs/diagrams/submission_3/`, truy vết chung sang `docs/traceability/submission_3.md`, log AI vào các thư mục cá nhân sẵn có và đầu ra xuất bản vào `output/submission_3/`. Không tạo thêm cây `docs/submission_3/` song song; không di chuyển hay ghi đè Sub1/Sub2.

## Điểm vào

- [Hướng dẫn đầy đủ](<../../../GUIDANCE_FOR_SUB_3.md>).
- [Quyền sở hữu và hợp đồng chung](<shared/shared_contracts.md>).
- [Chỉ mục sơ đồ](<../../diagrams/submission_3/README.md>).
- [Truy vết chung 17 UC](<../../traceability/submission_3.md>).
- [Vấn đề tự báo](<shared/open_issues.md>).
- [Quy tắc file xuất](<../../../output/submission_3/README.md>).

## Phần việc từng thành viên

| Thành viên | Điểm vào |
| --- | --- |
| TV1 — Nguyễn Thành Đạt — SS1 | [Báo cáo / task / truy vết](<TV1_NguyenThanhDat/REPORT_SUB3.md>) |
| TV2 — Nguyễn Anh Tài — SS2 | [Báo cáo / task / truy vết](<TV2_NguyenAnhTai/REPORT_SUB3.md>) |
| TV3 — Phạm Tiến Đạt — SS3 | [Báo cáo / task / truy vết](<TV3_PhamTienDat/REPORT_SUB3.md>) |
| TV4 — Đặng Hoàng Quý Nhân — SS4 | [Báo cáo / task / truy vết](<TV4_DangHoangQuyNhan/REPORT_SUB3.md>) |
| TV5 — Dương Đăng Khoa — SS5 | [Báo cáo / task / truy vết](<TV5_DuongDangKhoa/REPORT_SUB3.md>) |
| TV6 — Hoàng Văn Tấn — SS6 | [Báo cáo / task / truy vết](<TV6_HoangVanTan/REPORT_SUB3.md>) |
| TV7 — Nguyễn Trung Nguyên — SS7 | [Báo cáo / task / truy vết](<TV7_NguyenTrungNguyen/REPORT_SUB3.md>) |

## Cách bắt đầu

1. Mở báo cáo cá nhân và đọc hợp đồng chung; ID use case đã được điền từ manifest hiện tại.
2. Hoàn thiện source PlantUML tại đúng thư mục SS, mô tả lớp/phương thức trong báo cáo và cập nhật truy vết cá nhân.
3. Viết test bonus nếu thực hiện; tự kiểm tra, tự sửa rồi cập nhật `self_check.md`. Mọi ô ban đầu đều chưa đánh dấu.
4. Ghi phạm vi AI và prompt thực tế; không coi khung được sinh tự động là đóng góp hoàn chỉnh của cá nhân.
5. Xuất ảnh sau khi thiết kế hoàn thiện; đưa đủ hình, bảng, thuyết minh và các phụ lục cần thiết vào PDF để nộp theo LMS.

Các file `.puml` phải được kiểm tra theo trạng thái ở [chỉ mục sơ đồ](<../../diagrams/submission_3/README.md>); không coi source đã điền là ảnh đã render hoặc xác nhận của chủ sở hữu. Không tạo PDF/PNG rỗng hoặc tự ghi PASS để làm đủ danh sách. `mau.png` là tệp sẵn có được giữ nguyên.
