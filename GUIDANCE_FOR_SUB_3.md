# GUIDANCE FOR SUBMISSION 3

> **Cập nhật trạng thái06/11/2026:** phân công và hạn trong bản1.3 là kế hoạch gốc. Bộ nguồn tích hợp hiện đã có đủ7 phần thiết kế; xem docs/review/REVIEW_SUBMISSION_3_20261106.md và docs/report/submission_3/COMPLETION_PLAN.md. Xác nhận tác giả và LMS vẫn chờ thực hiện; không hiểu các ô task ban đầu là tình trạng nguồn hiện tại.

**Dự án:** Smart E-Mobility Hub — BEE BRAVE (Nhóm 7)  
**Môn học:** Công nghệ Phần mềm CO3001 — HK261  
**Trưởng nhóm:** Nguyễn Thành Đạt — 2410709  
**Ngày bắt đầu:** **21/10/2026** — giữ theo kế hoạch ban đầu.  
**Ngày kết thúc / hạn hoàn thành và nộp:** **30/10/2026** (Thứ Sáu).  
**Múi giờ của toàn bộ lịch:** Việt Nam, UTC+7 (Asia/Ho_Chi_Minh).  
**Phiên bản hướng dẫn:** 1.3 — cập nhật ngày 22/10/2026; khớp cấu trúc dự án và trình bày bảng gọn hơn.

> Ngày 30/10 là hạn do trưởng nhóm cung cấp; giờ đóng LMS chưa được xác minh. TV1 kiểm tra giờ đóng, định dạng và cách nộp trên LMS. Thành viên tự sắp xếp công việc trong khoảng bắt đầu–kết thúc; không có lịch bàn giao trung gian hoặc lịch họp cố định trong hướng dẫn này.

> Tài liệu này là kế hoạch giao việc, không phải biên bản xác nhận các thành viên đã nhận hoặc hoàn thành nhiệm vụ. Tất cả checklist ban đầu để trống; chỉ đánh dấu khi có sản phẩm và bằng chứng kiểm tra.

## 1. Mục tiêu và căn cứ thực hiện

### 1.1. Submission 3 phải có gì?

Theo mục **Submission #3 detail** trong [đề bài chính thức](../BTL_SoftwareEngineering_HK261_v1.pdf):

| Nội dung | Mức yêu cầu trong đề | Cách triển khai của nhóm |
| --- | --- | --- |
| Deployment view | Bắt buộc | TV7 tổng hợp sơ đồ triển khai chung; từng người giải thích vị trí phân hệ của mình |
| Development/Implementation view | Bắt buộc | TV3 tổng hợp sơ đồ module, tầng và phụ thuộc; từng người cung cấp ánh xạ mã nguồn |
| Class diagram | Bắt buộc | Mỗi người thiết kế phân hệ cũ; TV3 tổng hợp sơ đồ liên kết cấp hệ thống |
| Method descriptions | Bắt buộc cho **tất cả phương thức có trong class diagram** | Chủ sở hữu lớp tự viết, đối chiếu và chịu trách nhiệm về mô tả |
| Class descriptions | Có trong mô tả tổng quát của Submission 3 | Viết trách nhiệm, thuộc tính, quan hệ và ràng buộc của từng lớp |
| Test case | **Bonus** | Hoàn thành phần bắt buộc trước; tận dụng kiểm thử hiện có và bổ sung trường hợp có giá trị |

Đề nêu bốn tài liệu cá nhân nhưng không ghi nhãn việc nhóm/cá nhân cho từng dòng của Submission 3. **Quy ước tổ chức nội bộ:** cùng dùng một phiên bản kiến trúc chung; mỗi người đưa đủ hai view kiến trúc và thiết kế chi tiết phân hệ mình vào báo cáo cá nhân, ghi rõ người đóng góp cho phần chung. Nếu LMS hoặc giảng viên có hướng dẫn cụ thể khác, TV1 cập nhật cách đóng gói theo hướng dẫn đó.

Các quy định về số lượng test, tên file, tự kiểm tra và cách bố trí thư mục bên dưới là **quy ước nội bộ**, không phải tiêu chí chấm điểm được tự bổ sung vào đề.

### 1.2. Đầu vào phải kế thừa

1. [SRS hiện tại](docs/requirements-analysis.md): yêu cầu chức năng, phi chức năng, user story và quy tắc nghiệp vụ.
2. [Manifest truy vết Submission 2](docs/traceability/submission_2.json): 17 use case hiện hành và người phụ trách.
3. [Scenario và sơ đồ Submission 2](<docs/diagrams/Use-case detail-scenario>): đọc scenario, sequence, activity; dùng state chart nếu có.
4. [Chính sách nghiệp vụ](docs/policies/submission_2.md) và [hằng số thực thi](src/core/policies.py): đối chiếu trước khi ghi thời gian, giá, ngưỡng hoặc đơn vị.
5. Mã nguồn `src/components/`, `src/core/` và kiểm thử `tests/`: bằng chứng cho phần đã triển khai.
6. [Phân công cũ](docs/tasks-assignment.md): chỉ dùng để tham khảo thành viên/MSSV. Một số tên và số lượng use case ở kế hoạch Sub1 đã cũ; dùng manifest hiện tại để chốt phạm vi Sub3.

**Nguyên tắc truy vết:** `US/FR → Use case → thông điệp Sequence/nhánh Activity → lớp → phương thức → test case`.

Không tự đổi mã US, FR hoặc UC. Không coi một lifeline là một lớp một cách máy móc: actor, giao diện ngoài, module và đối tượng miền có vai trò khác nhau. Không cần tạo thêm use case chỉ để tăng số lượng sơ đồ.

### 1.3. Thiết kế phải phản ánh đúng mức triển khai

- Prototype hiện dùng Python/Streamlit, các module nghiệp vụ và dữ liệu trong session. Giải thích đúng vòng đời dữ liệu, rerun và reset của ứng dụng.
- Có thể đề xuất lớp/service để thay thế hàm hoặc dictionary, nhưng phải đánh dấu **đã triển khai**, **thiết kế đề xuất** hoặc **mở rộng tương lai**; ghi ánh xạ đến code hiện có.
- SSO, QR/PIN, IoT và thanh toán mô phỏng phải được thể hiện đúng trạng thái. Không mô tả thành tích hợp sản xuất đã hoạt động.
- Đề không bắt buộc có database. Nếu đưa database, API server, message broker hoặc microservice vào kiến trúc tương lai, tách rõ khỏi deployment hiện tại và giải thích nhu cầu.
- Không bắt buộc viết lại toàn bộ code sang hướng đối tượng trong đợt này. Nếu sửa code để khớp thiết kế, phải kiểm tra hành vi bị ảnh hưởng.

## 2. Phân công tổng thể và quyền sở hữu

### 2.1. Ma trận trách nhiệm

| Thành viên | Phạm vi cá nhân | Phần chung phụ trách |
| --- | --- | --- |
| TV1 — **Nguyễn Thành Đạt — 2410709** | SS1, 3 UC: đặt/nhận, trả/quyết toán, hủy/hết hạn | Chốt kiến trúc, hợp đồng dùng chung, chính sách; theo dõi tiến độ và chuẩn bị nộp |
| TV2 — **Nguyễn Anh Tài — 2413035** | SS2, 4 UC: đăng ký, đặt chỗ, check-in, check-out | Áp dụng hợp đồng tài chính và sạc đã quy định ở mục 2.3 |
| TV3 — **Phạm Tiến Đạt — 2410724** | SS3, 2 UC: dashboard/KPI/doanh thu và cảnh báo | Tổng hợp **Development/Implementation view** và class diagram cấp hệ thống |
| TV4 — **Đặng Hoàng Quý Nhân — 2412401** | SS4, 2 UC: điều chuyển và sự cố phương tiện | Tổng hợp các vấn đề do thành viên tự báo, người phụ trách và trạng thái xử lý |
| TV5 — **Dương Đăng Khoa — 2411589** | SS5, 2 UC: lập lịch sạc và quản lý hàng chờ/phí | Cung cấp chính sách sạc, công suất và hợp đồng phiên sạc cho SS2/SS7 |
| TV6 — **Hoàng Văn Tấn — 2213074** | SS6, 2 UC: Metro Surge và dự báo 24 giờ | Tổng hợp bảng truy vết 17 UC và danh mục test từ bảng cá nhân |
| TV7 — **Nguyễn Trung Nguyên — 2011710** | SS7, 2 UC: sự cố hạ tầng và gợi ý Hub thay thế | Tổng hợp **Deployment view** hiện tại; tự kiểm tra khả năng chạy theo mô tả |

**Mỗi thành viên tự thực hiện, tự kiểm tra, tự sửa lỗi và chịu trách nhiệm về tính đúng đắn, đầy đủ, tiến độ của sản phẩm mình bàn giao.** Mỗi người gửi kèm checklist tự kiểm tra và công khai các giới hạn/vấn đề còn mở. Trưởng nhóm theo dõi tiến độ, tiếp nhận sản phẩm và điều phối phần chung; người tổng hợp hợp nhất đúng phiên bản đã bàn giao. Trách nhiệm nội dung cá nhân vẫn thuộc tác giả.

Các thành viên áp dụng trực tiếp phân công, dữ liệu và giao tiếp đã chốt ở mục 2.2–2.3, tự bảo đảm phần mình tuân thủ. Khi gặp mâu thuẫn với code hoặc yêu cầu, ghi rõ vấn đề và gửi trưởng nhóm bằng tin nhắn/ghi chú; không cần chờ họp để bắt đầu các phần việc độc lập.

### 2.2. Lớp và dữ liệu dùng chung — quyết định áp dụng

**Phân công và quy ước trong mục này đã được chốt cho thiết kế Submission 3.** Mỗi nhóm lớp có đúng một chủ sở hữu; các thành viên khác tham chiếu bản của người đó, không cần tổ chức họp lấy ý kiến trước khi làm. Đây là quyết định thiết kế tài liệu; các lớp chưa có trong code vẫn phải ghi là thiết kế đề xuất.

**Kiến trúc chốt:** một ứng dụng Python/Streamlit dạng module, chia phần trình bày, dịch vụ nghiệp vụ, mô hình/chính sách và adapter dữ liệu session. Các service dưới đây là giao tiếp nội bộ, không phải các microservice hay API server riêng. Deployment hiện tại không yêu cầu thêm database hoặc dịch vụ ngoài.

**1. TV1 — Mô hình người dùng và đặt xe**

- **Lớp/kiểu sở hữu:** `User`, `Vehicle`, `SharedVehicle`, `Booking`, `BookingService`, kiểu kết quả chung `OperationResult`.
- **Dữ liệu và trách nhiệm:** User có ID/vai trò; Vehicle có ID, ownership, Hub, SoC và trạng thái. SharedVehicle là xe dùng chung. Booking có ID sinh viên/xe/Hub đi–đến, thời điểm tạo/nhận/trả, `expires_at` và trạng thái. BookingService điều phối đặt/nhận/hủy/trả/điều hướng.
- **Bên sử dụng:** TV2, TV4, TV5, TV7 tham chiếu ID và mô hình chung; cả nhóm dùng OperationResult.

**2. TV1 — Tài chính dùng chung**

- **Lớp/kiểu sở hữu:** `Wallet`, `Transaction`, `Invoice`, `ChargeLine`, `DepositResult`, `SettlementResult`, `BillingService`.
- **Dữ liệu và trách nhiệm:** Wallet phân biệt số dư khả dụng, cọc đang giữ, nợ và ledger. Invoice chứa các dòng phí, khoản đã thu, hoàn tiền và nợ. BillingService là nơi duy nhất ghi thay đổi tài chính và chống thu trùng trong thiết kế.
- **Bên sử dụng:** TV2/TV5 gửi dòng phí; TV3 đọc dữ liệu thu thực tế.

