# Kế hoạch hoàn thiện Smart E-Mobility Hub — Submission 1–3

Chạy từ thư mục gốc của repo chứa README.md, src/, tests/ và scripts/. Đây là kế hoạch thực hiện. Các ô đánh dấu ban đầu đều để trống. Chỉ đánh dấu khi có bằng chứng thu được trên phiên bản đang làm.

## Mục tiêu và nguồn đối chiếu

- **Mốc A — BTL và demo local.** Cài mới được, hoàn thiện các luồng SS1–SS7, thiết kế và hiện thực xử lý một sự kiện IoT giả lập, đồng bộ yêu cầu chung → UML → phương thức → test.
- **Mốc B — IoT real-time, mục tiêu điểm cộng 0,25.** Bộ phát tự gửi sự kiện, dashboard đang mở tự cập nhật và các phân hệ dùng được trạng thái mới.
- **Mốc C — Server của nhóm, mục tiêu cộng thêm 0,25.** Chạy ứng dụng cùng luồng real-time trên server của nhóm và kiểm chứng từ máy khác.
- Nguồn chính: đề BTL_SoftwareEngineering_HK261_v1.pdf ở thư mục cha, trang 3–6; FAQ giảng viên về IoT và triển khai do người dùng cung cấp; docs/requirements-analysis.md; docs/policies/submission_2.md; docs/traceability/submission_{2,3}.json; các sơ đồ và tài liệu thiết kế chung. Dữ liệu mẫu bên ngoài và Azure là lựa chọn tham khảo.
- **Ngoài phạm vi:** scenario chi tiết theo người phụ trách; tài liệu cá nhân và định dạng DOC/DOCX/PDF; khai báo AI, bằng chứng làm việc nhóm; hạn, quy cách tải lên và trạng thái nộp bài. Khi một công cụ hiện kiểm cả các mục này, giữ nguyên chức năng kiểm tra hiện có và cung cấp chế độ kiểm tra kỹ thuật riêng nếu cần. Không yêu cầu các đầu việc ngoài phạm vi để hoàn tất mốc A hoặc B.

## 1. Thiết lập bản chạy tái lập

- [x] **1.1 · F01.** Đọc git status/diff trước khi sửa. Tại mốc review a959f44, working tree đang xóa requirements.txt, requirements-tested.txt và requirements-dev.txt. Đối chiếu HEAD, metadata hiện hành và môi trường đã chạy được để cung cấp bộ phụ thuộc phù hợp. Nếu repo đã chuyển sang cơ chế quản lý phụ thuộc khác, dùng cơ chế hiện hành. Sửa tên thư mục sau lệnh clone và hướng dẫn cài/chạy trong README.md.
- [x] **1.2 · F03/F11, phần kỹ thuật.** Đồng bộ đường dẫn đến nguồn thiết kế chung, hướng dẫn demo và checksum được README sử dụng. Chạy validator S2 và phần kỹ thuật của S3. Chỉ sửa đường dẫn hoặc logic thuộc phạm vi; giữ khả năng bắt lỗi UC thiếu, sơ đồ thiếu, mã tham chiếu sai và method thiếu mô tả.
- [x] **1.3 · Baseline.** Ghi phiên bản Python, lệnh cài/chạy, kết quả pytest và validator. Bộ 49 test đã pass ở lần review trước là mốc lịch sử. Trước mỗi bản sửa F05–F09, thêm hoặc chạy ca hồi quy thể hiện lỗi trên bản đang làm.
- **Nghiệm thu:** tạo venv sạch, làm theo đúng README, mở app và kiểm tra bảy màn hình. Nếu môi trường chặn mạng hoặc socket, ghi riêng bước bị chặn và chạy AppTest cùng các kiểm tra độc lập.

## 2. Sửa nghiệp vụ và tính nhất quán

