# ĐẶC TẢ USE CASE — PHÂN HỆ SS2

## Student EV Booking & Shared Services — Quản lý & Đặt xe điện dùng chung cho Sinh viên

> **Dự án:** Smart E-Mobility Hub — ĐHQG-HCM
> **Phân hệ:** SS2 — Student Personal EV Parking & Charging Services
> **Tác giả:** Nguyễn Anh Tài (TV2 — Developer / Analyst)  
> **MSSV:** 2413035  
> **Email:** tai.nguyenanh1906@hcmut.edu.vn
> **Nhóm:** Nhóm 7 Thành viên — BTL Công nghệ Phần mềm (CO3001) — HCMUT

---

<style>
  table { width: 100% !important; display: table !important; }
  th, td { width: auto !important; }
  td:first-child { width: 22% !important; white-space: nowrap; }
  td:last-child { width: 78% !important; }
</style>

## USE CASE 01: Đăng ký xe EV cá nhân lên hệ thống

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
      <td colspan="3"><code>UC_SS2_01</code></td>
    </tr>
    <tr>
      <td><strong>Use Case Name:</strong></td>
      <td colspan="3">UC_Dang_Ki_EV</td>
    </tr>
    <tr>
      <td><strong>Created By:</strong></td>
      <td>Nguyễn Anh Tài</td>
      <td><strong>Last Updated By:</strong></td>
      <td>Nguyễn Anh Tài</td>
    </tr>
    <tr>
      <td><strong>Date Created:</strong></td>
      <td>14/09/2026</td>
      <td><strong>Date Last Updated:</strong></td>
      <td>21/09/2026</td>
    </tr>
    <tr>
      <td><strong>Actors:</strong></td>
      <td colspan="3"><strong>Primary: </strong>Sinh viên ĐHQG-HCM (Student End-User).
      </td>
    </tr>
    <tr>
      <td><strong>Description:</strong></td>
      <td colspan="3">
        Sinh viên đăng ký thông tin xe điện cá nhân để sử dụng dịch vụ đỗ xe và sạc tại các Hub ĐHQG-HCM.
      </td>
    </tr>
    <tr>
      <td><strong>Trigger:</strong></td>
      <td colspan="3">
        Sinh viên chọn chức năng <strong>Đăng ký xe cá nhân</strong> trên ứng dụng.
      </td>
    </tr>
    <tr>
      <td><strong>Preconditions:</strong></td>
      <td colspan="3">
        1. Sinh viên đã đăng nhập/đăng ký bằng tài khoản hợp lệ và đang hoạt động với phân quyền vai trò <code>student</code><br>
        <code>(st.session_state["current_user"]["role"] == "student")</code>.
      </td>
    </tr>
    <tr>
      <td><strong>Postconditions:</strong></td>
      <td colspan="3">
        1. Hồ sơ xe được lưu, có mã định danh và được liên kết với tài khoản sinh viên.<br/>
        2. Xe được ghi nhận ở trạng thái <code>REGISTERED</code> và có thể được lựa chọn khi đặt dịch vụ.
      </td>
    </tr>
    <tr>
      <td><strong>Normal Flow:</strong></td>
      <td colspan="3">
        1. Sinh viên mở ứng dụng di động, hệ thống xác thực phiên làm việc người dùng <code>st.session_state["current_user"]</code> qua Cổng VNU-SSO</br>
        2. Sinh viên chọn chức năng <strong>Đăng ký xe cá nhân</strong>.<br/>
        3. Hệ thống hiển thị biểu mẫu đăng ký thông tin.<br/>
        4. Sinh viên nhập họ tên, mã số sinh viên, biển số, loại xe, dung lượng pin và hãng/model nếu có.<br/>
        5. Sinh viên xác nhận; hệ thống kiểm tra tính đầy đủ, hợp lệ của thông tin.<br/>
        6. Hệ thống cấp mã xe, lưu hồ sơ và ghi nhận thời điểm đăng ký.<br/>
        7. Hệ thống thông báo đăng ký thành công và hiển thị thông tin xe.
      </td>
    </tr>
    <tr>
      <td><strong>Alternative Flows:</strong></td>
      <td colspan="3">
        <strong>Alternative 1 (Không khai báo hãng/model):</strong> Tại bước 4, sinh viên có thể bỏ qua thông tin hãng/model nếu các thông tin bắt buộc đã đầy đủ, hoặc chỉ muốn đăng kí xe để đỗ.<br/>
        <strong>Alternative 2 (Xe đã đăng ký trong cùng tài khoản):</strong> Tại bước 5, hệ thống hiển thị hồ sơ hiện có để sinh viên tiếp tục sử dụng, không tạo hồ sơ trùng.<br/>
        <strong>Alternative 3 (Thông tin không hợp lệ):</strong> Tại bước 5, hệ thống chỉ rõ ô thông tin thiếu hoặc sai và yêu cầu điều chỉnh.<br/>
        <strong>Alternative 4 (Biển số thuộc tài khoản khác):</strong> Tại bước 6, hệ thống từ chối đăng ký, hiện thông báo và hướng dẫn sinh viên liên hệ bộ phận hỗ trợ.
      </td>
    </tr>
    <tr>
      <td><strong>Exceptions:</strong></td>
      <td colspan="3">
                <strong>Exception 1 (Sự cố hệ thống / Mất kết nối):</strong> Nếu hệ thống bị sập nguồn, mất kết nối CSDL hoặc lỗi server, hệ thống sẽ tự động đóng băng các giao dịch đang xử lý, lưu cache cục bộ và hiển thị thông báo lỗi "Hệ thống đang bảo trì hoặc gián đoạn. Vui lòng thử lại sau." để đảm bảo không mất dữ liệu của người dùng.<br/>
      </td>
    </tr>
    <tr>
      <td><strong>Notes and Issues:</strong></td>
      <td colspan="3">
        Đăng ký xe không phụ thuộc vào số chỗ đỗ còn trống tại Hub. sinh viên thực hiện đặt chỗ đỗ và sạc trong <code>UC_SS2_02</code>.
      </td>
    </tr>
  </tbody>