**3. TV2 — Xe cá nhân và lượt đỗ**

- **Lớp/kiểu sở hữu:** `PersonalVehicle`, `ParkingReservation`, `ParkingSession`, `PersonalEVService`.
- **Dữ liệu và trách nhiệm:** PersonalVehicle kế thừa phần định danh chung của Vehicle và có chủ xe/biển số/dung lượng pin. Reservation ghi giờ đến đã chọn, hạn check-in và nhu cầu sạc. ParkingSession ghi check-in/out và liên kết phiên sạc; không quản lý thuật toán cấp cổng.
- **Bên sử dụng:** TV3 đọc trạng thái; TV5 nhận yêu cầu sạc.

**4. TV3 — Hub, giám sát và cảnh báo**

- **Lớp/kiểu sở hữu:** `Hub`, `OccupancySnapshot`, `NetworkSnapshot`, `Alert`, `MonitoringService`.
- **Dữ liệu và trách nhiệm:** Hub ghi ID, tọa độ, sức chứa, chỗ trống, xe hiện diện, giữ chỗ đến, tải nền và thông tin cổng. Snapshot là bản đọc tại một thời điểm; MonitoringService tổng hợp KPI/cảnh báo, không tự sửa booking hoặc ví.
- **Bên sử dụng:** Cả nhóm dùng cùng định nghĩa Hub; các SS tự cập nhật phần trạng thái thuộc nghiệp vụ mình.

**5. TV4 — Điều chuyển và sự cố phương tiện**

- **Lớp/kiểu sở hữu:** `DispatchOrder`, `VehicleIncident`, `DispatchService`, `IncidentService`.
- **Dữ liệu và trách nhiệm:** Lệnh có ID, xe dùng chung, Hub đi/đến, người tạo và trạng thái. Incident có ID xe, người báo/tiếp nhận, nội dung, trạng thái và thời điểm xử lý. Chỉ SS4 điều phối vòng đời lệnh/sự cố phương tiện.
- **Bên sử dụng:** TV1/TV3 đọc trạng thái xe; không dùng lớp này thay sự cố hạ tầng SS7.

**6. TV5 — Phiên sạc và lập lịch**

- **Lớp/kiểu sở hữu:** `ChargingRequest`, `ChargingRequestResult`, `ChargingSession`, `ChargingPort`, `ChargingBill`, `PortFailureResult`, `ChargingService`, `SmartChargingScheduler`.
- **Dữ liệu và trách nhiệm:** Quản lý hàng chờ, phiên, cổng, công suất, kWh, SoC, ân hạn và dòng phí. ChargingService bọc các thao tác scheduler và tính phí; BillingService của TV1 thực hiện ghi nhận thu tiền.
- **Bên sử dụng:** TV2 yêu cầu sạc/lấy phí; TV3 đọc thống kê; TV7 yêu cầu xử lý cổng lỗi.

**7. TV6 — Nhu cầu, dự báo và Apply mô phỏng**

- **Lớp/kiểu sở hữu:** `DemandScenario`, `ForecastResult`, `ForecastService`, `DemandSimulationService`, `SimulationPreview`, `ApplyResult`, `SimulationCoordinator`; adapter đến `HubEventSimulator` hiện có.
- **Dữ liệu và trách nhiệm:** Sở hữu schema dự báo 24 giờ và preview dùng chung. SimulationCoordinator là đầu mối áp dụng preview SS6/SS7, kiểm tra phiên bản và ngăn áp dụng lặp; không ghi đè ví/booking bằng snapshot cũ.
- **Bên sử dụng:** TV3/TV4 đọc dự báo; TV7 dùng schema preview và thao tác Apply chung.

**8. TV7 — Sự cố hạ tầng và điều hướng**

- **Lớp/kiểu sở hữu:** `InfrastructureFailure`, `RouteSuggestion`, `InfrastructureSimulationService`, `ReroutingService`.
- **Dữ liệu và trách nhiệm:** Sở hữu nội dung kịch bản lỗi cổng/điện và danh sách Hub thay thế. Gợi ý chỉ chứa dữ liệu đề xuất; thay booking thật do BookingService thực hiện sau xác nhận người dùng.
- **Bên sử dụng:** TV1 nhận Hub thay thế; TV5 xử lý tác động trên phiên sạc thông qua hợp đồng ở mục 2.3.

**Kiểu dữ liệu và cách đặt tên đã chốt:**

- Lớp dùng `PascalCase`; thuộc tính và phương thức dùng `snake_case`. ID trao đổi là `str`, giữ nguyên ID hiện có từ dữ liệu/manifest; không sinh một ID mới cho cùng đối tượng khi qua phân hệ khác.
- Các tham chiếu xe dùng tên `vehicle_id`. Nếu code SS2 đang dùng `ev_id`, adapter ánh xạ sang `vehicle_id`; không yêu cầu sửa mã nguồn chỉ để đổi tên.
- Tiền dùng số nguyên VNĐ; phí/cọc không âm, giao dịch ledger có thể mang dấu để biểu diễn dòng tiền. SoC là phần trăm 0–100; công suất kW, năng lượng kWh, khoảng cách km.
- Thời gian thiết kế dùng `datetime` theo đồng hồ mô phỏng, quy ước UTC+7; adapter đọc/ghi định dạng thời gian hiện tại `YYYY-MM-DD HH:MM:SS`. Không trộn đồng hồ máy và đồng hồ mô phỏng trong tính hạn hoặc phí.
- Dùng lại `Ownership`, `UserRole`, `VehicleStatus`, `PortStatus`, `ChargingStatus` trong `src/core/state.py`. Booking dùng tập trạng thái `RESERVED / IN_USE / COMPLETED / CANCELLED / EXPIRED`; ParkingReservation dùng `RESERVED / CHECKED_IN / COMPLETED / EXPIRED`. TV1/TV2 mô tả enum riêng của booking/parking theo đúng tập này để tránh dùng nhầm enum xe.
- Quan hệ chính: User có nhiều Booking/PersonalVehicle; một Booking tham chiếu đúng một SharedVehicle và một Hub đi, Hub đích dự kiến có thể chưa chọn (`0.1`), khi trả phải có Hub trả thực tế. Một ParkingReservation thuộc một User, một PersonalVehicle, một Hub; một phiên sạc tại một thời điểm chỉ có một cổng và một xe. Xe/Hub/cổng có nhiều bản ghi lịch sử nhưng không được cấp trùng phiên đang hoạt động.
- Hub là lớp chuẩn do TV3 mô tả. Các SS dùng tham chiếu hoặc đánh dấu `shared`; không sao chép thành lớp Hub riêng khác thuộc tính. Wallet/Invoice và các lớp dùng chung khác áp dụng cùng nguyên tắc.

**Cách làm độc lập:** người sử dụng có thể viết ngay sơ đồ/mô tả dựa trên bảng này. Chủ sở hữu bổ sung chi tiết nội bộ nhưng giữ nguyên dữ liệu và giao tiếp đã chốt. TV1 chép các quyết định ở mục 2.2–2.3 vào `shared_contracts.md`; file đó là bản tập hợp để tái sử dụng, không phải một vòng phê duyệt mới. Nếu có mâu thuẫn thật sự, gửi ghi chú tới TV1; TV1 ghi quyết định cập nhật và thông báo bằng văn bản cho các bên liên quan.

### 2.3. Giao tiếp liên phân hệ — chữ ký và trách nhiệm đã chốt

Các chữ ký sau là **giao tiếp thiết kế mục tiêu của Sub3**, không khẳng định mọi lớp/phương thức đã tồn tại trong prototype. Hàm hiện tại có thể trả tuple/dictionary; tác giả ghi ánh xạ adapter thay vì tự tuyên bố code đã có service. Tham số `state` được ẩn ở lớp service và adapter session; các lời gọi dưới đây chạy nội bộ ứng dụng.

**Kiểu trao đổi chung:**

| Kiểu | Các trường tối thiểu và ý nghĩa |
| --- | --- |
| `OperationResult[T]` | `ok: bool`, `data: T hoặc None`, `error_code: str hoặc None`, `message: str`, `state_version: int`; lỗi không được âm thầm cập nhật một phần dữ liệu |
| `ChargeLine` | `charge_id`, `source_id`, `kind`, `amount_vnd`; mỗi khoản phí có ID ổn định. Cùng khoản đã thu không được tạo ID mới để thu lại |
| `SettlementResult` | `invoice_id`, các dòng phí, `paid_vnd`, `refunded_vnd`, `debt_vnd`, `status`; số đã thu lấy từ ledger, không tin cờ đã thanh toán do UI tự truyền |
| `ChargingRequestResult` | `request_id`, `vehicle_id`, `hub_id`, `status`, `session_id` tùy chọn; yêu cầu đang chờ chưa có phiên/cổng thực sự |
| `ChargingBill` | `session_id`, `energy_delivered_kwh`, `energy_fee_vnd`, `overstay_fee_vnd`, các `ChargeLine`, thông tin khoản đã thu; đây là dữ liệu đọc, không tự trừ ví |
| `NetworkSnapshot` | `captured_at`, `state_version`, danh sách OccupancySnapshot, KPI mạng lưới và doanh thu đã thu; tiền cọc đang giữ không phải doanh thu |
| `ForecastResult` | `forecast_id`, `hub_id`, `hours=24`, `seed`, giả định/đơn vị, danh sách 24 điểm dự báo có nhãn giờ, nhu cầu, hàng chờ và thời gian chờ |
| `SimulationPreview` | `preview_id`, `scenario_type`, `baseline_version`, `modified_hubs`, `charging_effects`, `summary`, trạng thái đã áp dụng; candidate được tách khỏi dữ liệu gốc |
| `RouteSuggestion` | `hub_id`, `distance_km`, chỗ/cổng khả dụng tại thời điểm đề xuất, lý do xếp hạng; thông tin này phải được kiểm tra lại khi áp dụng |

**Hợp đồng tài chính — TV1 sở hữu:**

**`BillingService.hold_deposit`**

**Bên gọi:** SS1/SS2.

```text
hold_deposit(
    owner_id,
    reference_id,
    amount_vnd,
    operation_key,
) -> OperationResult[DepositResult]
```

**Quy tắc:** Giữ cọc theo booking/reservation; thiếu tiền hoặc đang có nợ không được tạo lượt mới trái chính sách; cùng `operation_key` không giữ thêm lần nữa.

**`BillingService.release_deposit`**

**Bên gọi:** SS1/SS2.

```text
release_deposit(
    owner_id,
    reference_id,
    operation_key,
) -> OperationResult[DepositResult]
```

**Quy tắc:** Chỉ hoàn phần cọc của đúng reference, một lần; không dùng tổng cọc của ví để hoàn nhầm booking khác.

**`BillingService.settle_no_show`**

**Bên gọi:** SS1/SS2.

```text
settle_no_show(
    owner_id,
    reference_id,
    operation_key,
) -> OperationResult[SettlementResult]
```

**Quy tắc:** Sau điều kiện hết hạn của phân hệ gọi: cọc 50.000, phạt 10.000, hoàn 40.000 VNĐ; lời gọi lặp không phạt/hoàn lần hai.

**`BillingService.settle_invoice`**

**Bên gọi:** SS1/SS2/SS5.

```text
settle_invoice(
    owner_id,
    reference_id,
    charge_lines,
    operation_key,
) -> OperationResult[SettlementResult]
```

**Quy tắc:** Chỉ thu các `charge_id` còn phải thu, xử lý phần cọc theo loại reference và ghi nợ nếu thiếu tiền. Khoản đã được xử lý trả lại kết quả đã ghi nhận, không trừ ví lần nữa.

