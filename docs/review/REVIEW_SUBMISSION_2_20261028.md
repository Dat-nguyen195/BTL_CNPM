# Ôn báo cáo Submission 2 — Leader và SS1

**Người chuẩn bị:** Nguyễn Thành Đạt — Leader/PM, phụ trách SS1.  
**Ngày review:** 28/10/2026. **Buổi báo cáo:** 29/10/2026.  
**Baseline kiểm tra:** commit `9d9bca6`, báo cáo PDF 72 trang. Đây là ghi nhận review và tài liệu ôn tập; không thay đổi code hay nội dung bản nộp.

## 1. Kết luận và phạm vi kiểm tra

Hồ sơ có các loại sản phẩm mà Submission 2 yêu cầu: UI mockup ở cấp nhóm, sequence và activity ở cấp cá nhân; có thêm state-chart bonus. Đã có 17 nguồn sequence, 17 nguồn activity, 11 nguồn state-chart và 1 nguồn use-case bổ sung. Tổng 46 nguồn canonical cùng 8 panel báo cáo được kiểm tra cú pháp. Đủ số lượng không tự chứng minh các sơ đồ đúng ngữ nghĩa.

Đề chính thức, trang PDF 5: [BTL_SoftwareEngineering_HK261_v1.pdf](../../../BTL_SoftwareEngineering_HK261_v1.pdf). Class diagram, deployment và mô tả method thuộc Submission 3. Đề cũng cho phép dữ liệu mô phỏng; không bắt buộc hiện thực cơ sở dữ liệu cho MVP.

Bản PDF trong `docs/report/submission_2/`, bản xuất trong `output/pdf/` và PDF trong ZIP hiện khớp nhau. Manifest của ZIP được kiểm tra. Bộ test hiện có chạy đạt **49/49**. Tuy nhiên, thao tác đầy đủ trên UI SS1 tái hiện được lỗi hóa đơn mà bộ test chưa phát hiện. Vì vậy chưa thể kết luận demo SS1 đã sẵn sàng chỉ dựa vào kết quả test.

## 2. Phát hiện cần ưu tiên

P1/P2 dưới đây là mức ưu tiên xử lý trong lần review này, không phải điểm môn học hay phân loại MoSCoW.

### R1 — P1: Trả xe gây lỗi hiển thị hóa đơn

- Vị trí: `src/components/student_booking.py:331`; schema thực tế ở `src/core/billing.py:215`.
- Tái hiện bằng Streamlit AppTest: Reset → đặt xe không voucher, giữ chỗ KTX Khu B → nhận bằng PIN → nhập 45 phút → hoàn tất trả xe.
- Kết quả thực tế: `KeyError: 'free_minutes_applied'`. Booking đã `COMPLETED`, ví còn 135.000đ, cọc bằng 0 và hóa đơn lưu trong phiên có phí 15.000đ.
- Nguyên nhân: UI đọc `free_minutes_applied`, `gross_rental_fee`, `voucher_discount`, `final_cost`, `refund_amount`, `deducted_from_available`; service hiện trả về `free_minutes`, `base_fee`, `discount`, `total_fee`, `deposit_released` cùng các trường khác.
- Cần xử lý: thống nhất hợp đồng dữ liệu hóa đơn giữa service và UI, bao gồm dữ liệu hoàn dư/thu thêm. Chỉ đổi tên trường đầu tiên chưa giải quyết hết lỗi. Bổ sung kiểm thử đi qua chính nút trả xe và xác nhận không có exception.
- Tác động: lỗi xảy ra sau khi giao dịch đã cập nhật trạng thái; người dùng thấy lỗi dù chuyến đã kết thúc. Cần xử lý trước khi demo trực tiếp UC_SS1_02.

### R2 — P2: Voucher sai vẫn được giảm giá

- Vị trí: `src/core/booking.py:388`; UI kiểm tra hiển thị tại `src/components/student_booking.py:175`.
- Tái hiện: đặt với `SAIMA123`, nhận xe, trả sau 45 phút.
- Mong đợi: không giảm phí, tổng 15.000đ, hoặc từ chối mã sai rõ ràng.
- Thực tế: giảm 5.000đ, tổng 10.000đ.
- Nguyên nhân: khi tính phí chỉ dùng `bool(voucher_code)`; chuỗi bất kỳ không rỗng được coi là có voucher. Việc UI chỉ hiện thông báo thành công cho mã hợp lệ không bảo vệ logic tính tiền.
- Cần xử lý: xác thực voucher ở tầng nghiệp vụ; kiểm thử mã hợp lệ, sai và để trống.

