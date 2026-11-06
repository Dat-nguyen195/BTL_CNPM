# Hợp đồng và quyền sở hữu dùng chung — Submission 3

**Trạng thái:** quyết định thiết kế đã chốt, chưa phải xác nhận đã triển khai.  
**Đầu mối tập hợp:** TV1 — Nguyễn Thành Đạt.

[Hướng dẫn gốc](<../../../../GUIDANCE_FOR_SUB_3.md>) — nội dung dưới đây tập hợp mục 2.2–2.3 để các thành viên tham chiếu. Khi thay đổi quyết định, cập nhật đồng thời hướng dẫn gốc và bản này; ghi thay đổi bằng văn bản. Các lớp và service thiết kế mục tiêu vẫn cần mô tả chi tiết trong báo cáo của chủ sở hữu.

## 2.2. Lớp và dữ liệu dùng chung — quyết định áp dụng

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

## 2.3. Giao tiếp liên phân hệ — chữ ký và trách nhiệm đã chốt

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


## Revision tích hợp 06/11/2026

Không đổi quyền sở hữu/chữ ký mục 2.2–2.3. Các trường tối thiểu của SimulationPreview gồm `preview_id`, `scenario_type`, `baseline_version`, `modified_hubs`, `charging_effects`, `summary`, `is_applied`; được thêm `target_hub_id` và `event_log` để ánh xạ UI. Adapter ánh xạ `metrics` của prototype vào `summary`, không thay thế hay bỏ `charging_effects`. Thiết kế dùng `scenario_type=DEMAND/PORT_FAILURE`. Prototype chưa có đầy đủ DTO này.

Hub chuẩn có `hub_id/name/latitude/longitude/total_slots/available_slots/destination_holds/background_occupied/current_vehicles/charging_ports`. Trong sơ đồ con, Hub rỗng hoặc một projection không tạo lớp chủ sở hữu mới. `PersonalVehicle` kế thừa `Vehicle`, liên kết `User` qua `owner_id`; không kế thừa lớp gộp User/Vehicle.

Trong thiết kế, `datetime` dùng UTC+7 theo đồng hồ mô phỏng; adapter đọc chuỗi naive hiện có theo quy ước này, không khẳng định prototype đã timezone-aware. `BookingStatus` và `ParkingReservationStatus` là enum thiết kế riêng; không tuyên bố `ReservationStatus` hiện có chứa IN_USE/CHECKED_IN.

Snapshot doanh thu mục tiêu cộng khoản thu thực đã đối soát của SS1/SS2/SS5, loại cọc và tiền hoàn, tách khoản nợ; hiện dashboard chỉ cộng một số giao dịch SS1. Dashboard hiện ước tính `(total-available)*7.4 kW` có thể tính cả offline, khác scheduler mặc định 11 kW/cổng; không dùng ước tính này như số đo công suất thật. Các điểm này được ghi trong open_issues.md.