`DepositResult` tối thiểu có `reference_id`, `held_vnd`, `released_vnd`, trạng thái xử lý. Lặp `operation_key` với cùng dữ liệu trả kết quả cũ; cùng key nhưng dữ liệu khác trả `CONFLICTING_OPERATION`. Cùng `charge_id` mà số tiền khác trả `CONFLICTING_CHARGE`, không tự ghi đè lịch sử thu.

**Chốt trách nhiệm tính phí và thu tiền:** TV1 tính phí thuê SS1; TV2 tính phí đỗ SS2; TV5 tính điện/quá giờ SS5. Mọi biến động ví đi qua BillingService do TV1 thiết kế. Khi check-out xe cá nhân, TV2 lấy ChargingBill rồi gửi các dòng phí còn phải thu; nếu SS5 đã thu một dòng trước đó, ledger ngăn thu lại. Các khối phí quá giờ hoặc đợt tính phí khác nhau dùng `charge_id` riêng có tham chiếu phiên/kỳ tính phí; không đổi số tiền của dòng đã thu. Biểu phí đỗ mặc định của prototype giữ **5.000 VNĐ/lượt**; yêu cầu SRS tính theo giờ được ghi là chênh lệch còn tồn tại, không tự đổi đơn giá để che chênh lệch.

**Các giao tiếp nghiệp vụ khác:**

**`INT-01` — TV5 / `ChargingService`**

**Bên gọi:** SS2.

```text
request_charging(
    owner_id,
    vehicle_id,
    hub_id,
    current_soc,
    target_soc=100,
    reservation_id=None,
) -> OperationResult[ChargingRequestResult]
```

**Quy tắc:** Chỉ tạo yêu cầu khi check-in hợp lệ; không cấp trùng cho cùng lượt/xe. SS5 sở hữu cấp cổng, công suất và vòng đời phiên.

**`INT-02` — TV5 / `ChargingService`**

**Bên gọi:** SS2, SS3.

```text
get_bill(session_id) -> OperationResult[ChargingBill]
```

**Quy tắc:** Trả số đo/phí và khoản đã thu; chỉ đọc. SS2 không tự tính lại giá điện hoặc phí quá giờ bằng một công thức riêng.

**`INT-03` — TV3 / `MonitoringService`**

**Bên gọi:** Dashboard và các SS cần trạng thái.

```text
get_network_snapshot() -> OperationResult[NetworkSnapshot]
```

**Quy tắc:** Đọc trạng thái session hiện tại, ghi thời điểm/phiên bản; làm mới khi Streamlit rerun hoặc người dùng yêu cầu. Không giả định có push IoT/background worker thật.

**`INT-04` — TV6 / `ForecastService`**

**Bên gọi:** SS6; SS3/SS4 đọc kết quả.

```text
forecast(
    hub_id,
    base_arrival_rate,
    surge_multiplier,
    hours=24,
    seed=42,
) -> OperationResult[ForecastResult]
```

**Quy tắc:** Sub3 dùng 24 giờ; cùng đầu vào/seed tái tạo kết quả nghiệp vụ. SS4 chỉ dùng để tham khảo, không tự thực hiện lệnh điều chuyển.

**`INT-05` — TV5 / `ChargingService`**

**Bên gọi:** SS7 thông qua SimulationCoordinator trong bước Apply.

```text
handle_port_failure(
    hub_id,
    port_ids,
    operation_key,
) -> OperationResult[PortFailureResult]
```

**Quy tắc:** Ngừng sử dụng các cổng lỗi, trả danh sách phiên ảnh hưởng, cập nhật công suất/trạng thái tương ứng; không làm đổi số chỗ đỗ chỉ vì cổng lỗi.

**`INT-06` — TV7 / `ReroutingService`**

**Bên gọi:** SS1, SS7.

```text
suggest_hubs(
    target_hub_id,
    need_slots=True,
    need_ports=False,
    limit=2,
) -> OperationResult[list[RouteSuggestion]]
```

**Quy tắc:** Lọc theo nhu cầu/tình trạng, xếp theo khoảng cách Haversine; không có nơi phù hợp trả danh sách rỗng, không đổi booking.

**`INT-07` — TV1 / `BookingService`**

**Bên gọi:** UI SS1/SS7 sau xác nhận người dùng.

```text
accept_rerouting(
    booking_id,
    new_hub_id,
    expected_version,
    operation_key,
) -> OperationResult[Booking]
```

**Quy tắc:** Kiểm tra lại quyền, trạng thái booking, phiên bản và sức chứa; cập nhật giữ chỗ Hub cũ/mới cùng nghiệp vụ, thêm ưu đãi 15 phút tối đa một lần cho một booking; lỗi thì giữ dữ liệu trước thao tác.

**`INT-08` — TV6 / `DemandSimulationService`**

**Bên gọi:** UI SS6.

```text
preview_demand(
    hub_id,
    num_students,
    seed=42,
) -> OperationResult[SimulationPreview]
```

**Quy tắc:** Bản sao cách ly, `scenario_type=DEMAND`; không sửa Hub thật hoặc ví/booking.

**`INT-09` — TV7 / `InfrastructureSimulationService`**

**Bên gọi:** UI SS7.

```text
preview_port_failure(
    hub_id,
    num_ports_down,
    seed=42,
) -> OperationResult[SimulationPreview]
```

**Quy tắc:** Dùng schema do TV6 sở hữu, `scenario_type=PORT_FAILURE`; chỉ mô tả tác động dự kiến lên Hub/cổng/phiên.

**`INT-10` — TV6 / `SimulationCoordinator`**

**Bên gọi:** UI SS6 và SS7.

```text
apply_preview(
    preview_id,
    expected_version,
) -> OperationResult[ApplyResult]
```

**Quy tắc:** So `baseline_version` và `expected_version` với trạng thái hiện tại; chỉ commit khi cùng khớp và invariant hợp lệ. Apply đồng bộ tác động Hub/phiên liên quan, tăng `state_version`, đánh dấu đã áp dụng; không chép đè dữ liệu ví/booking từ snapshot.

`PortFailureResult` có `hub_id`, danh sách cổng/phiên bị ảnh hưởng và công suất sau xử lý. `ApplyResult` có `preview_id`, `applied`, `already_applied`, `new_state_version`. Apply lần nữa cùng preview trả trạng thái đã áp dụng, không gây tác động lần hai. Phối hợp tác động SS7–SS5 trong Apply phải được mô tả như một thao tác nhất quán; nếu kiểm tra thất bại thì không commit từng phần.

**Lỗi chung:** `NOT_FOUND`, `INVALID_INPUT`, `FORBIDDEN`, `INVALID_STATE`, `EXPIRED`, `NO_CAPACITY`, `INSUFFICIENT_FUNDS`, `DEBT_BLOCKED`, `STALE_STATE`, `CONFLICTING_OPERATION`, `CONFLICTING_CHARGE`; chỉ sử dụng mã phù hợp với thao tác. Kết quả xử lý có phát sinh nợ theo chính sách trả xe không bị nhầm với lỗi làm mất trạng thái trả xe vật lý.

**Trách nhiệm tự kiểm thử đã chốt:** chủ sở hữu service tự kiểm tra điều kiện và kết quả của service; bên gọi tự kiểm tra ánh xạ đầu vào/đầu ra và cách xử lý lỗi trong phần mình. Không giao nhiệm vụ kiểm tra bài của thành viên khác. Mỗi người ghi đầy đủ mô tả cho các phương thức đã đưa vào class diagram; không cần vẽ lại mọi service dùng chung nếu phân hệ chỉ tham chiếu giao tiếp của nó.

## 3. Timeline thực hiện

| Ngày bắt đầu | Ngày kết thúc |
| --- | --- |
| **21/10/2026** | **30/10/2026** |

Mỗi thành viên tự sắp xếp thứ tự làm việc trong khoảng này: đọc Sub1/Sub2 → thiết kế lớp và phương thức theo mục 2.2–2.3 → viết báo cáo → tự kiểm tra/sửa → bàn giao và nộp. Không chia deadline theo ngày hoặc theo task. Bản nguồn, ảnh, PDF và checklist tự kiểm tra phải đầy đủ khi bàn giao; mọi nội dung bắt buộc hoàn tất trước giờ đóng LMS của ngày kết thúc.

**Cách phối hợp:** cập nhật khi có sản phẩm, thay đổi ảnh hưởng phần chung hoặc vướng mắc, qua tin nhắn/ghi chú trên file. Dùng dữ liệu/giao tiếp đã chốt để làm độc lập; không chờ đủ thành viên hoặc chờ họp. TV1 điều phối các ngoại lệ bằng văn bản, TV4 tập hợp vấn đề do tác giả tự báo. Nếu thiếu thời gian, ưu tiên các phần bắt buộc trước test bonus và mở rộng demo.

## 4. Bộ sản phẩm và quy cách bàn giao

### 4.1. Cấu trúc thư mục đã điều chỉnh và khởi tạo

Dùng lại `docs/report/submission_3/` đã có của dự án; giữ nguyên `mau.png`. Báo cáo, sơ đồ, truy vết và file xuất được tách theo cấu trúc hiện hành, thay cho một cây `docs/submission_3/` mới trộn tất cả loại tài liệu.

```text
docs/
├── report/submission_3/
│   ├── README.md                       # Điểm vào và hướng dẫn sử dụng bộ khung
│   ├── mau.png                         # Mẫu sẵn có, giữ nguyên
│   ├── shared/
│   │   ├── shared_contracts.md          # TV1; quyết định mục 2.2–2.3
│   │   └── open_issues.md               # TV4; vấn đề do tác giả tự báo
│   ├── TV1_NguyenThanhDat/
│   ├── TV2_NguyenAnhTai/
│   ├── TV3_PhamTienDat/
│   ├── TV4_DangHoangQuyNhan/
│   ├── TV5_DuongDangKhoa/
│   ├── TV6_HoangVanTan/
│   └── TV7_NguyenTrungNguyen/
├── diagrams/submission_3/
│   ├── README.md
│   ├── shared/
│   │   ├── deployment.puml              # TV7
│   │   ├── implementation.puml          # TV3
│   │   └── system_classes.puml          # TV3
│   └── SS1/ ... SS7/
│       └── class_diagram.puml           # Nguồn sơ đồ cá nhân theo phân hệ
├── traceability/
│   └── submission_3.md                  # TV6; chỉ mục 17 UC và nguồn cá nhân
└── prompt-history/
    └── TVx_<HoTen>/                     # Dùng lại thư mục cá nhân hiện có
        └── prompt_history_<HoTen>_sub3.txt

Mỗi thư mục báo cáo cá nhân có:
  REPORT_SUB3.md                        # Khung nguồn báo cáo
  traceability.md                      # Truy vết cá nhân từ SRS/Sub2
  test_cases.md                        # Bonus; chưa chạy thì không ghi PASS
  self_check.md                        # Checklist tự chịu trách nhiệm
  ai_usage.md                          # Phạm vi AI và phần cá nhân tự hoàn thiện

output/submission_3/
  README.md                            # Quy tắc và tên đầu ra khi hoàn thiện
  REPORT_SUB3_<HoTen>_<MSSV>.pdf         # Tạo sau khi nội dung hoàn thiện
```

**Trạng thái khởi tạo:** các file Markdown là bản khung; nguồn PlantUML có nhãn DRAFT và chưa phải thiết kế hoàn chỉnh. Không tạo PDF/PNG rỗng để làm đủ danh sách. Khi hoàn thiện, ảnh `.png`/`.svg` được xuất cạnh `.puml`; PDF cá nhân được xuất vào `output/submission_3/`. Báo cáo phải dẫn đúng nguồn/ảnh chung, không sao chép thêm một phiên bản sơ đồ trong từng thư mục thành viên.

