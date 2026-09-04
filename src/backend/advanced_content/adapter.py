from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable

from .canonical import load_all, repo_root, validate_reference_package
from .ids import stable_uuid

CANONICAL_SCHEMA_VERSION = "ADV-QB-SCHEMA-v1.0"
TRANSPORT_SCHEMA_VERSION = "ADV-QB-IMPORT-v1.0"
TAXONOMY_VERSION = "ADV-TAXONOMY-v1.0"
QUESTION_TYPE_VERSION = "ADV-QTYPE-v1.0"
COMPATIBILITY_VERSION = "ADV-COMPAT-v1.0"
DISTRACTOR_VERSION = "ADV-DISTRACTOR-v1.0"

EXPECTED_COLUMNS = (
    "schema_version", "external_id", "question_revision", "lesson_id", "lesson_code",
    "subtopic_id", "subtopic_code", "secondary_subtopic_ids", "question_type", "stem",
    "stem_locale", "option_a", "option_b", "option_c", "option_d", "option_locale",
    "correct_option", "full_explanation", "explanation_a", "explanation_b",
    "explanation_c", "explanation_d", "explanation_locale", "misconception_a_id",
    "misconception_b_id", "misconception_c_id", "misconception_d_id", "difficulty",
    "difficulty_score_initial", "difficulty_model_version", "status", "source_type",
    "source_ref", "author_id", "reviewer_id", "tags", "media_type", "media_uri",
    "media_alt_text", "media_transcript", "media_source_ref", "taxonomy_version",
    "question_type_catalogue_version", "compatibility_version", "distractor_rules_version",
    "content_version",
)

LOCALE_MAP = {"fr": "fr-FR", "fa": "fa-IR", "fr-FR": "fr-FR", "fa-IR": "fa-IR"}
SOURCE_TYPE_MAP = {
    "BOOK_RULE_DERIVED": "PROJECT_SYNTHETIC_FROM_RULE",
    "BOOK_RULE_DERIVED_ORIGINAL": "PROJECT_SYNTHETIC_FROM_RULE",
    "BOOK_RULE_PLUS_SUPPORT_CONFIRMED": "EXTERNAL_REVIEWED",
    # Accepted only for already-adapted rows.
    "PROJECT_SYNTHETIC_FROM_RULE": "PROJECT_SYNTHETIC_FROM_RULE",
    "EXTERNAL_REVIEWED": "EXTERNAL_REVIEWED",
    "BOOK_DIRECT": "BOOK_DIRECT",
}


def _canonical_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


class AdvancedLookup:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or repo_root()
        self.data = load_all(self.root)
        validate_reference_package(self.data)

        self.lessons = {row["lesson_id"]: row for row in self.data["lessons"]["lessons"]}
        self.subtopics = {row["subtopic_id"]: row for row in self.data["subtopics"]["subtopics"]}
        self.misconceptions = {
            row["misconception_id"]: row
            for row in self.data["misconceptions"]["misconceptions"]
        }

        tag_rows = self.data["controlled_tags"]["tags"]
        self.controlled_tokens = {row["token"] for row in tag_rows}
        self.tag_aliases: dict[str, str] = {}
        for row in tag_rows:
            token = row["token"]
            for raw in (token, row.get("label_fr"), row.get("label_fa")):
                if raw:
                    self.tag_aliases[_canonical_text(raw)] = token
            # Conservative singular/plural bridge for obvious ASCII technical tokens.
            if token.endswith("s"):
                self.tag_aliases.setdefault(_canonical_text(token[:-1]), token)

        self.lesson_tags: dict[str, list[str]] = {}
        for row in self.data["lesson_tags"]["mappings"]:
            self.lesson_tags.setdefault(row["lesson_id"], []).append(row["tag_token"])

    def lesson_uuid(self, stable_id: str) -> str:
        if stable_id not in self.lessons:
            raise ValueError(f"Unknown canonical lesson ID: {stable_id}")
        return stable_uuid("lesson", stable_id)

    def subtopic_uuid(self, stable_id: str) -> str:
        if stable_id not in self.subtopics:
            raise ValueError(f"Unknown canonical subtopic ID: {stable_id}")
        return stable_uuid("subtopic", stable_id)

    def misconception_uuid(self, stable_id: str) -> str:
        if not stable_id:
            return ""
        if stable_id not in self.misconceptions:
            raise ValueError(f"Unknown canonical misconception ID: {stable_id}")
        return stable_uuid("misconception", stable_id)

    def actor_uuid(self, actor_id: str) -> str:
        if not actor_id:
            return ""
        return stable_uuid("actor", actor_id)

    def normalize_tags(self, raw_value: Any, lesson_id: str) -> str:
        if isinstance(raw_value, list):
            raw_tags = raw_value
        else:
            text = str(raw_value or "").strip()
            if not text:
                raw_tags = []
            elif text.startswith("["):
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid canonical tags JSON: {text}") from exc
                raw_tags = parsed if isinstance(parsed, list) else []
            else:
                raw_tags = [part for part in text.split("|") if part]

        selected: list[str] = []
        seen: set[str] = set()
        for raw in [*raw_tags, *self.lesson_tags.get(lesson_id, [])]:
            key = _canonical_text(raw)
            token = self.tag_aliases.get(key)
            if token and token not in seen:
                seen.add(token)
                selected.append(token)
        return "|".join(selected)


