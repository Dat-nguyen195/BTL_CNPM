#!/usr/bin/env python3
"""Validate the Sub3 handoff: canonical UC IDs, paths and method coverage.

This is a documentation integrity check, not a claim of design correctness.
Run from any directory: python3 scripts/validate_submission_3.py [--pdfs].
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def diagram_methods(path):
    owner = None
    found = []
    for line in path.read_text().splitlines():
        line = re.sub(r'\\n\s*', ' ', line)
        match = re.match(r'\s*class\s+(?:"([^"]+)"(?:\s+as\s+(\w+))?|(\w+)(?:<[^>]+>)?)', line)
        if match:
            owner = match[2] or match[3] or match[1]
        match = re.match(r'\s*(?:\{static\}\s*)?[+#-](\w+)\((.*)\)\s*:\s*(.*)', line)
        if match:
            found.append((owner, match[1], match[2], match[3]))
        if line.strip() == '}':
            owner = None
    return found


def validate(require_pdfs=False):
    errors = []
    manifest = json.loads((ROOT / 'docs/traceability/submission_3.json').read_text())
    baseline = json.loads((ROOT / 'docs/traceability/submission_2.json').read_text())['canonical_use_cases']
    srs = (ROOT / 'docs/requirements-analysis.md').read_text()
    ids = set(re.findall(r'\b(?:US|FR)-\d+[a-z]?\b', srs))
    rows = manifest['use_cases']
    if set(rows) != set(baseline):
        errors.append('UC set differs from canonical 17 UC baseline')
    for uc, row in rows.items():
        if row['name'] != baseline[uc]['name'] or row['owner'] != baseline[uc]['owner']:
            errors.append(f'{uc}: canonical title/owner mismatch')
        for key in ['scenario', 'sequence', 'activity', 'class_diagram']:
            if not (ROOT / row[key]).is_file():
                errors.append(f'{uc}: missing {key}: {row[key]}')
        for requirement in row['user_stories'] + row['functional_requirements']:
            if requirement not in ids:
                errors.append(f'{uc}: nonexistent SRS ID {requirement}')
        for test in row['prototype_tests']:
            path, name = test.split('::')
            if not (ROOT / path).is_file() or not re.search(r'^def ' + re.escape(name) + r'\(', (ROOT / path).read_text(), re.M):
                errors.append(f'{uc}: nonexistent test {test}')
    total = 0
    for number in range(1, 8):
        member = next((ROOT / 'docs/report/submission_3').glob(f'TV{number}_*'))
        catalog = (member / 'method_catalog.md').read_text()
        report = (member / 'REPORT_SUB3.md').read_text()
        for required in ['REPORT_SUB3.md', 'method_catalog.md', 'traceability.md', 'test_cases.md', 'self_check.md', 'ai_usage.md']:
            if not (member / required).is_file():
                errors.append(f'SS{number}: missing {required}')
        for owner, method, args, returns in diagram_methods(ROOT / f'docs/diagrams/submission_3/SS{number}/class_diagram.puml'):
            total += 1
            signature = f'{method}({args}) -> {returns}'
            if f'{owner}.{method}' not in catalog or signature not in catalog:
                errors.append(f'SS{number}: missing exact method description: {owner}.{signature}')
        if '[CHƯA ĐIỀN' in report or 'KHUNG CHƯA HOÀN THIỆN' in report:
            errors.append(f'SS{number}: mandatory report still has placeholders')
        if require_pdfs:
            if not list((ROOT / 'output/submission_3').glob(f'REPORT_SUB3_{member.name.split("_", 1)[1]}_*.pdf')):
                errors.append(f'SS{number}: missing canonical PDF')
    for kind in ['deployment', 'implementation', 'system_classes']:
        text = (ROOT / f'docs/diagrams/submission_3/shared/{kind}.puml').read_text()
        if 'DRAFT' in text or 'CHƯA HOÀN THIỆN' in text:
            errors.append(f'{kind}: draft shared diagram')
    print(f'Canonical UC: {len(rows)}; detailed diagram method entries: {total}; member reports: 7')
    for error in errors:
        print('ERROR:', error)
    print('PASS' if not errors else 'FAIL')
    return not errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdfs', action='store_true')
    raise SystemExit(0 if validate(parser.parse_args().pdfs) else 1)
