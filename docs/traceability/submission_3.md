# BẢNG MA TRẬN TRUY VẾT HỆ THỐNG — SUBMISSION 3
## Smart E-Mobility Hub — BEE BRAVE (Nhóm 7)

**Môn học:** Công nghệ Phần mềm (CO3001) — HK261  
**Đầu mối tổng hợp hệ thống:** TV6 — **Hoàng Văn Tấn** (MSSV: 2213074)  
**Trưởng nhóm điều phối:** TV1 — **Nguyễn Thành Đạt** (MSSV: 2410709)  
**Phiên bản chỉ mục:** 1.0 — Cập nhật ngày 02/11/2026  
**Căn cứ pháp lý & kỹ thuật:** Kế thừa từ [Manifest Submission 2](submission_2.json), [SRS Phân tích yêu cầu](../requirements-analysis.md) và hướng dẫn [GUIDANCE_FOR_SUB_3.md](../../GUIDANCE_FOR_SUB_3.md).

---

## 1. Nguyên tắc truy vết chuẩn hóa Sub 3
Hệ thống áp dụng chuỗi truy vết 6 cấp độ khép kín:
$$\text{Yêu cầu (US / FR)} \longrightarrow \text{Use Case Sub 2} \longrightarrow \text{Sơ đồ (Sequence / Activity)} \longrightarrow \text{Lớp thiết kế Sub 3} \longrightarrow \text{Phương thức (Method ID)} \longrightarrow \text{Mã nguồn / Đề xuất} \longrightarrow \text{Test Case ID}$$

> **Quy ước ghi nhận trạng thái:**  
> - Không tự tiện sao chép trạng thái `VERIFIED` của Sub 2 thành trạng thái hoàn tất Sub 3.  
> - TV6 tổng hợp dựa trên báo cáo thực tế được bàn giao từ các chủ sở hữu phân hệ. Ô nào chưa bàn giao hoặc còn DRAFT được ghi nhận trung thực là `CHỜ BÀN GIAO / DRAFT`.

---

## 2. Bảng ma trận tổng hợp 17 Use Case toàn hệ thống

