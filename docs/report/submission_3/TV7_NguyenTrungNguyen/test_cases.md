# Test case bonus — Nguyễn Trung Nguyên — SS7

**Trạng thái:** 6 ca được thiết kế; chưa thực thi riêng các ca trong bảng. Không ghi PASS trước khi có kết quả lệnh/test cụ thể.
**Quy ước:** test thiết kế cho hợp đồng Sub3 được phân biệt với test prototype hiện có.

## UC_SS7_01 — Mô phỏng sự cố hạ tầng

### `SS7-TC-01` — Sự cố ảnh hưởng cả cổng bận và cổng rảnh

- **Trạng thái:** `DESIGNED / NOT_RUN`.
- **Mức:** unit test cho `HubEventSimulator.simulate_port_failure`.
- **Dữ liệu:** Hub fixture `H-1`, `total=4`, `available=2`, `offline=0`; có hai xe trạng thái `CHARGING`; yêu cầu `num_ports_down=3`.
- **Bước:** giữ snapshot dữ liệu gốc; mô phỏng trên Hub này; đối chiếu output, metrics và snapshot ban đầu.
- **Kết quả mong đợi:** `failed_ports_total=3`; `busy_ports_interrupted=2`; `free_ports_disabled=1`; `remaining_available_ports=1`; hai xe đang sạc chuyển sang `WAITING`; Hub đầu vào vẫn có `available=2` và hai xe giữ nguyên trạng thái.
- **Truy vết:** UC_SS7_01 / `SS7-MTH-01`.

### `SS7-TC-02` — Preview không làm thay đổi Hub gốc

- **Trạng thái:** `DESIGNED / NOT_RUN` (hợp đồng service tương lai; test prototype hiện có kiểm tra một phần).
- **Mức:** service/component, `preview_port_failure` / INT-09.
- **Dữ liệu:** state khởi tạo; chọn `HUB-004`; ghi deep copy `hubs`, `state_version`, booking, ví và charging sessions trước khi chạy preview.
- **Bước:** tạo preview lỗi một số cổng; chưa Apply hoặc bấm Hủy.
- **Kết quả mong đợi:** `hubs`, booking, ví, charging sessions và `state_version` không đổi; preview có `scenario_type=PORT_FAILURE`, `baseline_version` bằng version trước mô phỏng. Hủy preview không tạo side effect.
- **Truy vết:** UC_SS7_01 / INT-09; test hiện có `test_port_failure_distinguishes_free_vs_busy_ports` chỉ chứng minh simulator không sửa Hub gốc, không kiểm tra toàn bộ session/service này.

### `SS7-TC-03` — Từ chối Apply preview cũ và Apply lặp

- **Trạng thái:** `DESIGNED / NOT_RUN` (hợp đồng INT-10; chưa triển khai coordinator).
- **Mức:** integration `SimulationCoordinator` + `ChargingService`.
- **Dữ liệu:** một preview tại version `v`; một phiên sạc gắn với cổng chịu ảnh hưởng; state sau đó được tăng version thành `v+1`.
- **Bước A:** gọi `apply_preview(preview_id, expected_version=v)`.
- **Kết quả A:** trả `STALE_STATE`; Hub, session/công suất, booking và ví không thay đổi một phần.
- **Bước B:** với state hợp lệ, Apply preview một lần rồi gọi Apply lại cùng preview.
- **Kết quả B:** lần đầu `applied=true`; lần sau `already_applied=true`; cổng/phiên chỉ bị tác động một lần; số slot đỗ không đổi chỉ vì lỗi cổng.
- **Truy vết:** UC_SS7_01 / INT-05 / INT-10.

## UC_SS7_02 — Gợi ý Hub thay thế

### `SS7-TC-04` — Lọc theo nhu cầu và xếp gần nhất trước

