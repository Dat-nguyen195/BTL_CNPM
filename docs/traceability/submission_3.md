# Truy vết hệ thống Submission 3 - 17 UC

Revision 06/11/2026; bản tích hợp đã đối chiếu SRS và source bàn giao. Bảng này không là xác nhận cá nhân hoặc điểm chấm của giảng viên. Chi tiết machine-readable: [submission_3.json](submission_3.json).

| UC | Chủ sở hữu | Yêu cầu SRS | Truy vết cá nhân | Trạng thái |
| --- | --- | --- | --- | --- |
| UC_SS1_01 | Nguyễn Thành Đạt | US-01, US-02, US-03, US-03b, US-04, FR-01, FR-01b, FR-01c | [SS1](../report/submission_3/TV1_NguyenThanhDat/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS1_02 | Nguyễn Thành Đạt | US-05b, US-06, FR-01c, FR-15b | [SS1](../report/submission_3/TV1_NguyenThanhDat/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS1_03 | Nguyễn Thành Đạt | US-05, FR-02 | [SS1](../report/submission_3/TV1_NguyenThanhDat/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS2_01 | Nguyễn Anh Tài | US-08, FR-03 | [SS2](../report/submission_3/TV2_NguyenAnhTai/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS2_02 | Nguyễn Anh Tài | US-09, US-10, FR-04, FR-05b | [SS2](../report/submission_3/TV2_NguyenAnhTai/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS2_03 | Nguyễn Anh Tài | US-11b, US-10, FR-03b, FR-04 | [SS2](../report/submission_3/TV2_NguyenAnhTai/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS2_04 | Nguyễn Anh Tài | US-09, US-10, US-11, US-11b, FR-03b, FR-05b, FR-15b | [SS2](../report/submission_3/TV2_NguyenAnhTai/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS3_01 | Phạm Tiến Đạt | US-07, US-13, FR-05, FR-15b | [SS3](../report/submission_3/TV3_PhamTienDat/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS3_02 | Phạm Tiến Đạt | US-13b, US-14, FR-05c, FR-06 | [SS3](../report/submission_3/TV3_PhamTienDat/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS4_01 | Đặng Hoàng Quý Nhân | US-15, FR-07 | [SS4](../report/submission_3/TV4_DangHoangQuyNhan/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS4_02 | Đặng Hoàng Quý Nhân | US-16, US-17, FR-08 | [SS4](../report/submission_3/TV4_DangHoangQuyNhan/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS5_01 | Dương Đăng Khoa | US-10, US-12, US-18, US-20, FR-04, FR-09, FR-11 | [SS5](../report/submission_3/TV5_DuongDangKhoa/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS5_02 | Dương Đăng Khoa | US-12, US-19, US-19b, FR-05b, FR-10, FR-10b, FR-15b | [SS5](../report/submission_3/TV5_DuongDangKhoa/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS6_01 | Hoàng Văn Tấn | US-21, FR-12 | [SS6](../report/submission_3/TV6_HoangVanTan/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS6_02 | Hoàng Văn Tấn | US-22, FR-13 | [SS6](../report/submission_3/TV6_HoangVanTan/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS7_01 | Nguyễn Trung Nguyên | US-23, US-24, FR-14, FR-15 | [SS7](../report/submission_3/TV7_NguyenTrungNguyen/traceability.md) | REVIEWED / OWNER_PENDING |
| UC_SS7_02 | Nguyễn Trung Nguyên | US-24, US-24b, FR-15, FR-15c | [SS7](../report/submission_3/TV7_NguyenTrungNguyen/traceability.md) | REVIEWED / OWNER_PENDING |

## Danh mục kiểm thử

49 trường hợp pytest (bao gồm tham số hóa) trong baseline đã chạy PASS; log ở [pytest-baseline.txt](../audit/submission_3/review_20261106/pytest-baseline.txt). Từng UC dẫn tên test đang tồn tại trong manifest JSON. Các test service/contract chưa có code được đánh dấu DESIGNED trong test_cases.md; không sao chép nhãn PASS từ bản tự báo khi không có nguồn thực thi.
