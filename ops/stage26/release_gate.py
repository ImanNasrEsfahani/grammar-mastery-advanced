#!/usr/bin/env python3
"""Fail-closed release gate for the Advanced clean-seed phase."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PASS = "PASS"
SCHEMA_VERSION = "advanced-seed-release-evidence-v1.0.0"
PLAN_VERSION = "advanced-schema-sequence-v1.0.0"
UNRESOLVED = {"", "REPLACE_ME", "UNRESOLVED", "TBD", "TODO", "NOT_RUN", "FAIL"}


def _pass(value: Any) -> bool:
    return value == PASS


def evaluate_evidence(evidence: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if evidence.get("schema_version") != SCHEMA_VERSION:
        errors.append("unsupported schema_version")

    target = evidence.get("target_environment")
    if target not in {"staging", "production"}:
        errors.append("target_environment must be staging or production")
        return errors

    mode = evidence.get("release_mode")
    if mode not in {"SCHEMA_ONLY", "FULL_PRODUCT"}:
        errors.append("release_mode must be SCHEMA_ONLY or FULL_PRODUCT")

    git_sha = evidence.get("git_sha", "")
    if not isinstance(git_sha, str) or len(git_sha) != 40 or any(
        c not in "0123456789abcdef" for c in git_sha
    ):
        errors.append("git_sha must be a lowercase 40-character SHA")

    ci = evidence.get("ci", {})
    for key in ("boundary", "python_compile", "frontend_validate"):
        if not _pass(ci.get(key)):
            errors.append(f"ci.{key} must be PASS")

    migrations = evidence.get("migrations", {})
    if migrations.get("plan_version") != PLAN_VERSION:
        errors.append("migration plan version mismatch")
    if not _pass(migrations.get("dry_run")):
        errors.append("migrations.dry_run must be PASS")
    if not _pass(migrations.get("applied")):
        errors.append("migrations.applied must be PASS")
    if migrations.get("canonical_data_applied") is not False:
        errors.append("canonical data must remain disabled in clean-seed phase")

    content = evidence.get("content", {})
    content_state = content.get("state")
    if content_state not in {
        "ADVANCED_CANONICAL_CONTENT_EMPTY",
        "ADVANCED_CANONICAL_CONTENT_FROZEN",
    }:
        errors.append("invalid content.state")

    if mode == "FULL_PRODUCT" and content_state != "ADVANCED_CANONICAL_CONTENT_FROZEN":
        errors.append("FULL_PRODUCT requires frozen Advanced canonical content")

    # Production stays impossible while this clean-seed contract says blocked.
    if target == "production":
        if contract.get("production_release") != "READY":
            errors.append(
                "production is blocked until the Advanced content/release contract is regenerated"
            )
        if mode != "FULL_PRODUCT":
            errors.append("production requires FULL_PRODUCT release mode")

    release_note = evidence.get("release_note", "")
    if not isinstance(release_note, str) or release_note.strip() in UNRESOLVED:
        errors.append("release_note must be recorded")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8-sig"))
    contract = json.loads(
        (
            args.repo_root
            / "config"
            / "stage26_operations_contract_v1.0.json"
        ).read_text(encoding="utf-8-sig")
    )
    errors = evaluate_evidence(evidence, contract)
    result = {"status": PASS if not errors else "FAIL", "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
