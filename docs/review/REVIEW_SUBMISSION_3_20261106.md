# Review chi tiết Submission 3 - 06/11/2026

## Phạm vi và căn cứ

Đọc đề giảng viên `BTL_SoftwareEngineering_HK261_v1.pdf`: trang4 Project guidelines, trang5 Submission #3 detail, trang6 Generative AI using. Đề gốc ở thư mục cha repository; đã trích xuất toàn bộ và kiểm tra ảnh trang5. Đây là tài liệu giảng viên thực tế được cung cấp; không có thông báo LMS hoặc nhận xét giảng viên khác trong nguồn đã kiểm tra. Không tự suy đoán giờ đóng hoặc sửa hạn theo ngày review.

- Trang4: mỗi thành viên làm yêu cầu/kiến trúc/thiết kế, bốn báo cáo cá nhân, định dạng doc/docx/pdf, deadline từ LMS; database không bắt buộc.
- Trang5: Deployment view; Development/Implementation view; Class diagram và mô tả **mọi phương thức được vẽ**; test case là bonus. Class descriptions có trong mô tả tổng quát trang4.
- Trang6: công khai công cụ/phạm vi/mức đóng góp AI, người học phải hiểu và chịu trách nhiệm; không được nhận nội dung AI hỗ trợ là phần tự làm chưa kiểm chứng.
- Đầu vào nội bộ: SRS `docs/requirements-analysis.md`;17 UC và scenario/sequence/activity Sub2; `GUIDANCE_FOR_SUB_3.md`; `shared_contracts.md`; code `src/`, kiểm thử `tests/`.

## Nguồn bàn giao

| TV | Nhánh / PR | Commit đã tiếp nhận | Kết quả đầu vào |
| --- | --- | --- | --- |
| TV2 | report/SS2/sub3 /22 | eed0caab5ec27c731ec9df318c3556ff97e9dc2d | Báo cáo/sơ đồ/PDF/truy vết/test/AI |
| TV5 | SS5 /21 | 4c9b892d01b2a9c8cb9112f599eeef6e804b96df | Có bài; thiếu ảnh chuẩn, giao tiếp chưa đủ kiểu, xác nhận/AI chưa đầy đủ |
| TV6 | TV6/sub3 /23 | 5ff99f8dff676b3212b00fd4245ce6a4beb592b3 | Có bài và truy vết17 UC; nhiều nhận định implementation/test vượt bằng chứng |
| TV7 | feature/2011710-ss7-usecase /20 | 3ee6c9ee3de08b5c0a7b58a620644b1c3c2f0ed2 | Đã sửa theo review03/11, có deployment chung; còn chờ xác nhận |
| TV1/3/4 | main | 9d9bca60215f24afbe79ea142cd791aaf08b2791 | SS1/SS3/SS4 chỉ là khung, chưa có thiết kế hoàn chỉnh |

## Phát hiện và xử lý trong revision tích hợp