- **Trạng thái:** `DESIGNED / NOT_RUN`.
- **Mức:** unit test cho `ReroutingService.suggest_hubs` / `core.routing`.
- **Dữ liệu:** Hub nguồn `H0` tại `(10, 0)`; Hub `HA` tại `(10, 1)` còn slot và cổng; `HB` tại `(11, 0)` còn slot và cổng; `HC` tại `(10, 0.5)` không còn cổng; yêu cầu `need_ports=true`, `need_slots=true`, `limit=2`.
- **Bước:** truy vấn gợi ý từ `H0`.
- **Kết quả mong đợi:** loại `H0` và `HC`; trả `HA`, `HB` theo thứ tự khoảng cách Haversine tăng dần; kết quả không sửa capacity. Sau khi một Hub bị lấp đầy trước thao tác xác nhận, acceptance phải từ chối/stale thay vì dùng snapshot cũ.
- **Truy vết:** UC_SS7_02 / INT-06.

### `SS7-TC-05` — Không có Hub đáp ứng nhu cầu

- **Trạng thái:** `DESIGNED / NOT_RUN`.
- **Mức:** unit test cho `ReroutingService.suggest_hubs`.
- **Dữ liệu:** Hub nguồn tồn tại; tất cả Hub khác không còn chỗ hoặc không còn cổng theo nhu cầu.
- **Bước:** yêu cầu gợi ý với `need_slots=true`, `need_ports=true`.
- **Kết quả mong đợi:** thành công với danh sách rỗng (hoặc cảnh báo không có ứng viên ở UI); không đổi booking, holds, ví, Hub hoặc thời gian thuê; không tự chọn Hub không đủ điều kiện.
- **Truy vết:** UC_SS7_02 / INT-06.

### `SS7-TC-06` — Chuyển booking sau xác nhận, ưu đãi không cộng dồn

- **Trạng thái:** `DESIGNED / NOT_RUN` cho hợp đồng INT-07; test prototype hiện có xác nhận một lần chuyển.
- **Mức:** integration `BookingService.accept_rerouting` / `core.booking.apply_rerouting_to_booking`.
- **Dữ liệu:** booking hợp lệ có giữ chỗ tại Hub cũ; Hub mới còn slot; ghi snapshot holds, capacity, ví và `extra_free_minutes`.
- **Bước:** người dùng xác nhận Hub mới; sau thành công gọi lại cùng yêu cầu/booking (hoặc điều hướng lại) theo chính sách idempotency.
- **Kết quả mong đợi:** Hub cũ được nhả đúng một slot; Hub mới giữ đúng một slot; tiền/cọc không đổi; `extra_free_minutes=15` tối đa một lần; yêu cầu lặp không làm giảm thêm capacity hoặc cộng thêm phút. Nếu Hub mới hết chỗ tại thời điểm nhận thì không sửa state.
- **Truy vết:** UC_SS7_02 / INT-07; test prototype `test_rerouting_selects_two_hubs_and_transfers_hold_once` kiểm tra luồng chuyển một lần hiện tại.

## Bằng chứng chạy hiện có

| Phạm vi test đã có | Lệnh | Kết quả trong lượt hỗ trợ |
|---|---|---|
| Mô phỏng cổng lỗi, cách ly deepcopy và metrics cơ bản | PowerShell: `$env:PYTHONPATH = (Resolve-Path .\src).Path; python -m pytest -q tests/test_simulations.py` | PASS — 2 passed. |
| Gợi ý 2 Hub và chuyển giữ chỗ | PowerShell: `$env:PYTHONPATH = (Resolve-Path .\src).Path; python -m pytest -q tests/test_submission_2_acceptance.py -k rerouting` | PASS — 1 passed, 12 deselected. |

Hai lệnh cần `PYTHONPATH=src` vì repository không có pytest configuration đưa thư mục `src` vào import path. Các ca `SS7-TC-01` đến `SS7-TC-06` là test case bonus được thiết kế, không phải kết quả kiểm thử riêng; kết quả PASS ở trên chỉ áp dụng cho test hiện có được nêu trong bảng.
