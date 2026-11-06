# Review Submission 2 — 28/10/2026

Baseline: commit `9d9bca6`. Chuẩn bị báo cáo ngày 29/10/2026 cho leader/SS1.

- `validation-headless.txt`: cấu trúc, truy vết, 54 nguồn PlantUML và 49 test hiện có đều PASS.
- `reproductions.json`: hai ca kiểm tra bổ sung đã chạy, tái hiện lỗi UI trả xe và voucher sai vẫn giảm giá. Hai ca này không nằm trong con số 49 test.
- `reproduce_ss1.py`: mã tái lập các quan sát bằng phiên AppTest riêng và state core riêng; không ghi vào phiên demo người dùng.
- PDF chính, bản xuất và PDF trong ZIP trùng nhau; manifest ZIP gồm 298 tệp được kiểm tra. Đây không phải bảo đảm mọi tiêu chí nghiệp vụ đều hoàn chỉnh.

Chạy tái lập từ thư mục gốc:

```bash
venv/bin/python docs/audit/submission_2/review_20261028/reproduce_ss1.py
JAVA_TOOL_OPTIONS=-Djava.awt.headless=true venv/bin/python scripts/validate_submission_2.py
```

Lần chạy validator đầu gặp lỗi Java không kết nối được X11; chạy lại với chế độ headless đã thành công. Đó là lỗi môi trường dựng hình, không phải bằng chứng sơ đồ sai cú pháp.

Kết quả và kịch bản ôn: `docs/review/REVIEW_SUBMISSION_2_20261028.md`. Không sửa code, PDF hoặc ZIP trong lượt review này.