| Hoàn tất | ID | Công việc và vị trí bắt đầu | Ca nghiệm thu |
|---|---|---|---|
| [x] | 2.1 · F08 | Sửa cách phân loại cổng rảnh, đang dùng, offline trong src/core/simulator.py và SS7. Loại các cổng đã hỏng khỏi năng lực có thể cấp hoặc hỏng thêm. | 2 cổng rảnh → hỏng 1 → hỏng 1: còn 0 rảnh, 0 đang dùng, 2 offline. Lần thứ ba không tăng offline. Kiểm tra cả sự cố khi có phiên đang sạc. |
| [x] | 2.2 · F06 | Đồng bộ check-in SS2 với cơ chế cấp cổng SS5 trong core/personal_ev.py, core/scheduler.py và UI tương ứng. Tách yêu cầu sạc, chờ sạc và phiên thực sự được cấp cổng. | Đặt lúc còn cổng, tới khi cổng cuối đã offline: vẫn check-in chỗ đỗ, xe chờ sạc. Cấp lại cổng chỉ tạo một phiên. |
| [x] | 2.3 · F05 | Sửa checkout SS2 và chính sách billing. Chỉ tính điện cho phiên có sử dụng; chỉ tính overstay khi xe thực sự giữ cổng sau ân hạn. Dùng biểu phí đỗ theo giờ của US-09. | Xe chỉ đỗ có phí điện và chiếm cổng bằng 0. Kiểm tra trước/đúng/sau 15 phút ân hạn, hóa đơn qua khung giá, ví thiếu tiền, checkout lặp. |
| [x] | 2.4 · F09 | Kiểm tra ownership trong core/booking.py trước khi giữ xe, cọc hoặc chỗ đích. Đối chiếu cách chuẩn hóa seed cũ. | Gọi core với xe PERSONAL phải bị từ chối và không đổi ví, cọc, xe, chỗ. Xe SHARED hợp lệ vẫn thuê được. |
| [x] | 2.5 · F07 | Tách ID xe vận hành khỏi seed thống kê trong core/simulator.py và SS6. | Apply hai đợt × 5 người ở hub đủ chỗ tạo 10 ID khác nhau. Cùng seed và trạng thái đầu tái lập được thống kê. Hủy preview không thêm xe. |
| [x] | 2.6 · SS4/SS6/SS7 | Kiểm tra lại đích, chỗ giữ và xe khi nhận điều phối. Bảo toàn version khi thay đổi hub/cổng/xe; từ chối Apply cũ hoặc lặp. | Sau một thay đổi trạng thái, preview cũ không ghi đè booking, ví, cổng hoặc xe. Lệnh điều phối chỉ hoàn tất sau khi xe đã thực sự vào đích. |

**Quyết định giá:** tra nguồn có thẩm quyền cho đơn giá đỗ theo giờ và cách làm tròn. Nếu chưa có, cô lập biểu phí thành cấu hình, dùng giá giả định có nhãn rõ ràng trong test, ghi quyết định cần nhóm chốt và tiếp tục các việc độc lập. Mức 5.000đ/lượt trong prototype cũ không xác lập giá 5.000đ/giờ.

## 3. IoT giả lập xuyên suốt S1–S3

Dùng một luồng làm tiêu chuẩn xuyên suốt: bộ phát gửi sự kiện cổng sạc của một Hub chuyển sang OFFLINE.

- [x] **3.1 · S1.** Cập nhật SRS và use-case diagram toàn hệ thống: actor ngoài hệ thống, mục tiêu nghiệp vụ, bên nhận thông báo và kết quả quan sát được.
- [x] **3.2 · S2.** Cập nhật hoặc bổ sung sequence/activity chung cho bản tin hợp lệ, trùng ID, sai hub/cổng, đến muộn. Thể hiện lúc hệ thống xác nhận, đổi trạng thái và phát cảnh báo.
- [x] **3.3 · S3.** Cập nhật class diagram, mô tả phương thức và implementation/deployment view chung. Tối thiểu xác định event_id, hub_id, port_id, event_type, occurred_at và received_at. Chốt cách ánh xạ định danh cổng vào seed hiện chỉ đếm số lượng. Ghi rõ trách nhiệm kiểm tra, chống xử lý trùng và xử lý sự kiện cũ.
- [x] **3.4 · Mốc A.** Cho bộ phát local gửi một bản tin vào đúng điểm tiếp nhận. SS3 hiển thị mã sự kiện, thời gian, hub/cổng, trước/sau và cảnh báo. Gửi trùng hoặc sai đích không gây thêm tác động.
- [ ] **3.5 · Mốc B.** Chạy bộ phát định kỳ độc lập với UI. Chọn cách chia sẻ các sự kiện và trạng thái cổng giữa bộ phát với các phiên Streamlit. Giữ booking/ví trong đúng phạm vi người dùng. Mở hai cửa sổ: cả hai nhận cùng event_id và trạng thái mới mà không cần nhấn Refresh. Ghi log và cách chạy/dừng bộ phát.
- [x] **3.6 · What-if.** Dùng chung quy tắc đổi trạng thái cổng: IoT cập nhật vận hành, simulator thực hiện trên bản sao. Tạo preview lúc còn 2 cổng; nhận tin hỏng 1; SS3 còn 1, SS5 không cấp cổng hỏng, SS7 từ chối preview cũ.

