# SS5 – TRACEABILITY MATRIX

## 1. UC_SS5_01 – Lập lịch ưu tiên sạc tự động

| Hạng mục | Nội dung |
|---|---|
| Use Case ID | UC_SS5_01 |
| Use Case Name | Lập lịch ưu tiên sạc tự động (Automatic Priority Charging Schedule) |
| Responsible Member | TV5 – Dương Đăng Khoa |
| Related User Stories | US-10, US-18, US-20 |
| Related Functional Requirements | FR-04, FR-05b, FR-09, FR-11 |
| Scenario | `docs/diagrams/Use-case detail-scenario/SS5/Usecase scenario/UC_SS5_DuongDangKhoa.md` |
| Sequence Diagram | `docs/diagrams/Use-case detail-scenario/SS5/Sequence diagrams/UC_SS5_01_DuongDangKhoa_sequence.puml` |
| Activity Diagram | `docs/diagrams/Use-case detail-scenario/SS5/Activity diagrams/UC_SS5_01_DuongDangKhoa_activity.puml` |
| Component / Source Code | `src/components/smart_charging.py`, `src/core/scheduler.py`, `src/core/policies.py` |

### 1.1. Class and Method Traceability

| Class / Component | Method / Attribute | Responsibility |
|---|---|---|
| ChargingRequest | `__post_init__()` | Tự động tính điểm ưu tiên khi request chưa có priority score. |
| ChargingRequest | `vehicle_id`, `hub_id`, `battery_soc`, `has_student_booking`, `requested_at`, `priority_score`, `port_kw` | Lưu thông tin phương tiện và yêu cầu sạc. |
| SmartChargingScheduler | `calculate_priority(request)` | Tính điểm ưu tiên dựa trên SoC, tình trạng booking và mức pin thấp. |
| SmartChargingScheduler | `add_request(request)` | Thêm yêu cầu vào hàng đợi và tính lại điểm ưu tiên. |
| SmartChargingScheduler | `get_sorted_queue()` | Sắp xếp hàng đợi theo điểm ưu tiên giảm dần, thời gian yêu cầu và vehicle ID. |
| SmartChargingScheduler | `allocate_ports(hub_id, available_port_count, current_active_kw)` | Phân bổ cổng sạc theo thứ tự ưu tiên và giới hạn công suất của hub. |
| ChargingSession | Các thuộc tính `session_id`, `vehicle_id`, `hub_id`, `port_id`, `port_kw`, `current_soc`, `target_soc`, `status` | Lưu thông tin phiên sạc được tạo sau khi phân bổ. |
| SmartChargingScheduler | `queue_length` | Trả về số lượng yêu cầu còn trong hàng đợi. |
| smart_charging.py | `_init_ss5()` | Khởi tạo scheduler và đồng bộ dữ liệu phương tiện ban đầu từ session state. |
| smart_charging.py | `render()` | Hiển thị giao diện hàng đợi, thông tin ưu tiên và chức năng phân bổ cổng sạc. |

### 1.2. Sequence Message / Activity Branch Traceability

| Message / Branch ID | Nội dung | Thành phần xử lý |
|---|---|---|
| MSG-SS5-01 | Operator mở chức năng lập lịch sạc. | `smart_charging.py` – `render()` |
| MSG-SS5-02 | UI lấy danh sách xe WAITING từ AppState. | `st.session_state`, `_init_ss5()` |
| MSG-SS5-03 | UI lấy SoC và trạng thái cổng sạc. | UI / dữ liệu mô phỏng; IoT là thành phần thiết kế |
| MSG-SS5-04 | UI lấy cấu hình giới hạn công suất. | `policies.py`, `HUB_POWER_CAP_KW` |
| MSG-SS5-05 | Gửi danh sách yêu cầu đến scheduler. | `SmartChargingScheduler.add_request()` |
| MSG-SS5-06 | Tính Priority Score cho từng yêu cầu. | `SmartChargingScheduler.calculate_priority()` |
| MSG-SS5-07 | Sắp xếp hàng đợi theo Priority Score. | `SmartChargingScheduler.get_sorted_queue()` |
| MSG-SS5-08 | Yêu cầu phân bổ cổng sạc. | `SmartChargingScheduler.allocate_ports()` |
| MSG-SS5-09 | Kiểm tra giới hạn công suất và số cổng khả dụng. | `SmartChargingScheduler.allocate_ports()` |
| MSG-SS5-10 | Tạo ChargingSession khi phân bổ thành công. | `ChargingSession`, `allocate_ports()` |
| MSG-SS5-11 | Hiển thị hàng đợi và phiên sạc đã phân bổ. | `smart_charging.py` – `render()` |

**Alternative / Exception Branches**