</table>

---

## USE CASE 02: Đặt chỗ đỗ và nhu cầu sạc xe EV cá nhân

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
      <td colspan="3"><code>UC_SS2_02</code>
      </td>
    </tr>
    <tr>
      <td><strong>Use Case Name:</strong></td>
      <td colspan="3">UC_Dat_Cho</td>
    </tr>
    <tr>
      <td><strong>Created By:</strong></td>
      <td>Nguyễn Anh Tài</td>
      <td><strong>Last Updated By:</strong></td>
      <td>Nguyễn Anh Tài</td>
    </tr>
    <tr>
      <td><strong>Date Created:</strong></td>
      <td>14/09/2026</td>
      <td><strong>Date Last Updated:</strong></td>
      <td>21/09/2026</td>
    </tr>
    <tr>
      <td><strong>Actors:</strong></td>
      <td colspan="3"><strong>Primary: </strong>Sinh viên ĐHQG-HCM (Student End-User).<br/><strong>Secondary: </strong>  Cổng xác thực VNU-SSO, Tài khoản & Ví điện tử nội bộ <code>(st.session_state["current_user"])</code>.
      </td>
    </tr>
    <tr>
      <td><strong>Description:</strong></td>
      <td colspan="3">
        Sinh viên đăng nhập hệ thống qua VNU-SSO, sinh viên tra cứu biểu phí, tham khảo thời gian đặt trước vị trí đỗ và đăng ký lịch sạc theo nhu cầu.
      </td>
    </tr>
    <tr>
      <td><strong>Trigger:</strong></td>
      <td colspan="3">
        Sinh viên chọn chức năng <strong>Đặt chỗ đỗ và sạc</strong>.
      </td>
    </tr>
    <tr>
      <td><strong>Preconditions:</strong></td>
      <td colspan="3">
        1. Sinh viên mở ứng dụng di động, hệ thống xác thực phiên làm việc người dùng <code>st.session_state["current_user"]</code> qua Cổng VNU-SSO và tài khoản sinh viên có ít nhất một xe cá nhân đã đăng ký.</br>
        2. Hub được chọn đang hoạt động và có vị trí đỗ <code>AVAILABLE</code> phù hợp trong khoảng thời gian yêu cầu.<br/>
        3. Ví nội bộ tài khoản của sinh viên có ít nhất 50,000VNĐ trong tài khoản <code>(st.session_state["current_user"]["wallet_balance"] ≥ 50000)</code> để làm cọc phí trong quá trình đặt và giữ chỗ.</br> 
        4. Nếu đăng ký sạc, Hub có các loại cổng sạc tương thích và khả dụng trong khung giờ yêu cầu.
      </td>
    </tr>
    <tr>
      <td><strong>Postconditions:</strong></td>
      <td colspan="3">
        1. Đơn đặt dịch vụ được xác nhận, liên kết với sinh viên, xe, Hub, vị trí đỗ và thời gian sử dụng.<br/>
        2. Vị trí đỗ chuyển từ <code>AVAILABLE</code> sang <code>RESERVED</code> đặt trong vòng 30 phút tính từ thời gian lịch bắt đầu <code>booking_start_time</code>.Nếu có nhu cầu sạc, yêu cầu sạc được ghi nhận và chuyển cho phân hệ lập lịch sạc để xử lý/phân bổ tài nguyên.<br/>
        3. Sinh viên nhận mã đặt chỗ và các mã QR phục vụ Check-in và mở trụ sạc.
      </td>
    </tr>
    <tr>
      <td><strong>Normal Flow:</strong></td>
      <td colspan="3">
        1. Sinh viên chọn xe đã đăng ký để đặt dịch vụ.<br/>
        2. Hệ thống hiển thị các Hub, khả năng phục vụ và biểu phí.<br/>
        3. Sinh viên chọn Hub, thời gian sử dụng, vị trí đỗ và loại dịch vụ.<br/>
        4. Nếu đăng ký sạc, sinh viên thêm tùy chọn sạc xe trong thời gian đỗ.<br/>
        5. Hệ thống kiểm tra khả dụng và hiển thị phí đỗ <code>[5,000VNĐ/giờ]</code> (tính theo giờ bắt đầu, tối thiểu 1 giờ), phí cọc giữ chỗ <code>[50,000VNĐ]</code>, phí sạc/kWh dự kiến theo biểu giá áp dụng (giờ cao điểm <code>[7,000VNĐ/kWh]</code> (16h-19h30 và 6h-9h) <code>[3,000VNĐ/kWh]</code> với giờ thấp điểm).<br/>
        6. Sinh viên kiểm tra lại thông tin, áp mã voucher (nếu có) và xác nhận đặt dịch vụ.<br/>
        7. Hệ thống kiểm tra lại khả dụng, xác nhận đơn và cập nhật vị trí đỗ cùng cổng sạc nếu có.<br/>
        8. Hệ thống thông báo thành công, hiển thị thông tin vị trí và mã QR của đơn.
      </td>
    </tr>
    <tr>
      <td><strong>Alternative Flows:</strong></td>
      <td colspan="3">
        <strong>Alternative 1 (Chỉ sử dụng dịch vụ đỗ xe):</strong> Tại bước 3, sinh viên chọn chỉ đỗ xe; hệ thống bỏ qua bước 4 và không giữ cổng sạc.<br/>
        <strong>Alternative 2 (Thay đổi lựa chọn):</strong> Tại bước 5, sinh viên có thể đổi Hub, thời gian hoặc dịch vụ; hệ thống kiểm tra và tính lại phí dự kiến.<br/>
        <strong>Alternative 3 (Hủy đơn trước Check-in):</strong> Sau bước 8, sinh viên được hủy đơn trước hạn Check-in (<code>booking_start_time</code> + 30 phút): hệ thống hoàn 100% tiền cọc 50,000VNĐ (cùng chính sách với SS1), cập nhật đơn sang <code>CANCELLED</code> và giải phóng vị trí từ <code>RESERVED</code> thành <code>AVAILABLE</code>. Từ thời điểm đến hạn, đơn không còn hủy được mà xử lý theo Alternative 6.<br/>
        <strong>Alternative 4 (Thông tin hoặc lịch đặt không hợp lệ):</strong> Tại bước 5 hoặc 7, thời gian không hợp lệ, lịch sạc ngoài thời gian đỗ hoặc xe có lịch sử dụng trùng nhau; hệ thống yêu cầu điều chỉnh form nhập.<br/>
        <strong>Alternative 5 (Không còn vị trí đỗ khả dụng):</strong> Tại bước 5 hoặc 7, hệ thống thông báo hết chỗ và gợi ý sinh viên chọn Hub lân cận hoặc khung giờ khác.<br/>
        <strong>Alternative 6 (Quá thời hạn giữ chỗ 30 phút - No-show Timeout):</strong> Nếu sinh viên không Check-in trong vòng 30 phút kể từ <code>booking_start_time</code>, hệ thống tự động cập nhật trạng thái đơn sang <code>EXPIRED</code>, giải phóng vị trí về <code>AVAILABLE</code> và quyết toán cọc 50.000 VNĐ: phạt 10.000 VNĐ, hoàn 40.000 VNĐ đúng một lần.
      </td>
    </tr>
    <tr>
      <td><strong>Exceptions:</strong></td>
      <td colspan="3">
        <strong>Exception 1 (Sự cố hệ thống / Mất kết nối CSDL):</strong> Nếu máy chủ gặp sự cố hoặc gián đoạn mạng, giao dịch được hoàn nguyên (rollback) an toàn, hiển thị thông báo lỗi và yêu cầu người dùng thử lại sau.
      </td>
    </tr>
    <tr>
      <td><strong>Notes and Issues:</strong></td>
      <td colspan="3">
        Khả dụng được xác định theo khoảng thời gian đặt. Phí hiển thị là phí dự kiến; phí thực tế được quyết định trong <code>UC_SS2_04</code>. Đơn hết hạn nhận chỗ trước Check-in được giải phóng theo chính sách áp dụng.
      </td>
    </tr>
  </tbody>
