# 📋 ĐẶC TẢ CHI TIẾT USE-CASE SCENARIO — PHÂN HỆ SS5

## Smart Charging Scheduler — Lập lịch sạc thông minh

> **Dự án:** Smart E-Mobility Hub — ĐHQG-HCM  
> **Phân hệ:** SS5 — Smart Charging Scheduler (Lập lịch sạc thông minh)  
> **Tác giả:** Dương Đăng Khoa (TV5 — Developer / Analyst)  
> **MSSV:** 2411589  
> **Email:** khoa.duong272dk@hcmut.edu.vn  
> **Nhóm:** Nhóm 7 Thành viên — BTL Công nghệ Phần mềm (CO3001) — HCMUT  

---

<style>
  table { width: 100% !important; display: table !important; }
  th, td { width: auto !important; }
  td:first-child { width: 22% !important; white-space: nowrap; }
  td:last-child { width: 78% !important; }
</style>

## 🔹 USE-CASE 1: Lập lịch ưu tiên sạc tự động

<table>
  <thead>
    <tr>
      <th style="width:20%">Field Name</th>
      <th colspan="3">Detail Content</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Use Case ID:</strong></td>
      <td colspan="3"><code>UC_SS5_01</code></td>
    </tr>
    <tr>
      <td><strong>Use Case Name:</strong></td>
      <td colspan="3"><code>UC_Lap_Lich_Uu_Tien_Sac_Tu_Dong</code> (Lập lịch ưu tiên sạc tự động — Smart Charging Priority Scheduler)</td>
    </tr>
    <tr>
      <td><strong>Created By:</strong></td>
      <td>Dương Đăng Khoa (TV5/Developer, Analyst)</td>
      <td><strong>Last Updated By:</strong></td>
      <td>Dương Đăng Khoa</td>
    </tr>
    <tr>
      <td><strong>Date Created:</strong></td>
      <td>19/09/2026</td>
      <td><strong>Date Last Updated:</strong></td>
      <td>23/09/2026</td>
    </tr>
    <tr>
      <td><strong>Actors:</strong></td>
      <td colspan="3"><strong>Primary:</strong> Chuyên viên sạc / Nhân viên vận hành (Charging Operator).<br/><strong>Secondary:</strong> Hệ thống Quản lý Hub (<code>st.session_state["hubs"]</code>), Trạm sạc &amp; Cổng sạc IoT, Mạng lưới Cảm biến IoT (đo SoC, nhiệt độ pin, công suất tiêu thụ kWh), Bộ lập lịch sạc (<code>src/core/scheduler.py</code>), Ví điện tử nội bộ (<code>st.session_state["current_user"]["wallet_balance"]</code>).</td>
    </tr>
    <tr>
      <td><strong>Description:</strong></td>
      <td colspan="3">Hệ thống tự động lập lịch và sắp xếp hàng đợi sạc cho các phương tiện điện tại Hub dựa trên thuật toán chấm điểm ưu tiên đa tiêu chí: mức pin hiện tại (SoC%), thời gian chờ trong hàng đợi, lịch sử dụng xe sắp tới (có booking đang chờ) và mức độ khẩn cấp. Hệ thống đồng thời xem xét cổng sạc khả dụng (<code>AVAILABLE</code>), công suất sạc tối đa (Peak Power Capping) do quản trị viên cấu hình (US-20), và biểu giá điện theo khung giờ cao điểm / thấp điểm (FR-05b) để lựa chọn thời điểm tối ưu và phân bổ tài nguyên sạc phù hợp, hạn chế vượt giới hạn công suất lưới điện.</td>
    </tr>
    <tr>
      <td><strong>Trigger:</strong></td>
      <td colspan="3">1. Chuyên viên sạc yêu cầu hệ thống lập lịch sạc thủ công.<br/>2. Hệ thống tự động kích hoạt khi phát hiện phương tiện mới ở trạng thái <code>WAITING</code> cần được đưa vào hàng đợi sạc.<br/>3. Hệ thống tự động tái lập lịch khi một cổng sạc được giải phóng (xe hoàn tất sạc hoặc rút sạc sớm).</td>
    </tr>
    <tr>
      <td><strong>Preconditions:</strong></td>
      <td colspan="3">
        1. Chuyên viên sạc (Charging Operator) đã đăng nhập thành công với vai trò <code>operator</code> hoặc <code>charging_staff</code> (<code>st.session_state["current_user"]["role"]</code>).<br/>
        2. Hệ thống đang hoạt động và có dữ liệu trạng thái các phương tiện / trạm sạc trong <code>st.session_state["hubs"]</code>.<br/>
        3. Có ít nhất 01 phương tiện đang ở trạng thái <code>WAITING</code> hoặc cần được đưa vào hàng đợi sạc.<br/>
        4. Hệ thống đã có thông tin về mức pin (SoC%), trạng thái phương tiện và trạng thái các cổng sạc từ Mạng lưới Cảm biến IoT.<br/>
        5. Giới hạn công suất tối đa (Peak Power Capping) đã được quản trị viên cấu hình trong <code>st.session_state["charging_config"]</code>.
      </td>
    </tr>
    <tr>
      <td><strong>Postconditions:</strong></td>
      <td colspan="3">
        1. Danh sách phương tiện cần sạc được sắp xếp theo điểm ưu tiên giảm dần (Scoring Algorithm).<br/>
        2. Phương tiện ưu tiên cao nhất được phân bổ vào cổng sạc <code>AVAILABLE</code>, trạng thái xe chuyển từ <code>WAITING</code> sang <code>CHARGING</code>.<br/>
        3. Hệ thống cập nhật lịch sạc kèm thời gian dự kiến bắt đầu/kết thúc sạc cho từng phương tiện.<br/>
        4. Trạng thái hàng đợi và cổng sạc được đồng bộ tức thì lên Dashboard Giám sát (SS3).<br/>
        5. Nếu tổng công suất phiên sạc vượt Peak Power Capping, hệ thống tự động điều chỉnh lịch sạc để không vượt giới hạn.<br/>
        6. Biểu giá sạc được áp dụng tự động: <strong>7,000 VNĐ/kWh</strong> (giờ cao điểm: 6h–9h, 16h–19h30) và <strong>3,000 VNĐ/kWh</strong> (giờ thấp điểm) theo FR-05b.
      </td>
    </tr>
    <tr>
      <td><strong>Normal Flow:</strong></td>
      <td colspan="3">
        1. Hệ thống thu thập danh sách phương tiện đang ở trạng thái <code>WAITING</code> hoặc mới được đưa vào hàng đợi sạc từ <code>st.session_state["hubs"]</code>.<br/>
        2. Hệ thống truy xuất dữ liệu từ Cảm biến IoT: mức pin hiện tại (SoC%), nhiệt độ pin, thời gian chờ trong hàng đợi (phút) và kiểm tra lịch sử dụng xe sắp tới (có booking đang chờ hay không).<br/>
        3. Hệ thống xác định các cổng sạc đang <code>AVAILABLE</code> và công suất sạc khả dụng tại Hub.<br/>
        4. Hệ thống tính toán điểm ưu tiên (Priority Score) của từng phương tiện theo thuật toán đa tiêu chí:<br/>
        &nbsp;&nbsp;<code>Score = w₁ × (100 − SoC) + w₂ × WaitTime + w₃ × Urgency + w₄ × PeakBonus</code><br/>
        &nbsp;&nbsp;Trong đó: <code>w₁ = 0.4</code> (trọng số pin thấp), <code>w₂ = 0.25</code> (thời gian chờ), <code>w₃ = 0.25</code> (mức khẩn cấp: có booking sắp tới = 10, SoC &lt; 20% = 8), <code>w₄ = 0.1</code> (thưởng sạc giờ thấp điểm).<br/>
        5. Hệ thống sắp xếp phương tiện theo điểm ưu tiên giảm dần và hiển thị hàng đợi sạc có thứ tự.<br/>
        6. Hệ thống phân bổ phương tiện có điểm ưu tiên cao nhất vào cổng sạc <code>AVAILABLE</code>, chuyển trạng thái xe từ <code>WAITING</code> sang <code>CHARGING</code> và kích hoạt phiên sạc.<br/>
        7. Hệ thống kiểm tra tổng công suất sạc đồng thời sau khi phân bổ: nếu tổng công suất vượt giới hạn Peak Power Capping (US-20), hệ thống tự động điều chỉnh thời gian bắt đầu sạc hoặc giảm công suất phiên sạc mới.<br/>
        8. Hệ thống cập nhật lịch sạc, ước tính thời gian hoàn tất, hiển thị thứ tự hàng đợi và biểu giá kWh áp dụng cho chuyên viên sạc.<br/>
        9. Khi một phương tiện hoàn tất sạc (SoC = 100%), hệ thống cập nhật trạng thái xe sang <code>AVAILABLE</code>, giải phóng cổng sạc và tự động kích hoạt lại chu trình lập lịch cho phương tiện tiếp theo trong hàng đợi.
      </td>
    </tr>
    <tr>
      <td><strong>Alternative Flows:</strong></td>
      <td colspan="3">
        <strong>Alternative 1 (Ưu tiên phương tiện pin cực thấp — Emergency Charge):</strong> Tại bước 4, nếu một phương tiện có mức SoC &lt; 20%, hệ thống tự động gán mức khẩn cấp cao nhất (Urgency = 10), tăng điểm ưu tiên và đưa phương tiện lên đầu hàng đợi.<br/>
        <strong>Alternative 2 (Ưu tiên phương tiện sắp được sử dụng — Upcoming Booking):</strong> Tại bước 4, nếu phương tiện có lịch sử dụng (booking) trong vòng 60 phút tới, hệ thống tăng mức ưu tiên để đảm bảo phương tiện được sạc kịp thời phục vụ sinh viên.<br/>
        <strong>Alternative 3 (Điều chỉnh theo khung giờ điện — Off-Peak Optimization):</strong> Tại bước 7, nếu hệ thống phát hiện đang trong giờ cao điểm (16h–19h30 hoặc 6h–9h), hệ thống ưu tiên điều chỉnh thời gian bắt đầu sạc các phương tiện không khẩn cấp (SoC &gt; 50%) sang khung giờ thấp điểm để tiết kiệm chi phí điện.<br/>
        <strong>Alternative 4 (Nhiều phương tiện cùng mức ưu tiên — FIFO Tiebreaker):</strong> Nếu nhiều phương tiện có cùng điểm ưu tiên, hệ thống sử dụng thời gian chờ (First-In-First-Out) để xác định thứ tự phục vụ.<br/>
        <strong>Alternative 5 (Điều chỉnh lịch theo Peak Power Capping):</strong> Nếu tổng công suất các phiên sạc dự kiến vượt mức Peak Power Capping do quản trị viên cấu hình (US-20), hệ thống điều chỉnh thứ tự hoặc dãn thời gian bắt đầu sạc để tổng công suất không vượt giới hạn lưới điện.<br/>
        <strong>Alternative 6 (Không còn cổng sạc khả dụng):</strong> Tại bước 3, nếu tất cả cổng sạc đều đang được sử dụng (<code>CHARGING</code>) hoặc bị lỗi (<code>ERROR</code>/<code>OFFLINE</code>), hệ thống giữ phương tiện ở trạng thái <code>WAITING</code> trong hàng đợi và thông báo cho Operator: "Tất cả cổng sạc đang bận, xe sẽ được tự động phân bổ khi có cổng trống."<br/>
        <strong>Alternative 7 (Vượt giới hạn công suất lưới):</strong> Tại bước 7, nếu tổng công suất dự kiến vượt giới hạn Peak Power Capping, hệ thống không thực hiện phân bổ đồng thời, điều chỉnh lại lịch sạc và hiển thị cảnh báo: "⚠️ Đã đạt giới hạn công suất tối đa. Phiên sạc mới sẽ được lên lịch khi công suất khả dụng."
      </td>
    </tr>
    <tr>
      <td><strong>Exceptions:</strong></td>
      <td colspan="3">
        
        <strong>Exception 3 (Cổng sạc bị lỗi giữa phiên sạc):</strong> Nếu cảm biến IoT phát hiện cổng sạc được phân bổ bị lỗi phần cứng (quá nhiệt, mất kết nối), hệ thống lập tức hủy phân bổ tại cổng đó, đánh dấu cổng sang trạng thái <code>ERROR</code>, chuyển phương tiện về <code>WAITING</code> trong hàng đợi để phân bổ lại cổng khác, đồng thời gửi cảnh báo kỹ thuật sang SS4 (<code>UC_SS4_02</code>).<br/>
        <strong>Exception 4 (Mất dữ liệu trạng thái từ IoT):</strong> Nếu hệ thống không nhận được dữ liệu SoC hoặc trạng thái cổng sạc từ Mạng lưới Cảm biến IoT trong &gt; 30 giây, hệ thống tạm ngưng phân bổ tự động đối với phương tiện bị thiếu dữ liệu, hiển thị cảnh báo "🔌 Mất kết nối IoT tại cổng [ID]" và thông báo cho Operator kiểm tra thủ công.

      </td>
    </tr>
    <tr>
      <td><strong>Notes and Issues:</strong></td>
      <td colspan="3">
        • Thuật toán ưu tiên dựa trên 4 tiêu chí: mức pin (SoC), thời gian chờ, mức độ khẩn cấp (có booking sắp tới hoặc SoC cực thấp) và khuyến khích sạc giờ thấp điểm.<br/>
        • Biểu giá sạc kWh theo FR-05b: <strong>7,000 VNĐ/kWh</strong> (peak: 6h–9h, 16h–19h30) | <strong>3,000 VNĐ/kWh</strong> (off-peak).<br/>
        • Thời gian xử lý thuật toán lập lịch &lt; 0.5s; dữ liệu đồng bộ tức thì với Dashboard SS3.<br/>
        • Dữ liệu trạng thái có thể được lấy từ IoT thực tế hoặc dữ liệu mô phỏng (<code>src/core/simulator.py</code>).<br/>
        • Tích hợp với module lập lịch: <code>src/core/scheduler.py</code> và giao diện: <code>src/components/smart_charging.py</code>.
      </td>
    </tr>
  </tbody>