**Điểm vào:** [README Submission 3](docs/report/submission_3/README.md). Các cây Sub1/Sub2 và prompt cũ được giữ nguyên. Chỉ mục truy vết Sub3 tham chiếu manifest Sub2, không sửa lại dữ liệu lịch sử hoặc tự ghi thiết kế Sub3 đã hoàn tất.

Nguồn, bảng và ảnh được đưa vào báo cáo PDF cuối; người chấm không phải mở nhiều file Markdown để đọc phần bắt buộc. Nếu LMS chỉ nhận một file, xuất theo định dạng yêu cầu; ZIP nguồn không thay cho báo cáo `.doc/.docx/.pdf`.

### 4.2. Bố cục báo cáo cá nhân

1. Trang bìa: môn, nhóm, dự án, họ tên, MSSV, SS phụ trách, phiên bản và ngày.
2. Phạm vi: các UC kế thừa và phần đóng góp cá nhân/phần dùng chung.
3. Deployment view: sơ đồ chung, chú giải, mức triển khai hiện tại và vị trí SS cá nhân.
4. Development/Implementation view: sơ đồ chung, module/tầng/phụ thuộc và ánh xạ SS vào code.
5. Class diagram cá nhân: các lớp riêng, lớp dùng chung liên quan, quan hệ và bội số.
6. Class descriptions: trách nhiệm, thuộc tính, kiểu/đơn vị và ràng buộc.
7. Method descriptions: mô tả **mọi phương thức được vẽ**, kể cả phương thức của lớp đề xuất nếu đưa vào sơ đồ.
8. Bảng truy vết từ Sub1/Sub2 đến thiết kế Sub3.
9. Test case bonus: dữ liệu, thao tác, kết quả mong đợi; kết quả thực tế nếu đã chạy.
10. Quyết định thiết kế, giới hạn, vấn đề còn mở, đóng góp và khai báo AI.

Sơ đồ tổng quan có thể lược thuộc tính/phương thức để dễ đọc nếu chú thích rõ và dẫn đến sơ đồ chi tiết đầy đủ. Không dùng sơ đồ lược giản để che thiếu mô tả phương thức.

### 4.3. Chuẩn class diagram

- Tên lớp thể hiện trách nhiệm; phân biệt entity, service, policy, repository/adapter nếu sử dụng.
- Thuộc tính/phương thức có kiểu dữ liệu; thể hiện tham số, kiểu trả về và phạm vi truy cập phù hợp.
- Association có vai trò và bội số; chỉ dùng composition/kế thừa khi giải thích được ý nghĩa vòng đời/quan hệ.
- Ghi đơn vị: VNĐ, phút, kW, kWh, phần trăm và km. Không dùng kW thay cho kWh.
- Enum/trạng thái khớp định nghĩa chung; nếu đề xuất thêm trạng thái, ghi rõ lý do và ảnh hưởng tới các sơ đồ cũ.
- Không đưa `st.button`, tab hoặc mọi biến `session_state` thành lớp nghiệp vụ. Có thể biểu diễn UI/adapter ở mức kiến trúc và mô tả trách nhiệm riêng.
- Không thêm hàng loạt CRUD/getter/setter không cần thiết. Phương thức nào đã đưa lên sơ đồ đều phải có mô tả.
- Ảnh phải đọc được ở kích thước trong PDF; tách sơ đồ nếu quá dày. Nguồn và ảnh xuất phải cùng phiên bản.

## 5. Nhiệm vụ và checklist từng thành viên

### 5.1. TV1 — Nguyễn Thành Đạt — SS1 và điều phối nhóm

**Phạm vi UC:**

- `UC_SS1_01`: Tra cứu, Đặt xe & Nhận xe qua QR/PIN.
- `UC_SS1_02`: Trả xe, Cập nhật vị trí & Quyết toán ví điện tử.
- `UC_SS1_03`: Hủy đặt chỗ & Hoàn cọc / Phạt quá giờ.

**Đọc trước:** `src/components/student_booking.py`, `src/core/booking.py`, `src/core/billing.py`, `src/core/state.py`, `src/core/policies.py`; scenario/sequence/activity SS1; `tests/test_reservation_30_minutes.py` và các test đặt/trả xe liên quan.

**Thiết kế cụ thể:**

1. Tách trách nhiệm tạo/nhận/hủy/trả booking khỏi giao diện; đề xuất các lớp như `Booking`, `SharedVehicle`, `BookingService`, `ReservationPolicy`, `Wallet`, `Invoice` nếu phù hợp.
2. Ánh xạ các thao tác đến hàm thực tế: `create_shared_booking`, `pickup_shared_vehicle`, `cancel_shared_booking`, `return_shared_vehicle`, `process_expired_bookings`, `apply_rerouting_to_booking` và các hàm tài chính liên quan. Không coi alias trong tài liệu cũ là một phương thức đã triển khai độc lập.
3. Đặc tả mốc hết hạn: SS1 tính từ lúc tạo booking; tại `now >= expires_at` không được nhận xe bằng booking chưa nhận. Hủy trong hạn, hết hạn và nhận xe phải có thứ tự kiểm tra rõ ràng.
4. Mô tả bảo toàn chỗ đỗ/xe; xe cá nhân không thuộc danh sách cho thuê; xử lý hoàn cọc/phạt/thu phí một lần; trả xe khi thiếu tiền phải thể hiện khoản nợ thay vì xóa phần thiếu.
5. Thiết kế tài chính dùng chung, cập nhật Hub trả và SharedVehicle theo quyền sở hữu/giao tiếp đã quy định ở mục 2.2–2.3; các bên sử dụng tham chiếu trực tiếp.
6. Với `US-06`, nêu rõ prototype chưa có số đo quãng đường chuyến đi. Nếu đề xuất bổ sung vào hóa đơn, ghi nguồn dữ liệu và trạng thái thiết kế, không ghi đã triển khai.

**Test bonus ưu tiên:** đặt/nhận/trả thành công; thiếu tiền hoặc pin thấp; nhận xe ở 29:59 và đúng 30:00; hủy trong hạn; hết hạn và sweep lặp; trả/quyết toán lặp; trả xe có phát sinh nợ.

**Checklist TV1:**

**Chuẩn bị và triển khai cho nhóm — đã hoàn thành:**

- [x] `TV1-P01` — Hoàn thiện hướng dẫn Sub3, phân công 7 thành viên và chốt quyền sở hữu/giao tiếp dùng chung ở mục 2.2–2.3.
- [x] `TV1-P02` — Điều chỉnh và khởi tạo cấu trúc tài liệu phù hợp dự án; có khung báo cáo, nguồn sơ đồ, truy vết và prompt history; đã kiểm tra đường dẫn/cú pháp nguồn.
- [x] `TV1-P03` — Gửi và triển khai hướng dẫn cho nhóm, theo xác nhận trực tiếp của trưởng nhóm.

**Task cá nhân và điều phối còn lại:**

- [ ] `TV1-01` — Kiểm tra quy định LMS, xác nhận phạm vi cá nhân và phổ biến hướng dẫn cho nhóm.
- [ ] `TV1-02` — Lập danh sách lớp SS1, giao tiếp sử dụng và ánh xạ đến code hiện có.
- [x] `TV1-03` — Tập hợp quyết định mục 2.2–2.3 vào `shared_contracts.md` để cả nhóm dùng trực tiếp.
- [ ] `TV1-04` — Tạo class diagram SS1 nguồn + ảnh, bao phủ cả 3 UC.
- [ ] `TV1-05` — Mô tả chính sách 30 phút, vòng đời booking và hợp đồng tài chính theo quyết định đã chốt.
- [ ] `TV1-06` — Mô tả đầy đủ lớp/phương thức SS1 và bảng truy vết.
- [ ] `TV1-07` — Hoàn thành báo cáo nháp, test case bonus nếu thực hiện và khai báo AI thực tế.
- [ ] `TV1-08` — Tự kiểm tra SS1, phần tài chính và điều hướng thuộc trách nhiệm mình; ghi `self_check.md`.
- [ ] `TV1-09` — Tự sửa lỗi, kiểm tra lại và công khai giới hạn của SS1/phần chung mình sở hữu.
- [ ] `TV1-10` — Xuất PDF cá nhân hoàn chỉnh, bàn giao cùng nguồn và ảnh đúng phiên bản.
- [ ] `TV1-11` — Tiếp nhận đủ 7 báo cáo và xác nhận tự kiểm tra của tác giả; tập hợp bộ file cuối.
- [ ] `TV1-12` — Điều phối nộp theo LMS; lưu đúng bộ file đã nộp và xác nhận nộp.

**Ghi nhận tiến độ:** `TV1-01` đã xong phần xác nhận phạm vi và phổ biến hướng dẫn; phần kiểm tra quy định LMS chưa có xác nhận nên task tổng vẫn để mở. Việc tạo file khung không đồng nghĩa đã hoàn thành class diagram, mô tả lớp/phương thức, PDF hoặc kiểm thử SS1. Các thành viên khác tự cập nhật phần việc của mình.

### 5.2. TV2 — Nguyễn Anh Tài — SS2: Xe cá nhân và chỗ đỗ

**Phạm vi UC:**

- `UC_SS2_01`: Đăng ký xe EV cá nhân lên hệ thống.
- `UC_SS2_02`: Đặt trước chỗ đỗ và nhu cầu sạc xe EV cá nhân.
- `UC_SS2_03`: Check-in xe EV cá nhân tại cổng Hub (QR/Biển số).
- `UC_SS2_04`: Check-out và thanh toán tổng hợp dịch vụ xe EV cá nhân.

**Đọc trước:** `src/components/personal_ev.py`, `src/core/personal_ev.py`, `src/core/billing.py`, `src/core/policies.py`; 4 bộ sơ đồ SS2; `tests/test_personal_ev.py`, `tests/test_reservation_30_minutes.py` và test tài chính liên quan.

**Thiết kế cụ thể:**

1. Thiết kế `PersonalVehicle`, `ParkingReservation`, `ParkingSession`, `PersonalEVService` và liên kết đến chủ xe, Hub, ví, hóa đơn, phiên sạc. Các lớp này là đề xuất nếu code hiện dùng dictionary/hàm.
2. Ánh xạ `register_personal_ev`, `reserve_personal_ev_slot`, `check_in_personal_ev`, `check_out_personal_ev`, `sweep_expired_personal_reservations` vào các thao tác của thiết kế.
3. Ghi rõ `expires_at = booking_start_time + 30 phút`; không lấy thời điểm tạo booking thay cho giờ đến đã chọn. Tại đúng hạn phải xử lý theo quy tắc hết hạn đã chốt.
4. Phân biệt chỗ đỗ giữ trước, xe đã vào Hub, yêu cầu sạc và cổng sạc thực sự được cấp. Không đồng nhất “yêu cầu sạc” với “đang sạc”.
5. Dùng phí sạc do TV5 cung cấp, tổng hợp phí đỗ của SS2 và gọi BillingService do TV1 thiết kế để ghi nhận thu tiền; kiểm tra cọc no-show, phí điện và quá giờ không bị trừ hai lần.
6. Dùng chính sách mặc định 5.000 VNĐ/lượt của prototype; ghi rõ chênh lệch với SRS yêu cầu tính theo giờ. Có thể thiết kế ParkingFeePolicy để thay chiến lược sau này, nhưng không ghi rằng chênh lệch đã được giải quyết bằng quyết định giữ giá hiện tại.

**Test bonus ưu tiên:** đăng ký hợp lệ/trùng biển số; đặt chỗ hợp lệ/hết chỗ; check-in trước/đúng hạn; check-in lặp; check-out không có sạc/có sạc; nợ và quyết toán lặp. Mục tiêu nội bộ: có ít nhất một luồng chính và một lỗi/ngoại lệ cho mỗi UC của SS2.