| Mã UC | Tên Use Case chuẩn hóa | SS | Thành viên phụ trách | Yêu cầu gốc (SRS) | Sơ đồ Sub 2 liên quan | Class Diagram Sub 3 | Trạng thái thiết kế Sub 3 | Báo cáo truy vết chi tiết |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| **`UC_SS1_01`** | Tra cứu, Đặt xe & Nhận xe qua QR/PIN | SS1 | Nguyễn Thành Đạt (TV1) | US-01, US-02, US-03, FR-01, FR-02 | [Sequence](<../diagrams/Use-case detail-scenario/SS1/Sequence diagrams/UC_SS1_01_NguyenThanhDat_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS1/Activity diagrams/UC_SS1_01_NguyenThanhDat_activity.puml>) | [SS1 Diagram](<../diagrams/submission_3/SS1/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV1](<../report/submission_3/TV1_NguyenThanhDat/traceability.md>) |
| **`UC_SS1_02`** | Trả xe, Cập nhật vị trí & Quyết toán ví điện tử | SS1 | Nguyễn Thành Đạt (TV1) | US-04, US-05, US-06, FR-03, FR-04 | [Sequence](<../diagrams/Use-case detail-scenario/SS1/Sequence diagrams/UC_SS1_02_NguyenThanhDat_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS1/Activity diagrams/UC_SS1_02_NguyenThanhDat_activity.puml>) | [SS1 Diagram](<../diagrams/submission_3/SS1/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV1](<../report/submission_3/TV1_NguyenThanhDat/traceability.md>) |
| **`UC_SS1_03`** | Hủy đặt chỗ & Hoàn cọc / Phạt quá giờ | SS1 | Nguyễn Thành Đạt (TV1) | US-07, US-08, FR-04, FR-05 | [Sequence](<../diagrams/Use-case detail-scenario/SS1/Sequence diagrams/UC_SS1_03_NguyenThanhDat_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS1/Activity diagrams/UC_SS1_03_NguyenThanhDat_activity.puml>) | [SS1 Diagram](<../diagrams/submission_3/SS1/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV1](<../report/submission_3/TV1_NguyenThanhDat/traceability.md>) |
| **`UC_SS2_01`** | Đăng ký xe EV cá nhân lên hệ thống | SS2 | Nguyễn Anh Tài (TV2) | US-09, FR-06 | [Sequence](<../diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_01_NguyenAnhTai_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_01_NguyenAnhTai_activity.puml>) | [SS2 Diagram](<../diagrams/submission_3/SS2/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV2](<../report/submission_3/TV2_NguyenAnhTai/traceability.md>) |
| **`UC_SS2_02`** | Đặt trước chỗ đỗ và nhu cầu sạc xe EV cá nhân | SS2 | Nguyễn Anh Tài (TV2) | US-09, US-10, FR-06, FR-07 | [Sequence](<../diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_02_NguyenAnhTai_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_02_NguyenAnhTai_activity.puml>) | [SS2 Diagram](<../diagrams/submission_3/SS2/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV2](<../report/submission_3/TV2_NguyenAnhTai/traceability.md>) |
| **`UC_SS2_03`** | Check-in xe EV cá nhân tại cổng Hub (QR/Biển số) | SS2 | Nguyễn Anh Tài (TV2) | US-11, FR-08 | [Sequence](<../diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_03_NguyenAnhTai_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_03_NguyenAnhTai_activity.puml>) | [SS2 Diagram](<../diagrams/submission_3/SS2/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV2](<../report/submission_3/TV2_NguyenAnhTai/traceability.md>) |
| **`UC_SS2_04`** | Check-out và thanh toán tổng hợp dịch vụ xe EV cá nhân | SS2 | Nguyễn Anh Tài (TV2) | US-12, FR-08, FR-09 | [Sequence](<../diagrams/Use-case detail-scenario/SS2/Sequence diagrams/UC_SS2_04_NguyenAnhTai_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS2/Activity diagrams/UC_SS2_04_NguyenAnhTai_activity.puml>) | [SS2 Diagram](<../diagrams/submission_3/SS2/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV2](<../report/submission_3/TV2_NguyenAnhTai/traceability.md>) |
| **`UC_SS3_01`** | Giám sát mạng lưới Hub, KPI & Doanh thu thời gian thực | SS3 | Phạm Tiến Đạt (TV3) | US-13, US-14, FR-10 | [Sequence](<../diagrams/Use-case detail-scenario/SS3/Sequence diagrams/UC_SS3_01_PhamTienDat_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS3/Activity diagrams/UC_SS3_01_PhamTienDat_activity.puml>) | [SS3 Diagram](<../diagrams/submission_3/SS3/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV3](<../report/submission_3/TV3_PhamTienDat/traceability.md>) |
| **`UC_SS3_02`** | Cảnh báo phân cấp chiếm dụng Hub & Sự cố IoT | SS3 | Phạm Tiến Đạt (TV3) | US-15, FR-10 | [Sequence](<../diagrams/Use-case detail-scenario/SS3/Sequence diagrams/UC_SS3_02_PhamTienDat_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS3/Activity diagrams/UC_SS3_02_PhamTienDat_activity.puml>) | [SS3 Diagram](<../diagrams/submission_3/SS3/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV3](<../report/submission_3/TV3_PhamTienDat/traceability.md>) |
| **`UC_SS4_01`** | Lập lệnh điều chuyển phương tiện cân bằng phụ tải | SS4 | Đặng Hoàng Quý Nhân (TV4) | US-16, US-17, FR-11 | [Sequence](<../diagrams/Use-case detail-scenario/SS4/Sequence diagrams/UC_SS4_01_DangHoangQuyNhan_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS4/Activity diagrams/UC_SS4_01_DangHoangQuyNhan_activity.puml>) | [SS4 Diagram](<../diagrams/submission_3/SS4/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV4](<../report/submission_3/TV4_DangHoangQuyNhan/traceability.md>) |
| **`UC_SS4_02`** | Báo cáo, tiếp nhận xử lý và khắc phục sự cố phương tiện | SS4 | Đặng Hoàng Quý Nhân (TV4) | US-18, FR-11 | [Sequence](<../diagrams/Use-case detail-scenario/SS4/Sequence diagrams/UC_SS4_02_DangHoangQuyNhan_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS4/Activity diagrams/UC_SS4_02_DangHoangQuyNhan_activity.puml>) | [SS4 Diagram](<../diagrams/submission_3/SS4/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV4](<../report/submission_3/TV4_DangHoangQuyNhan/traceability.md>) |
| **`UC_SS5_01`** | Lập lịch sạc tự động theo điểm ưu tiên & Giới hạn công suất lưới | SS5 | Dương Đăng Khoa (TV5) | US-19, FR-14 | [Sequence](<../diagrams/Use-case detail-scenario/SS5/Sequence diagrams/UC_SS5_01_DuongDangKhoa_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS5/Activity diagrams/UC_SS5_01_DuongDangKhoa_activity.puml>) | [SS5 Diagram](<../diagrams/submission_3/SS5/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV5](<../report/submission_3/TV5_DuongDangKhoa/traceability.md>) |
| **`UC_SS5_02`** | Giám sát hàng chờ sạc, hoàn thành, ân hạn & Tính phí quá giờ | SS5 | Dương Đăng Khoa (TV5) | US-20, FR-14, FR-15 | [Sequence](<../diagrams/Use-case detail-scenario/SS5/Sequence diagrams/UC_SS5_02_DuongDangKhoa_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS5/Activity diagrams/UC_SS5_02_DuongDangKhoa_activity.puml>) | [SS5 Diagram](<../diagrams/submission_3/SS5/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV5](<../report/submission_3/TV5_DuongDangKhoa/traceability.md>) |
| **`UC_SS6_01`** | Mô phỏng tăng đột biến nhu cầu khách Metro (What-if Metro Surge) | SS6 | Hoàng Văn Tấn (TV6) | US-21, FR-12 | [Sequence](<../diagrams/Use-case detail-scenario/SS6/Sequence diagrams/UC_SS6_01_HoangVanTan_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS6/Activity diagrams/UC_SS6_01_HoangVanTan_activity.puml>) | [SS6 Diagram](<../diagrams/submission_3/SS6/class_diagram.puml>) | **HOÀN THÀNH** | [Báo cáo TV6](<../report/submission_3/TV6_HoangVanTan/traceability.md>) |
| **`UC_SS6_02`** | Dự báo phụ tải nhu cầu và phân tích hàng đợi 24h | SS6 | Hoàng Văn Tấn (TV6) | US-21, US-22, FR-12, FR-13 | [Sequence](<../diagrams/Use-case detail-scenario/SS6/Sequence diagrams/UC_SS6_02_HoangVanTan_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS6/Activity diagrams/UC_SS6_02_HoangVanTan_activity.puml>) | [SS6 Diagram](<../diagrams/submission_3/SS6/class_diagram.puml>) | **HOÀN THÀNH** | [Báo cáo TV6](<../report/submission_3/TV6_HoangVanTan/traceability.md>) |
| **`UC_SS7_01`** | Mô phỏng sự cố hạ tầng & Mất điện trạm sạc | SS7 | Nguyễn Trung Nguyên (TV7) | US-23, FR-16 | [Sequence](<../diagrams/Use-case detail-scenario/SS7/Sequence diagrams/UC_SS7_01_NguyenTrungNguyen_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS7/Activity diagrams/UC_SS7_01_NguyenTrungNguyen_activity.puml>) | [SS7 Diagram](<../diagrams/submission_3/SS7/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV7](<../report/submission_3/TV7_NguyenTrungNguyen/traceability.md>) |
| **`UC_SS7_02`** | Đề xuất gợi ý điều hướng tự động sang Hub lân cận & Cảnh báo | SS7 | Nguyễn Trung Nguyên (TV7) | US-24, FR-17 | [Sequence](<../diagrams/Use-case detail-scenario/SS7/Sequence diagrams/UC_SS7_02_NguyenTrungNguyen_sequence.puml>) · [Activity](<../diagrams/Use-case detail-scenario/SS7/Activity diagrams/UC_SS7_02_NguyenTrungNguyen_activity.puml>) | [SS7 Diagram](<../diagrams/submission_3/SS7/class_diagram.puml>) | Đang hoàn thiện | [Báo cáo TV7](<../report/submission_3/TV7_NguyenTrungNguyen/traceability.md>) |

