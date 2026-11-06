# Danh mục phương thức SS3 - revision 06/11/2026

Mọi kiểu/đơn vị như class diagram. `OperationResult` là hợp đồng đề xuất; các tuple/dict hiện có được nêu ở ánh xạ. UC chi tiết và test được liên kết trong traceability.md.

## SS3-MTH-01: `MonitoringService.get_network_snapshot`

**Chữ ký:** `get_network_snapshot() -> OperationResult[NetworkSnapshot]`.

**Hành vi, điều kiện, lỗi và gọi lặp:** INT-03. Đọc một phiên bản session, timestamp theo đồng hồ mô phỏng; tính occupancy=(total_slots-available_slots)/total_slots*100 nếu total>0. Kiểm tra available+present+holds+background=total. Tổng doanh thu thiết kế là tổng khoản thu thực có đối soát, tách tiền cọc, hoàn và nợ. Đếm cổng offline riêng, không suy ra công suất từ total-available. Trả INVALID_INPUT nếu capacity <=0 hoặc dữ liệu bất nhất, không chia 0 và không sửa booking/ví. Rerun lấy snapshot mới, không có polling IoT nền. Prototype dashboard mới cộng một số loại giao dịch SS1, chưa phải doanh thu toàn hệ thống.

**Ánh xạ:** `src/components/hub_monitor.py:render`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.

## SS3-MTH-02: `MonitoringService.classify_occupancy`

**Chữ ký:** `classify_occupancy(occupancy_pct: float) -> str`.

**Hành vi, điều kiện, lỗi và gọi lặp:** Đầu vào phần trăm hữu hạn >=0. NORMAL khi <70; WARNING khi 70<=x<85; CRITICAL khi 85<=x<100; FULL khi >=100. Thuần đọc, cùng đầu vào cùng kết quả; adapter phải từ chối NaN/âm thay vì mặc định NORMAL. Không đồng nhất mức occupancy với tỷ lệ cổng hay kW. Khóa đặt chỗ thuộc service đặt chỗ, không thuộc phương thức phân loại.

**Ánh xạ:** `src/core/policies.py:get_occupancy_level`. Chữ ký prototype có thể khác service; không khẳng định service đã có trong code.