</table>

---

## USE CASE 03: Check-in xe EV cá nhân

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
      <td colspan="3">
        <code>UC_SS2_03</code>
      </td>
    </tr>
    <tr>
      <td><strong>Use Case Name:</strong></td>
      <td colspan="3">UC_Check_In</td>
    </tr>
    <tr>
      <td><strong>Created By:</strong></td>
      <td>Nguyễn Anh Tài</td>
      <td><strong>Last Updated By:</strong></td>
      <td>Nguyễn Anh Tài</td>
    </tr>
    <tr>
      <td><strong>Date Created:</strong></td>
      <td>14/09/2026</td>
      <td><strong>Date Last Updated:</strong></td>
      <td>21/09/2026</td>
    </tr>
    <tr>
      <td><strong>Actors:</strong></td>
      <td colspan="3">
        <strong>Primary: </strong> Sinh viên ĐHQG-HCM (Student End-User).<br/><strong>Secondary: </strong> Khối Vận hành (Operators); Hệ thống IoT/Cảm biến vị trí barier.
      </td>
    </tr>
    <tr>
      <td><strong>Description:</strong></td>
      <td colspan="3">
        Xác thực xe tại cổng vào, ghi nhận thời điểm đến và bắt đầu phiên đỗ tại vị trí đã đặt.
      </td>
    </tr>
    <tr>
      <td><strong>Trigger:</strong></td>
      <td colspan="3">
        Sinh viên đưa xe đến cổng vào Hub và thực hiện xác thực.
      </td>
    </tr>
    <tr>
      <td><strong>Preconditions:</strong></td>
      <td colspan="3">
        1. Xe đã đăng ký và có đơn đặt chỗ còn hiệu lực tại đúng Hub.<br/>
        2. Sinh viên có quyền sử dụng xe và đến trong khung giờ được phép Check-in.<br/>
        3. Vị trí đỗ đã được giữ cho đơn ở trạng thái <code>RESERVED</code> và có thể sử dụng.
      </td>
    </tr>
    <tr>
      <td><strong>Postconditions:</strong></td>
      <td colspan="3">
        1. Thời điểm vào thực tế được ghi nhận và phiên đỗ bắt đầu.<br/>
        2. Đơn chuyển sang <code>CHECKED_IN</code>; vị trí đỗ chuyển từ <code>RESERVED</code> sang <code>OCCUPIED</code>. Cổng sạc giữ trạng thái được phân bổ/RESERVED cho tới khi sinh viên xác thực tại trụ và kết nối xe thành công.<br/>
        3. Xe được ghi nhận hiện diện tại Hub và sinh viên được hướng dẫn đến vị trí đã cấp.
      </td>
    </tr>
    <tr>
      <td><strong>Normal Flow:</strong></td>
      <td colspan="3">
        1. Sinh viên quét mã QR.<br/>
        2. Hệ thống đối chiếu xe, quyền sử dụng, đơn đặt chỗ, Hub và khung giờ.<br/>
        3. Hệ thống xác thực thành công và mở barie cổng vào.<br/>
        4. Khi xác nhận xe đã vào Hub, hệ thống ghi nhận thời điểm Check-in.<br/>
        5. Hệ thống kích hoạt phiên đỗ và chuyển vị trí từ <code>RESERVED</code> sang <code>OCCUPIED</code>.<br/>
        6. Hệ thống thông báo Check-in thành công, hướng dẫn vị trí đỗ và lịch sạc nếu có.
        7. Sinh viên tiến hành quét mã QR tại vị trí sạc để mở khóa trụ sạc và thực hiện việc cắm sạc<br/>.
      </td>
    </tr>
    <tr>
      <td><strong>Alternative Flows:</strong></td>
      <td colspan="3">
        <strong>Alternative 1 (Xác thực bằng PIN):</strong> Tại bước 1, nếu sinh viên không sử dụng mã QR của đơn thì có thể tiếp tục xác thực bằng cách chọn xác thực bằng mã PIN.<br/>
        <strong>Alternative 2 (Thông tin xác thực không hợp lệ):</strong> Tại bước 2 hoặc bước 7, nếu mã QR hoặc PIN không khớp, hệ thống từ chối mở cổng/trụ và cho phép nhập lại tối đa 3 lần.<br/>
        <strong>Alternative 3 (Đơn hoặc khung giờ không hợp lệ):</strong> Tại bước 2, nếu đơn đặt sai Hub hoặc ngoài khung giờ cho phép, hệ thống từ chối Check-in và hiển thị thông tin vi phạm quy định.<br/>
        <strong>Alternative 4 (Vị trí đã bị chiếm dụng trái phép):</strong> Tại bước 2, nếu vị trí đỗ bị chiếm dụng ngoài dự kiến, hệ thống tự động đổi sang slot trống khác tương đương và gửi cảnh báo cho Operator.<br/>
        <strong>Alternative 5 (Hết cổng sạc lúc Check-in):</strong> Tại bước 5, nếu đơn có đăng ký sạc nhưng cổng sạc của Hub đã hết hoặc bị lỗi sau thời điểm đặt chỗ, xe vẫn được Check-in vào vị trí đỗ; yêu cầu sạc được đưa vào hàng đợi của phân hệ lập lịch sạc (SS5) với trạng thái <code>WAITING</code> và được cấp cổng ngay khi có cổng trống.
      </td>
    </tr>
    <tr>
      <td><strong>Exceptions:</strong></td>
      <td colspan="3">
        <strong>Exception 1 (Sự cố phần cứng barie / Mất kết nối cổng IoT):</strong> Nếu cổng barie bị kẹt cơ học hoặc cảm biến trạm mất tín hiệu IoT, hệ thống chuyển sang chế độ mở cổng thủ công và thông báo cho Kỹ thuật viên hiện trường.
      </td>
    </tr>
    <tr>
      <td><strong>Notes and Issues:</strong></td>
      <td colspan="3">
        Check-in sử dụng vị trí đã giữ nên không yêu cầu Hub còn chỗ trống khác và không giữ thêm chỗ lần thứ hai. Phiên sạc do SS5 quản lý: khi pin đầy, SS5 ngừng tính tiền điện và bắt đầu 15 phút ân hạn; nếu xe vẫn chiếm cổng sau ân hạn, SS5 tính phí chiếm dụng quá giờ <code>[10,000VNĐ / mỗi 15 phút]</code>. Điện năng và phí quá giờ được chốt và gộp vào hóa đơn tổng hợp trong <code>UC_SS2_04</code>, chỉ thu một lần.
      </td>
    </tr>
  </tbody>