**Checklist TV2:**

- [ ] `TV2-01` — Xác nhận đủ 4 UC SS2, danh sách lớp và ánh xạ đến code hiện có.
- [ ] `TV2-02` — Áp dụng giao tiếp tài chính, `INT-01` và `INT-02` ở mục 2.3 trong thiết kế SS2.
- [ ] `TV2-03` — Tạo class diagram nguồn + ảnh, có chủ xe, Hub, lượt đỗ và liên kết phiên sạc.
- [ ] `TV2-04` — Mô tả ownership, chỗ giữ trước và hạn check-in 30 phút từ giờ đến đã chọn.
- [ ] `TV2-05` — Mô tả toàn bộ phương thức; mỗi UC có lớp/phương thức chịu trách nhiệm.
- [ ] `TV2-06` — Dùng phí đỗ mặc định 5.000 VNĐ/lượt và ghi rõ chênh lệch với yêu cầu tính theo giờ.
- [ ] `TV2-07` — Hoàn thành báo cáo nháp, truy vết, test case bonus nếu thực hiện và khai báo AI.
- [ ] `TV2-08` — Tự kiểm tra đủ 4 UC, tiền cọc và quyết toán; ghi `self_check.md`.
- [ ] `TV2-09` — Tự đối chiếu ánh xạ dữ liệu SS2 vào giao tiếp BillingService/ChargingService đã chốt.
- [ ] `TV2-10` — Tự sửa lỗi SS2, kiểm tra lại và ghi kết quả thực tế.
- [ ] `TV2-11` — Xuất PDF hoàn chỉnh, bàn giao cùng nguồn và bản kiến trúc chung đúng phiên bản.
- [ ] `TV2-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

### 5.3. TV3 — Phạm Tiến Đạt — SS3 và Development/Implementation view

**Phạm vi UC:**

- `UC_SS3_01`: Giám sát mạng lưới Hub, KPI & Doanh thu thời gian thực.
- `UC_SS3_02`: Cảnh báo phân cấp chiếm dụng Hub & Sự cố IoT.

**Đọc trước:** `src/components/hub_monitor.py`, `src/core/state.py`, `src/core/policies.py`, `src/app.py`; cấu trúc `src/components/`, `src/core/`; scenario và sơ đồ SS3.

**Thiết kế cụ thể:**

1. Thiết kế các trách nhiệm `Hub`, `OccupancySnapshot`, `NetworkSnapshot`, `MonitoringService`, `Alert`, `RevenueReport`; giải thích dữ liệu đầu vào của từng KPI. TV3 sở hữu thêm RevenueReport nếu đưa lớp này vào sơ đồ.
2. Chuẩn hóa occupancy với các mức `<70%`, `70–<85%`, `85–<100%`, `>=100%`; phân biệt tỷ lệ chỗ đỗ, tỷ lệ dùng cổng sạc và công suất điện.
3. Đối chiếu sức chứa: chỗ trống, xe hiện diện, giữ chỗ đến và tải nền phải được giải thích nhất quán. Không cộng hai lần cùng một xe/chỗ.
4. Phân biệt doanh thu thực thu, khoản cọc đang giữ, tiền hoàn và nợ. Ghi nguồn dữ liệu và cách làm mới dashboard; không mặc định có luồng IoT hoặc background polling thật.
5. Vẽ **Development/Implementation view**: UI Streamlit → thành phần giao diện → xử lý nghiệp vụ/core → dữ liệu/adapter và phần mô phỏng. Ghi phụ thuộc thực tế; các tầng mới đề xuất phải có chú thích.
6. Tổng hợp class diagram cấp hệ thống từ bản chủ sở hữu bàn giao và quy ước mục 2.2–2.3; ưu tiên liên kết và ranh giới, dẫn đến sơ đồ chi tiết thay vì nhét mọi thuộc tính vào một ảnh quá lớn.

**Test bonus ưu tiên:** phân loại tại 69,99/70/84,99/85/99,99/100%; bảo toàn sức chứa; cập nhật dashboard sau giao dịch; không coi cọc đang giữ là doanh thu; cảnh báo và dữ liệu thiếu.

**Checklist TV3:**

- [ ] `TV3-01` — Lập danh sách lớp SS3 và các nguồn dữ liệu dùng cho KPI/cảnh báo.
- [ ] `TV3-02` — Mô tả kiến trúc module/tầng hiện tại dựa trên code và quyết định mục 2.2–2.3.
- [ ] `TV3-03` — Tạo class diagram SS3 và Development/Implementation view, đủ nguồn + ảnh.
- [ ] `TV3-04` — Mô tả Hub, snapshot, Alert, đơn vị KPI và phụ thuộc theo định nghĩa đã chốt.
- [ ] `TV3-05` — Hoàn thành mô tả lớp/phương thức SS3, nguồn tính KPI và doanh thu thực thu.
- [ ] `TV3-06` — Tổng hợp class diagram hệ thống từ sản phẩm các chủ sở hữu và quy ước chung.
- [ ] `TV3-07` — Hoàn thành báo cáo nháp, truy vết, test case bonus nếu thực hiện và khai báo AI.
- [ ] `TV3-08` — Tự kiểm tra SS3 và các sơ đồ chung mình tổng hợp; ghi `self_check.md`.
- [ ] `TV3-09` — Tự sửa lỗi, kiểm tra lại; xuất sơ đồ Implementation và class diagram hệ thống hoàn chỉnh.
- [ ] `TV3-10` — Cung cấp nguồn, ảnh, thuyết minh và phiên bản kiến trúc chung cho cả nhóm.
- [ ] `TV3-11` — Xuất PDF cá nhân hoàn chỉnh, kiểm tra hình và ánh xạ mã nguồn rồi bàn giao.
- [ ] `TV3-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

### 5.4. TV4 — Đặng Hoàng Quý Nhân — SS4 và tổng hợp vấn đề được báo

**Phạm vi UC:**

- `UC_SS4_01`: Lập lệnh điều chuyển phương tiện cân bằng phụ tải.
- `UC_SS4_02`: Báo cáo, tiếp nhận xử lý và khắc phục sự cố phương tiện.

**Đọc trước:** `src/components/dispatch_incident.py`, `src/core/state.py`, `src/core/routing.py`; scenario/sơ đồ SS4; test điều chuyển và sự cố trong `tests/test_submission_2_readiness_fixes.py` cùng các test liên quan.

**Thiết kế cụ thể:**

1. Đề xuất `DispatchOrder`, `DispatchService`, `VehicleIncident`, `IncidentService`. Một phần xử lý hiện nằm trong UI; phải chỉ rõ phần nào được đề xuất tách thành service.
2. Mô tả vòng đời lệnh, điều kiện tạo/thực hiện/hoàn tất và tác động tới xe/Hub. Nếu bổ sung thao tác hủy lệnh, ghi rõ là thiết kế đề xuất và quy tắc hoàn tác.
3. Chỉ cho điều chuyển xe dùng chung đủ điều kiện; không điều chuyển xe cá nhân hoặc xe đã bị giữ/đang dùng khi không được phép.
4. Kiểm tra sức chứa Hub đích tại lúc thực hiện; mô tả cách tránh cập nhật dở dang giữa Hub đi, Hub đến và trạng thái xe.
5. Phân biệt sự cố phương tiện SS4 với sự cố cổng/điện SS7. Xe được khôi phục chỉ quay lại trạng thái hợp lệ, không tự mất ràng buộc sạc hoặc booking.
6. Tổng hợp `open_issues.md` từ thông tin các thành viên tự báo: mã lỗi, file/vị trí, mức độ, người phụ trách, bằng chứng và kết quả tự kiểm tra. Tác giả phần việc tự cập nhật nội dung và chịu trách nhiệm trạng thái lỗi của mình.

**Test bonus ưu tiên:** điều chuyển hợp lệ; xe cá nhân bị từ chối; xe không khả dụng; Hub đích đầy; hoàn tất lặp; tiếp nhận/xử lý sự cố và khôi phục hợp lệ.

**Checklist TV4:**

- [ ] `TV4-01` — Xác nhận đủ 2 UC SS4, danh sách lớp và phụ thuộc đến mô hình dùng chung.
- [ ] `TV4-02` — Tạo class diagram nguồn + ảnh, chỉ rõ xử lý đang ở UI và service thiết kế đề xuất.
- [ ] `TV4-03` — Ghi quyết định thiết kế SS4 theo mục 2.2–2.3 và vấn đề còn mở nếu có.
- [ ] `TV4-04` — Mô tả điều kiện xe hợp lệ, sức chứa và trạng thái sau điều chuyển/xử lý sự cố.
- [ ] `TV4-05` — Hoàn thành mô tả mọi phương thức, lỗi, cập nhật dữ liệu và xử lý lặp.
- [ ] `TV4-06` — Hoàn thành báo cáo nháp, truy vết, test case bonus nếu thực hiện và khai báo AI.
- [ ] `TV4-07` — Tự kiểm tra điều chuyển và sự cố SS4; ghi `self_check.md`.
- [ ] `TV4-08` — Tổng hợp vấn đề các thành viên tự báo, giữ nguyên người phụ trách và trạng thái tác giả cung cấp.
- [ ] `TV4-09` — Tự sửa/kiểm tra lại SS4; cập nhật danh sách vấn đề theo báo cáo của từng tác giả.
- [ ] `TV4-10` — Xuất PDF cá nhân hoàn chỉnh, bàn giao cùng nguồn và ảnh.
- [ ] `TV4-11` — Báo TV1 lỗi chặn nộp còn mở; không tự đánh dấu đã xử lý khi chưa kiểm tra.
- [ ] `TV4-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

### 5.5. TV5 — Dương Đăng Khoa — SS5: Lập lịch và tính phí sạc

**Phạm vi UC:**

- `UC_SS5_01`: Lập lịch sạc tự động theo điểm ưu tiên & Giới hạn công suất lưới.
- `UC_SS5_02`: Giám sát hàng chờ sạc, hoàn thành, ân hạn & Tính phí quá giờ.

**Đọc trước:** `src/components/smart_charging.py`, `src/core/scheduler.py`, `src/core/billing.py`, `src/core/policies.py`, `src/core/state.py`; sơ đồ SS5; `tests/test_scheduler_and_charging.py`.

**Thiết kế cụ thể:**

1. Kế thừa các lớp **đang có** `ChargingRequest`, `ChargingSession`, `SmartChargingScheduler`; bổ sung policy/service/port nếu cần và ghi trạng thái triển khai.
2. Đối chiếu tên thao tác thực tế: `calculate_priority`, `add_request`, `remove_request`, `get_sorted_queue`, `allocate_ports`, `advance_simulation_tick`, `unplug_vehicle`; không sao chép tên alias cũ khi code đã khác.
3. Mô tả công thức ưu tiên, cách phá hòa và điều kiện cấp cổng. Tổng công suất đang dùng không vượt giới hạn cấu hình; dùng 150 kW làm giá trị mặc định hiện tại, không thay thành số cổng.
4. Mô tả hàng chờ → sạc → hoàn thành → ân hạn → quá giờ; thông báo ở các ngưỡng liên quan phải khớp hành vi thực tế và không phát sinh thu phí lặp.
5. Giữ riêng các chính sách: **ân hạn 15 phút**, **khối quá giờ 15 phút**, **10.000 VNĐ/khối** theo hằng số hiện hành. Thay đổi giữ chỗ 30 phút không tự đổi các giá trị này.
6. Áp dụng quyết định mục 2.3: TV5 tính phí điện/quá giờ và xuất ChargingBill; BillingService ghi nhận khoản thu. Tác động cổng lỗi từ SS7 dùng `INT-05` trong bước Apply, không yêu cầu thêm cuộc họp để phân chia trách nhiệm.
7. Với `US-12`, mô tả rõ thiết kế bước nhân viên vận hành xác nhận thanh toán và trạng thái triển khai/kiểm chứng; không ghi hành trình đó đã đầy đủ chỉ vì có hàm tính phí.

**Test bonus ưu tiên:** ưu tiên và phá hòa; không vượt công suất; không cấp cổng lỗi; thông báo/hoàn thành; đúng mốc ân hạn và khối quá giờ; unplug trả cổng/công suất; phí không thu hai lần.

**Checklist TV5:**

- [ ] `TV5-01` — Lập danh sách lớp hiện có/lớp đề xuất SS5 và ánh xạ đến code.
- [ ] `TV5-02` — Thiết kế ChargingService theo `INT-01`, `INT-02`, `INT-05` và quy tắc thu tiền mục 2.3.
- [ ] `TV5-03` — Tạo class diagram nguồn + ảnh, tên phương thức đã được đối chiếu code.
- [ ] `TV5-04` — Mô tả kW/kWh, công suất, trạng thái cổng/phiên và quyền cập nhật theo mục 2.2.
- [ ] `TV5-05` — Mô tả đủ phương thức, thuật toán, điều kiện trước/sau và cách phá hòa ưu tiên.
- [ ] `TV5-06` — Ghi rõ ân hạn/khối phí 15 phút và giới hạn của luồng nhân viên xác nhận thanh toán.
- [ ] `TV5-07` — Hoàn thành báo cáo nháp, truy vết, test case bonus nếu thực hiện và khai báo AI.
- [ ] `TV5-08` — Tự kiểm tra SS5, thuật toán, dữ liệu điện/phí; ghi `self_check.md`.
- [ ] `TV5-09` — Tự đối chiếu đầu vào/đầu ra giao tiếp SS2/SS7 và việc gọi BillingService đúng trách nhiệm.
- [ ] `TV5-10` — Tự sửa lỗi SS5, kiểm tra lại và lưu kết quả thực tế.
- [ ] `TV5-11` — Xuất PDF hoàn chỉnh, bàn giao cùng nguồn và chính sách sạc đúng phiên bản.
- [ ] `TV5-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

