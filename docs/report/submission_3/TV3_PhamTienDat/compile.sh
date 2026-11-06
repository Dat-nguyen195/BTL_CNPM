#!/bin/sh
# Biên dịch file LaTeX báo cáo sang PDF
xelatex -interaction=nonstopmode REPORT_SUB3_PhamTienDat_2410724.tex
xelatex -interaction=nonstopmode REPORT_SUB3_PhamTienDat_2410724.tex
rm -f REPORT_SUB3_PhamTienDat_2410724.aux REPORT_SUB3_PhamTienDat_2410724.log REPORT_SUB3_PhamTienDat_2410724.out REPORT_SUB3_PhamTienDat_2410724.toc
echo "Đã biên dịch thành công: REPORT_SUB3_PhamTienDat_2410724.pdf"
