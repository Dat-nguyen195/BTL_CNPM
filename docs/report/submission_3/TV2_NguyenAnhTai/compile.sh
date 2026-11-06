#!/bin/sh
# Biên dịch file LaTeX báo cáo sang PDF
xelatex -interaction=nonstopmode REPORT_SUB3_NguyenAnhTai_2413035.tex
xelatex -interaction=nonstopmode REPORT_SUB3_NguyenAnhTai_2413035.tex
rm -f REPORT_SUB3_NguyenAnhTai_2413035.aux REPORT_SUB3_NguyenAnhTai_2413035.log REPORT_SUB3_NguyenAnhTai_2413035.out REPORT_SUB3_NguyenAnhTai_2413035.toc
echo "Đã biên dịch thành công: REPORT_SUB3_NguyenAnhTai_2413035.pdf"