### 5.6. TV6 — Hoàng Văn Tấn — SS6 và tổng hợp truy vết

**Phạm vi UC:**

- `UC_SS6_01`: Mô phỏng tăng đột biến nhu cầu khách Metro (What-if Metro Surge).
- `UC_SS6_02`: Dự báo phụ tải nhu cầu và phân tích hàng đợi 24h.

**Đọc trước:** `src/components/sim_demand.py`, `src/core/simulator.py`, `src/core/state.py`; sơ đồ SS6; `tests/test_simulations.py` và test preview/apply/dự báo liên quan.

**Thiết kế cụ thể:**

1. Kế thừa `HubEventSimulator`; TV6 sở hữu schema `DemandScenario`, `ForecastResult`, `SimulationPreview` và `SimulationCoordinator` theo mục 2.2. TV7 dùng trực tiếp schema và giao tiếp Apply chung, đồng thời sở hữu nghiệp vụ tạo preview sự cố của mình.
2. Ánh xạ `simulate_metro_surge` và `generate_demand_forecast`; mô tả đầu vào, khoảng thời gian, seed, đầu ra và giới hạn thuật toán.
3. UC yêu cầu **24 giờ**: thể hiện rõ cách yêu cầu horizon 24 giờ; không suy ra đã đúng từ giá trị mặc định của một hàm có thể đang là 12 giờ.
4. Preview dùng dữ liệu tách biệt; Apply kiểm tra trạng thái đã thay đổi kể từ lúc preview, tránh ghi đè và áp dụng cùng kết quả nhiều lần.
5. Phân biệt lượng được tiếp nhận, lượng không được phục vụ, độ dài hàng chờ và thời gian chờ; ghi đơn vị, giả định và cách xử lý dữ liệu không hợp lệ.
6. Cùng đầu vào và seed phải tái tạo được kết quả nghiệp vụ; tách thời gian log khỏi tiêu chí so sánh nếu log dùng đồng hồ thực.
7. Với `US-21`, ghi rõ mô hình biến động doanh thu theo nhu cầu còn thiếu ở prototype. Đề xuất đầu vào/công thức/kết quả nếu thiết kế mở rộng; không nhận doanh thu hiện tại của dashboard làm bằng chứng cho mô hình dự báo doanh thu.
8. Tổng hợp bảng truy vết của cả nhóm; kiểm tra đủ 17 UC và báo chủ phân hệ sửa ô thiếu. Tổng hợp test bằng cách dẫn nguồn, không tự ghi PASS thay tác giả.

**Test bonus ưu tiên:** nhu cầu bằng 0; nhu cầu vượt sức chứa; dữ liệu âm/không hợp lệ; tái lập theo seed; dự báo đủ 24 giờ; preview không đổi gốc; Apply hợp lệ/stale/lặp.

**Checklist TV6:**