</table>

---

## 🔹 USE-CASE 2: Giám sát hàng chờ sạc & Overstay Fee

<table>
  <thead>
    <tr>
      <th style="width:20%">Field Name</th>
      <th colspan="3">Detail Content</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Use Case ID:</strong></td>
      <td colspan="3"><code>UC_SS5_02</code></td>
    </tr>
    <tr>
      <td><strong>Use Case Name:</strong></td>
      <td colspan="3"><code>UC_Giam_Sat_Hang_Cho_Sac</code> (Giám sát hàng chờ sạc &amp; Xử lý phí chiếm dụng quá giờ — Queue Monitoring &amp; Overstay Fee)</td>
    </tr>
    <tr>
      <td><strong>Created By:</strong></td>
      <td>Dương Đăng Khoa (TV5/Developer, Analyst)</td>
      <td><strong>Last Updated By:</strong></td>
      <td>Dương Đăng Khoa</td>
    </tr>
    <tr>
      <td><strong>Date Created:</strong></td>
      <td>19/09/2026</td>
      <td><strong>Date Last Updated:</strong></td>
      <td>23/09/2026</td>
    </tr>
    <tr>
      <td><strong>Actors:</strong></td>
      <td colspan="3"><strong>Primary:</strong> Chuyên viên sạc / Nhân viên vận hành (Charging Operator).<br/><strong>Secondary:</strong> Sinh viên ĐHQG-HCM (nhận thông báo sạc xong &amp; cảnh báo Overstay), Hệ thống Quản lý Hub (<code>st.session_state["hubs"]</code>), Mạng lưới Cảm biến IoT trạm sạc (đo SoC real-time, trạng thái cổng), Ví điện tử nội bộ (<code>st.session_state["current_user"]["wallet_balance"]</code>).</td>
    </tr>
    <tr>
      <td><strong>Description:</strong></td>
      <td colspan="3">Hệ thống cho phép chuyên viên sạc theo dõi trạng thái toàn bộ phương tiện trong hàng chờ sạc, trạng thái từng cổng sạc và tiến trình sạc theo thời gian thực. Hệ thống tự động cập nhật thứ tự hàng đợi khi có phương tiện hoàn tất sạc, gửi thông báo đẩy (Push Notification) cho sinh viên / chủ xe khi xe đạt mức pin 90% (cảnh báo sớm) và 100% (hoàn tất sạc) theo US-19. Đồng thời, hệ thống phát hiện phương tiện đã sạc đầy nhưng vẫn chiếm dụng cổng sạc, kích hoạt thời gian ân hạn 15 phút. Sau 15 phút ân hạn, nếu xe vẫn chưa được di dời hoặc rút cáp sạc, hệ thống tự động áp dụng Phí chiếm dụng quá giờ (Overstay Fee) theo US-19b / FR-10b và khấu trừ trực tiếp vào ví điện tử của sinh viên.</td>
    </tr>
    <tr>
      <td><strong>Trigger:</strong></td>
      <td colspan="3">1. Chuyên viên sạc mở chức năng "Giám sát hàng chờ sạc" trên giao diện phân hệ SS5.<br/>2. Hệ thống tự động kích hoạt khi trạng thái phương tiện hoặc cổng sạc thay đổi (sự kiện IoT).<br/>3. Hệ thống tự động kích hoạt khi Cảm biến IoT phát hiện xe đạt SoC ≥ 90% hoặc SoC = 100%.</td>
    </tr>
    <tr>
      <td><strong>Preconditions:</strong></td>
      <td colspan="3">
        1. Hệ thống đang hoạt động bình thường, Hub chưa ở trạng thái <code>OFFLINE</code>.<br/>
        2. Có dữ liệu về phương tiện và trạng thái các cổng sạc trong <code>st.session_state["hubs"]</code>.<br/>
        3. Hàng chờ sạc đã được tạo bởi <code>UC_SS5_01</code> hoặc đang có ít nhất 01 phương tiện ở trạng thái <code>CHARGING</code>.<br/>
        4. Hệ thống có thể nhận dữ liệu trạng thái real-time từ trạm sạc / cảm biến IoT.<br/>
        5. Sinh viên / chủ xe đã cài đặt ứng dụng Smart E-Mobility Hub và cho phép nhận thông báo đẩy.
      </td>
    </tr>
    <tr>
      <td><strong>Postconditions:</strong></td>
      <td colspan="3">
        1. Hàng chờ sạc được cập nhật chính xác theo trạng thái mới nhất từ IoT.<br/>
        2. Trạng thái các phương tiện (<code>WAITING</code>, <code>CHARGING</code>, <code>AVAILABLE</code>) và cổng sạc (<code>AVAILABLE</code>, <code>CHARGING</code>, <code>ERROR</code>) được hiển thị trực quan trên Dashboard.<br/>
        3. Sinh viên nhận được thông báo đẩy khi xe đạt SoC 90% (cảnh báo sớm) và 100% (sạc hoàn tất) kèm biên nhận năng lượng tiêu thụ (kWh &amp; chi phí điện) theo US-19.<br/>
        4. Cổng sạc được giải phóng về <code>AVAILABLE</code> khi xe rút sạc trong thời gian ân hạn, sẵn sàng để <code>UC_SS5_01</code> phân bổ xe tiếp theo.<br/>
        5. Nếu xe chiếm dụng cổng quá 15 phút ân hạn, hệ thống ghi nhận Overstay Fee (<strong>10,000 VNĐ / 15 phút</strong>) và tự động khấu trừ <code>st.session_state["current_user"]["wallet_balance"]</code>.
      </td>
    </tr>
    <tr>
      <td><strong>Normal Flow:</strong></td>
      <td colspan="3">
        1. Chuyên viên sạc truy cập tab "Giám sát hàng chờ sạc" trên giao diện phân hệ SS5 (<code>src/components/smart_charging.py</code>).<br/>
        2. Hệ thống truy xuất danh sách phương tiện đang ở trạng thái <code>WAITING</code> và <code>CHARGING</code> từ <code>st.session_state["hubs"]</code>.<br/>
        3. Hệ thống hiển thị bảng tổng quan hàng đợi: thứ tự ưu tiên, mã xe, mức SoC hiện tại (%), thời gian chờ (phút) của từng phương tiện trong hàng đợi.<br/>
        4. Hệ thống hiển thị trạng thái từng cổng sạc: <code>AVAILABLE</code> (sẵn sàng), <code>CHARGING</code> (đang sạc, kèm ID xe &amp; SoC% tiến trình), <code>ERROR</code> (lỗi phần cứng).<br/>
        5. Hệ thống liên tục nhận và cập nhật dữ liệu trạng thái từ trạm sạc / Cảm biến IoT (polling interval &lt; 5 giây).<br/>
        6. Khi cảm biến phát hiện xe đạt <strong>SoC ≥ 90%</strong>, hệ thống gửi thông báo đẩy cảnh báo sớm đến ứng dụng sinh viên: <em>"🔋 Xe [ID] của bạn đã sạc được 90%. Vui lòng chuẩn bị di dời xe trong ~10 phút tới."</em><br/>
        7. Khi xe đạt <strong>SoC = 100%</strong> (hoàn tất sạc), hệ thống:<br/>
        &nbsp;&nbsp;a. Gửi thông báo đẩy cho sinh viên / chủ xe: <em>"✅ Xe [ID] đã sạc đầy 100%! Vui lòng di dời xe khỏi trụ sạc trong vòng 15 phút để tránh Phí chiếm dụng (Overstay Fee)."</em><br/>
        &nbsp;&nbsp;b. Gửi kèm biên nhận năng lượng tiêu thụ: tổng kWh đã nạp, biểu giá áp dụng (peak/off-peak), tổng chi phí sạc (VNĐ).<br/>
        &nbsp;&nbsp;c. Bắt đầu bộ đếm thời gian ân hạn 15 phút (<code>grace_timer = 15:00</code>).<br/>
        8. <strong>Kịch bản A — Xe di dời đúng hạn:</strong> Nếu sinh viên rút cáp sạc hoặc di dời xe trong vòng 15 phút ân hạn, hệ thống xác nhận giải phóng cổng sạc về <code>AVAILABLE</code>, ghi nhận phiên sạc hoàn tất và thông báo cho hệ thống lập lịch (<code>UC_SS5_01</code>) phân bổ phương tiện tiếp theo.<br/>
        9. <strong>Kịch bản B — Xe chiếm dụng quá giờ ân hạn (Overstay):</strong> Nếu hết 15 phút ân hạn mà xe vẫn chiếm dụng cổng sạc:<br/>
        &nbsp;&nbsp;a. Hệ thống tự động áp dụng Phí chiếm dụng quá giờ (Overstay Fee): <strong>10,000 VNĐ / mỗi 15 phút</strong> chiếm dụng thêm.<br/>
        &nbsp;&nbsp;b. Hệ thống tự động khấu trừ từ ví điện tử: <code>st.session_state["current_user"]["wallet_balance"] -= overstay_fee</code>.<br/>
        &nbsp;&nbsp;c. Gửi thông báo đẩy cảnh báo đỏ: <em>"⚠️ Phí chiếm dụng trụ sạc đã được tính: 10,000 VNĐ. Mỗi 15 phút tiếp tục sẽ tính thêm 10,000 VNĐ. Vui lòng di dời xe ngay!"</em><br/>
        &nbsp;&nbsp;d. Đánh dấu xe là "Overstay" trên Dashboard Operator với highlight đỏ nổi bật.<br/>
        10. Hệ thống cập nhật toàn bộ thông tin hàng chờ, trạng thái cổng sạc và Overstay log trên Dashboard giám sát (SS3).
      </td>
    </tr>
    <tr>
      <td><strong>Alternative Flows:</strong></td>
      <td colspan="3">
        <strong>Alternative 1 (Thứ tự hàng đợi được cập nhật bởi UC_SS5_01):</strong> Nếu hệ thống lập lịch tự động (<code>UC_SS5_01</code>) cập nhật thứ tự ưu tiên do có phương tiện mới khẩn cấp hơn, hệ thống giám sát phản ánh thứ tự mới trên Dashboard ngay lập tức.<br/>
        <strong>Alternative 2 (Phương tiện rút sạc sớm — Early Unplug):</strong> Nếu sinh viên rút sạc trước khi SoC đạt 100%, hệ thống cập nhật trạng thái phương tiện, giải phóng cổng sạc về <code>AVAILABLE</code>, tính phí sạc thực tế dựa trên kWh đã nạp và thông báo xe tiếp theo trong hàng đợi.<br/>
        <strong>Alternative 3 (Phương tiện đã sạc đầy và di dời đúng hạn):</strong> Hệ thống phát hiện phương tiện đã rời cổng hoặc rút sạc trong vòng 15 phút ân hạn, giải phóng cổng về <code>AVAILABLE</code> và xóa countdown timer. Không phát sinh Overstay Fee.<br/>
        <strong>Alternative 4 (Ví điện tử không đủ số dư trừ Overstay Fee):</strong> Tại bước 9b, nếu <code>wallet_balance &lt; overstay_fee</code>, hệ thống vẫn xử lý giải phóng cổng sạc an toàn, ghi nhận khoản nợ vào <code>st.session_state["current_user"]["debt_balance"]</code>, tạm khóa quyền đặt xe mới cho đến khi hoàn tất thanh toán khoản nợ, và gửi thông báo nhắc nhở sinh viên.
      </td>
    </tr>
    <tr>
      <td><strong>Exceptions:</strong></td>
      <td colspan="3">
        <strong>Exception 1 (Mất dữ liệu trạng thái IoT):</strong> Nếu hệ thống không nhận được dữ liệu SoC hoặc trạng thái cổng sạc từ trạm sạc / IoT trong &gt; 30 giây, hệ thống đánh dấu cổng là <code>UNKNOWN</code>, hiển thị cảnh báo "⚠️ Mất kết nối IoT tại cổng [ID]", tạm ngưng tự động phân bổ xe vào cổng bị mất kết nối và thông báo cho Operator kiểm tra thủ công.<br/>
        <strong>Exception 2 (Cổng sạc bị lỗi phần cứng):</strong> Nếu cảm biến IoT phát hiện lỗi quá nhiệt hoặc hỏng mạch, hệ thống chuyển trạng thái cổng sang <code>ERROR</code>, ngắt an toàn phiên sạc đang hoạt động, chuyển xe về <code>WAITING</code> để phân bổ lại, đồng thời gửi cảnh báo kỹ thuật sang SS4 (<code>UC_SS4_02</code>).<br/>
        <strong>Exception 3 (Mất điện lưới đột ngột — Power Outage):</strong> Nếu Hub xảy ra sự cố mất điện (<code>UC_SS7_01</code>), hệ thống tạm ngưng toàn bộ bộ đếm Overstay, đóng băng SoC hiện tại, miễn 100% phí chiếm dụng trong thời gian sự cố, chuyển toàn bộ xe <code>CHARGING</code> sang <code>WAITING</code> và kích hoạt nguồn dự phòng UPS cho bộ điều khiển cục bộ.
      </td>
    </tr>
    <tr>
      <td><strong>Notes and Issues:</strong></td>
      <td colspan="3">
        • UC_SS5_02 tập trung vào giám sát hàng đợi, trạng thái cổng sạc, thông báo cho sinh viên khi sạc xong (US-19) và xử lý phương tiện sạc đầy nhưng chưa rời cổng (US-19b / FR-10b).<br/>
        • Thuật toán xác định mức độ ưu tiên và lập lịch sạc thuộc <code>UC_SS5_01</code>.<br/>
        • Overstay Fee: <strong>10,000 VNĐ / 15 phút</strong> chiếm dụng sau hết ân hạn 15 phút đầu tiên.<br/>
        • Chuỗi cảnh báo SoC: 90% (cảnh báo sớm) → 100% (hoàn tất + bắt đầu ân hạn 15 phút) → Hết ân hạn (tính phí).<br/>
        • Tích hợp: <code>src/components/smart_charging.py</code> &amp; <code>src/core/scheduler.py</code>.
      </td>
    </tr>
  </tbody>
