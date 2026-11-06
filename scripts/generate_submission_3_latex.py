#!/usr/bin/env python3
"""Generate self-contained LaTeX source files and build PDFs for Submission 3 members."""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB3_DIR = ROOT / 'docs/report/submission_3'
DATA = json.loads((ROOT / 'docs/traceability/submission_3.json').read_text())

SUBSYSTEMS = {
    '1': r'SS1: Đặt \& Quản lý Xe dùng chung (Shared E-Vehicle)',
    '2': r'SS2: Đăng ký Sạc \& Đỗ xe cá nhân (Personal EV Charging \& Parking)',
    '3': r'SS3: Giám sát Mạng lưới Hub (Hub Network Monitoring)',
    '4': r'SS4: Điều phối \& Xử lý Sự cố (Dispatch \& Incident Handling)',
    '5': r'SS5: Lập lịch Sạc Thông minh (Smart Charging Scheduler)',
    '6': r'SS6: Mô phỏng What-if Nhu cầu (Demand Simulator)',
    '7': r'SS7: Mô phỏng What-if Hạ tầng (Infrastructure Simulator)',
}

PANDOC_DEFS = r"""
\usepackage{color}
\usepackage{fancyvrb}
\newcommand{\VerbBar}{|}
\newcommand{\VERB}{\Verb[commandchars=\\\{\}]}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\},fontsize=\small}
\newenvironment{Shaded}{}{}
\newcommand{\AlertTok}[1]{\textcolor[rgb]{1.00,0.00,0.00}{\textbf{#1}}}
\newcommand{\AnnotationTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textbf{\textit{#1}}}}
\newcommand{\AttributeTok}[1]{\textcolor[rgb]{0.49,0.56,0.16}{#1}}
\newcommand{\BaseNTok}[1]{\textcolor[rgb]{0.25,0.63,0.44}{#1}}
\newcommand{\BuiltInTok}[1]{\textcolor[rgb]{0.00,0.50,0.00}{#1}}
\newcommand{\CharTok}[1]{\textcolor[rgb]{0.25,0.44,0.63}{#1}}
\newcommand{\CommentTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textit{#1}}}
\newcommand{\CommentVarTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textbf{\textit{#1}}}}
\newcommand{\ConstantTok}[1]{\textcolor[rgb]{0.53,0.00,0.00}{#1}}
\newcommand{\ControlFlowTok}[1]{\textcolor[rgb]{0.00,0.44,0.13}{\textbf{#1}}}
\newcommand{\DataTypeTok}[1]{\textcolor[rgb]{0.56,0.13,0.00}{#1}}
\newcommand{\DecValTok}[1]{\textcolor[rgb]{0.25,0.63,0.44}{#1}}
\newcommand{\DocumentationTok}[1]{\textcolor[rgb]{0.73,0.13,0.13}{\textit{#1}}}
\newcommand{\ErrorTok}[1]{\textcolor[rgb]{1.00,0.00,0.00}{\textbf{#1}}}
\newcommand{\ExtensionTok}[1]{#1}
\newcommand{\FloatTok}[1]{\textcolor[rgb]{0.25,0.63,0.44}{#1}}
\newcommand{\FunctionTok}[1]{\textcolor[rgb]{0.02,0.16,0.49}{#1}}
\newcommand{\ImportTok}[1]{\textcolor[rgb]{0.00,0.50,0.00}{\textbf{#1}}}
\newcommand{\InformationTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textbf{\textit{#1}}}}
\newcommand{\KeywordTok}[1]{\textcolor[rgb]{0.00,0.44,0.13}{\textbf{#1}}}
\newcommand{\NormalTok}[1]{#1}
\newcommand{\OperatorTok}[1]{\textcolor[rgb]{0.40,0.40,0.40}{#1}}
\newcommand{\OtherTok}[1]{\textcolor[rgb]{0.00,0.44,0.13}{#1}}
\newcommand{\PreprocessorTok}[1]{\textcolor[rgb]{0.74,0.48,0.00}{#1}}
\newcommand{\RegionMarkerTok}[1]{#1}
\newcommand{\SpecialCharTok}[1]{\textcolor[rgb]{0.25,0.44,0.63}{#1}}
\newcommand{\SpecialStringTok}[1]{\textcolor[rgb]{0.73,0.40,0.53}{#1}}
\newcommand{\StringTok}[1]{\textcolor[rgb]{0.25,0.44,0.63}{#1}}
\newcommand{\VariableTok}[1]{\textcolor[rgb]{0.10,0.09,0.49}{#1}}
\newcommand{\VerbatimStringTok}[1]{\textcolor[rgb]{0.25,0.44,0.63}{#1}}
\newcommand{\WarningTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textbf{\textit{#1}}}}
"""

