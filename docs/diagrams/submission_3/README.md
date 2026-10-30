# Sơ đồ Submission 3

**Trạng thái:** nguồn, PNG và SVG của Deployment view chung và các view cá nhân SS7 của TV7 đã được tạo. Các sơ đồ còn lại vẫn là khung DRAFT. Nguồn tách khỏi báo cáo và sơ đồ use case Sub1/Sub2.

## Phân công nguồn

- `shared/deployment.puml` — TV7.
- `shared/implementation.puml` — TV3.
- `shared/system_classes.puml` — TV3 tổng hợp từ nguồn các chủ sở hữu.
- `SS7/implementation_view.puml` — ánh xạ module cá nhân SS7 do TV7 cung cấp; không thay thế view hệ thống của TV3.




| Phân hệ | Nguồn cá nhân |
| --- | --- |
| SS1 — TV1 | [class_diagram.puml](<SS1/class_diagram.puml>) |
| SS2 — TV2 | [class_diagram.puml](<SS2/class_diagram.puml>) |
| SS3 — TV3 | [class_diagram.puml](<SS3/class_diagram.puml>) |
| SS4 — TV4 | [class_diagram.puml](<SS4/class_diagram.puml>) |
| SS5 — TV5 | [class_diagram.puml](<SS5/class_diagram.puml>) |
| SS6 — TV6 | [class_diagram.puml](<SS6/class_diagram.puml>) |
| SS7 — TV7 | [class_diagram.puml](<SS7/class_diagram.puml>) |

## Đầu ra sơ đồ TV7

| View | PlantUML | PNG | SVG |
|---|---|---|---|
| Deployment view chung hiện tại | [deployment.puml](<shared/deployment.puml>) | [deployment.png](<shared/deployment.png>) | [deployment.svg](<shared/deployment.svg>) |
| Implementation view riêng SS7 | [implementation_view.puml](<SS7/implementation_view.puml>) | [implementation_view.png](<SS7/implementation_view.png>) | [implementation_view.svg](<SS7/implementation_view.svg>) |
| Class diagram SS7 | [class_diagram.puml](<SS7/class_diagram.puml>) | [class_diagram.png](<SS7/class_diagram.png>) | [class_diagram.svg](<SS7/class_diagram.svg>) |

## Kiểm tra và xuất ảnh

Chạy từ gốc repository; các lệnh sau được đối chiếu với `tools/plantuml.jar` hiện có:


```bash
# Chỉ kiểm tra cú pháp các nguồn Sub3, không xuất ảnh
java -jar path/to/plantuml.jar --check-syntax "docs/diagrams/submission_3/**/*.puml"

# Sau khi chủ sở hữu đã hoàn thiện nội dung, xuất ảnh cạnh file nguồn
java -jar path/to/plantuml.jar --png "docs/diagrams/submission_3/**/*.puml"
java -jar path/to/plantuml.jar --svg "docs/diagrams/submission_3/**/*.puml"
```

Lệnh kiểm tra cú pháp đạt chỉ chứng minh file đọc được, không chứng minh thiết kế đầy đủ. Script `scripts/render_all_diagrams.py` hiện nhắm vào cây use case cũ; không dùng kết quả của nó để khẳng định sơ đồ Sub3 đã được xuất.