### R3 — P2: UI mô tả sai thời điểm hoàn cọc

- Vị trí: `src/components/student_booking.py:186`.
- Bảng giá ghi hoàn 100% khi nhận xe/hủy đúng hạn. Thực tế nhận xe vẫn giữ cọc; khi trả mới quyết toán phí và hoàn phần dư.
- Cách giải thích đúng: “Nhận xe bắt đầu chuyến đi, cọc vẫn đang giữ. Trả xe thì quyết toán cọc; hủy hợp lệ trước deadline thì hoàn toàn bộ.”

### R4 — P2: Một số ngữ nghĩa UML còn chưa chặt

- Activity SS1_01, khoảng dòng 35–60: kiểm tra thời hạn nhưng không tách nhánh PIN sai; sau đó dùng fork để cập nhật trạng thái và hiển thị đang di chuyển. Code thực hiện kiểm tra PIN và cập nhật trạng thái trước khi giao diện thông báo. Nên bổ sung guard PIN và biểu diễn thứ tự rõ hơn nếu sơ đồ mô tả hiện thực hiện tại.
- Sequence SS1_03, dòng 33: luôn trả “Hợp lệ (còn hạn)” trước `alt`, nhưng bên dưới vẫn có nhánh hết hạn. Kết quả kiểm tra thời hạn phải dẫn đến các nhánh tương ứng; không xác nhận còn hạn vô điều kiện.
- `st.session_state` trong sơ đồ đang gộp trách nhiệm điều khiển nghiệp vụ và lưu trạng thái. Khi giải thích phải nói đây là cách biểu diễn logic của prototype; các hàm trong `core/` mới thực hiện kiểm tra và điều phối thao tác. Có thể tách lifeline service/state trong lần chỉnh thiết kế tiếp theo.
- 54 nguồn biên dịch được xác nhận cú pháp PlantUML; không phải bằng chứng các nhánh hay quan hệ nhân quả đều đúng UML.

### R5 — P2: Scenario SS1 cũ vẫn lệch với báo cáo/code mới

- File: `docs/diagrams/Use-case detail-scenario/SS1/Usecase scenario/UC_SS1_NguyenThanhDat.md`.
- Dòng 171 ghi trả xe làm chỗ trống tại Hub đích **tăng 1**, trong khi xe đến chiếm chỗ: phải dùng chỗ đã giữ hoặc giảm chỗ trống nếu chưa giữ.
- Dòng 57 còn ghi SoC `>20%`; code và hình mới dùng `>=20%`.
- Một số đoạn còn dùng tên ví cũ `wallet_balance`, `locked_balance`, mô tả geofencing/IoT và Green Points chưa được hiện thực đầy đủ.
- Khi báo cáo cần phân biệt đặc tả mục tiêu với phạm vi prototype. Nếu cập nhật tài liệu phải đối chiếu cả bản Markdown và Word, không chỉ sửa hình/PDF chung.

### R6 — Cần chuẩn bị cách giải thích với vai trò leader

- Bảng thành viên dùng cột “Đóng góp” và ghi 100% cho cả 7 người. Nếu ý nghĩa là hoàn thành phần việc được giao thì tên cột chưa rõ; đây không thể tự động coi là tỷ lệ phân chia đóng góp tổng của cả nhóm.
- US-09 còn kỳ vọng tính phí gửi xe theo giờ, trong khi chính sách prototype hiện dùng phí theo lượt. Đây là giới hạn đã có ghi chú trong `docs/policies/submission_2.md`; không nên gọi VERIFIED là đáp ứng mọi câu chữ của yêu cầu.
- Không tuyên bố đã có xác thực SSO, phân quyền người dùng thật, phần cứng IoT hay bảo đảm 500 người đồng thời. Các con số NFR là mục tiêu khi chưa có phép đo tương ứng.

## 3. Leader cần trình bày điều gì?

### Mở đầu khoảng một phút