PREAMBLE_TEMPLATE = r"""\documentclass[11pt,a4paper]{article}

\usepackage{iftex}
\ifxetex
  \usepackage{fontspec}
  \setmainfont{DejaVu Sans}
  \setmonofont{DejaVu Sans Mono}
\else
  \usepackage[utf8]{inputenc}
  \usepackage[T5]{fontenc}
  \usepackage[vietnamese]{babel}
\fi

\usepackage{geometry}
\geometry{a4paper, left=2.5cm, right=2cm, top=2.5cm, bottom=2.5cm, headheight=15pt}

\usepackage{graphicx}
\graphicspath{{../../assets/}{../../../diagrams/}{./}}

\usepackage{float}
\usepackage{fancyhdr}
\usepackage{tabularx}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage{calc}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{calc}
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=blue,
    pdftitle={Submission 3 - __SS__ - __NAME__},
    pdfauthor={Nhóm BEE BRAVE - __NAME__}
}

\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\newcommand{\passthrough}[1]{#1}
""" + PANDOC_DEFS + r"""
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Smart E-Mobility Hub -- Submission 3}
\fancyhead[R]{\small SS__N__ -- __NAME__}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\fancypagestyle{plain}{
  \fancyhf{}
  \fancyhead[L]{\small Smart E-Mobility Hub -- Submission 3}
  \fancyhead[R]{\small SS__N__ -- __NAME__}
  \fancyfoot[C]{\thepage}
  \renewcommand{\headrulewidth}{0.4pt}
}

\begin{document}

% ============================================================
%                       TRANG BÌA
% ============================================================
\begin{titlepage}
    \noindent
    \begin{tikzpicture}[remember picture, overlay]
        \draw[line width = 2pt] ($(current page.north west) + (1.5cm,-1.0cm)$) rectangle ($(current page.south east) + (-0.8cm,1.0cm)$);
        \draw[line width = 0.8pt] ($(current page.north west) + (1.6cm,-1.1cm)$) rectangle ($(current page.south east) + (-0.9cm,1.1cm)$);
    \end{tikzpicture}%
    \centering
    \textbf{\large ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH}\\[0.2cm]
    \textbf{\Large TRƯỜNG ĐẠI HỌC BÁCH KHOA}\\[0.2cm]
    \textbf{\large KHOA KHOA HỌC VÀ KỸ THUẬT MÁY TÍNH}\\[0.6cm]

    \includegraphics[width=6cm]{mau.png}\\[0.5cm]

    \rule{\textwidth}{0.5pt}\\[0.6cm]

    {\fontsize{22}{26}\selectfont\textbf{BÁO CÁO BÀI TẬP LỚN}}\\[0.3cm]
    {\Large\textbf{SUBMISSION \#3}}\\[0.6cm]

    {\large MÔN HỌC: \textbf{CÔNG NGHỆ PHẦN MỀM (CO3001)} --- HK261}\\[0.3cm]
    {\large ĐỀ TÀI:}\\[0.2cm]
    {\Large\textbf{SMART E-MOBILITY HUB}}\\[0.2cm]
    {\large Phân hệ: \textbf{__SUBSYSTEM_DESC__}}\\[0.6cm]

    \rule{\textwidth}{0.5pt}\\[0.6cm]

    \begin{flushleft}
        \hspace{1cm}\textbf{Giảng viên hướng dẫn:} TS. Trần Thị Ngọc Trâm\\[0.3cm]
        \hspace{1cm}\textbf{Lớp học phần:} L02\\[0.3cm]
        \hspace{1cm}\textbf{Nhóm báo cáo:} BEE BRAVE (Nhóm 7)\\[0.3cm]
        \hspace{1cm}\textbf{Sinh viên thực hiện:} __NAME__\\[0.3cm]
        \hspace{1cm}\textbf{MSSV:} __MSSV__\\[0.3cm]
        \hspace{1cm}\textbf{Revision:} 06/11/2026 (Bản kỹ thuật trước nộp LMS)
    \end{flushleft}
    \vfill
    Thành phố Hồ Chí Minh, Tháng 11/2026
\end{titlepage}

\setcounter{page}{1}
\tableofcontents
\newpage

"""