</table>

---

## USE CASE 04: Check-out và thanh toán dịch vụ xe EV cá nhân

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
      <td colspan="3">
        <code>UC_SS2_04</code>
      </td>
    </tr>
    <tr>
      <td><strong>Use Case Name:</strong></td>
      <td colspan="3">UC_Check_Out</td>
    </tr>
    <tr>
      <td><strong>Created By:</strong></td>
      <td>Nguyễn Anh Tài</td>
      <td><strong>Last Updated By:</strong></td>
      <td>Nguyễn Anh Tài</td>
    </tr>
    <tr>
      <td><strong>Date Created:</strong></td>
      <td>14/09/2026</td>
      <td><strong>Date Last Updated:</strong></td>
      <td>21/09/2026</td>
    </tr>
    <tr>
      <td><strong>Actors:</strong></td>
      <td colspan="3">
        <strong>Primary: </strong>Sinh viên ĐHQG-HCM (Student End-User).<br/><strong>Secondary:</strong> Khối Vận Hành (Operators); Hệ thống IoT/Cảm biến vị trị cổng, Cổng xác thực VNU-SSO, Cổng thanh toán & Ví điện tử nội bộ <code>(st.session_state["current_user"]).</code>
      </td>
    </tr>
    <tr>
      <td><strong>Description:</strong></td>
      <td colspan="3">
        Tổng hợp phí đỗ và phí sạc thực tế, thực hiện thanh toán và xác nhận xe rời Hub để kết thúc phiên sử dụng.
      </td>
    </tr>
    <tr>
      <td><strong>Trigger:</strong></td>
      <td colspan="3">
        Sinh viên yêu cầu thanh toán, Check-out hoặc xác thực tại cổng ra.
      </td>
    </tr>
    <tr>
      <td><strong>Preconditions:</strong></td>
      <td colspan="3">
        1. Xe có phiên đỗ đang hoạt động tại Hub và đã Check-in thành công.<br/>
        2. Sinh viên có quyền sử dụng xe và đang sử dụng dịch vụ đỗ/sạc.
      </td>
    </tr>
    <tr>
      <td><strong>Postconditions:</strong></td>
      <td colspan="3">
        1. Hóa đơn tổng hợp được thanh toán; giao dịch và thời điểm Check-out được lưu.<br/>
        2. Xe đã rời Hub, phiên sử dụng kết thúc và đơn chuyển sang <strong>COMPLETED</strong>.<br/>
        3. Vị trí đỗ và cổng sạc được giải phóng theo điều kiện sử dụng thực tế; hồ sơ đăng ký xe được giữ nguyên.
      </td>
    </tr>
    <tr>
      <td><strong>Normal Flow:</strong></td>
      <td colspan="3">
        1. Sinh viên yêu cầu Check-out; hệ thống xác thực và xác định phiên sử dụng.<br/>
        2. Hệ thống kết thúc phiên sạc và chốt lượng điện tiêu thụ theo từng khung giá.<br/>
        3. Hệ thống tính phí đỗ thực tế theo thời gian từ Check-in đến Check-out (theo giờ bắt đầu, tối thiểu 1 giờ), lấy phí sạc và phí chiếm dụng quá giờ (nếu có) do phân hệ lập lịch sạc SS5 tính, và hiển thị một hóa đơn tổng hợp.<br/>
        4. Sinh viên kiểm tra hóa đơn và xác nhận thanh toán qua ví nội bộ.<br/>
        5. Ví xử lý giao dịch; hệ thống ghi nhận thanh toán thành công và lưu hóa đơn điện tử và giải phóng khoản tiền tạm giữ và thu chính xác số tiền hóa đơn thực tế.<br/>
        6. Tại cổng ra, hệ thống đối chiếu xe và kiểm tra đã hoàn tất quyết toán.<br/>
        7. Hệ thống mở barie; khi xác nhận xe đã rời Hub, ghi nhận Check-out và kết thúc phiên.<br/>
        8. Hệ thống giải phóng phần vị trí đỗ, cổng sạc còn được giữ hoặc sử dụng bởi phiên và cung cấp hóa đơn cho sinh viên.
      </td>
    </tr>
    <tr>
      <td><strong>Alternative Flows:</strong></td>
      <td colspan="3">
        <strong>Alternative 1 (Không sử dụng dịch vụ sạc):</strong> Tại bước 2–3, hệ thống bỏ qua xử lý sạc và chỉ tính phí đỗ.<br/>
        <strong>Alternative 2 (Không thanh toán bằng ví nội bộ được do thiếu số dư):</strong> Tại bước 4–5, nếu giao dịch bị từ chối do thiếu số dư, sinh viên được chuyển hướng nạp tiền nhanh hoặc đổi hình thức thanh toán.<br/>
        <strong>Alternative 3 (Thanh toán chưa đủ hạn mức):</strong> Tại bước 6, hệ thống từ chối mở barie, yêu cầu thanh toán dứt điểm khoản còn thiếu trước khi mở cổng.
      </td>
    </tr>
    <tr>
      <td><strong>Exceptions:</strong></td>
      <td colspan="3">
        <strong>Exception 1 (Sự cố cảm biến cổng / Barie không nhận diện xe ra):</strong> Tại bước 7, nếu cảm biến quang điện không phát hiện xe đi qua sau khi mở cổng, hệ thống giữ phiên ở trạng thái kiểm tra và cảnh báo Operator can thiệp.
      </td>
    </tr>
    <tr>
      <td><strong>Notes and Issues:</strong></td>
      <td colspan="3">
        Thanh toán là một phần của luồng Check-out. Nhân viên xác nhận dựa trên kết quả giao dịch. Thời điểm chốt phí và thời hạn rời bãi sau thanh toán áp dụng theo chính sách dịch vụ. Trong prototype, nếu ví không đủ số dư, phần thiếu được ghi nợ minh bạch vào ví và xe vẫn được Check-out; tài khoản đang có nợ bị chặn đặt chỗ mới cho tới khi thanh toán xong (đơn giản hóa so với Alternative 2–3).
      </td>
    </tr>
  </tbody>