- [ ] `TV6-01` — Lập danh sách lớp SS6, đầu vào/đầu ra dự báo và ánh xạ đến code.
- [ ] `TV6-02` — Tạo class diagram nguồn + ảnh, phân biệt mô hình, service và UI.
- [ ] `TV6-03` — Mô tả ForecastResult, SimulationPreview và SimulationCoordinator theo quyết định mục 2.2–2.3.
- [ ] `TV6-04` — Mô tả đủ phương thức, đơn vị, seed, horizon 24 giờ và preview/apply.
- [ ] `TV6-05` — Ghi rõ giả định và giới hạn mô hình doanh thu US-21.
- [ ] `TV6-06` — Hoàn thành báo cáo nháp, test case bonus nếu thực hiện, khai báo AI và truy vết SS6.
- [ ] `TV6-07` — Tổng hợp truy vết đủ 17 UC theo bảng các tác giả cung cấp; ghi các ô còn thiếu và chủ sở hữu.
- [ ] `TV6-08` — Tự kiểm tra SS6 và cơ chế preview/apply mình sở hữu; ghi `self_check.md`.
- [ ] `TV6-09` — Tự sửa/kiểm tra lại SS6; cập nhật truy vết/test index theo bản bàn giao của từng tác giả.
- [ ] `TV6-10` — Phân biệt test đã chạy, chưa chạy và mới thiết kế trong bảng chung.
- [ ] `TV6-11` — Xuất PDF cá nhân hoàn chỉnh, bàn giao nguồn và bảng truy vết cuối.
- [ ] `TV6-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

### 5.7. TV7 — Nguyễn Trung Nguyên — SS7 và Deployment view

**Phạm vi UC:**

- `UC_SS7_01`: Mô phỏng sự cố hạ tầng & Mất điện trạm sạc.
- `UC_SS7_02`: Đề xuất gợi ý điều hướng tự động sang Hub lân cận & Cảnh báo.

**Đọc trước:** `src/components/sim_infrastructure.py`, `src/core/simulator.py`, `src/core/routing.py`, `src/core/booking.py`, `src/core/scheduler.py`, `src/app.py`; sơ đồ SS7; test mô phỏng/điều hướng liên quan.

**Thiết kế cụ thể:**

1. Kế thừa simulator chung với TV6; đề xuất `InfrastructureFailure`, `RouteSuggestion`, `ReroutingService` nếu phù hợp. Ánh xạ `simulate_port_failure`, `find_alternative_hubs`/`find_nearest_alternative_hubs` và xử lý áp dụng gợi ý.
2. Phân biệt cổng rảnh bị lỗi, cổng đang sạc bị lỗi và mất điện. Ghi ảnh hưởng tới cổng, phiên, hàng chờ, công suất và dữ liệu Hub; không tự làm thay đổi sức chứa chỗ đỗ khi chỉ có lỗi cổng sạc.
3. Gợi ý Hub phải kiểm tra nhu cầu chỗ đỗ/cổng sạc, tình trạng hoạt động và khoảng cách. Kiểm tra lại điều kiện khi Apply; không coi gợi ý cũ là bảo đảm còn chỗ.
4. Việc thay đổi booking phải thể hiện xác nhận người dùng và cập nhật giữ chỗ ở Hub cũ/mới. **Ưu đãi điều hướng hiện là 15 phút** theo `REROUTING_EXTRA_FREE_MINUTES`, tách biệt thời hạn giữ chỗ 30 phút.
5. Dùng schema `SimulationPreview` và `SimulationCoordinator.apply_preview` theo mục 2.3, không tự tạo một cơ chế Apply thứ hai. Không ghi đã hỗ trợ phục hồi tự động nếu mới là thao tác mô phỏng/đề xuất.
6. Vẽ **Deployment view** hiện tại: trình duyệt → tiến trình ứng dụng Streamlit/Python → module và dữ liệu seed/session. Ghi rõ vị trí lưu dữ liệu, vòng đời session, reset và thành phần mô phỏng. Giao thức/cổng chỉ ghi khi có căn cứ cấu hình hoặc ghi là cấu hình dự kiến.
7. Nếu có deployment tương lai, vẽ riêng và chú thích rõ database/SSO/IoT/payment gateway chưa phải tích hợp đang vận hành. Đối chiếu hướng dẫn chạy bằng `streamlit run src/app.py`.

**Test bonus ưu tiên:** lỗi cổng rảnh/đang bận; không còn Hub thay thế; lọc Hub đầy/lỗi; xếp hạng khoảng cách; preview không đổi dữ liệu gốc; Apply stale/lặp; áp dụng điều hướng và ưu đãi đúng một lần.

**Checklist TV7:**

- [ ] `TV7-01` — Lập danh sách lớp SS7 và thông tin thực tế cho Deployment view.
- [ ] `TV7-02` — Mô tả triển khai hiện tại và sử dụng schema preview/Apply đã chốt ở mục 2.3.
- [ ] `TV7-03` — Tạo class diagram SS7 và Deployment view, đủ nguồn + ảnh.
- [ ] `TV7-04` — Mô tả tác động sự cố, gợi ý Hub và cách gọi giao tiếp `INT-05` đến `INT-10` trong phần SS7.
- [ ] `TV7-05` — Mô tả đủ phương thức, điều kiện Apply/điều hướng và giới hạn tích hợp ngoài.
- [ ] `TV7-06` — Hoàn thành báo cáo nháp, truy vết, test case bonus nếu thực hiện và khai báo AI.
- [ ] `TV7-07` — Tự kiểm tra SS7, sự cố, điều hướng và Deployment view; ghi `self_check.md`.
- [ ] `TV7-08` — Tự đối chiếu ánh xạ dữ liệu vào ChargingService/SimulationCoordinator; kiểm tra hướng dẫn chạy và vòng đời session.
- [ ] `TV7-09` — Tự sửa lỗi, kiểm tra lại; xuất Deployment view hoàn chỉnh có chú giải/thuyết minh.
- [ ] `TV7-10` — Cung cấp nguồn, ảnh, phiên bản và thuyết minh triển khai chung cho cả nhóm.
- [ ] `TV7-11` — Xuất PDF cá nhân hoàn chỉnh, kiểm tra hình deployment và bàn giao cùng nguồn.
- [ ] `TV7-12` — Xác nhận đúng bộ file và hoàn tất trách nhiệm nộp theo LMS.

## 6. Mẫu nội dung để các thành viên làm thống nhất

### 6.1. Mẫu mô tả lớp

| Trường | Nội dung cần điền |
| --- | --- |
| Class ID / tên lớp | Ví dụ `SS1-CLS-01 / Booking`; dùng một tên xuyên suốt |
| Trách nhiệm | Lớp chịu trách nhiệm gì, thuộc SS nào, ai chủ trì |
| Mức triển khai | Đã có trong code / ánh xạ từ hàm-dictionary / thiết kế đề xuất / tương lai |
| Thuộc tính | Tên, kiểu, đơn vị, bắt buộc/tùy chọn và ý nghĩa |
| Quan hệ | Lớp liên quan, vai trò, bội số, quyền sở hữu và vòng đời |
| Ràng buộc | Điều kiện dữ liệu/trạng thái luôn phải đúng |
| Phương thức | Danh sách ID phương thức tương ứng phần mô tả chi tiết |
| Truy vết | US/FR/UC và vị trí code có liên quan |

### 6.2. Mẫu mô tả phương thức

| Trường | Nội dung cần điền |
| --- | --- |
| Method ID | Ví dụ `SS1-MTH-03` |
| Lớp và chữ ký | Chữ ký theo ví dụ bên dưới; phải khớp class diagram. |
| Mục đích và bên gọi | Thực hiện hành vi gì, ai có quyền gọi |
| Tham số | Tên, kiểu, đơn vị, phạm vi hợp lệ; quy ước thời gian/ID |
| Kết quả trả về | Kiểu, trường dữ liệu và ý nghĩa; tránh chỉ ghi “success” |
| Điều kiện trước | Trạng thái và quyền phải thỏa trước khi thực hiện |
| Xử lý chính | Các bước nghiệp vụ, kiểm tra quan trọng và giao tiếp ngoài |
| Điều kiện sau | Dữ liệu/trạng thái sau thành công và các invariant được giữ |
| Lỗi/ngoại lệ | Mã/lý do lỗi và hệ thống có thay đổi dữ liệu hay không |
| Xử lý lặp/xung đột | Lời gọi lặp, dữ liệu stale, thao tác cạnh tranh nếu có |
| Tác động dữ liệu | Ví, xe, chỗ đỗ, cổng, hóa đơn, log; chỉ ra phạm vi cập nhật |
| Truy vết và kiểm thử | UC, thông điệp sequence, code hiện có, test case liên quan |

Ví dụ chữ ký:

```text
BookingService.cancel_booking(
    booking_id: str,
): OperationResult[CancellationResult]
```

ví dụ thiết kế theo quy ước snake_case, không phải khẳng định tên lớp đã có trong code.

**Ví dụ ràng buộc cho hủy SS1:** booking còn được phép hủy; `now < expires_at`; giải phóng giữ chỗ/xe theo đúng trạng thái; hoàn cọc một lần. Nếu `now >= expires_at`, chuyển sang xử lý hết hạn theo chính sách, không áp dụng nhầm hoàn cọc toàn phần. Quy tắc này phải xuất hiện nhất quán ở sơ đồ, mô tả và test.

### 6.3. Mẫu bảng truy vết

| Trường | Nội dung mẫu |
| --- | --- |
| US/FR có thật | Điền từ SRS/manifest |
| UC hiện hành | `UC_SSx_yy` |
| File/thông điệp Sequence hoặc nhánh Activity | Ghi tên file và thông điệp/nhánh cụ thể |
| Lớp | Tên thống nhất |
| Method ID/chữ ký | Khớp sơ đồ và mô tả |
| Code hiện tại hoặc đề xuất | Đường dẫn + tên hàm; hoặc ghi chưa triển khai |
| Test ID | Test tương ứng hoặc chưa thiết kế |

Một UC có thể ánh xạ nhiều lớp/phương thức. Không chỉ ghi “SS1 → BookingService” rồi coi là đã truy vết đủ. Với luồng lỗi, phải xác định nơi kiểm tra điều kiện và nơi xử lý hậu quả.

### 6.4. Mẫu test case bonus

| Trường | Nội dung |
| --- | --- |
| Test ID / UC / Method ID | Ví dụ `TC-SS1-EXP-02`, liên kết được đến thiết kế |
| Tiền điều kiện | Trạng thái ban đầu, thời điểm, ví, xe/Hub/cổng liên quan |
| Dữ liệu vào | Giá trị cụ thể và đơn vị |
| Các bước | Từng thao tác có thể lặp lại |
| Kết quả mong đợi | Trạng thái, dữ liệu, số tiền và invariant cụ thể |
| Kết quả thực tế | Chỉ điền khi đã chạy; kèm bằng chứng/log nếu có |
| Trạng thái | `DESIGNED`, `NOT_RUN`, `PASS`, `FAIL` hoặc `BLOCKED` |
| Người/ngày kiểm tra | Ghi đúng thực tế, không suy ra từ ngày tạo tài liệu |

Mục tiêu nội bộ: mỗi UC có ít nhất một ca chính và một ca lỗi/ngoại lệ; bổ sung ca biên quan trọng như đúng deadline và lời gọi lặp. Có thể dùng lại test sẵn có nếu chỉ rõ nó kiểm tra phương thức/tiêu chí nào. **Không ghi PASS cho test chỉ mới được viết trong tài liệu.**

### 6.5. Mẫu tự kiểm tra và danh sách vấn đề

| Trường | Nội dung mẫu |
| --- | --- |
| Issue ID | `S3-ISS-001` |
| SS/file/vị trí | Điền cụ thể |
| Vấn đề và ảnh hưởng | Ghi điều sai/thiếu và kết quả mong muốn |
| Mức độ | Blocker/Major/Minor |
| Tác giả phụ trách | TVx |
| Bằng chứng sửa | File/commit/ảnh |
| Kết quả tự kiểm tra lại | Kết quả do tác giả ghi |
| Trạng thái | OPEN/FIXED/SELF_CHECKED hoặc để mở có lý do |

- **Blocker:** thiếu nội dung bắt buộc, file không mở được, thiếu cả UC hoặc không thể nộp đúng yêu cầu.
- **Major:** sai chính sách, mâu thuẫn giao tiếp, thiếu mô tả phương thức, sai trạng thái/tài chính/sức chứa hoặc tuyên bố triển khai không đúng.
- **Minor:** lỗi diễn đạt/định dạng không làm sai nghĩa nhưng vẫn cần sửa khi có thời gian.
- `FIXED` nghĩa là tác giả đã sửa; `SELF_CHECKED` nghĩa là tác giả đã tự đối chiếu lại kết quả và lưu bằng chứng. Hạn chế đã biết có thể được ghi mở rõ ràng, không tự biến thành tính năng đã hoàn thành.

Trong `self_check.md`, mỗi thành viên ghi: họ tên, phạm vi chịu trách nhiệm, phiên bản file, ngày tự kiểm tra, kết quả từng tiêu chí ở mục 8.1 và vấn đề còn mở. Khi bàn giao, tác giả xác nhận **đã tự kiểm tra và chịu trách nhiệm về nội dung, tiến độ, bằng chứng thực hiện của phần mình**. Chỉ xác nhận khi thực sự đã làm.

## 7. Các chính sách phải đồng bộ trong Sub3

Giá trị dưới đây đối chiếu từ `src/core/policies.py` và chính sách hiện tại lúc lập hướng dẫn. Nếu nhóm thay đổi, TV1 ghi quyết định và cập nhật đồng thời các tài liệu, sơ đồ, code/test liên quan; không sửa riêng từng báo cáo.

| Chủ đề | Giá trị/quy tắc cần giữ nhất quán | Chủ sở hữu mô tả |
| --- | --- | --- |
| Giữ xe dùng chung SS1 | 30 phút từ lúc tạo booking; chưa nhận và `now >= expires_at` thì hết hạn | TV1 |
| Hạn đến SS2 | 30 phút từ `booking_start_time`; không phải từ lúc bấm đặt | TV2 |
| Cọc/no-show SS1 và SS2 | Cọc 50.000 VNĐ; phạt 10.000; hoàn phần còn lại 40.000; không quyết toán lặp | TV1 |
| Ưu đãi điều hướng | Thêm 15 phút miễn phí theo hằng số hiện hành, không phải kéo TTL giữ chỗ | TV1 |
| Ân hạn và phí chiếm dụng sạc | Ân hạn 15 phút; khối phí 15 phút; 10.000 VNĐ/khối bắt đầu sau ân hạn | TV5 |
| Công suất sạc | Mặc định 150 kW/Hub, 11 kW/cổng; ràng buộc theo cấu hình và công suất đang hoạt động | TV5 |
| Cảnh báo occupancy | Normal <70%; Warning 70–<85%; Critical 85–<100%; Full >=100% | TV3 |
| Xe cá nhân và xe chung | Ownership tách biệt; xe PERSONAL không cho thuê SS1 hoặc điều chuyển SS4 | TV1 |
| Giá trị tài chính | VNĐ lưu số nguyên; nợ và khoản đã thu được thể hiện rõ | TV1 |
| Đơn vị năng lượng/công suất | Phân biệt kW và kWh trong thuộc tính, giao tiếp và công thức | TV5 |
| Mô phỏng | Preview cách ly; Apply kiểm tra trạng thái/phiên bản và tránh áp dụng trùng | TV6 |

Các điểm phải công khai trong thiết kế và theo dõi quyết định:

1. **US-06:** hóa đơn chưa có dữ liệu đo quãng đường chuyến đi trong prototype.
2. **US-12:** hành trình nhân viên vận hành xác nhận thanh toán chưa được kiểm chứng đầy đủ.
3. **US-21:** chưa có mô hình biến động doanh thu theo nhu cầu.
4. **Phí đỗ xe cá nhân:** thiết kế mặc định giữ 5.000 VNĐ/lượt như prototype; vẫn ghi rõ phần này chưa đáp ứng cách tính theo giờ của SRS.

Đây là điểm cần thiết kế/ghi giới hạn, không phải yêu cầu tự động triển khai toàn bộ tính năng còn thiếu trong đợt này. Chủ sở hữu phải nêu phương án, phạm vi và trạng thái thực tế.

## 8. Tự kiểm tra, bàn giao và chuẩn bị nộp

### 8.1. Mỗi thành viên tự kiểm tra gì?

Mỗi thành viên tự đọc **PDF và nguồn sơ đồ của mình**, đối chiếu các tiêu chí dưới đây và bàn giao kèm `self_check.md`. Các tác giả tự xử lý lỗi thuộc phần mình, cập nhật kết quả sau sửa và tự bảo đảm phần giao tiếp tuân thủ hợp đồng đã chốt ở mục 2.3.

- [ ] Có đủ Deployment view và Development/Implementation view; phân biệt đúng vai trò hai view.
- [ ] Phạm vi UC cá nhân đầy đủ: SS1 có 3, SS2 có 4, SS3–SS7 mỗi SS có 2.
- [ ] Class diagram thể hiện trách nhiệm, kiểu dữ liệu, quan hệ và bội số hợp lý.
- [ ] Mọi phương thức được vẽ có mô tả tương ứng; tên và chữ ký khớp nhau.
- [ ] Có điều kiện trước/sau, lỗi, tác động dữ liệu và quy tắc xử lý lặp khi cần.
- [ ] Truy vết đến đúng UC và thông điệp/nhánh từ Sub2; không dùng ID tự đặt thay ID chuẩn.
- [ ] Lớp và giao tiếp dùng chung khớp bản đã chốt; không có bảy định nghĩa Hub khác nhau.
- [ ] Mốc 30 phút đúng phạm vi; các quy tắc 15 phút khác không bị thay theo.
- [ ] Trạng thái và đơn vị đúng; bảo toàn sức chứa, công suất và tài chính được giải thích.
- [ ] Phân biệt code hiện tại với thiết kế đề xuất, mock và mở rộng tương lai.
- [ ] Test có đầu vào/kết quả cụ thể; trạng thái PASS có bằng chứng thực thi.
- [ ] PDF đọc được, không cắt hình/bảng; đóng góp cá nhân và AI được khai báo đúng.

### 8.2. Kiểm tra kỹ thuật khi có sửa code hoặc sơ đồ

Chạy từ thư mục gốc `smart-emobility-hub`, dùng môi trường Python đã cài dependencies của dự án:

```bash
# Chạy demo và kiểm tra các luồng bị ảnh hưởng khi có thay đổi triển khai
streamlit run src/app.py