def main():
    for n, (slug, name, mssv) in DATA['members'].items():
        member_dir = SUB3_DIR / f'TV{n}_{slug}'
        print(f'=== Processing TV{n}_{slug} ===')

        body = ''
        report_md = member_dir / 'REPORT_SUB3.md'
        r1 = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', str(report_md)], capture_output=True, text=True, errors='replace')
        body += r1.stdout

        # Appendices
        appendices = [
            ('method_catalog.md', r'Danh mục Phương thức'),
            ('traceability.md', r'Ma trận Truy vết Yêu cầu'),
            ('test_cases.md', r'Kiểm thử \& Test Cases'),
        ]
        for fn, title in appendices:
            p = member_dir / fn
            if p.is_file():
                esc_fn = fn.replace('_', r'\_')
                body += rf"""
\newpage
\section*{{PHỤ LỤC: {title} ({esc_fn})}}
\addcontentsline{{toc}}{{section}}{{PHỤ LỤC: {title} ({esc_fn})}}
"""
                r = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', str(p)], capture_output=True, text=True, errors='replace')
                body += r.stdout

        # Architecture Appendix
        arch_p = SUB3_DIR / 'shared/architecture.md'
        if arch_p.is_file():
            body += r"""
\newpage
\section*{PHỤ LỤC: Kiến trúc Hệ thống Chung (architecture.md)}
\addcontentsline{toc}{section}{PHỤ LỤC: Kiến trúc Hệ thống Chung (architecture.md)}
"""
            r = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', str(arch_p)], capture_output=True, text=True, errors='replace')
            body += r.stdout

        cur_preamble = (
            PREAMBLE_TEMPLATE
            .replace('__SS__', f'SS{n}')
            .replace('__N__', str(n))
            .replace('__NAME__', name)
            .replace('__MSSV__', mssv)
            .replace('__SUBSYSTEM_DESC__', SUBSYSTEMS.get(str(n), f'SS{n}'))
        )

        full_tex = cur_preamble + body + '\n\\end{document}\n'
        tex_file = member_dir / f'REPORT_SUB3_{slug}_{mssv}.tex'
        tex_file.write_text(full_tex)
        print(f'  Created LaTeX source: {tex_file.relative_to(ROOT)}')

        # Clean old aux/toc before compiling to prevent obsolete babel entries
        for ext in ['.aux', '.log', '.out', '.toc']:
            old_f = member_dir / f'{tex_file.stem}{ext}'
            if old_f.is_file():
                old_f.unlink()

        # Compile twice with xelatex to resolve TOC and page numbers
        print(f'  Compiling (run 1) with xelatex in {member_dir.name}...')
        compile_res = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', tex_file.name],
            cwd=str(member_dir),
            capture_output=True,
            text=True,
            errors='replace'
        )
        if compile_res.returncode != 0:
            errs = [l for l in compile_res.stdout.splitlines() if l.startswith('!') or 'Error' in l]
            print(f'  [!] Compilation error in {member_dir.name}:', errs[:5])
        else:
            print(f'  Compiling (run 2 for TOC) in {member_dir.name}...')
            subprocess.run(
                ['xelatex', '-interaction=nonstopmode', tex_file.name],
                cwd=str(member_dir),
                capture_output=True,
                text=True,
                errors='replace'
            )
            print(f'  [✓] Successfully built {member_dir.name}/{tex_file.stem}.pdf')

        # Clean auxiliary compilation files
        for ext in ['.aux', '.log', '.out', '.toc']:
            aux_f = member_dir / f'{tex_file.stem}{ext}'
            if aux_f.is_file():
                aux_f.unlink()

        # Also create a small compile helper script in member_dir
        compile_sh = member_dir / 'compile.sh'
        compile_sh.write_text(f"""#!/bin/sh
# Biên dịch file LaTeX báo cáo sang PDF
xelatex -interaction=nonstopmode {tex_file.name}
xelatex -interaction=nonstopmode {tex_file.name}
rm -f {tex_file.stem}.aux {tex_file.stem}.log {tex_file.stem}.out {tex_file.stem}.toc
echo "Đã biên dịch thành công: {tex_file.stem}.pdf"
""")
        compile_sh.chmod(0o755)

        # Remove top-level PDF in SUB3_DIR if any exists
        outside_pdf = SUB3_DIR / f'REPORT_SUB3_{slug}_{mssv}.pdf'
        if outside_pdf.is_file():
            outside_pdf.unlink()

    print('\nAll 7 members processed successfully!')


if __name__ == '__main__':
    main()