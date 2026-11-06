#!/bin/sh
# Biên dịch file LaTeX báo cáo sang PDF
xelatex -interaction=nonstopmode REPORT_SUB3_NguyenThanhDat_2410709.tex
xelatex -interaction=nonstopmode REPORT_SUB3_NguyenThanhDat_2410709.tex
rm -f REPORT_SUB3_NguyenThanhDat_2410709.aux REPORT_SUB3_NguyenThanhDat_2410709.log REPORT_SUB3_NguyenThanhDat_2410709.out REPORT_SUB3_NguyenThanhDat_2410709.toc
echo "Đã biên dịch thành công: REPORT_SUB3_NguyenThanhDat_2410709.pdf"