# Chạy bộ kiểm thử hiện có khi thay đổi code dùng chung hoặc trước tích hợp
python -m pytest -q

# Kiểm tra cú pháp một sơ đồ Sub3 đã tạo bằng PlantUML
java -jar tools/plantuml.jar --check-syntax "docs/diagrams/submission_3/**/*.puml"

# Xuất ảnh từ đúng file nguồn đó; thay đường dẫn theo thành viên/sơ đồ
java -jar tools/plantuml.jar --png "docs/diagrams/submission_3/**/*.puml"
```

Nguồn sơ đồ khung Sub3 đã được tạo; chỉ xuất ảnh sau khi kiểm tra và cập nhật nội dung cần dùng. Nếu dùng Draw.io thì kiểm tra nguồn `.drawio` và xuất ảnh/PDF tương ứng. Script render hiện tại `scripts/render_all_diagrams.py` nhắm vào cây sơ đồ use case cũ; không mặc định coi nó đã render thư mục Sub3 mới. Không cần chạy lại toàn bộ test cho mỗi lần sửa câu chữ; chọn kiểm tra phù hợp và lưu kết quả khi thực sự đã chạy.

### 8.3. Checklist bàn giao

- [ ] Cả 7 thành viên nộp đủ nguồn và PDF cá nhân; tên và MSSV chính xác.
- [ ] Hai view kiến trúc chung v1.0 được đưa vào các báo cáo cùng phiên bản.
- [ ] Class diagram cấp hệ thống khớp liên kết giữa các SS; ảnh tổng quan có thể đọc được.
- [ ] Tổng cộng 17 UC đã được truy vết; từng người xác nhận phạm vi của mình.
- [ ] Mỗi phương thức trên sơ đồ có mô tả; không còn ô mẫu hoặc chỗ “TODO” trong phần bắt buộc.
- [ ] Hợp đồng tài chính SS1–SS2–SS5, sạc SS2–SS5–SS7 và mô phỏng SS6–SS7 được xác nhận.
- [ ] Thời hạn 30 phút và các chính sách dùng chung nhất quán với quyết định cuối.
- [ ] Mỗi tác giả xác nhận phần mình không còn Blocker; Major đã tự sửa/kiểm tra lại hoặc giới hạn được ghi rõ cùng phương án xử lý và người chịu trách nhiệm.
- [ ] Mỗi người bàn giao `self_check.md`, ghi phiên bản và tự chịu trách nhiệm về thiết kế, bằng chứng và giới hạn của phần mình.
- [ ] Khai báo AI/đóng góp đúng thực tế; prompt history không chứa hội thoại hay mốc giờ bị bịa.
- [ ] Mở PDF kiểm tra trực quan: mục lục, số trang, bảng, sơ đồ, phông chữ và ký tự tiếng Việt.
- [ ] Bộ file nộp có phiên bản rõ ràng, được lưu riêng để tránh nhầm với bản nháp.

### 8.4. Checklist nộp bài

- [ ] TV1 đối chiếu lại giờ đóng, tài khoản cần nộp, số lượng/định dạng và giới hạn dung lượng trên LMS.
- [ ] Nếu nộp cá nhân: cả 7 người nộp đúng báo cáo của mình; không mặc định một người nộp thay là đủ.
- [ ] Nếu LMS yêu cầu nộp nhóm: chỉ định rõ người thực hiện và file/bộ file được yêu cầu.
- [ ] Mở lại đúng các file sẽ tải lên, kiểm tra tên, nội dung, hình và khả năng đọc.
- [ ] Hoàn tất nộp trước giờ đóng LMS của ngày kết thúc.
- [ ] Kiểm tra trạng thái nộp thành công/biên nhận; lưu bằng chứng theo cách hệ thống cho phép.
- [ ] Nếu có thay file, kiểm tra lại phiên bản cuối đã nằm trên LMS và trạng thái đã lưu/gửi.
- [ ] Lưu bộ file đã nộp, nguồn tương ứng và ghi nhận đóng góp của từng người.

## 9. Bảng theo dõi nhanh dành cho trưởng nhóm

Điền `Chưa bắt đầu / Đang làm / Đang tự kiểm tra / Cần sửa / Đã tự kiểm tra / Đã bàn giao` kèm link hoặc phiên bản thực tế. Dấu `—` hiện tại nghĩa là **chưa ghi nhận**, không phải hoàn thành. Trạng thái chất lượng nội dung do chính tác giả xác nhận; trưởng nhóm theo dõi thời hạn và tiếp nhận bản bàn giao.

Các hạng mục theo dõi: Lớp/giao tiếp, Sơ đồ, Mô tả, PDF nháp, Tự kiểm tra, Tự sửa, PDF cuối, Xác nhận nộp.

| Thành viên | Tiến độ / đường dẫn sản phẩm |
| --- | --- |
| TV1 — Nguyễn Thành Đạt | Có bộ nguồn/PDF revision tích hợp06/11/2026; đã review kỹ thuật, chờ chủ sở hữu đọc/xác nhận. |
| TV2 — Nguyễn Anh Tài | Có bộ nguồn/PDF revision tích hợp06/11/2026; đã review kỹ thuật, chờ chủ sở hữu đọc/xác nhận. |
| TV3 — Phạm Tiến Đạt | Có bộ nguồn/PDF revision tích hợp06/11/2026; đã review kỹ thuật, chờ chủ sở hữu đọc/xác nhận. |
| TV4 — Đặng Hoàng Quý Nhân | Có bộ nguồn/PDF revision tích hợp06/11/2026; đã review kỹ thuật, chờ chủ sở hữu đọc/xác nhận. |
| TV5 — Dương Đăng Khoa | Có bộ nguồn/PDF revision tích hợp06/11/2026; đã review kỹ thuật, chờ chủ sở hữu đọc/xác nhận. |
| TV6 — Hoàng Văn Tấn | Có bộ nguồn/PDF revision tích hợp06/11/2026; đã review kỹ thuật, chờ chủ sở hữu đọc/xác nhận. |
| TV7 — Nguyễn Trung Nguyên | Có bộ nguồn/PDF revision tích hợp06/11/2026; đã review kỹ thuật, chờ chủ sở hữu đọc/xác nhận. |

| Sản phẩm chung | Chủ sở hữu / tổng hợp | Nội dung và trạng thái |
| --- | --- | --- |
| Hướng dẫn và phân công | TV1 | `GUIDANCE_FOR_SUB_3.md`; **Trạng thái:** đã hoàn thiện và gửi cho nhóm theo xác nhận trưởng nhóm. |
| Cấu trúc và bộ khung Sub3 | TV1 điều phối, có hỗ trợ AI | Cây báo cáo, sơ đồ, truy vết, prompt và đầu ra theo mục 4.1; **Trạng thái:** đã khởi tạo và kiểm tra cấu trúc; nội dung cá nhân còn là khung. |
| Hợp đồng liên phân hệ | TV1 | `docs/report/submission_3/shared/shared_contracts.md` tập hợp quyết định mục 2.2–2.3; **Trạng thái:** đã hoàn thành tài liệu hợp đồng thiết kế, chưa phải xác nhận đã triển khai code. |
| Development/Implementation view | TV3 | Đã bổ sung nguồn/ảnh/thuyết minh trong revision tích hợp06/11; chờ TV3 xác nhận. |
| Deployment view | TV7 | Đã tiếp nhận từ PR20, dùng chung revision tích hợp06/11; chờ xác nhận cuối. |
| Class diagram cấp hệ thống | TV3 | Đã bổ sung tổng quan quyền sở hữu/liên kết; chi tiết ở7 sơ đồ SS, chờ TV3 xác nhận. |
| Truy vết 17 UC và danh mục test | TV6 | Đã sửa ID/path/test theo SRS và nguồn;17 UC REVIEWED/OWNER_PENDING. |
| Danh sách vấn đề tự báo | TV4 | Đã bổ sung13 vấn đề chốt nộp/giới hạn prototype, ghi chủ sở hữu và trạng thái có bằng chứng. |
| Bộ báo cáo sẵn sàng nộp | Mỗi người; TV1 tập hợp | PDF, nguồn, ảnh, xác nhận tự kiểm tra và danh sách phiên bản; **Trạng thái:** — |

## 10. Cách sử dụng AI và ghi nhận đóng góp

- Có thể dùng AI hỗ trợ phân tích, đề xuất thiết kế, rà soát và định dạng; mỗi người tự đối chiếu code/đề và giải thích được quyết định của mình.
- Ghi đúng công cụ, phạm vi và mức đóng góp; không viết mẫu cam kết “chỉ tham khảo” nếu AI thực tế đã tạo phần lớn nội dung.
- Lưu prompt thực tế của Submission 3 tại thư mục prompt history cá nhân; ghi phần tự sửa, kiểm tra và quyết định giữ/bỏ gợi ý của AI.
- Không tự dựng hội thoại, thời gian họp, xác nhận tự kiểm tra, kết quả test hay xác nhận đã nộp. Phần tóm tắt phải ghi là tóm tắt.
- Khi tái sử dụng kiến trúc/lớp chung, ghi người chủ trì và phần mình tham gia; không nhận toàn bộ sản phẩm nhóm là sản phẩm cá nhân.
- Các thư mục/biên bản Sub1 và Sub2 là lịch sử; cập nhật phần hiện hành cho Sub3 mà không sửa prompt gốc hoặc ghi lại lịch sử thành việc mới hoàn thành.

**Việc đầu tiên của mỗi thành viên:** đọc phạm vi SS/UC, sequence/activity và quyết định mục 2.2–2.3; bắt đầu thiết kế phần mình mà không chờ họp. **Việc đầu tiên của trưởng nhóm:** kiểm tra LMS, cung cấp hướng dẫn này cho nhóm và tập hợp các quyết định dùng chung vào `shared_contracts.md`.


## Revision tích hợp 06/11/2026

Không đổi quyền sở hữu/chữ ký mục 2.2–2.3. Các trường tối thiểu của SimulationPreview gồm `preview_id`, `scenario_type`, `baseline_version`, `modified_hubs`, `charging_effects`, `summary`, `is_applied`; được thêm `target_hub_id` và `event_log` để ánh xạ UI. Adapter ánh xạ `metrics` của prototype vào `summary`, không thay thế hay bỏ `charging_effects`. Thiết kế dùng `scenario_type=DEMAND/PORT_FAILURE`. Prototype chưa có đầy đủ DTO này.

Hub chuẩn có `hub_id/name/latitude/longitude/total_slots/available_slots/destination_holds/background_occupied/current_vehicles/charging_ports`. Trong sơ đồ con, Hub rỗng hoặc một projection không tạo lớp chủ sở hữu mới. `PersonalVehicle` kế thừa `Vehicle`, liên kết `User` qua `owner_id`; không kế thừa lớp gộp User/Vehicle.

Trong thiết kế, `datetime` dùng UTC+7 theo đồng hồ mô phỏng; adapter đọc chuỗi naive hiện có theo quy ước này, không khẳng định prototype đã timezone-aware. `BookingStatus` và `ParkingReservationStatus` là enum thiết kế riêng; không tuyên bố `ReservationStatus` hiện có chứa IN_USE/CHECKED_IN.

Snapshot doanh thu mục tiêu cộng khoản thu thực đã đối soát của SS1/SS2/SS5, loại cọc và tiền hoàn, tách khoản nợ; hiện dashboard chỉ cộng một số giao dịch SS1. Dashboard hiện ước tính `(total-available)*7.4 kW` có thể tính cả offline, khác scheduler mặc định 11 kW/cổng; không dùng ước tính này như số đo công suất thật. Các điểm này được ghi trong open_issues.md.