## 4. Hoàn thiện KPI, yêu cầu còn thiếu và truy vết

- [x] **4.1 · F10, SS3/SS5.** Đối soát khoản thực thu thuê xe, gửi đỗ và sạc. Tách cọc, hoàn, nợ và dự báo. Tính công suất từ phiên đang sạc và cấu hình cổng. Ca kiểm tra gồm một chuyến thuê, một phiên cá nhân, một khoản nợ và một cổng offline có công suất 0 kW.
- [x] **4.2 · US-06.** Bổ sung quãng đường trên hóa đơn thuê xe, nêu rõ đơn vị và nguồn mô phỏng. Lưu giá trị khi kết thúc chuyến. Đọc lại hóa đơn phải cho cùng kết quả.
- [x] **4.3 · US-12.** Cho operator kiểm tra và xác nhận đúng hóa đơn/phiên sạc; ghi được trạng thái xác nhận. Nhấn lại hoặc rerun không thu tiền hai lần.
- [x] **4.4 · US-21.** Hoàn thiện dự báo 24 giờ gồm tải, thời gian chờ và biến động doanh thu theo giả định công bố. Đối chiếu hai mức nhu cầu. Forecast/preview không tác động ví hoặc doanh thu thực thu.
- [x] **4.5 · F02, tài liệu chung.** Đồng bộ bảng chung S1, SRS, manifest và UML theo bốn mã SS2: _01 đăng ký, _02 đặt chỗ/sạc, _03 check-in, _04 check-out. Giữ truy vết 17 UC; ghi rõ phần thiết kế và phần đã hiện thực. Chỉ sửa các nguồn chung trong phạm vi.
- [ ] **4.6 · NFR.** Đo thời gian từ phát → nhận → hiển thị với cách đo và môi trường cụ thể. Kiểm tra bộ phát dừng/khởi động lại, tiếp nhận sự kiện trùng và hành vi sau khi ứng dụng khởi động lại. Ghi giới hạn thực tế của lưu trữ, phân quyền và tải.

## 5. Kiểm thử toàn hệ thống và bàn giao kỹ thuật

Từ môi trường đã cấu hình theo README, chạy các lệnh phù hợp với phiên bản sau sửa. Điểm bắt đầu ở bản hiện tại:

~~~bash
PYTHONPATH=src venv/bin/python -m pytest -q tests/
JAVA_TOOL_OPTIONS=-Djava.awt.headless=true venv/bin/python scripts/validate_submission_2.py
venv/bin/python -m streamlit run src/app.py
~~~

Ghi thêm lệnh kiểm tra kỹ thuật S3, cú pháp UML, chạy bộ phát và kiểm tra real-time sau khi các entry point được chốt. Đọc cấu hình trước khi chạy; dùng dữ liệu thử nghiệm.

- [ ] **5.1** Đặt/nhận/trả hoặc hủy xe chung, kiểm tra biên giữ 30 phút, hoàn cọc, điều hướng và hóa đơn.
- [ ] **5.2** Xe cá nhân chỉ gửi đỗ: tính đúng phí đỗ, điện và overstay bằng 0, SS1 từ chối thuê xe này.
- [ ] **5.3** Hai xe cần sạc, chỉ còn một cổng: một xe sạc, một xe chờ, SS2/SS3/SS5 thống nhất.
- [ ] **5.4** Để nguyên dashboard, nhận sự cố IoT lúc có preview mở: quan sát cập nhật, cảnh báo, cấp phát và từ chối preview cũ.
- [ ] **5.5** Apply hai đợt Metro Surge rồi điều phối xe: mã duy nhất, chỗ được bảo toàn và đúng xe đến đích.
- [ ] **5.6** Đối soát cuối phiên: tổng thực thu bằng các khoản thực thu trên hóa đơn, phân biệt được nợ, cọc và dự báo.
- **Bàn giao:** ghi lệnh tái lập, kết quả pass/fail, phát hiện còn mở, file liên quan, trạng thái mốc A/B/C. Phân biệt “Đã xác minh khi chạy”, “Đã đối chiếu mã hoặc tài liệu”, “Chưa xác minh”.

