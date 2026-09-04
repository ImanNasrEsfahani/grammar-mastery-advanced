#!/usr/bin/env python3
"""Advanced seed PostgreSQL schema migration runner.

Dry-run by default. It never seeds lesson/taxonomy/question content.
Production execution is deliberately blocked until the Advanced canonical
content and the production release contract are regenerated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_contract(repo_root: Path) -> dict:
    path = repo_root / "config" / "stage26_operations_contract_v1.0.json"
    return json.loads(path.read_text(encoding="utf-8-sig"))


def verify_plan(repo_root: Path, contract: dict) -> list[str]:
    errors: list[str] = []
    policy = contract["migration_policy"]
    sequence = policy["canonical_sequence"]

    orders = [row["order"] for row in sequence]
    if orders != list(range(1, len(sequence) + 1)):
        errors.append("migration order is not contiguous")

    canonical_paths = {row["path"] for row in sequence}

    for forbidden in policy.get("superseded_files_forbidden", []):
        if forbidden in canonical_paths:
            errors.append(f"superseded migration is canonical: {forbidden}")
        if (repo_root / forbidden).exists():
            errors.append(
                f"superseded migration is still present and must be deleted: {forbidden}"
            )

    for row in sequence:
        path = repo_root / row["path"]
        if not path.is_file():
            errors.append(f"missing migration: {row['path']}")
            continue
        actual = git_blob_sha(path)
        if actual != row["git_blob_sha"]:
            errors.append(f"migration identity mismatch: {row['path']}")

    if contract.get("canonical_data_bootstrap_policy", {}).get("enabled") is not False:
        errors.append("Advanced seed must not enable canonical data bootstrap yet")

    return errors


def connection_configured() -> bool:
    return bool(
        os.getenv("PGSERVICE")
        or (os.getenv("PGHOST") and os.getenv("PGDATABASE") and os.getenv("PGUSER"))
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument(
        "--target",
        choices=["development", "staging", "production"],
        required=True,
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually invoke psql. Default is verification/dry-run only.",
    )
    parser.add_argument("--confirm-release-id", default="")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    contract = load_contract(root)
    errors = verify_plan(root, contract)

    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
        return 2

    sequence = contract["migration_policy"]["canonical_sequence"]

    if args.target == "production":
        payload = {
            "status": "BLOCKED",
            "target": "production",
            "reason": contract.get(
                "production_release",
                "BLOCKED_UNTIL_ADVANCED_CANONICAL_CONTENT_FROZEN",
            ),
        }
        print(json.dumps(payload, indent=2))
        return 2

    if not args.execute:
        print(
            json.dumps(
                {
                    "status": "DRY_RUN",
                    "target": args.target,
                    "plan_version": contract["migration_policy"]["plan_version"],
                    "schema_only": True,
                    "files": [row["path"] for row in sequence],
                    "canonical_data": "DISABLED",
                },
                indent=2,
            )
        )
        return 0

    if not args.confirm_release_id.strip():
        print(
            "Refusing execution: --confirm-release-id is required",
            file=sys.stderr,
        )
        return 2

    if not connection_configured():
        print(
            "Refusing execution: configure PGSERVICE or PGHOST/PGDATABASE/PGUSER "
            "through runtime secret injection.",
            file=sys.stderr,
        )
        return 2

    for row in sequence:
        migration = root / row["path"]
        completed = subprocess.run(
            ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-f", str(migration)],
            cwd=root,
            check=False,
        )
        if completed.returncode != 0:
            print(
                json.dumps(
                    {
                        "status": "FAIL",
                        "failed_migration": row["path"],
                        "release_id": args.confirm_release_id,
                    },
                    indent=2,
                )
            )
            return completed.returncode or 2

    print(
        json.dumps(
            {
                "status": "PASS",
                "target": args.target,
                "release_id": args.confirm_release_id,
                "plan_version": contract["migration_policy"]["plan_version"],
                "schema_only": True,
                "canonical_data": "NOT_APPLIED",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
