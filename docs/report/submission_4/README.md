# Submission 4 · Smart E-Mobility Hub

`REPORT_SUBMISSION_4.tex` là điểm vào của báo cáo, dùng bìa, kiểu chữ và
định dạng đầu trang kế thừa từ các phase trước. PDF biên dịch hoàn chỉnh
nằm cùng thư mục. Nội dung của phần 1–3 được dàn từ nguồn, có chung mục lục,
danh mục hình, tham chiếu và số trang.

| Đường dẫn | Nội dung |
| --- | --- |
| `sections/` | Bìa, phân công, tổng quan, danh mục UC, kịch bản UC rút gọn, kiến trúc chạy local, demo và khai báo AI |
| `figures/demo/` | 11 ảnh chụp trình duyệt từ lần demo ngày 24/11/2026 |
| `evidence/demo-run.json` | Mã bản tin, mốc thời gian quan sát và revision chạy |
| `build/generated/` | Các chương LaTeX do script sinh, có thể tạo lại |
| `../../../scripts/build_submission_4.py` | Sinh chương và biên dịch bằng XeLaTeX |
| `../../../scripts/package_submission_4.py` | Tạo ZIP và bản PDF để tải lên trong `output/submission_4/` |

Nguồn yêu cầu lấy từ `docs/requirements-analysis.md` và manifest UC.
Phần giao diện và sơ đồ tương tác dùng lại nguồn LaTeX Submission 2 cùng hình
UML của repo. Các chương thiết kế dùng báo cáo tổng Submission 3 và phần SS2
đã chỉnh ở mốc `aae0877`. Kịch bản của 17 use case được tóm lược ngay sau danh mục
use case trong thân PDF. Đặc tả cá nhân đầy đủ và sơ đồ nằm trong `ca_nhan/`
của ZIP. Ma trận truy vết và bộ test được lưu tại repo.
Phần hiện thực mô tả hai phiên bản trong ZIP. Phiên bản 1 là bản Streamlit
minh họa thiết kế tổng thể. Phiên bản 2 là bản web đóng gói, phân quyền
người dùng và điều phối viên. Hướng dẫn ZIP ghi cách chạy từng phiên bản.

Dữ liệu IoT phát trên loopback và được quan sát ở hai cửa sổ đã mở trước lúc phát.
Mã bản tin, trạng thái trước/sau từ lần đọc lại feed và hash ảnh nằm trong
`evidence/demo-run.json`. MVP dùng tình trạng Hub riêng theo phiên và feed cảm biến chung.

## Dựng lại

Cần Python 3, Pandoc, latexmk, XeLaTeX, gói TeX tiếng Việt
và font Liberation. Từ thư mục gốc repo, chạy:

```bash
python3 scripts/build_submission_4.py
```

Để chỉ sinh chương dẫn xuất, dùng `--prepare-only`. Sau đó có thể mở tệp chính
bằng trình soạn thảo LaTeX và build với working directory là thư mục này.

Sau khi dựng PDF, cài `pdftoppm` (Poppler) để xuất ảnh cho các sơ đồ use case
cá nhân hiện có bản PDF. Tạo lại gói nộp từ thư mục gốc repo:

```bash
python3 scripts/package_submission_4.py
```

ZIP gồm `REPORT_SUBMISSION_4.pdf`, `source/` để chạy ứng dụng,
`HUONG_DAN.txt` và `ca_nhan/` để xem kịch bản và sơ đồ của bảy thành viên.

## Kiểm tra mã và sơ đồ

Tại thư mục gốc repo, sau khi cài các tệp requirements:

```bash
venv/bin/python -m pytest -q
JAVA_TOOL_OPTIONS=-Djava.awt.headless=true venv/bin/python scripts/validate_submission_2.py
venv/bin/python scripts/validate_submission_3.py --technical-only
```

Validator S2 cần Java và `tools/plantuml.jar`; JAR là công cụ ngoài gói nộp.
Validator S3 ở chế độ kỹ thuật dùng Python cùng các manifest và tài liệu trong mã nguồn.
Chụp mới bằng Selenium cần Chrome và ChromeDriver tương thích.
