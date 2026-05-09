from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
SCHEMA_DIR = DATA_DIR / 'schemas'
UNIT_CODE_RE = re.compile(r'^[A-Z]{4}[0-9]{4}$')


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str

    def format(self) -> str:
        return f'{self.path.relative_to(ROOT)}: {self.message}'


def load_yaml(path: Path) -> dict:
    with path.open(encoding='utf-8') as handle:
        data = yaml.safe_load(handle)
    return data or {}


def load_schema(name: str) -> dict:
    with (SCHEMA_DIR / name).open(encoding='utf-8') as handle:
        return json.load(handle)


def schema_issues(path: Path, schema_name: str) -> list[ValidationIssue]:
    data = load_yaml(path)
    validator = Draft202012Validator(load_schema(schema_name), format_checker=FormatChecker())
    issues = []
    for error in sorted(validator.iter_errors(data), key=lambda e: e.path):
        location = '.'.join(str(part) for part in error.path)
        prefix = f'{location}: ' if location else ''
        issues.append(ValidationIssue(path, f'{prefix}{error.message}'))
    return issues


def validate_schemas() -> list[ValidationIssue]:
    checks = [
        ('units/*.yaml', 'unit.json'),
        ('degrees/*.yaml', 'degree.json'),
        ('clubs/*.yaml', 'club.json'),
        ('benefits/*/_category.yaml', 'benefit_category.json'),
        ('benefits/*/[!_]*.yaml', 'benefit.json'),
    ]
    issues = []
    for pattern, schema_name in checks:
        for path in DATA_DIR.glob(pattern):
            issues.extend(schema_issues(path, schema_name))
    return issues


def degree_unit_codes(degree: dict) -> set[str]:
    codes = set()
    for year in degree.get('years') or []:
        for semester in year.get('semesters') or []:
            for unit in semester.get('units') or []:
                code = unit.get('code', '')
                if UNIT_CODE_RE.match(code):
                    codes.add(code)
    return codes


def prerequisite_codes(unit: dict) -> set[str]:
    prereqs = unit.get('prerequisites') or {}
    codes = set(prereqs.get('all_of') or [])
    for group in prereqs.get('any_of') or []:
        codes.update(code for code in group if UNIT_CODE_RE.match(str(code)))
    return codes


def validate_references() -> list[ValidationIssue]:
    unit_paths = sorted((DATA_DIR / 'units').glob('*.yaml'))
    degree_paths = sorted((DATA_DIR / 'degrees').glob('*.yaml'))
    club_paths = sorted((DATA_DIR / 'clubs').glob('*.yaml'))

    unit_codes = {load_yaml(path).get('code') for path in unit_paths}
    club_slugs = {load_yaml(path).get('slug') for path in club_paths}

    issues: list[ValidationIssue] = []

    for path in unit_paths:
        unit = load_yaml(path)
        for slug in unit.get('associated_clubs') or []:
            if slug not in club_slugs:
                issues.append(ValidationIssue(path, f'unknown associated_club {slug!r}'))
        for code in prerequisite_codes(unit):
            if code not in unit_codes:
                issues.append(ValidationIssue(path, f'unknown prerequisite unit {code!r}'))

    for path in degree_paths:
        degree = load_yaml(path)
        for code in sorted(degree_unit_codes(degree)):
            if code not in unit_codes:
                issues.append(ValidationIssue(path, f'unknown degree unit {code!r}'))

    return issues


def run_validation() -> list[ValidationIssue]:
    return [*validate_schemas(), *validate_references()]


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate stUwa YAML catalogue data.')
    parser.parse_args()

    issues = run_validation()
    if issues:
        for issue in issues:
            print(issue.format())
        return 1

    print('Data validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
