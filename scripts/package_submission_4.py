#!/usr/bin/env python3
"""Package the final report, runnable app, instructions, and individual work."""
import hashlib
from pathlib import Path
import shutil
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "docs/report/submission_4"
OUTPUT = ROOT / "output/submission_4"
BUILD = REPORT_DIR / "build"
LIMIT_BYTES = 20_000_000
DIAGRAMS = ROOT / "docs/diagrams"
MEMBERS = (
    "NguyenThanhDat",
    "NguyenAnhTai",
    "PhamTienDat",
    "DangHoangQuyNhan",
    "DuongDangKhoa",
    "HoangVanTan",
    "NguyenTrungNguyen",
)
DIAGRAM_TYPES = {
    "Usecase scenario": "Use_Case",
    "Sequence diagrams": "Sequence",
    "Activity diagrams": "Activity",
    "State-chart diagrams": "State_Chart",
}
DIAGRAM_FORMATS = {".png", ".puml", ".drawio"}

GUIDE = r"""SMART E-MOBILITY HUB | NHÓM BEE BRAVE | SUBMISSION FINAL #4

NỘI DUNG GÓI
  REPORT_SUBMISSION_4.pdf  Báo cáo tổng kết.
  source/                 Mã nguồn, dữ liệu mẫu và cấu hình chạy ứng dụng.
  HUONG_DAN.txt           Hướng dẫn đọc và chạy dự án.
  ca_nhan/                Bảy thư mục SS1–SS7 theo tên thành viên.

Trong mỗi thư mục cá nhân, mở tệp .md ở Use_Case_Scenario/ để xem kịch bản.
Thư mục Diagrams/ chứa sơ đồ use case, sequence, activity, state-chart và
sơ đồ thiết kế của phân hệ. Xem ảnh .png trực tiếp; dùng .puml hoặc .drawio
để mở nguồn sơ đồ. Giữ ca_nhan/common.puml tại vị trí gốc để PlantUML đọc.
Thư mục ca_nhan/ là nơi tra các tệp kịch bản được nhắc đến ở mục 2.2 của báo cáo.

CHẠY ỨNG DỤNG
Cần Python 3.12. Giải nén gói và mở terminal tại thư mục source/.

Linux / macOS:
  python3.12 -m venv venv
  venv/bin/python -m pip install -r requirements-tested.txt
  EMOBILITY_IOT_ENABLED=1 venv/bin/python -m streamlit run src/app.py

Windows PowerShell:
  py -3.12 -m venv venv
  .\venv\Scripts\python.exe -m pip install -r requirements-tested.txt
  $env:EMOBILITY_IOT_ENABLED = "1"
  .\venv\Scripts\python.exe -m streamlit run src/app.py

Mở http://localhost:8501. Để gửi một bản tin IoT, mở terminal thứ hai
trong cùng source/, vào phân hệ SS3 trên trình duyệt rồi chạy:

  Linux / macOS:
  venv/bin/python scripts/iot_producer.py --hub HUB-001 --port 1 --count 1

  Windows PowerShell:
  .\venv\Scripts\python.exe scripts/iot_producer.py --hub HUB-001 --port 1 --count 1

Đối chiếu mã bản tin ở bảng sự kiện SS3 với mã được in ở terminal.
Có thể chạy bằng Docker Compose với lệnh docker compose up --build từ source/.
"""


def write_application(bundle):
    paths = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "src"],
        cwd=ROOT, text=True,
    ).split("\0")
    application_files = {
        "Dockerfile", "compose.yaml", "requirements.txt", "requirements-tested.txt",
        "requirements-dev.txt", "scripts/iot_producer.py",
    }
    for relative in sorted(application_files.union(filter(None, paths))):
        bundle.write(ROOT / relative, f"source/{relative}")


def write_individual_work(bundle):
    bundle.write(DIAGRAMS / "common.puml", "ca_nhan/common.puml")
    for number, member in enumerate(MEMBERS, 1):
        subsystem = f"SS{number}"
        personal = f"ca_nhan/{subsystem}_{member}"
        design = DIAGRAMS / "Use-case detail-scenario" / subsystem
        scenario = design / "Usecase scenario" / f"UC_{subsystem}_{member}.md"
        bundle.write(scenario, f"{personal}/Use_Case_Scenario/{scenario.name}")

        for folder, kind in DIAGRAM_TYPES.items():
            destination = f"{personal}/Diagrams/{kind}"
            for path in sorted((design / folder).iterdir()):
                if path.suffix in DIAGRAM_FORMATS:
                    bundle.write(path, f"{destination}/{path.name}")
                elif path.name.endswith("_diagram.pdf") and not path.with_suffix(".png").exists():
                    # These use-case diagrams have a one-page PDF export instead of a PNG.
                    png = subprocess.check_output(
                        ["pdftoppm", "-png", "-singlefile", "-scale-to", "3000", str(path)]
                    )
                    bundle.writestr(f"{destination}/{path.stem}.png", png)

        for path in sorted((DIAGRAMS / "submission_3" / subsystem).iterdir()):
            if path.suffix in DIAGRAM_FORMATS:
                bundle.write(path, f"{personal}/Diagrams/Design/{path.name}")


def main():
    pdf = REPORT_DIR / "REPORT_SUBMISSION_4.pdf"
    compiled = BUILD / pdf.name
    if not pdf.is_file() or not compiled.is_file() or pdf.read_bytes() != compiled.read_bytes():
        raise SystemExit("Dựng lại PDF trước: python3 scripts/build_submission_4.py")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    archive = OUTPUT / "SMART_EMOBILITY_HUB_SUBMISSION_4_BEE_BRAVE.zip"
    staging = archive.with_suffix(".zip.tmp")
    try:
        with ZipFile(staging, "w", ZIP_DEFLATED, compresslevel=9) as bundle:
            bundle.write(pdf, pdf.name)
            write_application(bundle)
            bundle.writestr("HUONG_DAN.txt", GUIDE)
            write_individual_work(bundle)
        if staging.stat().st_size >= LIMIT_BYTES:
            raise SystemExit(f"ZIP vượt giới hạn 20 MB: {staging.stat().st_size:,} byte")
        with ZipFile(staging) as bundle:
            if error := bundle.testzip():
                raise RuntimeError(f"File ZIP bị lỗi: {error}")
            if [name for name in bundle.namelist() if name.lower().endswith(".pdf")] != [pdf.name]:
                raise RuntimeError("ZIP phải chứa đúng một PDF")
            if hashlib.sha256(bundle.read(pdf.name)).digest() != hashlib.sha256(pdf.read_bytes()).digest():
                raise RuntimeError("PDF trong ZIP không khớp artefact")
        staging.replace(archive)
    finally:
        staging.unlink(missing_ok=True)
    shutil.copy2(pdf, OUTPUT / pdf.name)
    print(f"{archive.relative_to(ROOT)}: {archive.stat().st_size:,} byte")


if __name__ == "__main__":
    main()
