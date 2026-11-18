# Bằng chứng kiểm tra bản hiện hành

Các lệnh chạy từ gốc repo bằng Python 3.12.

| Kiểm tra | Kết quả |
|---|---|
| PYTHONPATH=src venv/bin/python -m pytest -q tests/ | 60 passed, 7,40 giây |
| Cùng lệnh bằng /tmp/smart-emobility-clean-venv/bin/python | 60 passed, 7,04 giây |
| JAVA_TOOL_OPTIONS=-Djava.awt.headless=true venv/bin/python scripts/validate_submission_2.py | PASS: cấu trúc, manifest, 54 PlantUML và pytest |
| venv/bin/python scripts/validate_submission_3.py --technical-only | PASS: 17 UC, 70 mục method |
| java headless render docs/diagrams/telemetry/*.puml | Thành công 5 sơ đồ PNG |
| docker compose config -q | Thành công |
| Bộ phát CLI --count 2 --interval 0.2, đọc lại bằng hai observer | Cùng ID cuối, 2 bản tin mỗi observer, hub trở về ONLINE |
| Streamlit server trực tiếp | Bị sandbox từ chối mở socket |
| docker info | Từ chối quyền Docker socket |
| git diff --check | PASS |

Các test mới nằm tại tests/test_integrated_telemetry.py. Có ca kiểm tra nguồn CLI độc lập qua feed và ca AppTest với hai cửa sổ logic. Chưa có bằng chứng tự cập nhật trình duyệt thật. Độ trễ replay feed khoảng 0,11 giây của hai consumer không đại diện hiệu năng mạng hoặc NFR tải lớn.

Gói mã hiện hành có source, tests, hướng dẫn và manifest hash, tạo bằng scripts/package_submission_2.py. PDF revision trước được giữ trong gói như tài liệu lịch sử; đối chiếu runtime mới bằng docs/current/CURRENT_TECHNICAL_DESIGN.md và docs/current/REALTIME_DEMO.md.

Các giả định và giới hạn vận hành được công khai trong hai tài liệu trên, đặc biệt giá đỗ demo, pin 3,5 kWh, quãng đường mô phỏng, adapter cổng tổng hợp và trạng thái nghiệp vụ per-session. Server thật chờ nhóm cung cấp hạ tầng.
