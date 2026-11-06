#!/usr/bin/env python3
"""Compose the unified Sub3 report from the reviewed source, not merged PDFs.

Run with the Codex document runtime Python. Render using render_docx.py.
The --pages JSON option materializes the verified contents page numbers.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from docx import Document
from docx.enum.section import WD_SECTION_START, WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Cm, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/report/submission_3'
TEMP = ROOT / 'tmp/submission_3_total'
MANIFEST = json.loads((ROOT / 'docs/traceability/submission_3.json').read_text())
MEMBERS = MANIFEST['members']
BLOCKS = []
CHAPTERS = []
FIGURES = []
CATALOG = {}
REPEATED = []
CLASSES = {}
NAVIGATION = []
CAPTIONS = {}
BODY_WIDTH = 16 / 2.54


def norm(s):
    s = s.replace('Chương ', 'Mục ').replace('chương ', 'mục ')
    s = s.replace('—', '-').replace('–', '-').replace('\u2011', '-')
    s = s.replace('Không tự bịa số km.', 'Chưa có dữ liệu đo quãng đường trong prototype.')
    s = s.replace('không khẳng định service đã có trong code.', 'service OOP vẫn thuộc thiết kế mục tiêu.')
    s = s.replace('Mô tả chi tiết và giới hạn UI/prototype xem mục 6 báo cáo.', 'Giới hạn tích hợp UI/prototype được trình bày tại mục 6.4.')
    s = s.replace('; phải nêu là giới hạn.', '; đây là giới hạn hiện tại của prototype.')
    s = s.replace('(thiết kế TV5)', '(thiết kế SS5)').replace('DTO/INT-10 TV6', 'DTO/INT-10 của SS6')
    s = s.replace('powerước', 'power ước').replace('giới hạnSS1', 'giới hạn ở SS1')
    s = re.sub(r'SoC(?=\d)', 'SoC ', s)
    # Preserve literal filenames and paths while normalizing prose spacing.
    pieces = re.split(r'(`[^`]+`|(?<!\w)[\w./-]+\.(?:md|pdf|docx|json|py|puml|svg|png|txt|tex)\b)', s)
    for i in range(0, len(pieces), 2):
        pieces[i] = re.sub(r'(?<=[a-zà-ỹ])(?=\d)', ' ', pieces[i])
        pieces[i] = pieces[i].replace('mục6', 'mục 6')
    return ''.join(pieces).strip()


def h(level, text):
    BLOCKS.append(('heading', level, text))
    if level == 1:
        CHAPTERS.append(text)


def p(text): BLOCKS.append(('paragraph', norm(text)))
def code(text): BLOCKS.append(('code', text))
def table(headers, rows, widths=None): BLOCKS.append(('table', headers, rows, widths))
def figure(path, title, portrait=False):
    FIGURES.append((path, title))
    BLOCKS.append(('figure', path, f'Hình {len(FIGURES)}  {title}', portrait))


def parse_classes(n):
    source = ROOT / f'docs/diagrams/submission_3/SS{n}/class_diagram.puml'
    result = []
    current = None
    for raw in source.read_text().splitlines():
        line = re.sub(r'\\n\s*', ' ', raw)
        match = re.match(r'\s*class\s+(?:"([^"]+)"(?:\s+as\s+(\w+))?|(\w+)(?:<[^>]+>)?)', line)
        if match:
            name = match[2] or match[3] or match[1]
            stereo = re.search(r'<<(.+?)>>', line)
            current = {'name':name,'label':match[1] or name,'fields':[], 'methods':[], 'stereotype':stereo[1] if stereo else ''}
            result.append(current)
        elif current:
            method = re.match(r'\s*(?:\{static\}\s*)?[+#-](\w+)\((.*)\)\s*:\s*(.*)', line)
            field = re.match(r'\s*[+#-](\w+)\s*:\s*(.*)', line)
            if method: current['methods'].append((method[1],method[2],method[3]))
            elif field: current['fields'].append((field[1], field[2]))
        if line.strip() == '}': current = None
    return result


def read_catalog(n):
    member = next(DEST.glob(f'TV{n}_*'))
    text = (member/'method_catalog.md').read_text()
    result=[]
    for part in re.split(r'^## ',text,flags=re.M)[1:]:
        lines=part.splitlines()
        name=re.search(r'`([^`]+)`',lines[0])
        signature=re.search(r'\*\*Chữ ký:\*\* `([^`]+)`',part)
        if not name or not signature: continue
        body=re.search(r'\*\*(?:Hành vi, điều kiện, lỗi và gọi lặp|Điều kiện, hành vi, kết quả, lỗi và gọi lặp):\*\* ([\s\S]*?)(?=\n\n\*\*|\Z)',part)
        mapping=re.search(r'\*\*Ánh xạ:\*\* ([^\n]+)',part)
        result.append({'name':name[1],'signature':signature[1],'body':norm(body[1]) if body else '', 'mapping':mapping[1] if mapping else '', 'ss':n})
    return result


for number in range(1,8): CLASSES[number]=parse_classes(number)
# Prefer the actual owner of shared services when the same method is drawn twice.
for number in [1,5,6,7,2,3,4]:
    for entry in read_catalog(number):
        key=entry['name']
        if key in CATALOG:REPEATED.append((number,key,CATALOG[key]['ss']))
        else:CATALOG[key]=entry

SCOPE={
1:('Đặt và quản lý xe dùng chung','student_booking.py','booking.py và billing.py',
'SS1 quản lý hành trình của xe dùng chung từ tra cứu, đặt giữ chỗ và nhận xe đến trả xe, hủy hoặc hết hạn. BookingService điều phối thay đổi xe và chỗ đỗ; BillingService tiếp nhận các khoản cọc và phí. Thiết kế tách quyền định danh, trạng thái phương tiện và biến động ví để các phân hệ khác có thể dùng cùng một hợp đồng tài chính.',
'User có nhiều Booking; mỗi Booking tham chiếu một SharedVehicle và Hub nguồn. Hub đích dự kiến có bội số 0..1; khi trả phải xác định Hub trả thực tế. SharedVehicle kế thừa Vehicle với ownership SHARED. User sở hữu Wallet, Wallet có lịch sử Transaction, Invoice chứa các ChargeLine. Các quan hệ lịch sử không cho phép hai lượt đang hoạt động cùng giữ một xe.',
'Core đã có các hàm đặt, nhận, trả, hủy và xử lý hết hạn; dữ liệu booking/ví chủ yếu là dictionary. Service OOP, sổ cọc theo reference và dedup charge_id dùng chung chưa được hiện thực. Core đặt xe còn cần kiểm tra ownership bên cạnh bộ lọc UI; ưu đãi điều hướng cần marker một lần; nguồn số đo quãng đường cho US-06 chưa có.'),
2:('Xe cá nhân và quản lý chỗ đỗ','personal_ev.py','personal_ev.py và billing.py',
'SS2 quản lý hồ sơ xe cá nhân, đặt trước chỗ đỗ, check-in và check-out. PersonalVehicle kế thừa Vehicle và liên kết chủ xe qua owner_id. ParkingReservation thể hiện quyền giữ một chỗ đến hạn; ParkingSession ghi nhận sự hiện diện thực tế và tham chiếu yêu cầu hoặc phiên sạc do SS5 quản lý.',
'Một User có nhiều PersonalVehicle; mỗi ParkingReservation gắn một xe, một chủ xe và một Hub. Một reservation kích hoạt tối đa một ParkingSession. Khi check-in, chỗ giữ trước chuyển thành hiện diện vật lý mà không giảm available_slots lần hai. Request sạc đang chờ có thể chưa có session_id hoặc cổng thực sự.',
'Core đã có đăng ký, reserve, check-in/out và sweep. Adapter đổi ev_id thành vehicle_id trong thiết kế. Hợp đồng ChargingService và BillingService chưa được tích hợp đầy đủ; check-in có thể gán CHARGING trước khi được cấp cổng. Phí đỗ hiện là 5.000 VNĐ/lượt, khác yêu cầu theo giờ; điện năng và quá giờ là đầu vào mô phỏng, tariff chọn tại checkout. Barie và QR là tương tác mô phỏng.'),
3:('Giám sát mạng lưới Hub','hub_monitor.py','state.py và policies.py',
'SS3 cung cấp một bản đọc trạng thái mạng lưới tại cùng thời điểm và phiên bản. Hub là mô hình dùng chung; OccupancySnapshot mô tả một trạm, NetworkSnapshot tổng hợp KPI toàn mạng và Alert thể hiện cảnh báo theo ngưỡng hoặc cổng offline mô phỏng. MonitoringService chỉ đọc, không sở hữu thay đổi booking hoặc ví.',
'Một NetworkSnapshot chứa nhiều OccupancySnapshot; mỗi snapshot và Alert tham chiếu một Hub. Chỗ đỗ, chỗ giữ trước và hiện diện vật lý được đếm riêng. Công suất sạc phải lấy từ các phiên đang CHARGING; cổng offline không được coi là đang tiêu thụ điện. Held deposit và debt được tách khỏi doanh thu đã thu.',
'Dashboard hiện xử lý trong render() khi Streamlit rerun; chưa có lớp MonitoringService hay push IoT nền. Tổng thu hiện chỉ cộng một số giao dịch SS1; chưa đại diện đầy đủ cho SS2/SS5. Ước tính power theo total-minus-available nhân 7,4 kW có thể đếm offline và khác scheduler mặc định 11 kW/cổng.'),
4:('Điều chuyển và sự cố phương tiện','dispatch_incident.py','state.py',
'SS4 tách điều chuyển phương tiện và xử lý sự cố thành DispatchService và IncidentService. DispatchOrder theo dõi tập xe đi từ Hub nguồn đến Hub đích; VehicleIncident lưu người báo, người tiếp nhận, mức độ và thời điểm xử lý. Hai nghiệp vụ cùng bảo vệ vòng đời tài nguyên nhưng có bản ghi và trạng thái riêng.',
'Mỗi lệnh điều chuyển gắn một Hub nguồn, một Hub đích và ít nhất một SharedVehicle. Chỉ xe SHARED đủ điều kiện được điều chuyển. VehicleIncident tham chiếu đúng một Vehicle và không thay thế InfrastructureFailure của SS7. Khi phục hồi, trạng thái xe phải xét các binding booking/charging còn hiệu lực.',
'Các thao tác hiện nằm trong UI render(), chưa có hai service độc lập hoặc operation_key. Prototype có giữ chỗ đích cho lệnh; bước nhận còn cần kiểm tra lại hold/capacity. Resolve hiện đưa xe AVAILABLE trực tiếp, chưa bảo vệ đầy đủ previous_status và các binding. Nhật ký nằm trong session, chưa là log lưu bền.'),
5:('Lập lịch và quản lý phiên sạc','smart_charging.py','scheduler.py và billing.py',
'SS5 tiếp nhận nhu cầu sạc, xếp queue, cấp tài nguyên theo mức ưu tiên và giới hạn công suất, mô phỏng tiến trình sạc, tính phí điện và phí chiếm dụng cổng. ChargingRequest, ChargingSession và SmartChargingScheduler đã có trong core; ChargingService chuẩn hóa giao tiếp với SS2, SS3 và SS7 trong thiết kế mục tiêu.',
'Scheduler quản lý nhiều yêu cầu và phiên. Một phiên đang hoạt động liên kết một xe, một Hub và một cổng; lịch sử có thể có nhiều phiên nhưng không cấp trùng tài nguyên đang dùng. ChargingBill chứa các ChargeLine và số đã thu; BillingService thuộc SS1 chịu trách nhiệm ghi nhận tiền, SS5 không tự tạo một sổ ví khác.',
'Thuật toán core dùng SoC và booking để tính điểm; requested_at dùng phá hòa, chưa phải trọng số chờ tăng dần. Giá điện chưa là trọng số score. ChargingService, ChargingPort vật lý và adapter lỗi cổng chưa có; các hàm billing hiện vẫn có thể sửa ví trực tiếp. Luồng nhân viên xác nhận thanh toán US-12 cần hoàn thiện trước demo/final.'),
6:('Mô phỏng nhu cầu và dự báo 24 giờ','sim_demand.py','simulator.py và state.py',
'SS6 tạo kịch bản nhu cầu cách ly và chuỗi dự báo 24 giờ. DemandSimulationService và ForecastService bọc HubEventSimulator; SimulationCoordinator là đầu mối Apply chung cho SS6/SS7 trong thiết kế. Dự báo ghi giả định và seed để có thể tái lập; preview lưu baseline_version để phát hiện dữ liệu đã đổi.',
'ForecastResult chứa đúng 24 ForecastPoint theo thiết kế Sub3. SimulationPreview là bản sao candidate cùng charging_effects, summary và trạng thái Apply; không chứa một bản ví/booking để chép đè. Coordinator quản lý preview, gọi SS5 khi có lỗi cổng và chỉ commit khi toàn bộ điều kiện đều hợp lệ.',
'HubEventSimulator đã triển khai, service/coordinator/DTO OOP vẫn là đề xuất. UI và core mặc định 12 giờ nhưng cho phép chọn 24 tường minh. Apply hiện nằm riêng trong hai UI và có version check; chưa là transaction chung với SS5. US-21 chưa có mô hình biến động doanh thu. Log dùng đồng hồ thực cần loại khỏi tiêu chí so sánh kết quả nghiệp vụ.'),
7:('Sự cố hạ tầng và gợi ý Hub thay thế','sim_infrastructure.py','simulator.py và routing.py',
'SS7 mô phỏng lỗi cổng hoặc mức mất điện của Hub, đánh giá ảnh hưởng và gợi ý điểm đến thay thế. InfrastructureSimulationService tạo preview PORT_FAILURE theo DTO chung; ReroutingService chỉ trả danh sách đề xuất. Thay đổi booking thuộc BookingService và chỉ diễn ra sau xác nhận của người dùng.',
'InfrastructureFailure ghi bối cảnh sự cố, không tạo một cơ chế Apply mới. RouteSuggestion tham chiếu Hub cùng khoảng cách km và số chỗ/cổng tại thời điểm đề xuất. Danh sách rỗng là kết quả hợp lệ. Gợi ý không giữ tài nguyên; chỗ/cổng và phiên bản phải được kiểm tra lại khi người dùng chấp nhận.',
'Simulator hiện dùng số đếm cổng và deepcopy; chưa có port ID/session adapter hoặc IoT thật. Routing chưa có bộ lọc OFFLINE chuẩn. Lỗi cổng không được làm thay đổi capacity đỗ. INT-05 xử lý phiên sạc và INT-10 Apply là hợp đồng mục tiêu; không suy ra đã có cơ chế phục hồi điện thực tế.')}

ROLES={
'BookingService':'Điều phối vòng đời booking xe chung, quyền sử dụng xe, giữ chỗ đích và xác nhận điều hướng; gọi BillingService khi có biến động tiền.',
'BillingService':'Đầu mối tài chính dùng chung: giữ và hoàn cọc theo reference, phạt no show, quyết toán dòng phí và ghi phần nợ. Thiết kế bảo vệ lịch sử bằng operation_key và charge_id.',
'PersonalEVService':'Điều phối hồ sơ xe cá nhân và vòng đời đặt chỗ, check-in/out; phối hợp ChargingService và BillingService để giữ một nguồn phí và tài nguyên thống nhất.',
'MonitoringService':'Tạo snapshot và phân loại occupancy từ dữ liệu cùng phiên bản; chỉ đọc, không tự sửa tài nguyên hoặc ghi doanh thu.',
'DispatchService':'Kiểm tra điều kiện xe và capacity, giữ chỗ đích rồi hoàn tất điều chuyển trong ranh giới cập nhật nhất quán.',
'IncidentService':'Quản lý report, acknowledge và resolve sự cố xe; phối hợp các chủ sở hữu booking/charging trước khi cách ly hoặc phục hồi phương tiện.',
'SmartChargingScheduler':'Quản lý queue và các phiên sạc đang hoạt động; tính ưu tiên, cấp công suất/cổng, tick trạng thái và giải phóng phiên khi rút xe.',
'ChargingService':'Hợp đồng chuẩn hóa yêu cầu sạc, hóa đơn chỉ đọc và xử lý cổng lỗi; kết nối SS2/SS3/SS7 với scheduler mà không tạo sổ ví riêng.',
'DemandSimulationService':'Kiểm tra đầu vào Metro Surge, gọi engine trên candidate cách ly và đóng gói SimulationPreview để người dùng xem trước khi Apply.',
'ForecastService':'Chuẩn hóa đầu vào dự báo và tạo ForecastResult đủ 24 điểm với seed, giả định và các đơn vị rõ ràng.',
'SimulationCoordinator':'Đầu mối Apply chung cho SS6/SS7: phát hiện stale, stage tác động liên phân hệ, commit toàn bộ và ngăn áp dụng cùng preview lần hai.',
'InfrastructureSimulationService':'Tạo preview PORT_FAILURE và mô tả ảnh hưởng hạ tầng; giao quyền commit cho SimulationCoordinator thay vì tự đổi Hub đang vận hành.',
'ReroutingService':'Lọc và xếp hạng Hub thay thế theo tài nguyên, trạng thái và khoảng cách; trả gợi ý để người dùng xác nhận, không tự đổi booking.',
'RoutingModule':'Ký hiệu module core.routing với các hàm tìm Hub thay thế hiện có; đây là module hàm, không phải service OOP đã hiện thực.',
'SS7UI':'Ký hiệu module giao diện sim_infrastructure.render hiện có; nhận tham số mô phỏng, hiển thị preview/gợi ý và xử lý thao tác Apply trong prototype.',
'User':'Lưu định danh và vai trò; danh tính hiện được chọn trong mô phỏng. Thiết kế ràng buộc mỗi thao tác tới người dùng có quyền.',
'Vehicle':'Mô hình chung cho định danh, ownership, Hub, SoC và trạng thái; SoC tính theo phần trăm từ 0 đến 100.',
'SharedVehicle':'Chuyên biệt của Vehicle cho xe dùng chung. Ownership luôn SHARED; xe đang bị giữ, đang dùng hoặc sự cố không được cấp lại.',
'Booking':'Lưu vòng đời giữ và sử dụng xe, các mốc thời gian và Hub liên quan. EXPIRED chỉ áp dụng khi chưa nhận xe.',
'Wallet':'Phân biệt số dư khả dụng, cọc đang giữ và nợ; các đại lượng không âm, tiền lưu VNĐ nguyên.',
'Transaction':'Bản ghi dòng tiền có định danh và tham chiếu nghiệp vụ. Thiết kế xem lịch sử đã ghi là bất biến.',
'Invoice':'Tập hợp dòng phí, khoản đã thu và phần nợ theo reference; không bổ sung số đo quãng đường khi chưa có dữ liệu.',
'ChargeLine':'Khoản phí có charge_id ổn định. Cùng khoản đã thu không được đổi ID để thu lại hoặc thay số tiền của lịch sử.',
'DepositResult':'Kết quả xử lý cọc theo đúng reference, ghi phần đang giữ, phần đã hoàn và trạng thái.',
'SettlementResult':'Kết quả quyết toán với paid, refunded, debt và danh sách phí; khoản nợ được thể hiện rõ thay vì bỏ phần thiếu.',
'OperationResult':'Kiểu kết quả dùng chung: thành công/dữ liệu hoặc mã lỗi/thông điệp, kèm state_version. Lỗi không cho phép commit một phần.',
'PersonalVehicle':'Hồ sơ xe cá nhân với ownership PERSONAL, định danh chủ xe, biển số chuẩn hóa và dung lượng pin kWh.',
'ParkingReservation':'Quyền giữ chỗ từ giờ đến đã chọn tới hạn check-in. Deadline bằng booking_start_time cộng 30 phút.',
'ParkingSession':'Lượt đỗ thực tế, ghi check-in/out và tham chiếu sạc. Request đang chờ không được đồng nhất với phiên/cổng đã cấp.',
'Hub':'Định nghĩa chuẩn do SS3 sở hữu cho chỗ đỗ, xe, giữ chỗ, tải nền và số đếm cổng. Không tạo bảy mô hình Hub khác nhau.',
'OccupancySnapshot':'Bản đọc một Hub tại captured_at; lượng hiện diện, giữ chỗ và background được tách để kiểm tra bảo toàn sức chứa.',
'NetworkSnapshot':'Bản đọc toàn mạng theo version, kèm doanh thu đã thu, cọc và nợ; không sửa các bản ghi nghiệp vụ.',
'Alert':'Cảnh báo occupancy hoặc offline mô phỏng với thời điểm và Hub; không khẳng định đã có cảm biến/push nền thật.',
'DispatchOrder':'Lệnh chuyển tập xe giữa hai Hub khác nhau. Thiết kế CREATED/IN_TRANSIT/COMPLETED; prototype tạo thẳng IN_TRANSIT.',
'VehicleIncident':'Sự cố xe REPORTED/ACKNOWLEDGED/RESOLVED, có previous_status để hỗ trợ phục hồi hợp lệ.',
'ChargingRequest':'Yêu cầu đang chờ, có SoC, thời điểm, booking và công suất. Lớp dataclass đã có trong scheduler.py.',
'ChargingSession':'Phiên sạc hiện có: định danh xe/cổng, SoC, kW, kWh, thời điểm, thông báo và dữ liệu grace/overstay.',
'ChargingRequestResult':'DTO trả về yêu cầu mới; session_id có thể rỗng khi vẫn chờ. Đây là thiết kế đề xuất.',
'ChargingPort':'Cổng có định danh, Hub, trạng thái và công suất tối đa; là lớp đề xuất, khác số đếm cổng trong seed.',
'ChargingBill':'Bản đọc lượng điện, phí điện/quá giờ, dòng phí và khoản đã thu; bản thân DTO không trừ tiền ví.',
'PortFailureResult':'Kết quả xử lý cổng lỗi, liệt kê cổng/phiên bị ảnh hưởng và công suất sau xử lý; không làm đổi số chỗ đỗ.',
'DemandScenario':'Dữ liệu đầu vào kịch bản nhu cầu không âm và seed; không tự cập nhật mạng lưới.',
'ForecastPoint':'Một mốc giờ với arrivals, queue theo người và wait_time_min theo phút; đây là ước lượng mô hình.',
'ForecastResult':'Kết quả đủ 24 điểm, có giả định và seed. Service rate 8 xe/giờ là giả định, không phải số đo mọi Hub.',
'SimulationPreview':'DTO chuẩn dùng chung cho DEMAND/PORT_FAILURE, chứa candidate cách ly và tác động dự kiến; metrics prototype được adapter ánh xạ vào summary.',
'ApplyResult':'Phân biệt lần Apply thành công với lần gọi lại đã áp dụng; new_state_version chỉ tăng khi commit mới.',
'InfrastructureFailure':'Kịch bản/kết quả sự cố hạ tầng theo Hub; không được dùng thay VehicleIncident của SS4.',
'RouteSuggestion':'Thông tin gợi ý tại một thời điểm, gồm khoảng cách km và tài nguyên; không bảo đảm tài nguyên vẫn còn khi xác nhận.',
'HubEventSimulator':'Động cơ core đã có. _original giữ dữ liệu đầu vào, các phép mô phỏng deepcopy trước khi thay đổi; constructor không tự tạo trạng thái vận hành mới.',
'BillingFunctions':'Ký hiệu nhóm hàm trong core/billing.py, không phải một class instance được triển khai. Caller quản lý vòng đời và thời điểm ghi tiền.',
'SS2UI':'Ký hiệu module UI personal_ev với khởi tạo trạng thái và render; không thay thế lớp miền hoặc authorization thật.',
'PersonalEVModule':'Ký hiệu module core.personal_ev đã có; adapter trả tuple/dictionary, khác API OOP mục tiêu.'}


def compose():
    h(1,'1 Giới thiệu và phạm vi báo cáo')
    p('Báo cáo trình bày thiết kế tổng thể của Smart E-Mobility Hub cho mạng lưới trạm phương tiện điện trong Khu đô thị ĐHQG-HCM. Nhóm BEE BRAVE tổ chức hệ thống thành bảy phân hệ dùng chung mô hình tài nguyên, hợp đồng tài chính và cơ chế mô phỏng. Tài liệu hợp nhất thiết kế kiến trúc, lớp và phương thức, đồng thời truy vết tới 17 use case đã xác lập ở Submission 2.')
    p('Kiến trúc triển khai hiện tại là một ứng dụng Python/Streamlit dạng module với dữ liệu seed và trạng thái trong bộ nhớ theo session. Các service OOP được thiết kế để làm rõ ranh giới trách nhiệm và điều kiện nhất quán; báo cáo ghi riêng mức ánh xạ tới prototype, phần đã hiện thực và phần còn là đề xuất. Sự phân biệt này được giữ xuyên suốt các chương.')
    h(2,'1.1 Căn cứ và nội dung cần trình bày')
    p('Theo mục Submission 3 detail trong đề giảng viên (trang 5), báo cáo cần có Deployment view, Development/Implementation view, class diagram và mô tả tất cả phương thức trên class diagram; test case là nội dung bonus. Mô tả tổng quát ở trang 4 còn nêu class descriptions. Báo cáo này bổ sung truy vết và hợp đồng liên phân hệ để các quyết định thiết kế có thể được kiểm tra cùng SRS và mã nguồn.')
    table(['Nội dung','Vị trí trong báo cáo'],[['Triển khai và cấu trúc module','Chương 3'],['Mô hình dùng chung và giao tiếp','Chương 4'],['Class diagram và mô tả lớp phương thức SS1 đến SS7','Chương 5 đến 11'],['Truy vết 17 use case','Chương 12'],['Test case và bằng chứng hiện có','Chương 13'],['Giới hạn và đóng góp của nhóm','Chương 14 và 15']],[2.9,3.9])
    h(2,'1.2 Quy ước đọc bản thiết kế')
    p('Nhãn đã triển khai chỉ áp dụng cho lớp, hàm hoặc module thực sự có trong src/. Nhãn đề xuất áp dụng cho service, DTO và bảo đảm giao dịch chưa có code tương ứng. Ký hiệu shared là tham chiếu tới chủ sở hữu chuẩn, không tạo một bản định nghĩa khác. Kiểu datetime trong thiết kế theo đồng hồ mô phỏng quy ước UTC+7; prototype hiện lưu chuỗi naive, chưa tự mang thông tin múi giờ.')
    h(1,'2 Phạm vi hệ thống và phân công')
    p('Sinh viên sử dụng xe chung hoặc gửi xe cá nhân; nhân viên vận hành giám sát, điều phối và quản lý sạc; kỹ thuật viên xử lý sự cố; nhà phân tích đánh giá kịch bản nhu cầu và hạ tầng. Dữ liệu IoT, thanh toán, QR/barie và danh tính được mô phỏng trong phạm vi prototype. Đề bài cho phép hard-code dữ liệu và không bắt buộc database cho giai đoạn này (trang 4).')
    rows=[]
    for n,(slug,name,mssv) in MEMBERS.items():
        rows.append([f'SS{n}',name,mssv,str(sum(x['subsystem']==f'SS{n}' for x in MANIFEST['use_cases'].values())),SCOPE[int(n)][0]])
    table(['SS','Thành viên','MSSV','UC','Phạm vi'],rows,[.45,1.6,.8,.35,2.4])
    h(2,'2.1 Nguyên tắc phân chia trách nhiệm')
    p('SS1 sở hữu User, Vehicle và tài chính; SS3 sở hữu Hub; SS5 sở hữu yêu cầu, phiên và dịch vụ sạc; SS6 sở hữu ForecastResult, SimulationPreview và SimulationCoordinator. Các phân hệ còn lại giữ tham chiếu tới những mô hình này. Một khoản tiền chỉ được ghi qua hợp đồng tài chính thiết kế, còn quyền thay đổi xe, giữ chỗ và phiên sạc thuộc service phụ trách nghiệp vụ tương ứng.')
    h(1,'3 Thiết kế kiến trúc hệ thống')
    h(2,'3.1 Deployment view')
    p('Trình duyệt giao tiếp với tiến trình Python/Streamlit trên máy chạy ứng dụng. app.py điều hướng tới các component; core thực hiện các phép xử lý. state.py đọc src/data/mock_hubs.json khi khởi tạo hoặc reset. st.session_state giữ Hub, ví, booking, queue/scheduler, preview và version ở phía server theo từng phiên.')
    p('Rerun chạy lại script theo tương tác và làm mới giao diện; không phải một worker IoT hoặc background polling. Reset tạo lại trạng thái từ seed; dữ liệu session không là lưu trữ bền. Các phiên trình duyệt khác nhau không mặc nhiên cùng đọc một cơ sở dữ liệu mạng lưới. Host/cổng tùy cấu hình; chạy từ repository bằng lệnh dưới đây.')
    code('streamlit run src/app.py')
    figure('docs/diagrams/submission_3/shared/deployment.png','Sơ đồ triển khai hiện tại')
    h(2,'3.2 Development và Implementation view')
    p('Mã nguồn chia thành entry point, components giao diện và core. booking/personal_ev/billing/scheduler/simulator/routing/state/policies là các module hiện có. SS3, SS4 và các thao tác Apply SS6/SS7 còn chứa xử lý nghiệp vụ trong render(). Các service trong class diagram là bước tổ chức thiết kế mục tiêu, không phải các package core.services/core.domain đang chạy.')
    figure('docs/diagrams/submission_3/shared/implementation.png','Cấu trúc module và phụ thuộc chính')
    table(['Thành phần','Trách nhiệm','Ánh xạ'],[['Trình bày','Nhận thao tác và hiển thị kết quả','src/app.py và src/components'],['Nghiệp vụ và chính sách','Vòng đời tài nguyên và tính phí','src/core'],['Dữ liệu phiên','Seed reset và trạng thái tạm thời','state.py và st.session_state'],['Thiết kế mục tiêu','Service DTO và adapter dùng chung','Class diagram và hợp đồng trong báo cáo']],[1.3,2.5,3.0])
    h(2,'3.3 Class diagram cấp hệ thống')
    p('Sơ đồ tổng quan thể hiện ranh giới sở hữu và liên kết giữa các phân hệ. Thuộc tính và phương thức được trình bày ở các sơ đồ chi tiết và catalog trong chương 5 đến 11. Các nhãn trên sơ đồ không hàm ý toàn bộ lớp đã được hiện thực; prototype vẫn có các hàm và dictionary đóng vai trò adapter.')
    figure('docs/diagrams/submission_3/shared/system_classes.png','Liên kết lớp cấp hệ thống')
    h(2,'3.4 Ràng buộc chất lượng')
    p('Thiết kế đặt kiểm tra quyền, trạng thái và version ở ranh giới service, không chỉ ở UI. Thay đổi Hub, booking, wallet và charging phải được kiểm tra trước rồi commit đồng bộ; lỗi không được để lại phần dữ liệu đã cập nhật. Với nhiều người dùng cần storage/version/transaction chia sẻ và xác thực thật. Unit test của prototype per-session chưa chứng minh các NFR về tải, độ trễ, availability hay bảo mật production.')
    table(['Mã SRS và chỉ tiêu','Đáp ứng thiết kế và cách xác minh'],[
        ['NFR-01 UI ≤ 2 giây; NFR-02 ít nhất 500 yêu cầu đồng thời','Đo thời gian end-to-end và kiểm thử tải trên hạ tầng xác định. Metro Surge mô phỏng nhu cầu không thay thế phép đo 500 request thực. Chưa có benchmark.'],
        ['NFR-03 cập nhật ≤ 5 giây; NFR-04 uptime ≥ 99,5% trong 06:00-22:00; NFR-05 điều hướng ≤ 30 giây','Snapshot SS3 và INT-05/06 xác định trách nhiệm. Cần đo refresh, availability và thời gian phát hiện/gợi ý; Streamlit rerun hiện tại chưa chứng minh polling nền hoặc các chỉ tiêu này.'],
        ['NFR-06 nhất quán dữ liệu','Version, operation_key, charge_id và commit nguyên tử bảo vệ invariant. Cần kiểm thử đồng thời trên storage chia sẻ; session riêng không là state lock toàn hệ thống.'],
        ['NFR-07 desktop ≥ 1024px, mobile ≥ 375px; NFR-08 đặt xe ≤ 3 bước; NFR-09 tiếng Việt','Giữ luồng chọn Hub, chọn xe, xác nhận. Cần kiểm tra giao diện ở hai kích thước và thử với người dùng; unit test không thay kiểm thử khả dụng.'],
        ['NFR-10 VNU-SSO; NFR-11 ví và audit; NFR-12 Student/Operator/Admin','Auth mock chỉ phục vụ demo. Thiết kế cần kiểm tra quyền tại service và ledger có truy vết. Vai trò kỹ thuật viên/nhà phân tích cần ánh xạ quyền rõ khi mở rộng RBAC.'],
        ['NFR-13 module hóa; NFR-14 docstring mục đích, tham số, kết quả','components tách theo SS, core tái sử dụng; service mục tiêu giảm nghiệp vụ trong render. Rà docstring và dependency khi bàn giao; việc có module không bảo đảm mọi thay đổi đều độc lập.']
    ],[2.9,3.9])
    h(1,'4 Mô hình dùng chung và hợp đồng liên phân hệ')
    h(2,'4.1 Chính sách và đơn vị')
    table(['Quy tắc','Giá trị và điều kiện'],[['Giữ xe chung','30 phút từ lúc tạo booking; now bằng expires_at là hết hạn khi chưa nhận'],['Giữ chỗ xe cá nhân','30 phút từ booking_start_time đã chọn'],['Cọc và no show','50.000 VNĐ; phạt 10.000 và hoàn 40.000 VNĐ một lần'],['Thuê xe chung','Miễn 30 phút đầu; sau đó 1.000 VNĐ/phút; voucher hợp lệ giảm 5.000'],['Điều hướng','Thêm 15 phút miễn phí tối đa một lần; không đổi TTL giữ xe'],['Ân hạn và overstay','Ân hạn 15 phút; 10.000 VNĐ cho mỗi khối 15 phút bắt đầu sau ân hạn'],['Công suất mặc định','150 kW/Hub và 11 kW/cổng; từng cấu hình/test có thể dùng giá trị khác'],['Phí và tariff','Prototype đỗ 5.000 VNĐ/lượt; điện cao điểm 7.000 và thấp điểm 3.000 VNĐ/kWh'],['Ngưỡng occupancy','NORMAL dưới 70; WARNING từ 70 đến dưới 85; CRITICAL từ 85 đến dưới 100; FULL từ 100 phần trăm']],[1.7,5.1])
    p('Tiền lưu số nguyên VNĐ; công suất kW khác năng lượng kWh; SoC dùng phần trăm, khoảng cách km. Capacity được bảo toàn theo available_slots + present_vehicles + destination_holds + background_occupied = total_slots. Present không tính xe IN_USE đã rời Hub. Giữ chỗ đến và xe hiện diện không được cộng hai lần cho cùng một chỗ.')
    h(2,'4.2 Kiểu trao đổi và xử lý lặp')
    p('OperationResult trả ok, data hoặc error_code, message và state_version. ChargeLine có charge_id, source_id, kind, amount_vnd ổn định; SettlementResult tách paid, refunded và debt. Lặp operation_key với cùng payload trả kết quả cũ; khác payload trả CONFLICTING_OPERATION. Cùng charge_id nhưng khác tiền trả CONFLICTING_CHARGE, không ghi đè lịch sử.')
    p('SimulationPreview thống nhất cho DEMAND và PORT_FAILURE gồm preview_id, scenario_type, baseline_version, modified_hubs, charging_effects, summary và is_applied; target_hub_id/event_log hỗ trợ adapter UI. metrics của prototype được ánh xạ sang summary. Preview chứa candidate cách ly, không dùng snapshot ví/booking cũ để chép đè trạng thái hiện tại.')
    contracts=[('INT-01','SS5 ChargingService','SS2','request_charging','Tạo yêu cầu sau check-in hợp lệ; request đang chờ chưa có cổng'),('INT-02','SS5 ChargingService','SS2 SS3','get_bill','Đọc hóa đơn sạc và khoản đã thu; không trừ ví'),('INT-03','SS3 MonitoringService','Dashboard','get_network_snapshot','Đọc cùng timestamp/version; tách cọc và nợ'),('INT-04','SS6 ForecastService','SS6 SS3 SS4','forecast','Yêu cầu 24 giờ tường minh; seed tái lập'),('INT-05','SS5 ChargingService','Coordinator','handle_port_failure','Stage tác động cổng/phiên trong Apply; không đổi slot đỗ'),('INT-06','SS7 ReroutingService','SS1 SS7','suggest_hubs','Lọc tài nguyên/tình trạng và xếp Haversine; không đổi booking'),('INT-07','SS1 BookingService','UI sau xác nhận','accept_rerouting','Kiểm tra lại quyền/version/capacity; chuyển hold và ưu đãi một lần'),('INT-08','SS6 DemandSimulationService','SS6','preview_demand','Tạo preview DEMAND cách ly'),('INT-09','SS7 InfrastructureSimulationService','SS7','preview_port_failure','Tạo preview PORT_FAILURE theo cùng schema'),('INT-10','SS6 SimulationCoordinator','SS6 SS7','apply_preview','Commit đồng bộ sau validation; chống stale và Apply lặp')]
    table(['ID','Chủ sở hữu và bên gọi','Giao tiếp và trách nhiệm'],[[a,b+'; gọi từ '+c,d+' - '+e] for a,b,c,d,e in contracts],[.7,2.1,4.15])
    h(2,'4.3 Luồng tài chính và sạc')
    p('SS2 xác nhận check-in rồi gửi nhu cầu sạc qua INT-01. SS5 quản lý queue và cấp cổng theo công suất. Khi check-out, SS2 lấy ChargingBill qua INT-02, cộng dòng phí đỗ và gửi BillingService.settle_invoice. Chỉ các charge_id chưa thu được xử lý; phần thiếu được ghi nợ minh bạch. SS2 không tính lại phí SS5 bằng một công thức khác khi giao tiếp mục tiêu đã được dùng.')
    h(2,'4.4 Luồng preview và Apply')
    p('SS6 hoặc SS7 lấy snapshot/version, tạo candidate bằng deepcopy và lưu preview. Khi Apply, coordinator kiểm tra baseline_version, expected_version và version hiện tại cùng invariant. Nếu là PORT_FAILURE, tác động SS5 qua INT-05 được stage cùng thay đổi Hub. Chỉ commit khi mọi kiểm tra thành công, tăng version một lần và ghi is_applied; lỗi giữ nguyên state. Gọi lại preview đã áp dụng trả already_applied trước khi kiểm tra stale, không gây tác động lần hai.')
    h(2,'4.5 Luồng điều hướng')
    p('SS7 trả RouteSuggestion theo nhu cầu slot/cổng và khoảng cách. UI trình đề xuất cho người dùng; chỉ sau xác nhận mới gọi INT-07. BookingService kiểm tra lại version, quyền, trạng thái và capacity của Hub mới, chuyển giữ chỗ cũ/mới trong cùng thao tác và áp dụng ưu đãi tối đa một lần. Gợi ý cũ không là bảo đảm tài nguyên còn trống.')

    for n in range(1,8):
        title,ui,core,overview,relations,limits=SCOPE[n]
        chapter=n+4
        h(1,f'{chapter} Thiết kế SS{n} {title.lower()}')
        p(overview)
        ucs=[(k,v) for k,v in MANIFEST['use_cases'].items() if v['subsystem']==f'SS{n}']
        table(['Use case','Phạm vi'],[[k,v['name']] for k,v in ucs],[1.0,5.8])
        p(f'Phần trình bày hiện tại nằm ở src/components/{ui}; ánh xạ nghiệp vụ tại src/core/{core}. Chủ sở hữu theo phân công là {MEMBERS[str(n)][1]}, MSSV {MEMBERS[str(n)][2]}.')
        h(2,f'{chapter}.1 Class diagram và quan hệ')
        p(relations)
        figure(f'docs/diagrams/submission_3/SS{n}/class_diagram.png',f'Class diagram SS{n}',portrait=(n==3))
        # The wide SS2 SS5 SS7 diagrams have separate whole service boxes for print readability.
        for target in {2:['PersonalEVService','PersonalEVModule'],5:['SmartChargingScheduler','ChargingService','BillingFunctions'],7:['InfrastructureSimulationService','ReroutingService']}.get(n,[]):
            cropped=class_crop(n,target)
            if cropped:figure(str(cropped.relative_to(ROOT)),f'Chi tiết {target} trong sơ đồ SS{n}')
        h(2,f'{chapter}.2 Mô tả lớp và thuộc tính')
        for cls in CLASSES[n]:
            name=cls['name']
            external=any(w in cls['stereotype'].lower() for w in ['shared','external'])
            if external:continue
            if n==7 and name=='HubEventSimulator':
                p('HubEventSimulator là động cơ dùng chung đã mô tả ở chương 10; SS7 sử dụng thêm simulate_port_failure được đặc tả tại mục phương thức của chương này.')
                continue
            h(3,name if name!='OperationResult' else 'OperationResult tổng quát')
            role=ROLES.get(name, f'{name} điều phối các phương thức được liệt kê trong mục tiếp theo; ánh xạ đến hàm/module hiện có không đồng nghĩa class service đã được triển khai.')
            p(role)
            stereo=cls['stereotype'].lower()
            status='Đã có trong prototype' if ('implemented' in stereo and 'not implemented' not in stereo) or name=='HubEventSimulator' else 'Thiết kế đề xuất'
            p(f'Mức triển khai: {status}.')
            if cls['fields']:
                p('Thuộc tính: '+'; '.join('`'+a+': '+b+'`' for a,b in cls['fields'])+'.')
            elif not cls['methods']:p('Lớp được tham chiếu ở mức trách nhiệm; các trường dữ liệu chi tiết theo mô hình chuẩn của chủ sở hữu.')
            if name=='SmartChargingScheduler':p('queue_length là property đọc số phần tử queue, không làm thay đổi scheduler. Đọc property không tạo request, phiên hoặc khoản thu.')
        h(2,f'{chapter}.3 Mô tả phương thức')
        own=[x for x in CATALOG.values() if x['ss']==n]
        for entry in own:
            BLOCKS.append(('method',entry['name']))
            code(entry['signature'])
            p(entry['body'])
            if entry['mapping']:p('Ánh xạ hiện tại: '+entry['mapping'])
        repeat=[x for x in REPEATED if x[0]==n]
        if repeat:
            p('Các phương thức shared được tham chiếu trên sơ đồ nhưng chỉ đặc tả một lần trong báo cáo tổng: '+ '; '.join(f'`{name}` tại chương {owner+4}' for _,name,owner in repeat)+'. Việc tham chiếu không tạo service hoặc chữ ký mới.')
        h(2,f'{chapter}.4 Ánh xạ và giới hạn triển khai')
        p(limits)
        if n==5:
            p('Điểm ưu tiên hiện tại: score = 0,5 × (100 - SoC) + 100 khi SoC < 20 + 60 khi có booking + 30 khi SoC < 50. Queue sắp theo (-score, requested_at, vehicle_id). Cấp cổng kiểm tra tổng công suất của các phiên CHARGING đang có và phần cấp mới. Tick cập nhật SoC/energy và phát sự kiện; unplug giải phóng phiên, còn UI/service chịu đồng bộ số cổng và khoản thu.')
        if n==6:
            p('Dự báo dùng service_rate = 8 xe/giờ, hệ số cao điểm 2,5 tại 7/8/17/18 giờ và 1,5 tại 9/16/19 giờ. Nhiễu Gaussian có độ lệch chuẩn 1,5; arrivals được chặn không âm. Queue cuối giờ bằng max(0, queue trước + arrivals - 8), thời gian chờ ước lượng bằng queue/8 nhân 60 phút. Đây là mô hình giả định, chưa là dữ liệu dự báo doanh thu hoặc số đo chờ thực tế.')

    h(1,'12 Truy vết yêu cầu và thiết kế')
    p('Chuỗi truy vết được giữ từ SRS tới use case, scenario và sequence/activity của Submission 2, sau đó tới lớp/phương thức Sub3 và test. Mã UC, người phụ trách và đường dẫn sơ đồ kế thừa manifest chuẩn. Các alias hàm cũ trong Sub2 không được dùng để khẳng định một method OOP hiện đã có code.')
    for n in range(1,8):
        h(2,f'12.{n} Truy vết SS{n}')
        for uc,row in MANIFEST['use_cases'].items():
            if row['subsystem']!=f'SS{n}':continue
            BLOCKS.append(('method',uc+' '+row['name']))
            p('Yêu cầu: '+', '.join(row['user_stories']+row['functional_requirements'])+'.')
            p('Thiết kế phụ trách: '+', '.join('`'+m+'`' for m in row['design_methods'])+'.')
            p('Đầu vào Sub2: '+Path(row['sequence']).name+' và '+Path(row['activity']).name+'. Scenario: '+Path(row['scenario']).name+'.')
            p('Bằng chứng test prototype: '+ '; '.join('`'+t+'`' for t in row['prototype_tests'])+'.')
    h(1,'13 Test case và bằng chứng kiểm tra')
    p('Log review ngày 06/11/2026 ghi nhận 49 trường hợp pytest đạt trên bộ core/UI prototype. Đây là kết quả của lần chạy được lưu tại docs/audit/submission_3/review_20261106/pytest-baseline.txt, không phải tuyên bố đã chạy lại trong lần soạn báo cáo này. Test của hàm core/UI không chứng minh service OOP đề xuất đã được triển khai.')
    code('PYTHONPATH=src python -m pytest -q')
    cases=[
('TC-T01','SS1 giữ xe và hết hạn','Tạo booking lúc 08:00; nhận ở 08:29:59 và ở lượt độc lập 08:30:00','Trước hạn nhận được; đúng hạn EXPIRED, phạt10.000/hoàn40.000; sweep lặp không quyết toán lần hai','test_reservation_30_minutes.py'),
('TC-T02','SS1 trả xe và giữ chỗ','Giữ HubB rồi trả tại HubC; lặp thao tác trả','HoldB được trả, xe hiện diệnC, số chỗ bảo toàn; không thu hai lần','test_submission_2_readiness_fixes.py'),
('TC-T03','SS2 đăng ký và lượt đỗ','Đăng ký biển số với cách viết khác; reserve check-in/out','Từ chối biển số trùng; chuyển hold thành hiện diện không trừ slot hai lần','test_personal_ev.py'),
('TC-T04','SS2 giờ đến tương lai','Đặt giờ09:00; thử trước09:00 và đúng09:30','Trước giờ từ chối; đúng deadline xử lý hết hạn và quyết toán một lần','test_submission_2_acceptance.py'),
('TC-T05','SS3 occupancy','Đầu vào dưới70,70,85 và100 phần trăm','NORMAL WARNING CRITICAL FULL đúng biên','test_core_state_and_billing.py'),
('TC-T06','SS3 doanh thu prototype','Tạo booking/giao dịch trong session rồi mở dashboard','UI hiển thị ledger và khoản thu được assert; không chứng minh mọi loại thu SS2/SS5','test_submission_2_acceptance.py'),
('TC-T07','SS4 điều chuyển','Chọn xe SHARED AVAILABLE, nguồn khác đích; tạo và nhận','Xe di chuyển đúng vòng đời và capacity/hold bảo toàn','test_submission_2_acceptance.py'),
('TC-T08','SS4 sự cố xe','Report rồi acknowledge và resolve trong UI','Ghi lịch sử và trạng thái theo workflow được assert','test_submission_2_acceptance.py'),
('TC-T09','SS5 ưu tiên và power','Ba request7,4kW, cap20kW; allocate lặp','Chỉ hai phiên14,8kW; lần gọi sau không vượt cap','test_scheduler_and_charging.py và test_submission_2_readiness_fixes.py'),
('TC-T10','SS5 grace và overstay','Phiên98 phần trăm; tick15 phút,15 phút rồi5 phút','Vào grace khi đầy; đúng15 phút vẫn grace; sau đó overstay10.000','test_scheduler_and_charging.py'),
('TC-T11','SS6 forecast','rate15 multiplier1,5 hours24 seed42; chạy hai lần','Đúng24 mốc06:00 đến05:00, queue/wait không âm, kết quả tái lập','test_submission_2_acceptance.py'),
('TC-T12','SS6 Metro Surge','Nhu cầu50 tại Hub ít chỗ; so trước/sau','Nguồn không đổi; admitted theo chỗ trống và unserved phần thiếu','test_simulations.py'),
('TC-T13','SS7 lỗi cổng và stale','Tạo preview lỗi cổng; đổi version trước Apply','Preview cách ly; stale không ghi đè Hub hiện tại','test_simulations.py và test_submission_2_acceptance.py'),
('TC-T14','SS7 điều hướng','Tìm hai Hub phù hợp; chấp nhận gợi ý trong phạm vi test','Xếp khoảng cách và chuyển hold/ưu đãi theo các assert hiện có','test_submission_2_acceptance.py')]
    for id,title,inp,expected,src in cases:
        BLOCKS.append(('method',id+' '+title))
        p('Đầu vào và thao tác: '+inp+'.')
        p('Kết quả mong đợi: '+expected+'.')
        p('Phạm vi bằng chứng: có kiểm thử prototype trong tests/'+src+'. Trạng thái đạt trong baseline49; chi tiết các assert vẫn là giới hạn của bằng chứng.')
    h(2,'13.1 Ca kiểm thử hợp đồng mới thiết kế')
    table(['Ca','Điều kiện và kết quả mong đợi','Trạng thái'],[['Tài chính lặp','Cùng charge_id/key không thu lần hai; đổi tiền cùng ID phải CONFLICTING_CHARGE','DESIGNED'],['Apply nguyên tử','INT-05 lỗi thì rollback Hub/cổng/phiên, không tăng version','DESIGNED'],['Reroute nhiều lần','Đổi qua nhiều Hub vẫn chỉ thêm15 phút một lần','DESIGNED'],['Phục hồi binding','Xe còn booking/charging không trở lại AVAILABLE trái điều kiện','DESIGNED'],['Doanh thu toàn mạng','Cộng thực thu SS1/SS2/SS5, loại cọc/hoàn và tách debt','DESIGNED']],[1.25,4.65,.9])
    h(1,'14 Giới hạn và hướng hoàn thiện')
    p('Bản thiết kế đưa ra các trách nhiệm và giao tiếp cần có để bảo toàn tài nguyên khi nhiều luồng tương tác. Prototype hiện vẫn còn khoảng cách giữa service mục tiêu và hàm/UI thực thi. Nhóm ghi các khoảng cách này để tránh coi sơ đồ hoặc mô tả như bằng chứng tích hợp đã chạy.')
    table(['Hạng mục','Giới hạn hiện tại','Hướng hoàn thiện'],[['Tài chính và SS2 SS5','Chưa ledger cọc theo reference và dedup chung','Hiện thực BillingService và test không thu trùng'],['Charging và hạ tầng','Cổng số đếm, thiếu adapter phiên/cổng','ChargingService và INT-05 cùng coordinator'],['Mô phỏng','Hai UI Apply riêng; forecast mặc định12','Coordinator chung, validation DTO và24 giờ tường minh'],['Dashboard','Revenue giới hạnSS1 và powerước tính','Đọc ledger đối soát toàn mạng và active sessions'],['Quyền và incident','Mock auth; core/binding còn thiếu kiểm tra','Authorization tại service và khôi phục trạng thái hợp lệ'],['Yêu cầu mở rộng','Hourly parking, quãng đường và doanh thu dự báo chưa đầy đủ','Chốt chính sách và nguồn dữ liệu, thực thi theo phạm vi final'],['NFR đa người dùng','Session tách biệt, chưa benchmark production','Storage/transaction chia sẻ và đo tải/độ trễ']],[1.15,2.75,2.9])
    h(2,'14.1 Kế hoạch hoàn thiện và điều kiện bàn giao')
    p('Kế hoạch sắp theo phụ thuộc công việc, không tự đặt hạn thay thông báo giảng viên. Phân công dưới đây là đề xuất phối hợp theo chủ sở hữu phân hệ, cần được nhóm xác nhận khi chốt bản nộp.')
    table(['Bước và phụ trách','Kết quả cần chốt'],[
        ['1. Trưởng nhóm và cả bảy thành viên','Đọc đối chiếu SRS/Sub2/Sub3; xác nhận lớp, chữ ký, quy tắc dùng chung và phần đóng góp/AI cá nhân. Giữ nguyên ID yêu cầu; ghi rõ mọi mục chưa triển khai.'],
        ['2. SS1/SS2/SS5 và SS6/SS7','Ưu tiên ledger không thu trùng, ChargingService, DTO preview và Apply nguyên tử theo thứ tự phụ thuộc. Mỗi tích hợp có ca lỗi, gọi lặp và invariant; cập nhật tài liệu nếu chữ ký đổi.'],
        ['3. SS3/SS4 cùng chủ sở hữu liên quan','Đối soát doanh thu/công suất từ nguồn chuẩn, kiểm tra ownership/binding và bộ lọc Hub offline. Chạy lại bộ core/UI cùng kiểm thử hợp đồng vừa bổ sung; lưu log và revision.'],
        ['4. Trưởng nhóm và chủ báo cáo cá nhân','Kiểm đủ 17 UC, 70 lượt phương thức và dẫn chiếu shared, hình đọc được, mục lục đúng, Word/PDF đồng bộ. Đóng gói báo cáo tổng và tài liệu cá nhân theo yêu cầu LMS; kiểm tra tệp tải lên và lưu biên nhận khi nộp.']
    ],[2.0,4.8])
    p('Tài liệu tổng phục vụ việc đọc thiết kế toàn hệ thống; cách nộp và hạn cuối tuân theo thông báo LMS/giảng viên. Bản tổng không tự tạo xác nhận cá nhân hoặc biên nhận nộp bài. Trước khi sử dụng để nộp, nhóm cần xác nhận nội dung và khai báo đóng góp theo bản cuối.')
    h(1,'15 Đóng góp của nhóm')
    h(2,'15.1 Phạm vi đóng góp')
    p('Phạm vi phụ trách của bảy thành viên được giữ ở chương 2. Báo cáo tổng kế thừa nguồn thiết kế đã tích hợp, hợp đồng dùng chung và truy vết của nhóm; việc tổng hợp không thay đổi quyền sở hữu nội dung cá nhân. Bản báo cáo này không suy ra các thành viên đã đọc, tự kiểm tra hoặc xác nhận những chỉnh sửa được thực hiện trong phiên hỗ trợ.')


def class_crop(n,name):
    svg=ROOT/f'docs/diagrams/submission_3/SS{n}/class_diagram.svg'
    png=svg.with_suffix('.png')
    if not svg.exists():return None
    picture=Image.open(png).convert('RGB')
    for group in ET.parse(svg).iter():
        if group.get('class')!='entity':continue
        labels=[t.text or '' for t in group if t.tag.endswith('text')]
        if not (group.get('data-qualified-name')==name or group.get('data-entity')==name or name in labels):continue
        rects=[x for x in group if x.tag.endswith('rect') and x.get('width')]
        if not rects:continue
        box=max(rects,key=lambda x:float(x.get('width'))*float(x.get('height')))
        x,y,w,h=[float(box.get(k)) for k in ['x','y','width','height']]
        target=DEST/'shared/total_figures'/f'SS{n}_{name}.png';target.parent.mkdir(parents=True,exist_ok=True)
        picture.crop((max(0,int(x)-1),max(0,int(y)-1),min(picture.width,int(x+w)+2),min(picture.height,int(y+h)+2))).save(target)
        return target
    return None


def font(run,name='Liberation Serif',size=None,bold=None):
    run.font.name=name
    run.font.color.rgb=RGBColor(0,0,0)
    if size:run.font.size=Pt(size)
    if bold is not None:run.bold=bold
    rp=run._element.get_or_add_rPr()
    rf=rp.find(qn('w:rFonts'))
    if rf is None:rf=OxmlElement('w:rFonts');rp.insert(0,rf)
    for k in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+k),name)


def rich(paragraph,text,size=None):
    for part in re.split(r'(`[^`]+`|\*\*[^*]+\*\*)',text):
        if part.startswith('`') and part.endswith('`'):
            r=paragraph.add_run(part[1:-1]);font(r,'DejaVu Sans Mono',9 if size is None else min(size,9))
        elif part.startswith('**'):
            r=paragraph.add_run(part[2:-2]);font(r,size=size,bold=True)
        else:r=paragraph.add_run(part);font(r,size=size)


def configure(section,landscape=False,cover=False):
    """A4 and margins retained from the Submission 1/2 LaTeX sources."""
    section.page_width=Cm(29.7 if landscape else 21)
    section.page_height=Cm(21 if landscape else 29.7)
    section.orientation=WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    section.top_margin=Cm(2.5);section.bottom_margin=Cm(2.5)
    section.left_margin=Cm(3);section.right_margin=Cm(2)
    section.header_distance=Cm(1.2);section.footer_distance=Cm(1.2)
    for tag in ['pgBorders','pgNumType']:
        for el in list(section._sectPr.findall(qn('w:'+tag))):section._sectPr.remove(el)
    section.header.is_linked_to_previous=False
    section.footer.is_linked_to_previous=False
    hp=section.header.paragraphs[0];hp.clear()
    fp=section.footer.paragraphs[0];fp.clear()
    if cover:
        borders=OxmlElement('w:pgBorders');borders.set(qn('w:offsetFrom'),'page')
        for edge in ['top','left','bottom','right']:
            node=OxmlElement('w:'+edge)
            for key,value in [('val','double'),('sz','16'),('space','28'),('color','000099')]:node.set(qn('w:'+key),value)
            borders.append(node)
        section._sectPr.append(borders)
        return
    hp.alignment=WD_ALIGN_PARAGRAPH.LEFT
    width=section.page_width-section.left_margin-section.right_margin
    hp.paragraph_format.tab_stops.add_tab_stop(width,WD_TAB_ALIGNMENT.RIGHT)
    rich(hp,'CO3001 - Công nghệ Phần mềm HK261\tNhóm BEE BRAVE',9)
    border=OxmlElement('w:pBdr');line=OxmlElement('w:bottom')
    for key,value in [('val','single'),('sz','3'),('space','3'),('color','000000')]:line.set(qn('w:'+key),value)
    border.append(line);hp._p.get_or_add_pPr().append(border)
    fp.alignment=WD_ALIGN_PARAGRAPH.CENTER
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE')
    run=OxmlElement('w:r');text=OxmlElement('w:t');text.text='1';run.append(text);field.append(run);fp._p.append(field)


def word_table(doc,headers,rows,widths):
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    widths=widths or [BODY_WIDTH/len(headers)]*len(headers)
    total=sum(widths);widths=[x/total*BODY_WIDTH for x in widths]
    for i,w in enumerate(widths):t.columns[i].width=Inches(w)
    for i,text in enumerate(headers):t.rows[0].cells[i].text=text
    for row in rows:
        cells=t.add_row().cells
        for i,text in enumerate(row):cells[i].text=norm(str(text))
    props=t._tbl.tblPr
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
    props.append(borders)
    for ridx,row in enumerate(t.rows):
        no_split=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(no_split)
        if ridx==0:
            repeat=OxmlElement('w:tblHeader');row._tr.get_or_add_trPr().append(repeat)
        for cidx,cell in enumerate(row.cells):
            cell.width=Inches(widths[cidx]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=cell._tc.get_or_add_tcPr();margins=OxmlElement('w:tcMar')
            for name,val in [('top','85'),('bottom','85'),('left','90'),('right','90')]:
                m=OxmlElement('w:'+name);m.set(qn('w:w'),val);m.set(qn('w:type'),'dxa');margins.append(m)
            tcpr.append(margins)
            if ridx==0:
                shd=OxmlElement('w:shd');shd.set(qn('w:fill'),'E7E6E6');tcpr.append(shd)
            for paragraph in cell.paragraphs:
                paragraph.alignment=WD_ALIGN_PARAGRAPH.LEFT
                paragraph.paragraph_format.space_after=Pt(1);paragraph.paragraph_format.line_spacing=1.08
                for r in paragraph.runs:font(r,size=10.5,bold=(ridx==0))
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return t


def anchor_name(text):return 's'+hashlib.sha1(text.encode()).hexdigest()[:18]


def bookmark(paragraph,text):
    ident=str(int(hashlib.sha1(text.encode()).hexdigest()[:7],16))
    start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),ident);start.set(qn('w:name'),anchor_name(text))
    paragraph._p.insert(1 if paragraph._p.pPr is not None else 0,start)
    end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),ident);paragraph._p.append(end)


def chapter_title(text):
    number,body=text.split(' ',1)
    return f'Mục {number}: {body}'


def prepare_navigation():
    NAVIGATION.clear();CAPTIONS.clear()
    chapter=0;fig_no=0;table_no=0
    table_titles={1:['Đối chiếu nội dung báo cáo với yêu cầu Submission 3'],2:['Phạm vi phân hệ và số use case phụ trách'],3:['Các thành phần kiến trúc và ánh xạ mã nguồn','Đối chiếu yêu cầu phi chức năng'],4:['Chính sách nghiệp vụ và đơn vị','Danh mục hợp đồng liên phân hệ'],13:['Các ca kiểm thử hợp đồng được thiết kế'],14:['Giới hạn hiện tại và hướng hoàn thiện','Kế hoạch hoàn thiện và điều kiện bàn giao']}
    for i,block in enumerate(BLOCKS):
        if block[0]=='heading':
            if block[1]==1:chapter=int(block[2].split()[0]);fig_no=0;table_no=0
            if block[1]<=2:NAVIGATION.append((block[1],chapter_title(block[2]) if block[1]==1 else block[2]))
        elif block[0]=='figure':
            fig_no+=1;title=re.sub(r'^Hình \d+\s+','',block[2])
            CAPTIONS[i]=f'Hình {chapter}.{fig_no}: {title}'
        elif block[0]=='table':
            table_no+=1
            choices=table_titles.get(chapter,[f'Danh mục use case của SS{chapter-4}'])
            title=choices[min(table_no-1,len(choices)-1)]
            CAPTIONS[i]=f'Bảng {chapter}.{table_no}: {title}'
    record={'headings':NAVIGATION,'figures':[c for i,c in CAPTIONS.items() if BLOCKS[i][0]=='figure'],'tables':['Bảng 0.1: Danh sách thành viên và phân công nhiệm vụ']+[c for i,c in CAPTIONS.items() if BLOCKS[i][0]=='table'],'front':['Danh mục hình ảnh','Danh mục bảng biểu','Lời nói đầu']}
    (TEMP/'navigation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    return record


def caption(doc,text):
    para=doc.add_paragraph();para.paragraph_format.first_line_indent=Cm(0)
    para.paragraph_format.space_before=Pt(5);para.paragraph_format.space_after=Pt(7)
    para.alignment=WD_ALIGN_PARAGRAPH.CENTER;rich(para,text,10.5);bookmark(para,text)
    return para


def nav_line(doc,title,pages,level=1):
    para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.LEFT;para.paragraph_format.first_line_indent=Cm(0)
    para.paragraph_format.left_indent=Cm(.5 if level==2 else 0)
    para.paragraph_format.space_after=Pt(4 if level==1 else 2)
    para.paragraph_format.line_spacing=1.02
    para.paragraph_format.tab_stops.add_tab_stop(Cm(15.9),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
    link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),anchor_name(title));link.set(qn('w:history'),'1')
    run=OxmlElement('w:r');rp=OxmlElement('w:rPr')
    rf=OxmlElement('w:rFonts');rf.set(qn('w:ascii'),'Liberation Serif');rf.set(qn('w:hAnsi'),'Liberation Serif');rp.append(rf)
    col=OxmlElement('w:color');col.set(qn('w:val'),'003399');rp.append(col)
    size=OxmlElement('w:sz');size.set(qn('w:val'),'22' if level==1 else '21');rp.append(size)
    if level==1:rp.append(OxmlElement('w:b'))
    run.append(rp);txt=OxmlElement('w:t');txt.text=title;run.append(txt);link.append(run);para._p.append(link)
    rich(para,'\t'+str(pages.get(title,'')),10.5)
    return para


def front_title(doc,text):
    para=doc.add_paragraph(text,style='Title');para.paragraph_format.space_after=Pt(16);bookmark(para,text)
    return para


def write_docx(pages):
    navigation=prepare_navigation()
    doc=Document();configure(doc.sections[0],cover=True)
    styles=doc.styles
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Header','Footer']:
        st=styles[name];st.font.name='Liberation Serif';st.font.color.rgb=RGBColor(0,0,0)
    styles['Normal'].font.size=Pt(12);styles['Normal'].paragraph_format.line_spacing=1.12;styles['Normal'].paragraph_format.space_after=Pt(4)
    styles['Normal'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
    styles['Header'].paragraph_format.tab_stops.clear_all()
    for name,size in [('Heading 1',18),('Heading 2',15),('Heading 3',12.5)]:
        styles[name].font.size=Pt(size);styles[name].font.bold=True
        styles[name].paragraph_format.keep_with_next=True;styles[name].paragraph_format.space_before=Pt(10);styles[name].paragraph_format.space_after=Pt(6)
    styles['Title'].font.size=Pt(20);styles['Title'].font.bold=True
    styles['Heading 1'].paragraph_format.page_break_before=False
    styles['Heading 1'].paragraph_format.space_before=Pt(18)
    doc.core_properties.title='Báo cáo tổng Submission 3 Smart E Mobility Hub'
    doc.core_properties.author='Nhóm BEE BRAVE'
    doc.core_properties.subject='Thiết kế kiến trúc lớp và phương thức toàn hệ thống'
    for size,line in [(12,'ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH'),(14,'TRƯỜNG ĐẠI HỌC BÁCH KHOA'),(12,'KHOA KHOA HỌC VÀ KỸ THUẬT MÁY TÍNH')]:
        para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;rich(para,'**'+line+'**',size)
        para.paragraph_format.space_after=Pt(5)
    para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before=Pt(8);para.paragraph_format.space_after=Pt(18)
    pic=para.add_run().add_picture(str(ROOT/'docs/report/assets/mau.png'),width=Cm(4.6));pic._inline.docPr.set('descr','Logo Trường Đại học Bách Khoa ĐHQG HCM')
    para=doc.add_paragraph('BÁO CÁO THIẾT KẾ KIẾN TRÚC\nVÀ CHI TIẾT HỆ THỐNG PHẦN MỀM',style='Title');para.alignment=WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after=Pt(12)
    para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;rich(para,'**SUBMISSION 3**',16)
    para.paragraph_format.space_after=Pt(14)
    for line,size in [('MÔN HỌC  CÔNG NGHỆ PHẦN MỀM CO3001 - HK261',12),('ĐỀ TÀI',12),('SMART E-MOBILITY HUB',18),('Hệ thống Điều phối Phương tiện Điện\ntrong Khu đô thị ĐHQG-HCM',12)]:
        para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;rich(para,('**'+line+'**') if size==18 else line,size)
    for line in ['**Giảng viên hướng dẫn:** TS. Trần Thị Ngọc Trâm','**Lớp học phần:** L02','**Nhóm báo cáo:** BEE BRAVE (7 thành viên)']:
        para=doc.add_paragraph();para.paragraph_format.left_indent=Cm(1);para.alignment=WD_ALIGN_PARAGRAPH.LEFT;rich(para,line,12)
        para.paragraph_format.space_after=Pt(8)
    para=doc.add_paragraph();para.paragraph_format.space_before=Pt(215);para.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rich(para,'**Thành phố Hồ Chí Minh, Tháng 11/2026**',12)
    para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;rich(para,'Học kỳ HK261',11)
    section=doc.add_section(WD_SECTION_START.NEW_PAGE);configure(section)
    num=OxmlElement('w:pgNumType');num.set(qn('w:start'),'1');section._sectPr.append(num)
    para=doc.add_paragraph();para.paragraph_format.space_before=Pt(80);para.paragraph_format.space_after=Pt(16)
    para.alignment=WD_ALIGN_PARAGRAPH.CENTER;rich(para,'**DANH SÁCH THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ**',14)
    caption(doc,'Bảng 0.1: Danh sách thành viên và phân công nhiệm vụ').paragraph_format.keep_with_next=True
    word_table(doc,['STT','Họ và tên','MSSV','Phân hệ phụ trách','Vai trò'],[[n,v[1],v[2],f'SS{n}: '+SCOPE[int(n)][0],'Leader/PM' if n=='1' else 'Dev/Analyst'] for n,v in MEMBERS.items()],[.45,1.4,.75,2.4,.8])
    para=doc.add_paragraph();rich(para,'Phạm vi phụ trách kế thừa phân công nhóm. Phạm vi đóng góp của các thành viên được trình bày ở Mục 15.',11)
    doc.add_page_break()
    front_title(doc,'Mục lục')
    for title in navigation['front']:nav_line(doc,title,pages)
    for level,title in NAVIGATION:nav_line(doc,title,pages,level)
    doc.add_page_break();front_title(doc,'Danh mục hình ảnh')
    for title in navigation['figures']:nav_line(doc,title,pages,2)
    doc.add_page_break();front_title(doc,'Danh mục bảng biểu')
    for title in navigation['tables']:nav_line(doc,title,pages,2)
    doc.add_page_break();front_title(doc,'Lời nói đầu')
    for text in [
        'Submission 3 trình bày thiết kế kiến trúc và thiết kế chi tiết của Smart E-Mobility Hub, kế thừa đặc tả yêu cầu ở Submission 1 và 17 use case cùng các mô hình tương tác của Submission 2. Báo cáo tập trung làm rõ cách triển khai hệ thống, tổ chức module, trách nhiệm của lớp và hành vi của từng phương thức.',
        'Bảy phân hệ được hợp nhất qua mô hình Hub, phương tiện, tài chính và các hợp đồng liên phân hệ. Ngoài sơ đồ, tài liệu mô tả điều kiện đầu vào, kết quả, lỗi và tác động trạng thái; ma trận truy vết giúp đối chiếu quyết định thiết kế với yêu cầu và kiểm thử.',
        'Nhóm phân biệt thiết kế mục tiêu với phần đã hiện thực trong prototype Python/Streamlit. Những giới hạn về tích hợp sạc, đối soát tài chính, mô phỏng và yêu cầu phi chức năng được ghi rõ để làm căn cứ hoàn thiện ở giai đoạn tiếp theo.',
        'Nhóm BEE BRAVE trân trọng cảm ơn TS. Trần Thị Ngọc Trâm đã hướng dẫn học phần Công nghệ Phần mềm. Nhóm mong nhận được ý kiến góp ý của cô để tiếp tục hoàn thiện thiết kế và sản phẩm.'
    ]:rich(doc.add_paragraph(),text)
    para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.RIGHT;rich(para,'Thành phố Hồ Chí Minh, ngày 06 tháng 11 năm 2026\n**Tập thể Nhóm BEE BRAVE**',11)
    # Keep the scheduler diagram and its short lead-in on the same landscape
    # page, rather than leaving a fragment ahead of the section break.
    diagram_leadins={};deferred=set()
    for i,block in enumerate(BLOCKS[:-2]):
        if block[0]=='heading' and block[2].startswith('9.1 ') and BLOCKS[i+1][0]=='paragraph' and BLOCKS[i+2][0]=='figure':
            diagram_leadins[i+2]=(block,BLOCKS[i+1]);deferred.update([i,i+1])
    method_active=False
    for index, block in enumerate(BLOCKS):
        if index in deferred:continue
        kind=block[0]
        if kind=='heading':
            method_active=False
            title=chapter_title(block[2]) if block[1]==1 else block[2]
            para=doc.add_paragraph(title,style=f'Heading {block[1]}');bookmark(para,title)
            if block[1]==1 and block[2].startswith('1 '):para.paragraph_format.page_break_before=True
        elif kind=='paragraph':
            para=doc.add_paragraph();rich(para,block[1])
            if method_active or block[1].startswith(('Mức triển khai:','Thuộc tính:','Các phương thức shared')):
                para.alignment=WD_ALIGN_PARAGRAPH.LEFT
            if block[1].startswith('Mức triển khai:'):para.paragraph_format.space_after=Pt(2)
            following=BLOCKS[index+1] if index+1<len(BLOCKS) else None
            keep_prefixes=('Yêu cầu:', 'Thiết kế phụ trách:', 'Đầu vào Sub 2:', 'Đầu vào và thao tác:', 'Kết quả mong đợi:')
            if block[1].startswith(keep_prefixes) or (following and following[0]=='paragraph' and following[1].startswith(('Mức triển khai:', 'Thuộc tính:', 'Ánh xạ hiện tại:'))):
                para.paragraph_format.keep_with_next=True
        elif kind=='code':
            para=doc.add_paragraph();para.paragraph_format.space_after=Pt(4);para.paragraph_format.keep_with_next=True
            para.alignment=WD_ALIGN_PARAGRAPH.LEFT
            r=para.add_run(block[1]);font(r,'Liberation Mono',9)
        elif kind=='method':
            method_active=True
            para=doc.add_paragraph();para.paragraph_format.keep_with_next=True;para.paragraph_format.space_before=Pt(7)
            para.paragraph_format.space_after=Pt(3)
            para.alignment=WD_ALIGN_PARAGRAPH.LEFT
            rich(para,block[1],12);para.runs[0].bold=True
        elif kind=='table':
            caption(doc,CAPTIONS[index]).paragraph_format.keep_with_next=True
            word_table(doc,block[1],block[2],block[3])
        elif kind=='figure':
            _,path,title,portrait=block
            detail='total_figures' in path
            wide=not detail and ('system_classes' in path or any('/SS'+str(n)+'/' in path for n in [1,2,5,6,7]))
            if wide:configure(doc.add_section(WD_SECTION_START.NEW_PAGE),landscape=True)
            if index in diagram_leadins:
                lead_heading,lead_paragraph=diagram_leadins[index]
                para=doc.add_paragraph(lead_heading[2],style='Heading 2');bookmark(para,lead_heading[2])
                rich(doc.add_paragraph(),lead_paragraph[1])
            image=Image.open(ROOT/path)
            maxw=24.7/2.54 if wide else BODY_WIDTH
            maxh=(13.8 if wide else 18 if portrait else 11.7)/2.54
            if index in diagram_leadins:maxh=11.5/2.54
            if detail:maxw=min(maxw,image.width/96);maxh=9/2.54
            width=min(maxw,maxh*image.width/image.height)
            para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.keep_with_next=True
            para.paragraph_format.space_after=Pt(2)
            pic=para.add_run().add_picture(str(ROOT/path),width=Inches(width));pic._inline.docPr.set('descr',CAPTIONS[index])
            caption(doc,CAPTIONS[index])
            if wide:configure(doc.add_section(WD_SECTION_START.NEW_PAGE))
    # The starter document can contain theme-colored paragraph rules. Academic
    # headings use plain black text without decorative borders or theme fonts.
    for element in list(doc.styles.element.iter())+list(doc.element.iter()):
        if element.tag==qn('w:pBdr'):
            element.getparent().remove(element)
        if element.tag==qn('w:rFonts'):
            for key in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme','csTheme']:
                element.attrib.pop(qn('w:'+key),None)
    output=DEST/'REPORT_SUBMISSION_3.docx';doc.save(output)
    return output


def write_markdown():
    lines=['# Báo cáo tổng Submission 3 Smart E Mobility Hub','','Nhóm BEE BRAVE  |  CO3001  |  HK261  |  Tổng hợp ngày 06/11/2026','']
    for index,block in enumerate(BLOCKS):
        if block[0]=='heading':lines+=['#'*block[1]+' '+(chapter_title(block[2]) if block[1]==1 else block[2]),'']
        elif block[0] in ['paragraph','method']:lines+=[('**'+block[1]+'**') if block[0]=='method' else block[1],'']
        elif block[0]=='code':lines+=['```text',block[1],'```','']
        elif block[0]=='table':
            lines+=['**'+CAPTIONS[index]+'**','','| '+' | '.join(block[1])+' |','| '+' | '.join(['---']*len(block[1]))+' |']
            lines+=['| '+' | '.join(str(v).replace('|','\\|') for v in row)+' |' for row in block[2]];lines+=['']
        elif block[0]=='figure':lines+=[f'![{CAPTIONS[index]}](../../../{block[1]})','']
    (DEST/'REPORT_SUBMISSION_3.md').write_text('\n'.join(lines).strip()+'\n')


def verify():
    expected=[]
    for n in range(1,8):
        for cls in CLASSES[n]:
            for method,_,_ in cls['methods']:expected.append((n,cls['name']+'.'+method))
    missing=[name for _,name in expected if name not in CATALOG]
    if missing:raise RuntimeError('Methods missing descriptions: '+str(missing))
    if len(MANIFEST['use_cases'])!=17:raise RuntimeError('Expected17 UC')
    record={'source_commit':'312bb89','use_cases':17,'diagram_method_occurrences':len(expected),'unique_descriptions':len(CATALOG),'shared_references':REPEATED,'missing':missing,'chapters':CHAPTERS,'figures':FIGURES}
    (TEMP/'coverage.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['use_cases','diagram_method_occurrences','unique_descriptions','missing']},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pages',type=Path);args=parser.parse_args()
    TEMP.mkdir(exist_ok=True,parents=True)
    compose();verify();prepare_navigation();write_markdown()
    pages=json.loads(args.pages.read_text()) if args.pages else {}
    print(write_docx(pages))