> “Nhóm em xây dựng Smart E-Mobility Hub để quản lý xe điện, chỗ đỗ và tài nguyên sạc trong khu đô thị ĐHQG-HCM. Nhóm chia thành bảy phân hệ, mỗi thành viên phụ trách một phân hệ. Trong Submission 2, nhóm thực hiện UI mockup, sequence và activity cho 17 use case, kèm state-chart bonus. Prototype dùng Python/Streamlit và dữ liệu mô phỏng để minh họa các luồng tương tác. Em phụ trách SS1 và điều phối việc tích hợp, thống nhất chính sách, trạng thái và báo cáo ở cấp nhóm.”

Câu cuối phải điều chỉnh đúng công việc cá nhân thực sự đã làm. Không khẳng định đã kiểm tra từng phần của thành viên nếu chưa thực hiện.

### Bảy phân hệ trong một bảng

| SS | Thành viên | Nội dung phải giải thích được |
|---|---|---|
| SS1 | Nguyễn Thành Đạt | Đặt, nhận, trả, hủy xe dùng chung và quyết toán |
| SS2 | Nguyễn Anh Tài | Đăng ký xe cá nhân, đặt chỗ, check-in/out và phí dịch vụ |
| SS3 | Phạm Tiến Đạt | Đọc trạng thái Hub, cảnh báo chiếm dụng, booking và doanh thu |
| SS4 | Đặng Hoàng Quý Nhân | Điều chuyển xe, báo cáo và vòng đời xử lý sự cố phương tiện |
| SS5 | Dương Đăng Khoa | Xếp hàng sạc theo điểm ưu tiên và giới hạn công suất |
| SS6 | Hoàng Văn Tấn | Mô phỏng tăng nhu cầu và hàng đợi dự báo |
| SS7 | Nguyễn Trung Nguyên | Mô phỏng lỗi hạ tầng và gợi ý Hub thay thế |

### Kiến trúc cần nhớ

`app.py` khởi tạo trạng thái, quét lượt hết hạn và chọn phân hệ → `components/` nhận thao tác/hiển thị → `core/` kiểm tra và xử lý → cập nhật `st.session_state` → giao diện chạy lại.

Đây là một ứng dụng Python/Streamlit chia module. Không có bảy microservice hay backend database đang chạy riêng. Dữ liệu Hub ban đầu đến từ JSON mẫu. Cùng một phiên sử dụng trạng thái chung nên SS3 đọc được dữ liệu do SS1/SS2 thay đổi; chưa có cơ sở dữ liệu chia sẻ và transaction đa người dùng.

### Các mối nối quan trọng

- SS1 tạo booking, cập nhật xe, chỗ đích và ví; SS3 đọc để giám sát.
- SS1 gặp Hub trả đầy thì dùng chức năng gợi ý Hub thay thế; việc chuyển giữ chỗ do nghiệp vụ booking thực hiện khi người dùng chọn.
- SS4 điều chuyển xe làm thay đổi xe hiện diện và sức chứa hai Hub.
- SS2 gửi nhu cầu sạc đến SS5; kết quả sạc liên quan hóa đơn dịch vụ.
- SS6/SS7 có preview mô phỏng; cần phân biệt xem trước và Apply vào trạng thái phiên.

### Những con số có thể dùng

- 7 phân hệ; 30 user story; 23 functional requirement; 17 use case canonical.
- 27 US mang nhãn VERIFIED, 3 US PARTIAL trong ma trận hiện có.
- 108/119 = 90,76% là tỷ lệ xác thực theo trọng số **nội bộ**. MoSCoW chỉ là phân nhóm ưu tiên; không tự quy định công thức hay trọng số này.
- Ba PARTIAL đã công khai: US-06 thiếu quãng đường; US-12 thiếu xác thực đầy đủ hành trình thanh toán riêng của nhân viên; US-21 thiếu mô hình doanh thu biến động.
- 49 test đạt chỉ xác nhận các test đã chạy. Lỗi UI hóa đơn tái hiện trong review là ví dụ về khoảng trống độ bao phủ.

## 4. SS1 phải nắm ở mức giải thích được dữ liệu thay đổi

### UC_SS1_01 — Đặt và nhận xe

