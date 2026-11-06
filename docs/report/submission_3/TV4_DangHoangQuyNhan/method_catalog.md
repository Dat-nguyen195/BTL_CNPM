# Danh mục phương thức SS4 - revision 06/11/2026

Mọi kiểu/đơn vị như class diagram. `OperationResult` là hợp đồng đề xuất; các tuple/dict hiện có được nêu ở ánh xạ. UC chi tiết và test được liên kết trong traceability.md.

## SS4-MTH-01: `DispatchService.create_order`

**Chữ ký:** `create_order(actor_id: str, source_hub_id: str, destination_hub_id: str, vehicle_ids: list[str], operation_key: str) -> OperationResult[DispatchOrder]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Operator có quyền, Hub nguồn khác đích, danh sách xe duy nhất không rỗng; mọi xe SHARED/AVAILABLE và không bị booking/charging giữ. Kiểm tra đủ chỗ đích, tạo hold đích, đưa xe DISPATCHED ra khỏi nguồn và tăng chỗ nguồn trong một commit. Ghi người tạo/thời gian/ID lệnh. Key lặp cùng nội dung trả lệnh cũ; FORBIDDEN/INVALID_STATE/NO_CAPACITY/CONFLICTING_OPERATION không commit. Prototype logic nằm trong UI, chưa có service/key.

**Ánh xạ:** `src/components/dispatch_incident.py:render`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS4-MTH-02: `DispatchService.complete_order`

**Chữ ký:** `complete_order(actor_id: str, dispatch_id: str, operation_key: str) -> OperationResult[DispatchOrder]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Chỉ hoàn tất lệnh IN_TRANSIT, kiểm tra Hub đích và phần giữ chỗ của lệnh còn hợp lệ tại thời điểm nhận. Chuyển hold thành hiện diện xe, trạng thái xe AVAILABLE, lệnh COMPLETED, ghi completed_at và tăng version. Không giảm available_slots lần hai khi chuyển hold. Hoàn tất lặp trả kết quả đã ghi; không nhân đôi xe; NO_CAPACITY/INVALID_STATE không cập nhật một phần.

**Ánh xạ:** `src/components/dispatch_incident.py:render`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS4-MTH-03: `IncidentService.report_vehicle_incident`

**Chữ ký:** `report_vehicle_incident(actor_id: str, vehicle_id: str, description: str, severity: str, operation_key: str) -> OperationResult[VehicleIncident]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Người báo có quyền; xe tồn tại, mô tả không rỗng và chưa có incident mở cho cùng sự kiện. Lưu previous_status, REPORTED và sim timestamp; cách ly xe INCIDENT. Nếu xe đang gắn booking/charging thì phải điều phối chủ service trước khi đổi trạng thái, không tự xóa ràng buộc. Lặp key không tạo sự cố trùng. Sự cố cổng/điện là SS7/SS5, không dùng VehicleIncident thay thế.

**Ánh xạ:** `src/components/dispatch_incident.py:render`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS4-MTH-04: `IncidentService.acknowledge`

**Chữ ký:** `acknowledge(actor_id: str, incident_id: str) -> OperationResult[VehicleIncident]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Technician tiếp nhận incident REPORTED, ghi assigned_to và chuyển ACKNOWLEDGED. Không thay ví/chỗ đỗ/cổng. Đã ACKNOWLEDGED trả dữ liệu cũ; đã RESOLVED trả INVALID_STATE, không mở lại. NOT_FOUND/FORBIDDEN không cập nhật.

**Ánh xạ:** `src/components/dispatch_incident.py:render`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS4-MTH-05: `IncidentService.resolve`

**Chữ ký:** `resolve(actor_id: str, incident_id: str, operation_key: str) -> OperationResult[VehicleIncident]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Technician chỉ resolve incident ACKNOWLEDGED sau sửa chữa; kiểm tra binding booking/charging trước phục hồi. Ghi resolved_at theo mô phỏng, RESOLVED và trả xe về trạng thái hợp lệ; chỉ AVAILABLE nếu không còn binding. Không tăng chỗ/cổng vì sửa xe. Lặp key không phục hồi hai lần. Prototype hiện phục hồi xe về AVAILABLE trực tiếp, chưa bảo vệ đầy đủ previous_status/binding.

**Ánh xạ:** `src/components/dispatch_incident.py:render`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.