</table>

---

## 📎 PHỤ LỤC

### A. Ma trận Truy vết Yêu cầu (FR/US → UC Mapping)

| FR / US | Mô tả tóm tắt | UC ánh xạ |
| :--- | :--- | :--- |
| **FR-09** / US-18 | Lập lịch sạc tự động theo điểm ưu tiên (SoC, thời gian chờ, mức khẩn cấp, giá điện) | `UC_SS5_01` |
| **FR-10** / US-19 | Thông báo hoàn thành sạc & xuất biên nhận năng lượng tiêu thụ cho sinh viên | `UC_SS5_02` (Bước 6–7) |
| **FR-10b** / US-19b | Giám sát giải phóng trụ sạc & Tính phí chiếm dụng quá giờ (Overstay Fee) | `UC_SS5_02` (Bước 9) |
| **FR-11** / US-20 | Đặt giới hạn năng lượng tối đa (Peak Power Capping) | `UC_SS5_01` (Bước 7) |
| **FR-05b** / US-09, US-10 | Biểu giá sạc kWh theo khung giờ peak/off-peak | `UC_SS5_01` (Postcondition 6) |

### B. Quy chuẩn Trạng thái Hệ thống (Standardized State Machine)

| Đối tượng | Trạng thái Chuẩn | Diễn giải Nghiệp vụ | Liên kết Phân hệ |
| :--- | :--- | :--- | :--- |
| **Cổng sạc** | `AVAILABLE` | Cổng sạc sẵn sàng tiếp nhận phương tiện | SS2, **SS5** |
| **Cổng sạc** | `CHARGING` | Đang cấp điện sạc cho phương tiện | **SS5** |
| **Cổng sạc** | `ERROR` | Cổng sạc bị hỏng phần cứng | **SS5** → SS3, SS4 |
| **Cổng sạc** | `OFFLINE` | Cổng sạc mất điện lưới | SS7 → **SS5** |
| **Phương tiện** | `WAITING` | Đang chờ trong hàng đợi sạc | **SS5** |
| **Phương tiện** | `CHARGING` | Đang được cấp điện sạc tại cổng | **SS5** |
| **Phương tiện** | `AVAILABLE` | Xe sạc xong, sẵn sàng sử dụng | SS1, SS2, **SS5** |

---

> *Tài liệu được tạo bởi Dương Đăng Khoa (TV5 — Developer/Analyst) phục vụ BTL Công nghệ Phần mềm (CO3001) — HCMUT.*