1. Sinh viên mẫu chọn Hub và xe. UI lọc xe dùng chung `AVAILABLE`, pin tối thiểu 20%.
2. Core kiểm tra chưa có booking đang hoạt động, xe/pin và Hub hợp lệ, ví đủ 50.000đ, không có nợ chưa trả.
3. Khóa cọc: `balance -= 50.000`, `held_deposit += 50.000`. Xe/booking ở `RESERVED`; sinh PIN và `expires_at = created_at + 30 phút`.
4. Nếu chọn Hub đích trước: `available_slots -= 1`, `destination_holds += 1` tại Hub đích.
5. Nhận xe: kiểm tra còn hạn và đúng PIN → xe/booking `IN_USE`, ghi giờ nhận, tăng chỗ trống Hub đi một chỗ. Cọc chưa hoàn.

Nhận xe khác đặt xe ở việc xe thực sự rời Hub và thời gian thuê bắt đầu. Chưa nhận thì chưa tính thời gian chuyến đi.

### UC_SS1_02 — Trả xe và quyết toán

1. Booking phải đang `IN_USE`.
2. Hub nhận phải có chỗ hợp lệ: chỗ đã giữ cho chuyến hoặc chỗ trống còn lại.
3. Trả đúng Hub đã giữ: giảm `destination_holds`, không trừ chỗ trống lần hai. Trả Hub khác: giải phóng giữ chỗ cũ và tiêu thụ chỗ tại Hub thực nhận.
4. Chuyển xe đến Hub trả; pin còn >=20% thì `AVAILABLE`, dưới 20% thì code gán `CHARGING`. Đừng khẳng định chỉ gán trạng thái này đã tự chứng minh phiên sạc SS5 được cấp cổng hoàn chỉnh.
5. Tính phí, quyết toán cọc, hoàn dư hoặc thu thêm; nếu thiếu thì ghi nợ. Booking `COMPLETED`, hóa đơn lưu trong phiên.
6. UI hiển thị hóa đơn hiện có lỗi R1; kết quả xử lý core và kết quả hiển thị UI phải được đánh giá riêng.

### UC_SS1_03 — Hủy và no-show

- `RESERVED` và chưa đến deadline: `CANCELLED`, xe về `AVAILABLE`, hoàn 50.000đ, giải phóng chỗ đích đã giữ.
- Tại hoặc sau deadline mà chưa nhận: `EXPIRED`, phạt 10.000đ, hoàn 40.000đ, giải phóng xe/chỗ đích.
- Đã `IN_USE` thì phải trả xe, không hủy booking theo luồng này.
- Quét hết hạn dùng đồng hồ mô phỏng và được gọi khi ứng dụng chạy lại; hiện không có cron tự chạy độc lập khi người dùng không thao tác.

### Phân biệt trạng thái xe và booking

| Sự kiện | Xe | Booking |
|---|---|---|
| Đặt thành công | RESERVED | RESERVED |
| Nhận thành công | IN_USE | IN_USE |
| Hủy trước hạn | AVAILABLE | CANCELLED |
| Không nhận đúng hạn | AVAILABLE | EXPIRED |
| Trả thành công | AVAILABLE hoặc CHARGING | COMPLETED |

### Tài chính và bảo toàn sức chứa

```text
Phút tính phí = max(0, thời lượng − 30 − phút miễn phí điều hướng)
Phí gộp = phút tính phí × 1.000đ
Phí cuối = max(0, phí gộp − giảm giá hợp lệ)

available_slots + xe hiện diện + destination_holds
                + background_occupied = total_slots
```

Ưu đãi điều hướng là 15 phút, cộng một lần. Voucher hợp lệ trong chính sách hiện giảm tối đa 5.000đ; code xác thực voucher hiện còn lỗi R2.

| Tình huống, ví đầu 150.000đ | Phí đúng | Số dư cuối đúng | Nợ |
|---|---:|---:|---:|
| Thuê 25 phút, không voucher | 0đ | 150.000đ | 0đ |
| Thuê 45 phút, không voucher | 15.000đ | 135.000đ | 0đ |
| Thuê 45 phút, voucher hợp lệ | 10.000đ | 140.000đ | 0đ |
| Thuê 100 phút, không voucher | 70.000đ | 80.000đ | 0đ |
| Thuê 200 phút, không voucher | 170.000đ | 0đ | 20.000đ |
| Hủy trước deadline | 0đ | 150.000đ | 0đ |
| Không đến nhận đúng hạn | 10.000đ | 140.000đ | 0đ |