| Branch ID | Điều kiện | Expected Handling |
|---|---|---|
| BR-SS5-01 | Dữ liệu đầu vào không hợp lệ. | Thông báo lỗi và không thực hiện phân bổ. |
| BR-SS5-02 | Không có cổng sạc khả dụng. | Giữ yêu cầu trong hàng đợi WAITING. |
| BR-SS5-03 | Tổng công suất dự kiến vượt giới hạn hub. | Không phân bổ thêm phiên sạc làm vượt giới hạn công suất; yêu cầu tiếp tục chờ. |
| BR-SS5-04 | Có cổng sạc và công suất còn khả dụng. | Tạo phiên sạc và cập nhật kết quả phân bổ. |

*Lưu ý: BR-SS5-01 là nhánh trong UML; cần đối chiếu implementation để xác nhận cơ chế validation tương ứng. Code hiện tại không tự điều chỉnh thời điểm bắt đầu hoặc công suất để xử lý trường hợp vượt giới hạn.*

### 1.3. Test Case Traceability

| Test ID | Test Function | Test Objective | Expected Result | Actual Result |
|---|---|---|---|---|
| TC-SS5-01 | `test_priority_scores_matching_plan_specification()` | Kiểm tra tính chính xác của Priority Score theo PLAN.md mục 4.5. | SoC 5%, không booking: 177.5; SoC 30%, không booking: 65.0; SoC 30%, có booking: 125.0. | Not run – chưa có kết quả thực thi được xác nhận. |
| TC-SS5-02 | `test_deterministic_tie_breaking()` | Kiểm tra thứ tự ưu tiên khi các yêu cầu có cùng Priority Score. | Yêu cầu có `requested_at` sớm hơn được xếp trước. | Not run – chưa có kết quả thực thi được xác nhận. |
| TC-SS5-03 | `test_allocation_and_power_cap()` | Kiểm tra phân bổ cổng sạc theo giới hạn công suất. | Với cap 20 kW và mỗi cổng 7.4 kW, phân bổ 2 phiên và còn 1 yêu cầu trong hàng đợi. | Not run – chưa có kết quả thực thi được xác nhận. |

### 1.4. Implementation Status

- Đã triển khai các thành phần cốt lõi `ChargingRequest`, `ChargingSession` và `SmartChargingScheduler`.
- Đã có thuật toán tính điểm ưu tiên, sắp xếp hàng đợi và phân bổ cổng theo giới hạn công suất.
- Đã có giao diện quản lý hàng đợi và phân bổ cổng trong `smart_charging.py`.
- Việc lấy dữ liệu cảm biến IoT thực tế và tích hợp SSO không được xác nhận trong implementation SS5 hiện tại.
- Hợp đồng `ChargingService.request_charging(...)` là giao diện mục tiêu theo kiến trúc liên subsystem, chưa được xem là class đã triển khai trong code hiện tại.

---

## 2. UC_SS5_02 – Giám sát hàng đợi sạc và phí chiếm dụng Overstay

| Hạng mục | Nội dung |
|---|---|
| Use Case ID | UC_SS5_02 |
| Use Case Name | Giám sát hàng đợi sạc và phí chiếm dụng Overstay (Charging Queue Monitoring and Overstay Fee) |
| Responsible Member | TV5 – Dương Đăng Khoa |
| Related User Stories | US-12, US-19, US-19b |
| Related Functional Requirements | FR-04, FR-05b, FR-10, FR-10b |
| Scenario | `docs/diagrams/Use-case detail-scenario/SS5/Usecase scenario/UC_SS5_DuongDangKhoa.md` |
| Sequence Diagram | `docs/diagrams/Use-case detail-scenario/SS5/Sequence diagrams/UC_SS5_02_DuongDangKhoa_sequence.puml` |
| Activity Diagram | `docs/diagrams/Use-case detail-scenario/SS5/Activity diagrams/UC_SS5_02_DuongDangKhoa_activity.puml` |
| Component / Source Code | `src/components/smart_charging.py`, `src/core/scheduler.py`, `src/core/billing.py`, `src/core/policies.py` |

### 2.1. Class and Method Traceability

