#!/bin/sh
# Biên dịch file LaTeX báo cáo sang PDF
xelatex -interaction=nonstopmode REPORT_SUB3_NguyenTrungNguyen_2011710.tex
xelatex -interaction=nonstopmode REPORT_SUB3_NguyenTrungNguyen_2011710.tex
rm -f REPORT_SUB3_NguyenTrungNguyen_2011710.aux REPORT_SUB3_NguyenTrungNguyen_2011710.log REPORT_SUB3_NguyenTrungNguyen_2011710.out REPORT_SUB3_NguyenTrungNguyen_2011710.toc
echo "Đã biên dịch thành công: REPORT_SUB3_NguyenTrungNguyen_2011710.pdf"
