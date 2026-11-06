# Bằng chứng review và tích hợp Submission 3 - 06/11/2026

Baseline triển khai: origin/main9d9bca6; code src/ và tests/ không thay đổi trong revision tài liệu. Bốn đầu nhánh bàn giao và ma trận phát hiện/xử lý ghi trong docs/review/REVIEW_SUBMISSION_3_20261106.md.

- pytest-baseline.txt: chạy thực tế `PYTHONPATH=src <venv-project>/bin/python -m pytest -q`,49 passed. Bằng chứng áp dụng core/UI prototype, không chứng minh service OOP đề xuất đã triển khai.
- source-validation.txt: `python3 scripts/validate_submission_3.py --pdfs`, đúng17 UC/ID/path/test source và70 mục phương thức có chữ ký/mô tả tương ứng.
- plantuml-syntax.txt / plantuml-render.txt: lệnh Java jar PlantUML `--check-syntax`, `--png`, `--svg` cho14 nguồn Sub3; exit0. Dùng `-DPLANTUML_LIMIT_SIZE=12000` để không cắt ảnh rộng. Log rỗng khi thành công là hành vi công cụ; hashes nguồn/PNG/SVG trong diagram-artifacts.json.
- pdf-build.txt:7 PDF canonical được build bằng scripts/build_submission_3.py; mỗi PDF có mọi phụ lục bắt buộc, không chỉ link ra Markdown.
- pdf-qa.json: render toàn bộ trang bằng Poppler, đối chiếu word bounding boxes không tràn lề; xem contact sheets và các trang bảng/method representative, kiểm tra chữ tiếng Việt, không còn trang trắng do chuyển template. Hình tổng quan giữ quan hệ; trang chi tiết hiển thị nguyên lớp, không chia ảnh cắt ngang chữ ký. Các đường dẫn contact sheet là ảnh tạm tại môi trường review, PDF canonical và SHA256SUMS là artifact lưu trong repository.

Toolchain PDF dùng môi trường tách biệt, dependencies scripts/requirements-submission3.txt; không thêm dependency tài liệu vào runtime MVP. Các giới hạn chức năng/NFR chưa hiện thực được ghi công khai trong shared/open_issues.md, không gắn PASS thay tác giả hoặc xác nhận LMS.