---

## 3. Tổng mục kiểm thử hệ thống (System Test Suite Index)

Theo yêu cầu của mục `TV6-10`, danh mục kiểm thử hệ thống được phân định rõ ràng giữa các ca kiểm thử đã thực thi có bằng chứng và các ca kiểm thử dự kiến:

### 3.1. Các ca kiểm thử đã thực thi thực tế (Đạt PASS và có log xác minh)
Toàn bộ 7 ca kiểm thử của phân hệ SS6 do TV6 trực tiếp thực thi trên môi trường Python 3.12:

| Test Case ID | Phân hệ | Tên ca kiểm thử | Lớp / Phương thức kiểm tra | Kết quả thực tế | Ngày thực thi |
| :--- | :---: | :--- | :--- | :---: | :---: |
| `TC-SS6-SRG-01` | SS6 | Metro Surge trong ngưỡng sức chứa (Admitted 5, Unserved 0) | `DemandSimulationService.preview_demand` | **PASS** | 02/11/2026 |
| `TC-SS6-SRG-02` | SS6 | Metro Surge quá tải sức chứa (Admitted 8, Unserved 42) | `HubEventSimulator.simulate_metro_surge` | **PASS** | 02/11/2026 |
| `TC-SS6-SRG-03` | SS6 | Tính cách ly Deepcopy bảo vệ trạng thái trạm gốc | `DemandSimulationService.preview_demand` | **PASS** | 02/11/2026 |
| `TC-SS6-FC-01` | SS6 | Dự báo chuỗi thời gian đủ 24 mốc giờ (06:00 đến 05:00) | `ForecastService.forecast` | **PASS** | 02/11/2026 |
| `TC-SS6-FC-02` | SS6 | Tính tái lập kết quả dự báo ngẫu nhiên theo Seed=42 | `ForecastService.forecast` | **PASS** | 02/11/2026 |
| `TC-SS6-APL-01` | SS6 | Áp dụng Preview thành công & Tăng phiên bản state_version | `SimulationCoordinator.apply_preview` | **PASS** | 02/11/2026 |
| `TC-SS6-APL-02` | SS6 | Ngăn chặn Stale Version khi dữ liệu trạm bị thay đổi trước đó | `SimulationCoordinator.apply_preview` | **PASS** | 02/11/2026 |

