#!/usr/bin/env python3
"""Validate tese_doutorado canonical JSONs against their JSON Schemas.

Usage:
    python validate.py            # validate all
    python validate.py 02         # validate only 02_textuais.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator, RefResolver


REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = REPO_ROOT / "01_templates" / "tese_doutorado" / "caracteristicas"
SCHEMA_DIR = Path(__file__).parent

PAIRS: list[tuple[str, str]] = [
    ("01_pre_textuais.json", "01_pre_textuais.schema.json"),
    ("02_textuais.json", "02_textuais.schema.json"),
    ("03_pos_textuais.json", "03_pos_textuais.schema.json"),
    ("04_formatacao_global.json", "04_formatacao_global.schema.json"),
    ("05_citacoes.json", "05_citacoes.schema.json"),
]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_one(data_file: str, schema_file: str) -> tuple[bool, list[str]]:
    data_path = TEMPLATE_DIR / data_file
    schema_path = SCHEMA_DIR / schema_file
    data = load_json(data_path)
    schema = load_json(schema_path)

    resolver = RefResolver(base_uri=schema_path.resolve().as_uri(), referrer=schema)
    validator = Draft7Validator(schema, resolver=resolver)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    msgs = [f"  - {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}" for e in errors]
    return (len(msgs) == 0, msgs)


def main() -> int:
    arg_filter = sys.argv[1] if len(sys.argv) > 1 else None
    overall_ok = True

    for data_file, schema_file in PAIRS:
        if arg_filter and not data_file.startswith(arg_filter):
            continue
        ok, msgs = validate_one(data_file, schema_file)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {data_file}")
        for m in msgs:
            print(m)
        overall_ok = overall_ok and ok

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
