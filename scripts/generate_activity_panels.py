"""Render readable report panels from the canonical SS1 return activity.

The full activity remains beside its source. Report panels continue at connector
A; they do not introduce an extra initial/final node at the page boundary.
"""

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / (
    "docs/diagrams/Use-case detail-scenario/SS1/Activity diagrams/"
    "UC_SS1_02_NguyenThanhDat_activity.puml"
)
OUTPUT = ROOT / "docs/report/assets/activity_panels"


def main():
    source = SOURCE.read_text(encoding="utf-8")
    boundary = "endwhile ([Không])"
    before, after = source.split(boundary, 1)
    before += boundary + "\n"
    before = before.replace(
        "!include ../../../common.puml", "!include ../../../diagrams/common.puml"
    )
    before = re.sub(
        r"^title .*", "title UC_SS1_02 - Phần 1: Kiểm tra Hub & Điều hướng", before,
        flags=re.MULTILINE,
    )
    part1 = before + "\n|Giao diện SS1|\n(A)\ndetach\n@enduml\n"
    part2 = (
        "@startuml UC_SS1_02_NguyenThanhDat_activity_p2\n"
        "!include ../../../diagrams/common.puml\n"
        "title UC_SS1_02 - Phần 2: Nhận xe & Quyết toán\n\n"
        "|Giao diện SS1|\n(A)\n" + after.lstrip()
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for number, content in enumerate([part1, part2], 1):
        path = OUTPUT / f"{SOURCE.stem}_p{number}.puml"
        if number == 1:
            content = content.replace(
                "@startuml UC_SS1_02_NguyenThanhDat_activity\n",
                "@startuml UC_SS1_02_NguyenThanhDat_activity_p1\n", 1,
            )
        path.write_text(content, encoding="utf-8")
        subprocess.run(
            ["java", "-DPLANTUML_LIMIT_SIZE=16384", "-jar",
             str(ROOT / "tools/plantuml.jar"), "-Playout=smetana", "-charset",
             "UTF-8", "-tpng", str(path)], check=True,
        )
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
