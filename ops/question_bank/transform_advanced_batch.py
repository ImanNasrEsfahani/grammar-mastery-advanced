from __future__ import annotations

import argparse
from pathlib import Path

from src.backend.advanced_content.adapter import transform_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adapt a canonical ADV 46-column question CSV to the repository Stage23 transport contract."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args()
    count = transform_csv(args.source, args.destination, args.repo_root)
    print(f"PASS: adapted {count} question rows -> {args.destination}")


if __name__ == "__main__":
    main()
