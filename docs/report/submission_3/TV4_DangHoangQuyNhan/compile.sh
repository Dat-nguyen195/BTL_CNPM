#!/bin/sh
# Biên dịch file LaTeX báo cáo sang PDF
xelatex -interaction=nonstopmode REPORT_SUB3_DangHoangQuyNhan_2412401.tex
xelatex -interaction=nonstopmode REPORT_SUB3_DangHoangQuyNhan_2412401.tex
rm -f REPORT_SUB3_DangHoangQuyNhan_2412401.aux REPORT_SUB3_DangHoangQuyNhan_2412401.log REPORT_SUB3_DangHoangQuyNhan_2412401.out REPORT_SUB3_DangHoangQuyNhan_2412401.toc
echo "Đã biên dịch thành công: REPORT_SUB3_DangHoangQuyNhan_2412401.pdf"
