from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EXPECTED_COUNTS = {
    "lessons": 27,
    "subtopics": 116,
    "categories": 8,
    "subcategories": 27,
    "controlled_tags": 58,
    "lesson_tags": 98,
    "misconceptions": 116,
    "question_types": 15,
    "compatibility_records": 116,
    "dependencies": 43,
    "cross_references": 68,
    "review_sections": 8,
    "non_lesson_sections": 12,
}

FILES = {
    "lessons": "data/knowledge/ADV_lessons_v1.0.json",
    "subtopics": "data/knowledge/ADV_subtopics_v1.0.json",
    "source_map": "data/knowledge/ADV_source_map_v1.0.json",
    "dependencies": "data/knowledge/ADV_dependencies_v1.0.json",
    "cross_references": "data/knowledge/ADV_cross_references_v1.0.json",
    "sections": "data/knowledge/ADV_sections_v1.0.json",
    "non_lesson_sections": "data/knowledge/ADV_non_lesson_sections_v1.0.json",
    "categories": "data/taxonomy/ADV_categories_v1.0.json",
    "subcategories": "data/taxonomy/ADV_subcategories_v1.0.json",
    "controlled_tags": "data/taxonomy/ADV_controlled_tags_v1.0.json",
    "lesson_category_mapping": "data/taxonomy/ADV_lesson_category_mapping_v1.0.json",
    "lesson_tags": "data/taxonomy/ADV_lesson_tags_v1.0.json",
    "misconceptions": "data/question_authoring/ADV_misconceptions_v1.0.json",
    "question_types": "data/question_authoring/ADV_question_type_catalogue_v1.0.json",
    "compatibility": "data/question_authoring/ADV_question_type_compatibility_v1.0.json",
    "difficulty_plan": "data/planning/ADV_difficulty_plan_v1.0.json",
    "lesson_content": "data/product/ADV_lesson_content_v1.0.json",
    "review_map": "data/product/ADV_review_map_v1.0.json",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_json(key: str, root: Path | None = None) -> dict[str, Any]:
    root = root or repo_root()
    rel = FILES[key]
    path = root / rel
    if not path.is_file():
        raise FileNotFoundError(f"Advanced canonical file missing: {rel}")
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {rel}")
    return value


def load_all(root: Path | None = None) -> dict[str, dict[str, Any]]:
    return {key: load_json(key, root) for key in FILES}


def validate_reference_package(data: dict[str, dict[str, Any]]) -> None:
    checks = {
        "lessons": len(data["lessons"]["lessons"]),
        "subtopics": len(data["subtopics"]["subtopics"]),
        "categories": len(data["categories"]["categories"]),
        "subcategories": len(data["subcategories"]["subcategories"]),
        "controlled_tags": len(data["controlled_tags"]["tags"]),
        "lesson_tags": len(data["lesson_tags"]["mappings"]),
        "misconceptions": len(data["misconceptions"]["misconceptions"]),
        "question_types": len(data["question_types"]["types"]),
        "compatibility_records": len(data["compatibility"]["records"]),
        "dependencies": len(data["dependencies"]["dependencies"]),
        "cross_references": len(data["cross_references"]["records"]),
        "review_sections": len(data["sections"]["sections"]),
        "non_lesson_sections": len(data["non_lesson_sections"]["sections"]),
    }
    for key, actual in checks.items():
        expected = EXPECTED_COUNTS[key]
        if actual != expected:
            raise ValueError(f"{key} count mismatch: expected {expected}, got {actual}")

    lessons = {row["lesson_id"] for row in data["lessons"]["lessons"]}
    subtopics = {row["subtopic_id"]: row["lesson_id"] for row in data["subtopics"]["subtopics"]}
    if len(lessons) != 27 or len(subtopics) != 116:
        raise ValueError("Duplicate lesson/subtopic stable IDs detected")
    for subtopic_id, lesson_id in subtopics.items():
        if lesson_id not in lessons:
            raise ValueError(f"{subtopic_id} references unknown lesson {lesson_id}")
