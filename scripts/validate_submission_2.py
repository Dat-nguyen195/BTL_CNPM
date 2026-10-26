"""
validate_submission_2.py – Comprehensive Audit and Validation Script for Submission #2
Smart E-Mobility Hub – ĐHQG-HCM

Validates:
  1. Manifest coverage (30 US IDs, 23 FR IDs, 17 UCs across 7 subsystems)
  2. Subsystem directory structure (28 required directories)
  3. SRS identities/content, trace links, callable and test references
  4. PlantUML source syntax (not semantic UML acceptance)
  5. Computed MoSCoW evidence weights
  6. Python test suite execution
"""

import os
import sys
import json
import re
import subprocess
import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def check_manifest(data=None):
    manifest_path = REPO_ROOT / "docs" / "traceability" / "submission_2.json"
    if not manifest_path.exists():
        return False, f"Missing manifest: {manifest_path}"
    if data is None:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    stories = data.get("user_stories", {})
    if len(stories) != 30:
        return False, f"Expected 30 user stories, got {len(stories)}"
    
    ucs = data.get("canonical_use_cases", {})
    if len(ucs) != 17:
        return False, f"Expected 17 unique use cases, got {len(ucs)}"
    
    frs = data.get("functional_requirements", {})
    if len(frs) != 23:
        return False, f"Expected 23 functional requirements, got {len(frs)}"

    srs = (REPO_ROOT / "docs/requirements-analysis.md").read_text()
    baseline = dict(re.findall(r"\*\*(US-\d+b?):\*\*([^\n]+)", srs))
    if set(stories) != set(baseline):
        return False, f"SRS US IDs differ: missing={sorted(set(baseline)-set(stories))}, extra={sorted(set(stories)-set(baseline))}"
    expected_ucs = {f"UC_SS{ss}_{n:02d}" for ss, count in enumerate([3, 4, 2, 2, 2, 2, 2], 1) for n in range(1, count + 1)}
    if set(ucs) != expected_ucs:
        return False, "Canonical UC IDs differ from the assigned 17 use cases"
    baseline_frs = {}
    for line in srs.splitlines():
        if re.match(r"\| \*\*FR-", line):
            cells = line.split("|")
            baseline_frs[cells[1].strip().replace("**", "")] = (cells[2].strip(), re.findall(r"US-\d+b?", cells[3]))
    if set(frs) != set(baseline_frs):
        return False, "FR IDs differ from SRS"
    for fid, (description, ids) in baseline_frs.items():
        if frs[fid]["description"] != description or frs[fid]["user_stories"] != ids:
            return False, f"{fid} meaning/story links differ from SRS"
    tests = {node.name for p in (REPO_ROOT / "tests").glob("test_*.py") for node in ast.walk(ast.parse(p.read_text())) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}
    for sid, story in stories.items():
        if story["title"] != re.sub(r"[*`]+", "", baseline[sid]).strip():
            return False, f"{sid} meaning differs from SRS"
        expected_frs = {fid for fid, (_, ids) in baseline_frs.items() if sid in ids}
        if set(story["fr_links"]) != expected_frs:
            return False, f"{sid} FR links differ from SRS"
        if not set(story["canonical_ucs"]) <= set(ucs):
            return False, f"{sid} references unknown UC"
        if story["test_id"] not in tests:
            return False, f"{sid} references missing test {story['test_id']}"
        if story["status"] not in {"VERIFIED", "PARTIAL"} or not story.get("evidence_scope"):
            return False, f"{sid} is missing an explicit evidence scope/status"
        for key in ["component", "scenario_section", "sequence_path", "activity_path"]:
            if not (REPO_ROOT / story[key]).is_file():
                return False, f"{sid} has missing {key}: {story[key]}"
        functions = {n.name for n in ast.walk(ast.parse((REPO_ROOT / story["component"]).read_text())) if isinstance(n, ast.FunctionDef)}
        if story["function"] not in functions:
            return False, f"{sid} references missing function"
    for uid, uc in ucs.items():
        for key in ["component", "scenario_file", "sequence_file", "activity_file", "statechart_file"]:
            if not (REPO_ROOT / uc[key]).is_file():
                return False, f"{uid} references missing {key}"
    summary = data["moscow_summary"]
    for key in ["must", "should", "could"]:
        group = [s for s in stories.values() if s["moscow"] == key.upper()]
        verified = [s for s in group if s["status"] == "VERIFIED"]
        weight = sum(s["weight"] for s in group)
        verified_weight = sum(s["weight"] for s in verified)
        expected = {"count": len(group), "weight": weight, "verified_count": len(verified), "verified_weight": verified_weight, "coverage_pct": round(100 * verified_weight / weight, 2)}
        if summary[key] != expected:
            return False, f"Stale MoSCoW summary: {key}"
    weight = sum(s["weight"] for s in stories.values())
    verified_weight = sum(s["weight"] for s in stories.values() if s["status"] == "VERIFIED")
    if (summary["total_weight"], summary["overall_verified_weight"], summary["verified_count"], summary["overall_coverage_pct"]) != (weight, verified_weight, sum(s["status"] == "VERIFIED" for s in stories.values()), round(100 * verified_weight / weight, 2)):
        return False, "Stale overall MoSCoW summary"
    
    return True, f"SRS identities/content/links and evidence references valid: {len(stories)} US, {len(frs)} FR, {len(ucs)} UCs; {summary['verified_count']} prototype VERIFIED, {len(stories)-summary['verified_count']} PARTIAL"

