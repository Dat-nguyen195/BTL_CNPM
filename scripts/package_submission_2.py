"""Build a local submission archive with source, PDF and final evidence only."""
from hashlib import sha256
from pathlib import Path
import json
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/submission_2"
OUTPUT.mkdir(parents=True, exist_ok=True)
sources = set()
for folder in ["src", "docs", "tests", "scripts"]:
    for path in (ROOT / folder).rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in {"__pycache__", ".pytest_cache", "build", ".git", ".venv", "venv"} for part in rel.parts):
            continue
        if path.suffix.lower() in {".zip",".pyc", ".aux", ".log", ".out", ".toc", ".xdv", ".fls", ".fdb_latexmk", ".synctex", ".bak"}:
            continue
        if "docs/audit/" in rel.as_posix() and not rel.as_posix().startswith("docs/audit/submission_2/final/"):
            continue
        sources.add(path)
for name in ["README.md", "requirements.txt", "requirements-dev.txt", "requirements-tested.txt", "Dockerfile", "compose.yaml", ".gitignore", "tools/plantuml.jar"]:
    path = ROOT / name
    if not path.is_file():
        raise FileNotFoundError(path)
    sources.add(path)
manifest = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}
target = OUTPUT / "SMART_EMOBILITY_HUB_SUBMISSION_2.zip"
with ZipFile(target, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
    for path in sorted(sources):
        archive.write(path, "smart-emobility-hub/" + path.relative_to(ROOT).as_posix())
    archive.writestr("smart-emobility-hub/SUBMISSION_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
with ZipFile(target) as archive:
    assert archive.testzip() is None
    for relative, digest in manifest.items():
        assert sha256(archive.read("smart-emobility-hub/" + relative)).hexdigest() == digest
pdf = ROOT / "output/pdf/REPORT_SUBMISSION_2.pdf"
pdf.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(ROOT / "docs/report/submission_2/REPORT_SUBMISSION_2.pdf", pdf)
(OUTPUT / "SHA256SUMS.txt").write_text(f"{sha256(target.read_bytes()).hexdigest()}  {target.name}\n{sha256(pdf.read_bytes()).hexdigest()}  ../pdf/{pdf.name}\n")
print(f"Archive verified: {len(manifest)} files; {target.stat().st_size:,} bytes")
print(target)
print(pdf)
