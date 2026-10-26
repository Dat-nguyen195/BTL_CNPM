# Đồng bộ ký hiệu UML — 26/10/2026

Phạm vi: các nguồn activity/sequence/state-chart của Submission 2, hình đưa vào báo cáo và các bản xuất PDF/gói nộp. Không thay đổi mã nghiệp vụ ứng dụng.

## Sai lệch và cách sửa

| Vị trí | Trước | Sau |
|---|---|---|
| Style chung | SS1_02, một số sequence dùng common; các hình khác dùng theme/cấu hình riêng | 45 nguồn hành vi dùng cùng common.puml |
| Nút decision/merge | Điều kiện dùng hình sáu cạnh theo theme, merge hình thoi | Cùng dùng hình thoi; nhánh có guard trong [ ] |
| Nút cuối | Theme làm tâm nút cuối trắng, dễ nhầm vòng tròn kép | Chấm đặc trong vòng tròn, khớp Activity Final ở chú giải |
| Activity SS4 | Khối hành động và viền có màu riêng | Dùng quy ước chung |
| SS1_02 | repeat + break và vòng lặp thiếu nhãn nhánh | while/endwhile với [Có]/[Không], kiểm tra lại Hub sau điều hướng |
| SS1_02 | Mọi lượt trả đều trừ available_slots | Nếu đã giữ chỗ thì giảm destination_holds, không trừ chỗ hai lần |
| SS1_02 | Ghi km thực tế/hóa đơn bền vững trong hình | Ghi dữ liệu mô phỏng, hóa đơn trong phiên |
| SS1 / SS4 | MAINTENANCE_OFFLINE / PARKED | OFFLINE / AVAILABLE theo enum xe hiện tại |
| SS1 | SoC >20%, tên cọc/số dư cũ | SoC >=20%, held_deposit/balance |
| Báo cáo SS7 tích hợp SS1 | Một đoạn ghi +30 phút ưu đãi | +15 phút một lần theo policies.py |
| Thuyết minh ngoại lệ | Khẳng định có vùng ngắt và dùng lẫn Flow Final/Activity Final | Mô tả đúng nhánh lỗi đang vẽ, phân biệt ý nghĩa hai loại nút cuối |

## Tái lập

```bash
venv/bin/python scripts/render_all_diagrams.py
venv/bin/python scripts/generate_sequence_panels.py
venv/bin/python scripts/generate_activity_panels.py
venv/bin/python scripts/validate_submission_2.py
cd docs/report/submission_2
latexmk -xelatex -interaction=nonstopmode -halt-on-error REPORT_SUBMISSION_2.tex
```

Kết quả kiểm tra nằm trong validation.txt. Các kết quả PASS xác nhận cú pháp, truy vết và bộ test hiện có; không phải chứng nhận toàn bộ ngữ nghĩa UML hay mọi tính năng sản phẩm đã hoàn thiện. Hồ sơ final/ trước ngày này phản ánh baseline cũ, không được dùng làm checksum của bản mới.
