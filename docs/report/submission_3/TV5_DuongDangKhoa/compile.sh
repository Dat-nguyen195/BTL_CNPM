#!/bin/sh
# Biên dịch file LaTeX báo cáo sang PDF
xelatex -interaction=nonstopmode REPORT_SUB3_DuongDangKhoa_2411589.tex
xelatex -interaction=nonstopmode REPORT_SUB3_DuongDangKhoa_2411589.tex
rm -f REPORT_SUB3_DuongDangKhoa_2411589.aux REPORT_SUB3_DuongDangKhoa_2411589.log REPORT_SUB3_DuongDangKhoa_2411589.out REPORT_SUB3_DuongDangKhoa_2411589.toc
echo "Đã biên dịch thành công: REPORT_SUB3_DuongDangKhoa_2411589.pdf"
