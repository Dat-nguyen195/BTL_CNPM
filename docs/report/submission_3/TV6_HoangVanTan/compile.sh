#!/bin/sh
# Biên dịch file LaTeX báo cáo sang PDF
xelatex -interaction=nonstopmode REPORT_SUB3_HoangVanTan_2213074.tex
xelatex -interaction=nonstopmode REPORT_SUB3_HoangVanTan_2213074.tex
rm -f REPORT_SUB3_HoangVanTan_2213074.aux REPORT_SUB3_HoangVanTan_2213074.log REPORT_SUB3_HoangVanTan_2213074.out REPORT_SUB3_HoangVanTan_2213074.toc
echo "Đã biên dịch thành công: REPORT_SUB3_HoangVanTan_2213074.pdf"