def _parse_secondary(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    if text.startswith("["):
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise ValueError("secondary_subtopic_ids must be a JSON array in canonical rows")
        return [str(item).strip() for item in parsed if str(item).strip()]
    return [part.strip() for part in text.split("|") if part.strip()]


def _difficulty_score(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    score = float(text)
    if 0.0 <= score <= 1.0:
        return f"{1.0 + 3.0 * score:.2f}".rstrip("0").rstrip(".")
    # Idempotent support for rows already transformed to the physical 1..4 contract.
    if 1.0 <= score <= 4.0:
        return f"{score:.2f}".rstrip("0").rstrip(".")
    raise ValueError(f"difficulty_score_initial outside canonical/transport range: {text}")


def adapt_row(row: dict[str, Any], lookups: AdvancedLookup) -> dict[str, str]:
    if str(row.get("schema_version", "")).strip() not in {
        CANONICAL_SCHEMA_VERSION, TRANSPORT_SCHEMA_VERSION
    }:
        raise ValueError(f"Unsupported canonical schema_version: {row.get('schema_version')!r}")

    lesson_stable = str(row.get("lesson_id", "")).strip()
    subtopic_stable = str(row.get("subtopic_id", "")).strip()
    if lesson_stable not in lookups.lessons:
        raise ValueError(f"Unknown lesson_id {lesson_stable}")
    if subtopic_stable not in lookups.subtopics:
        raise ValueError(f"Unknown subtopic_id {subtopic_stable}")
    if lookups.subtopics[subtopic_stable]["lesson_id"] != lesson_stable:
        raise ValueError(f"Subtopic {subtopic_stable} does not belong to {lesson_stable}")

    out = {name: str(row.get(name, "") or "").strip() for name in EXPECTED_COLUMNS}
    out["schema_version"] = TRANSPORT_SCHEMA_VERSION
    out["lesson_id"] = lookups.lesson_uuid(lesson_stable)
    out["subtopic_id"] = lookups.subtopic_uuid(subtopic_stable)
    out["secondary_subtopic_ids"] = "|".join(
        lookups.subtopic_uuid(stable_id) for stable_id in _parse_secondary(row.get("secondary_subtopic_ids"))
    )

    for key in "abcd":
        field = f"misconception_{key}_id"
        out[field] = lookups.misconception_uuid(str(row.get(field, "") or "").strip())

    for field in ("stem_locale", "option_locale", "explanation_locale"):
        raw_locale = str(row.get(field, "") or "").strip()
        if raw_locale not in LOCALE_MAP:
            raise ValueError(f"Unsupported {field}: {raw_locale!r}")
        out[field] = LOCALE_MAP[raw_locale]

    out["difficulty_score_initial"] = _difficulty_score(row.get("difficulty_score_initial"))
    out["status"] = "DRAFT"

    source_type = str(row.get("source_type", "") or "").strip()
    if source_type not in SOURCE_TYPE_MAP:
        raise ValueError(f"Unsupported canonical source_type: {source_type!r}")
    out["source_type"] = SOURCE_TYPE_MAP[source_type]

    out["author_id"] = lookups.actor_uuid(str(row.get("author_id", "") or "").strip())
    out["reviewer_id"] = lookups.actor_uuid(str(row.get("reviewer_id", "") or "").strip())
    out["tags"] = lookups.normalize_tags(row.get("tags"), lesson_stable)
    out["media_type"] = str(row.get("media_type", "") or "").strip().upper() or "NONE"

    out["taxonomy_version"] = TAXONOMY_VERSION
    out["question_type_catalogue_version"] = QUESTION_TYPE_VERSION
    out["compatibility_version"] = COMPATIBILITY_VERSION
    out["distractor_rules_version"] = DISTRACTOR_VERSION

    return out


def transform_csv(source: Path, destination: Path, repo: Path | None = None) -> int:
    lookups = AdvancedLookup(repo)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
            raise ValueError("Canonical CSV does not have the exact frozen 46-column order")
        rows = [adapt_row(dict(row), lookups) for row in reader]

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