| Class / Component | Method / Attribute | Responsibility |
|---|---|---|
| SmartChargingScheduler | `advance_simulation_tick(minutes)` | Tiến hành mô phỏng quá trình sạc, cập nhật SoC, trạng thái phiên sạc và thời gian chiếm dụng cổng. |
| ChargingSession | `current_soc`, `target_soc`, `status`, `started_at`, `completed_at` | Lưu trạng thái và thông tin tiến trình sạc. |
| ChargingSession | `alert_90_sent` | Theo dõi việc gửi cảnh báo khi SoC đạt ngưỡng 90%. |
| ChargingSession | `grace_deadline`, `overstay_minutes`, `overstay_fee` | Lưu thời gian ân hạn, thời gian quá hạn và phí Overstay. |
| ChargingSession | `energy_delivered_kwh` | Lưu tổng năng lượng đã cung cấp cho phương tiện. |
| SmartChargingScheduler | `unplug_vehicle(session_id)` | Kết thúc phiên sạc và giải phóng phiên khỏi danh sách active sessions. |
| SmartChargingScheduler | `get_sorted_queue()` | Cung cấp hàng đợi đã được sắp xếp để giao diện giám sát. |
| SmartChargingScheduler | `get_queue_as_dicts()` | Chuyển dữ liệu hàng đợi sang dạng dictionary phục vụ giao diện. |
| billing.py | `settle_overstay_charging(...)` | Xử lý phí Overstay và phí năng lượng trên wallet trong implementation hiện tại. |
| billing.py | `calculate_private_ev_bill(...)` | Tính chi phí sạc cho xe điện cá nhân. |
| smart_charging.py | `render()` | Hiển thị phiên sạc, cảnh báo, trạng thái Overstay và chức năng rút xe. |
| smart_charging.py | `_init_ss5()` | Khởi tạo scheduler và dữ liệu phiên sạc phục vụ giao diện. |

**Target Architecture Interfaces (chưa phải implementation hiện tại)**

| Class / Interface | Method | Responsibility |
|---|---|---|
| ChargingService | `get_bill(session_id)` | Cung cấp thông tin hóa đơn sạc và các khoản phí đã tính; chỉ đọc dữ liệu. |
| ChargingService | `handle_port_failure(hub_id, port_ids, operation_key)` | Xử lý sự cố cổng sạc và trả về các phiên bị ảnh hưởng theo hợp đồng liên subsystem. |
| BillingService (TV1) | `settle_invoice(owner_id, reference_id, charge_lines, operation_key)` | Tiếp nhận và xử lý thanh toán theo hợp đồng BillingService do TV1 phụ trách. |

*Lưu ý: `ChargingService` và `BillingService` trong bảng trên là các interface mục tiêu theo thiết kế chung. Không mô tả chúng là class đã tồn tại trong code SS5 hiện tại.*

### 2.2. Sequence Message / Activity Branch Traceability

| Message / Branch ID | Nội dung | Thành phần xử lý |
|---|---|---|
| MSG-SS5-12 | Operator mở chức năng giám sát hàng đợi sạc. | `smart_charging.py` – `render()` |
| MSG-SS5-13 | UI lấy danh sách xe, hàng đợi và trạng thái cổng sạc. | `st.session_state`, `SmartChargingScheduler` |
| MSG-SS5-14 | Nhận dữ liệu SoC và trạng thái cổng sạc. | Dữ liệu mô phỏng hiện tại; IoT là thành phần thiết kế |
| MSG-SS5-15 | Cập nhật tiến trình và trạng thái phiên sạc. | `SmartChargingScheduler.advance_simulation_tick()` |
| MSG-SS5-16 | Kiểm tra ngưỡng SoC 90% và phát cảnh báo. | `advance_simulation_tick()` |
| MSG-SS5-17 | Kiểm tra trạng thái sạc hoàn tất khi đạt 100%. | `advance_simulation_tick()` |
| MSG-SS5-18 | Chuyển phiên sạc sang GRACE_PERIOD. | `advance_simulation_tick()` |
| MSG-SS5-19 | Theo dõi thời gian ân hạn 15 phút. | `ChargingSession`, `advance_simulation_tick()` |
| MSG-SS5-20 | Kiểm tra xe đã rời cổng hay chưa. | `smart_charging.py`, `unplug_vehicle()` |
| MSG-SS5-21 | Chuyển phiên sang OVERSTAY và tính phí. | `advance_simulation_tick()` |
| MSG-SS5-22 | Xử lý phí Overstay và phí năng lượng. | `billing.py` – `settle_overstay_charging()` |
| MSG-SS5-23 | Hiển thị cảnh báo và danh sách phiên Overstay. | `smart_charging.py` – `render()` |

**Alternative / Exception Branches**