*Bằng chứng log thực thi được lưu tại:* [`docs/report/submission_3/TV6_HoangVanTan/test_cases.md`](<../report/submission_3/TV6_HoangVanTan/test_cases.md>).

### 3.2. Danh mục test case của các phân hệ khác (Đang chờ tác giả cung cấp)
- **SS1 (TV1):** Các ca kiểm thử đặt/nhận xe, hủy cọc và hết hạn giữ xe 30 phút (`tests/test_reservation_30_minutes.py`).
- **SS2 (TV2):** Các ca kiểm thử đăng ký xe cá nhân, check-in, check-out và biểu phí đỗ 5.000đ (`tests/test_personal_ev.py`).
- **SS3 (TV3):** Các ca kiểm thử giám sát ngưỡng occupancy (<70%, 70-85%, 85-100%, >=100%) và doanh thu thực thu.
- **SS4 (TV4):** Các ca kiểm thử điều chuyển xe dùng chung và tiếp nhận sự cố phương tiện.
- **SS5 (TV5):** Các ca kiểm thử lập lịch sạc, ưu tiên, ân hạn 15 phút và phạt quá giờ (`tests/test_scheduler_and_charging.py`).
- **SS7 (TV7):** Các ca kiểm thử mất điện cổng sạc, điều hướng Hub lân cận và ưu đãi 15 phút.

*Trạng thái:* TV6 sẽ định kỳ cập nhật bảng này ngay khi các thành viên hoàn thành và nộp file `test_cases.md` cá nhân.

---

## 4. Báo cáo tình trạng ô trống và đề xuất trưởng nhóm
- **Phân hệ SS6:** Đã hoàn thành 100% sơ đồ lớp, mô tả phương thức, bảng truy vết và kiểm thử tự động.
- **Các phân hệ SS1, SS2, SS3, SS4, SS5, SS7:** Đang trong giai đoạn hoàn thiện báo cáo và sơ đồ chi tiết. TV6 khuyến nghị Trưởng nhóm TV1 đôn đốc các thành viên cập nhật đúng mã Method ID và trạng thái test thực tế vào file cá nhân trước hạn chót bàn giao.