def check_directories():
    base = REPO_ROOT / "docs" / "diagrams" / "Use-case detail-scenario"
    subsystems = [f"SS{i}" for i in range(1, 8)]
    subdirs = ["Activity diagrams", "Sequence diagrams", "State-chart diagrams", "Usecase scenario"]
    
    missing = []
    for ss in subsystems:
        for sd in subdirs:
            p = base / ss / sd
            if not p.is_dir():
                missing.append(str(p.relative_to(REPO_ROOT)))
                
    if missing:
        return False, f"Missing {len(missing)} directories: {missing[:3]}..."
    return True, "All 28 subsystem directories verified"

def check_puml_files():
    # Sub3 draft diagrams are outside the Sub2 baseline of 46 canonical sources.
    puml_files = list(REPO_ROOT.glob("docs/diagrams/Use-case detail-scenario/**/*.puml"))
    
    if len(puml_files) != 46:
        return False, f"Expected 46 puml files, got {len(puml_files)}"

    # Report panels must compile as well, with includes resolved from their own directory.
    puml_files += list(REPO_ROOT.glob("docs/report/assets/*_panels/*.puml"))
    
    # Check syntax using plantuml.jar
    jar_path = REPO_ROOT / "tools" / "plantuml.jar"
    if not jar_path.exists():
        return False, f"PlantUML JAR not found at {jar_path}"
        
    cmd = [
        "java", "-DPLANTUML_LIMIT_SIZE=16384",
        "-jar", str(jar_path),
        "-Playout=smetana",
        "-charset", "UTF-8",
        "-checkonly"
    ] + [str(p) for p in puml_files]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return False, f"PlantUML checkonly failed:\n{res.stderr}"
        
    return True, f"All {len(puml_files)} .puml files passed syntax validation"

def check_unit_tests():
    cmd = [
        str(REPO_ROOT / "venv" / "bin" / "python"),
        "-m", "pytest", "-q", "tests/"
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
    if res.returncode != 0:
        return False, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
    return True, f"Unit tests passed: {res.stdout.strip()}"

def main():
    print("=" * 60)
    print("VALIDATING SUBMISSION #2 ARTIFACTS AND SPECIFICATIONS")
    print("=" * 60)
    
    checks = [
        ("Directory Structure", check_directories),
        ("Traceability Manifest", check_manifest),
        ("PlantUML Syntax Validation", check_puml_files),
        ("Python Core Unit Tests", check_unit_tests),
    ]
    
    all_ok = True
    for name, fn in checks:
        ok, msg = fn()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {msg}")
        if not ok:
            all_ok = False
            
    print("=" * 60)
    if all_ok:
        print("🎉 ALL SUBMISSION #2 CORE QUALITY GATES PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME CHECKS FAILED. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