</table>

---

> *Cập nhật 23/11/2026: đồng bộ với prototype hiện tại (phí đỗ theo giờ, hủy đơn trước hạn hoàn 100% cọc, hết cổng sạc lúc Check-in, phí quá giờ do SS5 tính, ghi nợ khi thiếu số dư).*

> *Tài liệu được tạo bởi Nguyễn Anh Tài (TV2 — Developer/Analyst) phục vụ BTL Công nghệ Phần mềm (CO3001) — HCMUT.*

---

## 📎 PHỤ LỤC: Ma trận Truy vết Yêu cầu (FR/US → UC Mapping)

| FR / US | Mô tả tóm tắt | UC ánh xạ |
| :--- | :--- | :--- |
| **FR-03** / US-08 | Đăng ký xe EV cá nhân (biển số, loại xe, dung lượng pin) | `UC_SS2_01` |
| **FR-04** / US-10 | Đặt lịch sạc & đặt chỗ đỗ cho xe cá nhân | `UC_SS2_02` |
| **FR-05b** / US-09, US-10, US-11 | Tính phí đỗ xe & phí sạc kWh theo peak/off-peak | `UC_SS2_02`, `UC_SS2_04` |
| **FR-03b** / US-11b | Xác thực Check-in / Check-out xe cá nhân tại cổng Hub | `UC_SS2_03`, `UC_SS2_04` |
| **FR-15b** / US-06, US-11 | Xuất hóa đơn điện tử tích hợp phí đỗ + phí sạc | `UC_SS2_04` |