Tiền cọc đang giữ chưa phải doanh thu. Khi còn nợ thì chặn đặt lượt mới. Giá trị trong bảng là kết quả nghiệp vụ mong đợi, không xác nhận toàn bộ UI đã chạy thành công.

## 5. Đọc sơ đồ trước giảng viên

| Sơ đồ | Câu trả lời cần đưa ra |
|---|---|
| Sequence | Ai gọi ai, theo thứ tự nào, dữ liệu phản hồi là gì, điều kiện của mỗi nhánh alt |
| Activity | Trình tự thao tác, bên chịu trách nhiệm trong swimlane, guard rẽ nhánh, vòng lặp, điểm kết thúc |
| State-chart | Đối tượng nào đang được mô tả; sự kiện và điều kiện nào đổi trạng thái |

Ký hiệu activity: chấm đặc là bắt đầu; chấm trong vòng tròn là Activity Final; hình bo góc là hành động; hình thoi là decision/merge; thanh đậm là fork/join. Fork là song song; hai nhánh thay thế nhau phải dùng decision. Connector A nối hai phần SS1_02, không bắt đầu một use case mới.

Trong sequence, activation là khoảng đối tượng xử lý; mũi tên liền cho lời gọi, nét đứt cho phản hồi theo quy ước đang dùng. Lifeline SSO/IoT/Wallet mô tả trách nhiệm thiết kế; prototype hiện dùng dữ liệu và thao tác mô phỏng thay các tích hợp thật.

## 6. Vị trí mở nhanh trong PDF 72 trang

Các số dưới là **trang PDF**, không phải số trang in ở chân trang.

| Trang PDF | Nội dung |
|---:|---|
| 9 | Tổng quan UI và bảng tỷ lệ xác thực |
| 12 | UI SS1 |
| 23–24 | Sequence đặt/nhận và bảng thông điệp |
| 25 | Sequence trả/quyết toán |
| 26 | Sequence hủy/no-show |
| 48 | Chú giải ký hiệu UML |
| 49 | Activity đặt/nhận |
| 50–51 | Activity trả/quyết toán, nối A |
| 52 | Activity hủy/no-show |
| 66–67 | State-chart xe và bảng chuyển trạng thái |

## 7. Kịch bản nói khoảng 7 phút

1. **0:00–1:00:** Mục tiêu hệ thống, 7 phân hệ và sản phẩm Sub2.
2. **1:00–2:00:** Kiến trúc module, trạng thái chung, tích hợp đang mô phỏng và ba PARTIAL.
3. **2:00–3:00:** SS1_01: vì sao tách đặt/nhận, điều kiện pin/ví/PIN/thời hạn.
4. **3:00–4:15:** SS1_02: chỗ đích đã giữ, phí 45 phút, quyết toán cọc, dư nợ.
5. **4:15–5:00:** SS1_03: hủy trước hạn và no-show tại deadline.
6. **5:00–6:00:** Chọn một sequence và một activity để giải thích guard, nhánh và trạng thái.
7. **6:00–7:00:** Bằng chứng kiểm thử, lỗi còn tồn tại và bài học về thống nhất hợp đồng dữ liệu UI–service, kiểm thử đầy đủ luồng người dùng.

Nếu demo trực tiếp: ưu tiên sửa R1 trước; kiểm tra lại luồng đầy đủ bằng thao tác UI. Không gọi demo hiện tại là hoàn chỉnh khi lỗi trả xe còn tái hiện được. Nếu trình bày thiết kế bằng hình thì nêu rõ hành vi thiết kế và giới hạn hiện thực.

## 8. Các câu hỏi nên tập trả lời thành tiếng

**Tại sao chọn Streamlit?**

Để nhóm nhanh xây dựng giao diện tương tác minh họa nghiệp vụ và mô phỏng trên Python. Đổi lại, dữ liệu session và cơ chế chạy lại không thay được backend nhiều người dùng có lưu trữ bền vững.

**Vì sao tách đặt xe và nhận xe?**

Đặt chỉ giữ xe và cọc. Nhận xác nhận người dùng đến Hub, giải phóng chỗ đi và bắt đầu tính thời gian thuê.

**Tại sao phải có destination_holds?**

Để chỗ đã hứa cho xe đến không tiếp tục được coi là chỗ trống. Khi xe tới chỉ chuyển chỗ giữ thành xe hiện diện, tránh trừ chỗ hai lần.

