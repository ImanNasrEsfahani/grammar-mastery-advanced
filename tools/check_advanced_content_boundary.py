#!/usr/bin/env python3
"""Check that the Advanced clean seed cannot silently serve Intermediate content."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATHS = [
    ROOT / "frontend/public/grammar/grammaire-progressive-francais-intermediaire-3e",
    ROOT / "database/postgres/007_stage23_import_pipeline_v1.0.sql",
]

REQUIRED_PATHS = [
    ROOT / "frontend/.env.example",
    ROOT / "frontend/src/lib/grammar-content/books.ts",
    ROOT / "ops/stage26/migration_runner.py",
    ROOT / "config/stage26_operations_contract_v1.0.json",
    ROOT / "schemas/stage26_release_evidence_v1.0.schema.json",
]

errors: list[str] = []
warnings: list[str] = []

for path in FORBIDDEN_PATHS:
    if path.exists():
        errors.append(f"forbidden legacy path exists: {path.relative_to(ROOT)}")

for path in REQUIRED_PATHS:
    if not path.is_file():
        errors.append(f"required path missing: {path.relative_to(ROOT)}")

gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
if "!frontend/.env.example" not in gitignore:
    errors.append(".gitignore does not unignore frontend/.env.example")

books = (ROOT / "frontend/src/lib/grammar-content/books.ts").read_text(
    encoding="utf-8"
)
for marker in (
    "grammaire-progressive-francais-intermediaire-3e",
    "Niveau intermédiaire",
    "سطح متوسط",
):
    if marker in books:
        errors.append(f"legacy book marker remains in books.ts: {marker}")

dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
for marker in ("stage1_lessons_v1.0.csv", "stage1_subtopics_v1.0.csv"):
    if marker in dockerignore:
        errors.append(f"old content pin remains in .dockerignore: {marker}")

contract_path = ROOT / "config/stage26_operations_contract_v1.0.json"
if contract_path.is_file():
    contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    if contract.get("migration_policy", {}).get("plan_version") != (
        "advanced-schema-sequence-v1.0.0"
    ):
        errors.append("Advanced migration plan version mismatch")
    if contract.get("canonical_data_bootstrap_policy", {}).get("enabled") is not False:
        errors.append("canonical data bootstrap is unexpectedly enabled")
    if contract.get("production_release") == "READY":
        errors.append("production release must still be blocked in empty-content phase")

schema_path = ROOT / "schemas/stage26_release_evidence_v1.0.schema.json"
if schema_path.is_file():
    schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    properties = schema.get("properties", {})
    if properties.get("schema_version", {}).get("const") != (
        "advanced-seed-release-evidence-v1.0.0"
    ):
        errors.append("release evidence JSON schema still uses legacy Stage26 schema_version")
    if properties.get("release_mode", {}).get("enum") != [
        "SCHEMA_ONLY",
        "FULL_PRODUCT",
    ]:
        errors.append("release evidence JSON schema is not aligned with Advanced release modes")
    plan_const = (
        properties.get("migrations", {})
        .get("properties", {})
        .get("plan_version", {})
        .get("const")
    )
    if plan_const != "advanced-schema-sequence-v1.0.0":
        errors.append("release evidence JSON schema still uses legacy migration plan")

# Stage 16/17 algorithms are reusable, but historical source provenance is a
# deliberate warning until the actual Advanced source book is frozen.
for rel in ("config/stage16_contract.json", "config/stage17_contract.json"):
    path = ROOT / rel
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if "Niveau intermédiaire" in text:
            warnings.append(
                f"{rel}: legacy source provenance remains; regenerate after Advanced Stage 1"
            )

payload = {
    "status": "PASS" if not errors else "FAIL",
    "errors": errors,
    "warnings": warnings,
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
raise SystemExit(0 if not errors else 2)