| ID | Mức | Phát hiện / bằng chứng | Cách xử lý và kết quả |
| --- | --- | --- | --- |
| S3-01 | Blocker | SS1/SS3/SS4 REPORT_SUB3.md có22 ô CHƯA ĐIỀN mỗi bản; class diagram chỉ note DRAFT | Bổ sung lớp/thuộc tính/phương thức/ràng buộc/code mapping, class diagram, catalog, truy vết, test thiết kế và khai báo nguồn bổ sung; không ký thay tác giả |
| S3-02 | Blocker | shared/implementation.puml và system_classes.puml chỉ khung10 dòng | Vẽ module hiện có và tổng quan lớp mục tiêu từ quyền sở hữu, tách rõ triển khai/đề xuất; đưa vào phụ lục chung |
| S3-03 | Major | SS2 PersonalVehicle kế thừa lớp gộp User/Vehicle; projection Hub chưa ghi rõ | Tách User và Vehicle, inheritance chỉ Vehicle và association owner User; Hub shared projection |
| S3-04 | Major | SS5 class_diagram không đuôi ảnh; service/billing signatures thiếu kiểu/trả về | Chuẩn hóa PNG/SVG từ nguồn; typed signatures đối chiếu AST core hoặc hợp đồng TV1/TV5; bổ sung catalog mọi phương thức |
| S3-05 | Blocker | SS6 sơ đồ có nhiều method hơn8 mô tả: render/get_current_preview/adapter/engine; service/package/config giả định được vẽ như code thật | Rút về thiết kế có trách nhiệm rõ, mô tả mọi method; view implementation chỉ code hiện có và các service đề xuất vẽ riêng. Bỏ core.services/core.domain và constants không tồn tại |
| S3-06 | Major | SS6 SimulationPreview thiếu charging_effects/summary, tự dùng metrics thay schema chung | Khôi phục trường tối thiểu, adapter metrics->summary, giải thích DTO chung SS6/SS7; đồng bộ guidance và shared contracts |
| S3-07 | Major | SS6 ghi7/7 PASS gồm SimulationCoordinator class chưa tồn tại; không có script tương ứng trong bàn giao | Thay bằng test core/UI có nguồn/log49 case; các ca coordinator/transaction mới DESIGNED; không giữ PASS như bằng chứng service đã chạy |
| S3-08 | Major | Truy vết chung dùng US/FR sai vị trí, chỉ SS6 COMPLETE; một số đường dẫn SS4 tự gắn tên tác giả không tồn tại | Xây manifest17 UC đối chiếu SRS từng ID, dùng đúng source paths từ Sub2 và tên test hiện có; không đổi số UC/ID và không kế thừa VERIFIED Sub2 |
| S3-09 | Major | SS7 method simulate_port_failure được mô tả nhưng không liệt kê chữ ký trong class box; quan hệ failure_scenario có thể bị hiểu là field mới | Thêm chữ ký core đúng, đổi thành dependency bối cảnh, catalog3 method, ghi INT08 thuộc TV6, INT10 dùng chung |
| S3-10 | Major | Báo cáo có chỗ chỉ dẫn puml, PDF cũ không bảo đảm có hình/phụ lục của nguồn đã sửa | Nhúng hai view chung/class diagram và catalog/trace/test/AI vào build PDF revision; bỏ đầu ra cũ trùng vị trí khỏi bộ chuẩn, lưu bản trước trong lịch sử Git |
| S3-11 | Major | Các dấu SELF_CHECKED/FINAL cũ được dùng sau sửa nội dung; khai báo AI TV5 còn khung | Ghi revision và chờ chủ sở hữu xác nhận lại; khai báo AI đợt tổng hợp thực tế, không bịa model/hội thoại lịch sử hoặc biên nhận LMS |
| S3-12 | Major | SRS implementation flags mô tả gate/SSO/IoT, doanh thu, charging quá mức prototype | Thêm đối chiếu hiện trạng trong nguồn SRS, giữ nguyên yêu cầu/ID; báo cáo phân biệt mục tiêu thiết kế và giới hạn prototype |

## Đánh giá từng phần sau hiệu chỉnh

- SS1: thiết kế Booking/User/Vehicle và tài chính reference/charge/key; nêu đúng TTL30 phút, PIN4 chữ số trong core, thiếu km và quyền ở service; không nhận các service chưa viết là implemented.
- SS2: giữ nội dung chi tiết bàn giao, sửa inheritance; TTL từ giờ đến, ownership/capacity/deposit/ChargingService/BillingService được đối chiếu; parking per-visit, tariff theo checkout và barrier mock là chênh lệch rõ.
- SS3: chuẩn hóa Hub và snapshot, occupancy70/85/100, tách held/debt khỏi collected; thiết kế tránh lấy cổng offline làm active power. Dashboard hiện còn hạn chế ghi trong open_issues.
- SS4: thiết kế vòng đời điều chuyển/sự cố, capacity/hold/ownership và idempotency, nêu logic hiện nằm UI; thiết kế resolve không đưa xe AVAILABLE khi còn binding.
- SS5: giữ công thức score/tie/power/grace thực tế, không tuyên bố có weighting giá điện/thời gian chờ tăng điểm; service request/bill/port failure là đề xuất, không thu trùng qua SS2 theo thiết kế.
- SS6: đủ24 giờ là đầu vào tường minh của thiết kế; core/UI hiện mặc định12. Deepcopy có thật, coordinator/DTO/atomic cross-SS là mục tiêu; không có mô hình doanh thu US21 đang chạy.
- SS7: giữ mô tả prototype sự cố số đếm, routing chưa lọc OFFLINE chuẩn, booking do TV1 sau xác nhận; Deployment view chung dùng RAM/session, không giả định backend hoặc IoT thật.

## Kiểm tra và giới hạn

Kết quả tự động trong `docs/audit/submission_3/review_20261106/`: pytest baseline, PlantUML syntax/render, validator UC/path/method và PDF QA. Kết quả validator chỉ chứng minh tính đầy đủ/cấu trúc/đường dẫn, không tự chứng minh mọi quyết định thiết kế đúng hoặc chức năng mục tiêu đã chạy.

Không sửa mã nguồn MVP trong đợt tích hợp tài liệu này. Các chênh lệch code cần thay đổi hành vi được ghi công khai trong open_issues và kế hoạch; bản thiết kế sửa mô tả/giải pháp thay vì âm thầm tuyên bố đã triển khai. Chủ sở hữu phải rà soát nội dung sau hỗ trợ AI và xác nhận PDF trước nộp. Không có bằng chứng nộp LMS.
