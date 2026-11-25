#!/usr/bin/env python3
"""Compose editable LaTeX fragments from the current SRS and earlier submissions."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPORTS = DOCS / "report"
HERE = REPORTS / "submission_4"
GENERATED = HERE / "build" / "generated"


def pandoc(text, input_format="gfm+implicit_figures", division="section"):
    result = subprocess.run(
        ["pandoc", "--from", input_format, "--to", "latex", "--wrap=none", "--no-highlight",
         f"--top-level-division={division}"],
        input=text, encoding="utf-8", check=True, stdout=subprocess.PIPE,
    ).stdout
    result = result.replace(r"\begin{verbatim}", r"\begin{Verbatim}[fontsize=\small,breaklines=true]")
    result = result.replace(r"\end{verbatim}", r"\end{Verbatim}")
    lines = []
    verbatim = False
    for line in result.splitlines():
        if line.startswith(r"\begin{Verbatim}"):
            verbatim = True
        if not verbatim and not any(token in line for token in (
            r"\href{", r"\url{", r"\includegraphics", r"\label{", r"\hypertarget{"
        )):
            line = re.sub(r"(\\_|\{\[\}|\{\]\}|(?<=[a-zA-Z0-9])[./:](?=[A-Za-z]))",
                          r"\1\\allowbreak{}", line)
        if line.startswith(r"\end{Verbatim}"):
            verbatim = False
        lines.append(line)
    result = "\n".join(lines) + "\n"
    return format_tables(result)


def format_tables(text):
    """Let inherited tables wrap and span pages inside the report margins."""
    def sized(match):
        spec, contents = match.groups()
        widths = {
            2: (0.27, 0.73),
            3: (0.20, 0.49, 0.31),
            4: (0.15, 0.28, 0.32, 0.25),
            5: (0.15, 0.20, 0.24, 0.23, 0.18),
            6: (0.13, 0.17, 0.18, 0.18, 0.18, 0.16),
        }.get(len(spec), (1 / len(spec),) * len(spec))
        if "FR \\#" in contents or "FR #" in contents:
            widths = (0.13, 0.66, 0.21)
        elif "Mã NFR" in contents:
            widths = (0.12, 0.23, 0.37, 0.28)
        cols = "".join(
            r">{\raggedright\arraybackslash}p{" + str(width) + r"\reporttablewidth}"
            for width in widths
        )
        set_width = rf"\setlength{{\reporttablewidth}}{{\linewidth-{2*(len(spec)-1)}\tabcolsep}}"
        return (r"\begingroup\small" + set_width + "\n" + r"\begin{longtable}{@{}" + cols + "@{}}"
                + contents + r"\end{longtable}" + "\n" + r"\endgroup")

    return re.sub(
        r"\\begin\{longtable\}\[\]\{@\{\}([lcr]+)@\{\}\}(.*?)\\end\{longtable\}",
        sized, text, flags=re.S,
    )


def sanitize(text):
    """Drop heading decorations that cannot be typeset in the report fonts."""
    return re.sub(r"[\U0001F300-\U0001FAFF\uFE0F\u2705\u274C\u26A0]", "", text)


def fragment(name, text):
    (GENERATED / name).write_text(
        "% Nguồn dẫn xuất. Chạy scripts/build_submission_4.py để cập nhật.\n" + text,
        encoding="utf-8",
    )


def requirements():
    srs = (DOCS / "requirements-analysis.md").read_text(encoding="utf-8")
    first = srs.index("## 0.")
    last = srs.index("## 4.")
    nfr = srs[srs.index("## 6."):srs.index("## Ghi chú xác thực")]
    text = srs[first:last] + nfr
    # Exclude the lecturer-specified note and the three external-system rows
    # from the final report while retaining the original SRS for earlier phases.
    excluded = ("Hệ thống Ngoại vi (External Systems)",
                "Mạng lưới Cảm biến IoT tại trạm",
                "Cổng Thanh toán / Ví điện tử nội bộ")
    text = "\n".join(line for line in text.splitlines()
                     if not line.startswith("> *Ghi chú: Theo đề cương BTL môn học")
                     and not any(item in line for item in excluded))
    text = re.sub(r"^## \d+\. .*", lambda m: "## " + {
        "0": "Bối cảnh, mục tiêu và phạm vi",
        "1": "Bên liên quan",
        "2": "User story của bảy phân hệ",
        "3": "Ma trận yêu cầu chức năng",
        "6": "Yêu cầu phi chức năng",
    }[m[0][3]], text, flags=re.M)
    text = re.sub(r"^(###) \d+\.\d+\. ", r"\1 ", text, flags=re.M)
    # SRS proposed behavior and historic implementation claims have different lifetimes.
    # Keep the normative FR rows while omitting the historic implementation status.
    lines = text.splitlines()
    inside = False
    for i, line in enumerate(lines):
        if line.startswith("| FR #"):
            inside = True
        if inside:
            if line.startswith("|"):
                cells = line.strip("|").split("|")
                lines[i] = "| " + " | ".join(cell.strip() for cell in cells[:3]) + " |"
            else:
                inside = False
    fragment("requirements.tex", pandoc(sanitize("\n".join(lines)), division="chapter"))


def use_case_index():
    baseline = json.loads((DOCS / "traceability" / "submission_2.json").read_text(encoding="utf-8"))
    rows = ["| Mã | Tên use case |", "| :--- | :--- |"]
    for uc, entry in baseline["canonical_use_cases"].items():
        rows.append(f"| `{uc}` | {entry['name']} |")
    fragment("use-case-index.tex", pandoc("\n".join(rows)))


def interaction_design():
    path = REPORTS / "submission_2" / "REPORT_SUBMISSION_2.tex"
    text = path.read_text(encoding="utf-8")
    body = text[text.index(r"\section{Thiết kế Giao diện Người dùng"):text.index(r"\appendix")]
    body = body.replace(r"\input{generated_scope.tex}", r"\input{../submission_2/generated_scope.tex}")
    # The final report omits the assignment table while retaining the diagrams.
    body, removed = re.subn(
        r"\\begin\{table\}\[H\](?:(?!\\end\{table\}).)*?\\caption\{Ma trận Phân công Thực hiện 17 Sequence Diagrams\}(?:(?!\\end\{table\}).)*?\\end\{table\}",
        "", body, count=1, flags=re.S,
    )
    if removed != 1:
        raise ValueError("Không tìm thấy bảng phân công sequence trong nguồn Submission 2")
    # Remove the SS1 message exchange table specified for the final report.
    body, removed = re.subn(
        r"\\begin\{table\}\[H\](?:(?!\\end\{table\}).)*?\\label\{tab:msg-ss1-01\}(?:(?!\\end\{table\}).)*?\\end\{table\}",
        "", body, count=1, flags=re.S,
    )
    if removed != 1:
        raise ValueError("Không tìm thấy bảng thông điệp UC_SS1_01")
    target = "tuyệt đối không mô hình hóa bộ lập lịch ngầm"
    if body.count(target) != 1:
        raise ValueError("Không tìm thấy câu cần chỉnh trong nguồn Submission 2")
    body = body.replace(target, "không mô hình hóa bộ lập lịch ngầm", 1)
    body = re.sub(r"\\section(?=[\[{])", r"\\chapter", body)
    body = re.sub(r"\\subsection(?=[\[{])", r"\\section", body)
    body = re.sub(r"\\subsubsection(?=[\[{])", r"\\subsection", body)
    fragment("interaction.tex", body)


def catalog_methods(member, name_pattern):
    """Bring selected signatures and behavior from the member catalog into the PDF."""
    catalog = (member / "method_catalog.md").read_text(encoding="utf-8")
    selected = []
    for match in re.finditer(r"(?ms)^## `([^`]+)`\n(.*?)(?=^## |\Z)", catalog):
        name, body = match.groups()
        if re.fullmatch(name_pattern, name):
            body = body.split("**Truy vết:**", 1)[0].strip()
            body = body.replace("xem mục6 báo cáo", "xem phần mô tả service cùng chương")
            selected.append(f"**`{name}`**\n\n{body}")
    return "\n\n".join(selected) + "\n\n"


def design():
    s3 = REPORTS / "submission_3"
    group = (s3 / "REPORT_SUBMISSION_3.md").read_text(encoding="utf-8")
    # Replace the historical SS2 chapter with class and method content from the
    # member source that was updated in the same revision as the code.
    ss2 = s3 / "TV2_NguyenAnhTai"
    member = (ss2 / "REPORT_SUB3.md").read_text(encoding="utf-8")
    current = member[member.index("## 4. Class diagram"):member.index("## 7. Truy vết")]
    current = re.sub(r"^## [456]\. ", "## ", current, flags=re.M)
    current = re.sub(r"^### \d+\.\d+\. ", "### ", current, flags=re.M)
    current = re.sub(r"^.*\]\(.*class_diagram\.(?:svg|puml|png).*\).*$", "", current, flags=re.M)
    current = ("# Thiết kế SS2 xe cá nhân và quản lý chỗ đỗ\n\n"
               "![Sơ đồ lớp SS2 cập nhật](../../diagrams/submission_3/SS2/class_diagram.png)\n\n"
               + current)
    current += "\n\n## Hàm giao diện và nghiệp vụ trong prototype SS2\n\n"
    current += catalog_methods(ss2, r"(?:SS2UI|PersonalEVModule)\.\w+")
    prefix = group[group.index("# Mục 3:"):group.index("# Mục 6:")]
    # Exclude the historical traceability and test-case chapters from the final report.
    end = group[group.index("# Mục 7:"):group.index("# Mục 12:")]
    text = prefix + current + end
    # Preserve literal double underscores and the priority formula during Markdown conversion.
    text = re.sub(r"(?m)^\*\*((?:ChargingRequest|SmartChargingScheduler)\.__\w+__)\*\*$",
                  r"**`\1`**", text)
    formula = "Score=0.5*(100-SoC)+100*I(SoC<20)+60*I(has_booking)+30*I(SoC<50)"
    text = text.replace(formula, f"`{formula}`")
    start_deployment = text.index("Rerun chạy lại script")
    end_deployment = text.index("## 3.2 Development", start_deployment)
    text = (
        text[:start_deployment]
        + "Reset nạp lại seed. Các giao dịch nghiệp vụ chỉ tồn tại trong phiên. "
          "Khi bật IoT, fragment Streamlit chạy định kỳ 2 giây và đọc bản tin "
          "từ SQLite theo cursor riêng. Bộ phát mô phỏng chạy ở một tiến trình "
          "Python khác. Hai phiên có thể thấy cùng bản tin và vẫn giữ ví, "
          "lượt đặt và phiên sạc riêng. Hình dưới mô tả chế độ demo local.\n\n"
          "![Triển khai MVP local khi bật feed IoT mô phỏng]"
          "(../../diagrams/telemetry/deployment.png)\n\n"
        + text[end_deployment:]
    )
    text = text.replace("Prototype đỗ 5.000 VNĐ/lượt", "Đỗ xe cá nhân: giả định demo 5.000 VNĐ mỗi giờ bắt đầu, tối thiểu một giờ")
    text = text.replace("phí đỗ `5.000 VNĐ` + phí điện/quá giờ", "phí đỗ tính theo giờ bắt đầu + phí điện/quá giờ")
    text = text.replace(
        "parking_fee mặc định 5.000 VNĐ/lượt, tariff 7.000 cao điểm/3.000 thấp điểm; không mô hình hourly parking hay tích phân biểu giá theo từng tick.",
        "Hàm dùng phí đỗ truyền vào và áp một mức giá theo thời điểm tham chiếu. "
        "Đây là hàm tính dự toán cũ. Luồng check-out của MVP tính phí đỗ theo giờ "
        "bắt đầu và lấy số liệu điện, phí quá giờ đã tích lũy từ SS5.",
    )
    text = text.replace(
        "Streamlit rerun hiện tại chưa chứng minh polling nền hoặc các chỉ tiêu này.",
        "MVP đọc feed theo chu kỳ khi bật IoT. Quan sát cục bộ không đủ để xác nhận các chỉ tiêu này.",
    )
    text = text.replace("hợp đồng tài chính mục 2.3", "hợp đồng tài chính liên phân hệ")
    # Omit the historical mapping-and-limitations subsections in the final report.
    text, removed = re.subn(
        r"(?ms)^## \d+\.\d+ Ánh xạ và giới hạn triển khai\s*\n.*?(?=^#{1,2} |\Z)",
        "", text,
    )
    if removed != 6:
        raise ValueError(f"Cần bỏ 6 mục ánh xạ, đã tìm thấy {removed}")
    text = re.sub(r"^# Mục \d+: ", "# ", text, flags=re.M)
    text = re.sub(r"^## \d+\.\d+ ", "## ", text, flags=re.M)
    text = text.replace("../../../docs/diagrams/", "../../diagrams/")
    text = text.replace("../../../docs/report/submission_3/", "../submission_3/")
    text = re.sub(r"(?m)^(!\[.*\]\(.*\))$", r"\1\n", text)
    text = re.sub(r"!\[Hình \d+\.\d+: ", "![", text)
    text = re.sub(r"^\*\*Bảng \d+\.\d+: (.*?)\*\*$", r"**\1**", text, flags=re.M)
    figures = dict(re.findall(r"^!\[(.*?)\]\((.*?)\)$", text, flags=re.M))
    captions = {path: caption for caption, path in figures.items()}
    latex = pandoc(sanitize(text), division="chapter")
    latex = re.sub(r"(\\chapter\{Thiết kế (SS[1-7]) [^}]+\}\\label\{[^}]+\})",
                   lambda match: match[1] + rf"\label{{chap:design-{match[2].lower()}}}", latex)
    latex = latex.replace(
        "trong mục 5 đến 11",
        r"trong các chương~\ref{chap:design-ss1}--\ref{chap:design-ss7}",
    )
    latex = latex.replace("tại mục 5.", r"tại chương~\ref{chap:design-ss1}.")

    def figure(match):
        path = match[1]
        caption = pandoc(captions[path]).strip()
        return rf"\evidencefigure{{{path}}}{{{caption}}}{{fig:s3-{len(numbered)}}}"

    numbered = []
    def replace_figure(match):
        numbered.append(match[1])
        return figure(match)

    latex = re.sub(r"^\\includegraphics\{([^{}]+)\}$", replace_figure, latex, flags=re.M)
    fragment("architecture.tex", r"\begingroup\raggedright\sloppy" + "\n" + latex + "\n" + r"\par\endgroup")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    GENERATED.mkdir(parents=True, exist_ok=True)
    requirements()
    use_case_index()
    interaction_design()
    design()
    if not args.prepare_only:
        name = "REPORT_SUBMISSION_4"
        subprocess.run(
            ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error",
             "-outdir=build", f"{name}.tex"], cwd=HERE, check=True,
        )
        shutil.copy2(HERE / "build" / f"{name}.pdf", HERE / f"{name}.pdf")


if __name__ == "__main__":
    main()