## 6. Triển khai lên server của nhóm

- [x] **6.1 · Sau mốc B.** Chuẩn bị cấu hình chạy ứng dụng và bộ phát từ cùng một revision, kèm hướng dẫn khởi động, dừng, đọc log và phục hồi. Dùng hạ tầng và thông tin truy cập do nhóm cung cấp.
- [ ] **6.2 · Mốc C.** Khi có server và quyền triển khai, truy cập từ máy khác, quan sát dashboard tự cập nhật và khớp event_id với log trên server. Nếu thiếu đích triển khai hoặc quyền truy cập, hoàn tất kiểm tra local, ghi chính xác điều kiện còn thiếu và để mở 6.2.

**Thứ tự:** giai đoạn 1 → 2 → 3 → 4 → 5 → 6. Có thể tiếp tục hạng mục độc lập khi vướng đơn giá, socket, mạng hoặc server. Giữ lại các quyết định nghiệp vụ chưa có căn cứ dưới dạng mục chờ xác nhận.

## Nhật ký thực hiện trên working tree

### Giai đoạn 1 — đang dở

- Đã đọc `git status --short`, `git diff --stat`; lúc bắt đầu chỉ có ba requirements bị xóa và `plan.md` chưa theo dõi. Khôi phục riêng ba tệp từ HEAD; không reset/restore hàng loạt. README sửa thư mục clone và thay hai đường dẫn không tồn tại. `scripts/validate_submission_3.py --technical-only` giữ kiểm tra 17 UC, liên kết, test và method nhưng bỏ các kiểm tra cá nhân/khai báo AI ngoài phạm vi; chế độ mặc định vẫn giữ nguyên.
- Baseline Python 3.12.3: `PYTHONPATH=src venv/bin/python -m pytest -q tests/` → 49 passed; `JAVA_TOOL_OPTIONS=-Djava.awt.headless=true venv/bin/python scripts/validate_submission_2.py` → PASS, 54 PlantUML; `venv/bin/python scripts/validate_submission_3.py --technical-only` → PASS (17 UC, 70 method). Chế độ đầy đủ S3 báo thiếu self_check/ai_usage của 7 cá nhân, ngoài phạm vi.
- AppTest baseline mở được 7 màn hình, chưa chứng minh thao tác toàn bộ các luồng. Cài venv sạch `/tmp/smart-emobility-clean-venv` bằng `python3 -m venv` và `pip install -r requirements-tested.txt -r requirements-dev.txt` thành công; chạy pytest trong venv đó: 54 passed, gồm AppTest bảy màn hình. Chưa đánh dấu nghiệm thu toàn giai đoạn 1. Cần tiếp tục đối chiếu mọi đường dẫn/checksum và mở app trong môi trường sạch.

### Giai đoạn 2 — đang dở, chưa nghiệm thu

- F08: test `test_repeated_failures_do_not_count_offline_ports_as_busy` thất bại trước sửa; sau sửa mô phỏng trừ offline khi tính cổng bận và hạn chế số hỏng mới; biểu đồ SS7 tách offline. Chưa đồng bộ phiên sạc đang hoạt động và console SS7, chưa kiểm thử UI sự cố đang sạc.
- F06/F05: test `test_checkin_waits_if_port_fails_after_reservation` thất bại trước sửa; sau sửa xe chờ nếu hết cổng, đưa vào scheduler và cấp qua `allocate_hub_ports`; `test_waiting_personal_vehicle_can_be_allocated_once` đạt. Hóa đơn không tính điện/overstay cho lượt chưa từng cấp cổng. Chưa đạt: định danh cổng, đo năng lượng thực, xử lý rút sạc/overstay và biểu phí đỗ theo giờ. Giá cũ 5.000đ/lượt vẫn là prototype, không phải đơn giá/giờ được phê duyệt; nhóm cần chốt đơn giá và quy tắc làm tròn.
- F09: `test_personal_vehicle_cannot_be_booked_as_shared` thất bại trước sửa và đạt sau sửa; xe PERSONAL bị từ chối trước sweep và thay đổi tiền/xe/chỗ. Seed được chuẩn hóa SHARED. Chưa kiểm tra thao tác UI đầy đủ.
- F07: `test_surge_ids_are_unique_across_previews_from_changed_state` thất bại trước sửa và đạt sau sửa; ID xe dùng UUID độc lập với seed thống kê. Chưa kiểm tra hai lần Apply trên UI, hủy preview và toàn bộ tính tái lập.
- Sau thay đổi: `PYTHONPATH=src venv/bin/python -m pytest -q tests/` → 54 passed; validator S2 chạy lại PASS. `venv/bin/python -m streamlit run src/app.py --server.headless true --server.port 8501` khởi động và `curl -fsS http://localhost:8501/_stcore/health` trả `ok`; test điều hướng AppTest đạt 7 màn hình. Đây là bằng chứng test lõi/hiển thị, không phải nghiệm thu tương tác UI hay A/B.