**Hai người cùng đặt một xe thì sao?**

Core kiểm tra lại trạng thái trước khi đổi xe sang RESERVED trong một phiên. Prototype chưa chứng minh giải quyết cạnh tranh giữa nhiều người dùng thật; triển khai thật cần state chung và giao dịch/khóa ở phía server hoặc cơ sở dữ liệu.

**Đúng phút thứ 30 có được nhận hay hủy để hoàn đủ không?**

Không. Khi `now >= expires_at`, lượt chưa nhận hết hạn. Muốn nhận hoặc hủy hoàn đủ phải trước deadline.

**Pin đúng 20% có đặt được không?**

Có, nếu xe AVAILABLE và các điều kiện khác hợp lệ. Code từ chối khi pin dưới 20%.

**Vì sao thiếu tiền vẫn cho trả xe?**

Để kết thúc việc sử dụng xe và ghi nhận xe đã về Hub. Phần thiếu được lưu thành nợ, chặn đặt mới; không xóa mất khoản phải thu.

**49 test đều đạt, vì sao vẫn có lỗi?**

Các test chỉ bao phủ những trường hợp đã viết. Bộ hiện tại kiểm thử đặt trên UI và quyết toán qua core, chưa đi qua đủ màn hình trả xe SS1 nên bỏ sót schema hóa đơn lệch. Review đã tái hiện lỗi bằng AppTest.

**90,76% có phải điểm môn học hay công thức MoSCoW?**

Không. Đó là 108/119 trọng số nội bộ của các US được gắn VERIFIED. MoSCoW phân loại ưu tiên; các trọng số và cách tổng hợp này do nhóm bổ sung.

**Điều hướng có tìm đường giao thông thật không?**

Hiện lọc Hub đủ chỗ rồi sắp theo khoảng cách Haversine từ tọa độ mẫu. Chưa tính đường đi trên mạng đường bộ, thời gian giao thông hoặc GPS thật.

**Sạc thông minh có bảo đảm nghiệm tối ưu không?**

Thuật toán hiện dùng điểm ưu tiên theo pin/booking và ràng buộc công suất, kèm quy tắc phá hòa. Đây là heuristic minh bạch; không nên khẳng định đã chứng minh tối ưu toàn cục hay có mô hình AI học nhu cầu.

**Đăng nhập/phân quyền đã có chưa?**

Chưa có form đăng nhập và VNU-SSO thật. Code tạo người dùng mẫu; lựa chọn phân hệ ở sidebar chưa phải cơ chế bảo vệ phân quyền.

**AI đã tham gia ở đâu?**

Khai báo đúng công cụ và phạm vi đã dùng: gợi ý, code, tài liệu hoặc hình. Nêu phần bản thân đã đọc, kiểm tra, chỉnh sửa và quyết định; không học thuộc một lời khẳng định kiểm chứng mà mình chưa thực hiện.

## 9. Thứ tự chuẩn bị tối nay

1. Ưu tiên xử lý lỗi hóa đơn và xác thực voucher, rồi kiểm thử trực tiếp lại SS1 trước buổi demo.
2. Đọc ba sequence và ba activity SS1; đánh dấu PIN sai, deadline, chỗ đã giữ, tiền cọc và hai loại trạng thái.
3. Tập phần leader trong hai phút: bài toán, chia phân hệ, kiến trúc, bằng chứng và giới hạn.
4. Tập giải thích ví dụ 45 phút bằng số tiền, không chỉ đọc tên hàm.
5. Chuẩn bị PDF hiện tại và môi trường chạy; reset trước mỗi kịch bản độc lập. Ô thời lượng ở tab Trả xe quyết định thời lượng mô phỏng; nút +15 phút dùng để thử deadline giữ chỗ.

Lệnh chạy từ thư mục `smart-emobility-hub`:

```bash
venv/bin/python -m streamlit run src/app.py
```

Mở `http://localhost:8501`. Lệnh kiểm tra đầy đủ trong môi trường không có X11:

```bash
JAVA_TOOL_OPTIONS=-Djava.awt.headless=true venv/bin/python scripts/validate_submission_2.py
```

Bằng chứng review ngày 28/10 nằm tại `docs/audit/submission_2/review_20261028/`. Hai ca tái hiện bổ sung là kiểm tra có mục tiêu ngoài bộ 49 test hiện có.