| Branch ID | Điều kiện | Expected Handling |
|---|---|---|
| BR-SS5-05 | Dữ liệu IoT không hợp lệ hoặc mất kết nối. | Thông báo lỗi và không sử dụng dữ liệu không hợp lệ để cập nhật trạng thái. |
| BR-SS5-06 | SoC >= 90%. | Phát cảnh báo pin sắp đầy. |
| BR-SS5-07 | SoC < 90%. | Tiếp tục giám sát phiên sạc. |
| BR-SS5-08 | SoC đạt 100%. | Phát thông báo hoàn tất sạc và bắt đầu thời gian ân hạn. |
| BR-SS5-09 | SoC chưa đạt 100%. | Tiếp tục theo dõi tiến trình sạc. |
| BR-SS5-10 | Xe rời cổng trong thời gian ân hạn. | Kết thúc phiên sạc và giải phóng cổng. |
| BR-SS5-11 | Xe tiếp tục chiếm cổng sau thời gian ân hạn. | Chuyển trạng thái sang OVERSTAY và tính phí theo chính sách. |
| BR-SS5-12 | Wallet đủ số dư. | Xử lý khoản phí theo cơ chế thanh toán hiện tại. |
| BR-SS5-13 | Wallet không đủ số dư. | Ghi nhận khoản nợ theo cơ chế xử lý hiện tại. |

*Lưu ý: Các nhánh IoT và Notification mô tả hành vi trong UML. Cần phân biệt chúng với luồng mô phỏng hiện có trong code. Trong implementation hiện tại, `settle_overstay_charging()` xử lý wallet trực tiếp; chưa chuyển hoàn toàn sang hợp đồng BillingService của TV1.*

### 2.3. Test Case Traceability

| Test ID | Test Function | Test Objective | Expected Result | Actual Result |
|---|---|---|---|---|
| TC-SS5-04 | `test_simulation_tick_and_overstay()` | Kiểm tra tiến trình sạc, chuyển sang GRACE_PERIOD, chuyển sang OVERSTAY và giải phóng phiên sạc. | Sau khi sạc đầy, phiên chuyển sang GRACE_PERIOD; sau khi vượt quá 15 phút ân hạn, chuyển sang OVERSTAY với phí 10.000 VND; gọi `unplug_vehicle()` thì phiên được loại khỏi active sessions. | Not run – chưa có kết quả thực thi được xác nhận. |

### 2.4. Implementation Status

- Đã triển khai mô phỏng tiến trình sạc thông qua `advance_simulation_tick()`.
- Đã có cơ chế cập nhật SoC, cảnh báo ở ngưỡng 90%, trạng thái GRACE_PERIOD và OVERSTAY.
- Đã có cơ chế tính phí Overstay theo các chính sách cấu hình.
- Đã có chức năng kết thúc phiên sạc thông qua `unplug_vehicle()`.
- Đã có hàm `settle_overstay_charging()` để xử lý phí năng lượng, phí Overstay và khoản nợ ví trong implementation hiện tại.
- Việc tích hợp IoT thực tế, hệ thống Notification độc lập và hợp đồng thanh toán BillingService mục tiêu chưa được xác nhận là hoàn thiện.

---

## 3. Test File Reference

| Hạng mục | Nội dung |
|---|---|
| Test File | `tests/test_scheduler_and_charging.py` |
| Test Framework | Pytest |
| Total Test Functions | 4 |
| UC_SS5_01 | 3 test functions |
| UC_SS5_02 | 1 test function |
| Execution Status | Chưa có log chạy test được cung cấp; cần chạy pytest để xác nhận Pass/Fail. |

Lệnh chạy test:

```bash
pytest -v tests/test_scheduler_and_charging.py
```

## 4. Traceability Summary

| Use Case | User Stories | Functional Requirements | Class / Component | Test Cases |
|---|---|---|---|---|
| UC_SS5_01 | US-10, US-18, US-20 | FR-04, FR-05b, FR-09, FR-11 | ChargingRequest, SmartChargingScheduler, ChargingSession, smart_charging.py | TC-SS5-01, TC-SS5-02, TC-SS5-03 |
| UC_SS5_02 | US-12, US-19, US-19b | FR-04, FR-05b, FR-10, FR-10b | ChargingSession, SmartChargingScheduler, billing.py, smart_charging.py | TC-SS5-04 |

## 5. Notes and Limitations

1. Traceability được xây dựng dựa trên hai Use Case SS5, các sơ đồ UML và source code hiện có.
2. Các thành phần `ChargingService`, `ChargingBill`, `BillingService` và các interface liên subsystem được ghi nhận là thiết kế mục tiêu nếu chưa có implementation tương ứng.
3. Các thành phần IoT, SSO và Notification độc lập trong sơ đồ UML không được xem là đã tích hợp thực tế nếu chưa có source code hoặc bằng chứng triển khai.
4. Các test case được ánh xạ theo tên function thực tế trong `test_scheduler_and_charging.py`. Kết quả Pass/Fail chỉ được cập nhật sau khi chạy test.
5. SS5 chịu trách nhiệm tính toán trạng thái sạc, năng lượng và phí liên quan. Việc ghi nhận và thu tiền theo kiến trúc mục tiêu được thực hiện thông qua BillingService do TV1 phụ trách.