### Giai đoạn 3–6 — chưa thực hiện

- Chưa có bộ phát IoT độc lập, event_id hoặc phép đo real-time; chưa xác minh A/B. Không dùng các bước mô phỏng hiện có như bằng chứng IoT.
- Còn các mục KPI, truy vết, kiểm thử toàn hệ thống và cấu hình chạy server. Mốc C cần server đích và quyền truy cập từ nhóm; không triển khai khi chưa có.


## Kết quả bổ sung sau review

Các nhật ký phía trên giữ kết quả của đợt trước. Đợt hiện tại đã sửa checkout/rút sạc/sự cố tích hợp, cổng hỏng lặp, ownership và ID xe. Biểu phí giờ mặc định 5.000đ là giả định demo cấu hình được. Thêm điện năng theo mức pin còn thiếu, tích lũy phí điện theo phút qua khung giờ, bảo toàn phí sau rút cổng, xác nhận hóa đơn operator, quãng đường giả lập, forecast mặc định 24h và doanh thu dự kiến, KPI thực thu/công suất phiên.

- Runtime và môi trường clean-venv đã cài trước đó đều chạy **60 test pass**, gồm AppTest bảy màn hình và hồi quy IoT hai observer, rút sạc 30 phút rồi checkout thu 10.000đ, xác nhận hóa đơn không thu lặp.
- Validator S2 PASS cho 54 sơ đồ baseline, S3 technical-only PASS cho 17 UC/70 mục method. Năm sơ đồ bổ sung IoT đã render PNG, source/mô tả ở docs/diagrams/telemetry và docs/current/CURRENT_TECHNICAL_DESIGN.md.
- Bộ phát CLI độc lập ghi hai sự kiện OFFLINE/ONLINE; hai consumer nhận cùng event_id và replay ra offline=0. Độ trễ replay cuối khoảng 0,11 giây trong phép thử cục bộ. Đây là thời gian xử lý feed, chưa là phép đo tự cập nhật trình duyệt.
- Cấu hình Docker Compose parse thành công. Docker daemon từ chối quyền truy cập socket; chưa build image. Lệnh Streamlit trực tiếp bị sandbox chặn socket mạng. Vì vậy giữ mở 1.1, 3.5 và nghiệm thu UI thời gian thực 5.4. AppTest xác minh nhánh fragment nhưng chưa chứng minh callback định kỳ qua trình duyệt thật.
- Mốc A đã bổ sung code/test/tài liệu chung; nghiệm thu trình duyệt còn chờ môi trường cho mở cổng. Mốc B có bộ phát, feed bền và fragment định kỳ, chưa xác minh end-to-end qua trình duyệt. Mốc C có Dockerfile/Compose/hướng dẫn, chưa có server đích và quyền Docker.
- Model hiện dùng port_id theo chỉ số và adapter số lượng cổng; ngắt phiên theo thứ tự tạo tại Hub. Chưa ánh xạ đúng ổ cắm vật lý. Booking/ví vẫn per-session. Giá đỗ chính thức cần nhóm chốt. Các giới hạn này được ghi ở docs/current/REALTIME_DEMO.md.
- Gói mã hiện hành được tạo bởi scripts/package_submission_2.py vào output/submission_2, có manifest hash từng file. PDF trong gói vẫn là tài liệu lịch sử theo phạm vi người dùng đã loại.
