from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from src.backend.advanced_content.canonical import load_all, repo_root, validate_reference_package
from src.backend.advanced_content.ids import stable_uuid

SEED_VERSION = "ADV-REFERENCE-SEED-v1.0"
TAXONOMY_VERSION = "ADV-TAXONOMY-v1.0"
QUESTION_TYPE_VERSION = "ADV-QTYPE-v1.0"
COMPATIBILITY_VERSION = "ADV-COMPAT-v1.0"
DIFFICULTY_VERSION = "ADV-DIFFICULTY-v1.0"
CONTENT_VERSION = "ADV-CONTENT-v1.0"
MISCONCEPTION_VERSION = "ADV-MISCONCEPTION-v1.0"

QUESTION_TYPE_FA = {
    "CLOZE_SINGLE": "جای‌خالی تک‌جمله‌ای",
    "CLOZE_CONTEXT": "جای‌خالی بافت‌دار",
    "CORRECT_SENTENCE": "تشخیص جملهٔ درست",
    "INCORRECT_SENTENCE": "تشخیص جملهٔ نادرست",
    "ERROR_LOCATION": "یافتن محل خطا",
    "CONJUGATION": "صرف فعل",
    "TENSE_CHOICE": "انتخاب زمان",
    "PRONOUN_CHOICE": "انتخاب ضمیر",
    "PREPOSITION_CHOICE": "انتخاب حرف اضافه",
    "REWRITE_EQUIV": "بازنویسی هم‌ارز",
    "FR_TO_FA": "فرانسه به فارسی",
    "FA_TO_FR": "فارسی به فرانسه",
    "DIALOGUE_COMPLETE": "تکمیل گفت‌وگو",
    "REGISTER_CHOICE": "انتخاب سطح زبانی",
    "CONTRAST_RULES": "تمایز میان قواعد",
}

COGNITIVE_LEVEL = {
    "CLOZE_SINGLE": "APPLICATION",
    "CLOZE_CONTEXT": "APPLICATION",
    "CORRECT_SENTENCE": "DISCRIMINATION",
    "INCORRECT_SENTENCE": "DISCRIMINATION",
    "ERROR_LOCATION": "DISCRIMINATION",
    "CONJUGATION": "APPLICATION",
    "TENSE_CHOICE": "APPLICATION",
    "PRONOUN_CHOICE": "APPLICATION",
    "PREPOSITION_CHOICE": "APPLICATION",
    "REWRITE_EQUIV": "APPLICATION",
    "FR_TO_FA": "APPLICATION",
    "FA_TO_FR": "APPLICATION",
    "DIALOGUE_COMPLETE": "APPLICATION",
    "REGISTER_CHOICE": "DISCRIMINATION",
    "CONTRAST_RULES": "DISCRIMINATION",
}

COMPAT_STATUS = {
    "RECOMMENDED": ("PREFERRED", 1.0),
    "COMPATIBLE": ("ALLOWED", 0.5),
    "NOT_COMPATIBLE": ("NOT_SUITABLE", 0.0),
}


def _pages(source_pages: dict[str, Any], prefix: str) -> str:
    first = source_pages.get(f"{prefix}_first")
    last = source_pages.get(f"{prefix}_last")
    if first is None:
        return ""
    return str(first) if first == last or last is None else f"{first}–{last}"


def _lesson_source_ref(lesson: dict[str, Any]) -> str:
    pages = lesson["source_pages"]
    return (
        f"Lesson {lesson['sequence']}; printed p. {_pages(pages, 'printed')}; "
        f"PDF p. {_pages(pages, 'pdf')}"
    )


def seed(conn: Any, root: Path) -> dict[str, int]:
    data = load_all(root)
    validate_reference_package(data)

    categories = data["categories"]["categories"]
    subcategories = data["subcategories"]["subcategories"]
    lessons = data["lessons"]["lessons"]
    subtopics = data["subtopics"]["subtopics"]
    tags = data["controlled_tags"]["tags"]
    lesson_tags = data["lesson_tags"]["mappings"]
    qtypes = data["question_types"]["types"]
    misconceptions = data["misconceptions"]["misconceptions"]
    compat_records = data["compatibility"]["records"]
    dependencies = data["dependencies"]["dependencies"]
    cross_refs = data["cross_references"]["records"]
    difficulty = data["difficulty_plan"]

    category_by_lesson = {
        row["lesson_id"]: row["category_id"]
        for row in data["lesson_category_mapping"]["mappings"]
    }
    subcategory_by_lesson = {
        row["lesson_id"]: row["subcategory_id"] for row in subcategories
    }
    lesson_by_id = {row["lesson_id"]: row for row in lessons}
    subtopic_by_id = {row["subtopic_id"]: row for row in subtopics}
    tag_by_token = {row["token"]: row for row in tags}

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO system_versions(component,version,status,source_ref,metadata)
            VALUES (%s,%s,'ACTIVE',%s,%s::jsonb)
            ON CONFLICT(component) DO UPDATE SET
              version=EXCLUDED.version,status=EXCLUDED.status,
              source_ref=EXCLUDED.source_ref,metadata=EXCLUDED.metadata
            """,
            (
                "advanced.reference_seed",
                SEED_VERSION,
                "data/advanced/v1.0/ADV_REPOSITORY_MAPPING_v1.0.json",
                '{"canonical_question_target":6130,"lesson_count":27,"subtopic_count":116}',
            ),
        )

        # Taxonomy: categories first, then lesson-shaped subcategories.
        for row in categories:
            cur.execute(
                """
                INSERT INTO grammar_categories(
                  id,code,slug,node_kind,parent_id,display_name_fr,display_name_fa,
                  membership_rule_fa,display_order,status,taxonomy_version
                ) VALUES (%s,%s,%s,'CATEGORY',NULL,%s,%s,%s,%s,'ACTIVE',%s)
                ON CONFLICT(id) DO UPDATE SET
                  code=EXCLUDED.code,slug=EXCLUDED.slug,display_name_fr=EXCLUDED.display_name_fr,
                  display_name_fa=EXCLUDED.display_name_fa,membership_rule_fa=EXCLUDED.membership_rule_fa,
                  display_order=EXCLUDED.display_order,status='ACTIVE',
                  taxonomy_version=EXCLUDED.taxonomy_version
                """,
                (
                    stable_uuid("category", row["category_id"]),
                    row["category_id"].replace("-", "_"),
                    row["category_id"].lower(),
                    row["title_fr"],
                    row.get("title_fa"),
                    "Technical Advanced site category; not an official book heading.",
                    row["sequence"],
                    TAXONOMY_VERSION,
                ),
            )

        for row in subcategories:
            cur.execute(
                """
                INSERT INTO grammar_categories(
                  id,code,slug,node_kind,parent_id,display_name_fr,display_name_fa,
                  membership_rule_fa,display_order,status,taxonomy_version
                ) VALUES (%s,%s,%s,'SUBCATEGORY',%s,%s,%s,%s,%s,'ACTIVE',%s)
                ON CONFLICT(id) DO UPDATE SET
                  code=EXCLUDED.code,slug=EXCLUDED.slug,parent_id=EXCLUDED.parent_id,
                  display_name_fr=EXCLUDED.display_name_fr,display_name_fa=EXCLUDED.display_name_fa,
                  membership_rule_fa=EXCLUDED.membership_rule_fa,
                  display_order=EXCLUDED.display_order,status='ACTIVE',
                  taxonomy_version=EXCLUDED.taxonomy_version
                """,
                (
                    stable_uuid("subcategory", row["subcategory_id"]),
                    row["subcategory_id"].replace("-", "_"),
                    row["subcategory_id"].lower(),
                    stable_uuid("category", row["category_id"]),
                    row["title_fr"],
                    row.get("title_fa"),
                    "Technical site subcategory aligned one-to-one with the canonical lesson.",
                    row["sequence"],
                    TAXONOMY_VERSION,
                ),
            )

        for row in lessons:
            pages = row["source_pages"]
            cur.execute(
                """
                INSERT INTO grammar_lessons(
                  id,lesson_no,title_fr_official,system_short_title,category_id,subcategory_id,
                  tcf_weight,book_pages,pdf_pages,source_ref,active,extraction_status,
                  content_version,taxonomy_version
                ) VALUES (%s,%s,%s,%s,%s,%s,0,%s,%s,%s,true,%s,%s,%s)
                ON CONFLICT(id) DO UPDATE SET
                  lesson_no=EXCLUDED.lesson_no,title_fr_official=EXCLUDED.title_fr_official,
                  system_short_title=EXCLUDED.system_short_title,category_id=EXCLUDED.category_id,
                  subcategory_id=EXCLUDED.subcategory_id,tcf_weight=0,
                  book_pages=EXCLUDED.book_pages,pdf_pages=EXCLUDED.pdf_pages,
                  source_ref=EXCLUDED.source_ref,active=true,
                  extraction_status=EXCLUDED.extraction_status,
                  content_version=EXCLUDED.content_version,taxonomy_version=EXCLUDED.taxonomy_version,
                  updated_at=now()
                """,
                (
                    stable_uuid("lesson", row["lesson_id"]),
                    row["sequence"],
                    row["title_fr"],
                    row["lesson_code"],
                    stable_uuid("category", category_by_lesson[row["lesson_id"]]),
                    stable_uuid("subcategory", subcategory_by_lesson[row["lesson_id"]]),
                    _pages(pages, "printed"),
                    _pages(pages, "pdf"),
                    _lesson_source_ref(row),
                    "CANONICAL_ADV_V1_VALIDATED",
                    row["content_version"],
                    row["taxonomy_version"],
                ),
            )

        content_by_subtopic: dict[str, dict[str, Any]] = {}
        for lesson in data["lesson_content"]["lessons"]:
            for item in lesson["subtopics"]:
                content_by_subtopic[item["subtopic_id"]] = item

        for row in subtopics:
            content = content_by_subtopic.get(row["subtopic_id"], {})
            pages = row["source_pages"]
            cur.execute(
                """
                INSERT INTO grammar_subtopics(
                  id,lesson_id,subtopic_code,title_fr,title_fa,short_definition_fa,teaching_note_fa,
                  exceptions_register_note,source_book_pages,source_pdf_pages,source_ref,source_basis,
                  translation_status,content_version,active
                ) VALUES (%s,%s,%s,%s,%s,NULL,%s,%s,%s,%s,%s,%s,%s,%s,true)
                ON CONFLICT(id) DO UPDATE SET
                  lesson_id=EXCLUDED.lesson_id,subtopic_code=EXCLUDED.subtopic_code,
                  title_fr=EXCLUDED.title_fr,title_fa=EXCLUDED.title_fa,
                  teaching_note_fa=EXCLUDED.teaching_note_fa,
                  exceptions_register_note=EXCLUDED.exceptions_register_note,
                  source_book_pages=EXCLUDED.source_book_pages,source_pdf_pages=EXCLUDED.source_pdf_pages,
                  source_ref=EXCLUDED.source_ref,source_basis=EXCLUDED.source_basis,
                  translation_status=EXCLUDED.translation_status,content_version=EXCLUDED.content_version,
                  active=true
                """,
                (
                    stable_uuid("subtopic", row["subtopic_id"]),
                    stable_uuid("lesson", row["lesson_id"]),
                    row["subtopic_code"],
                    row["title_fr"],
                    row.get("title_fa"),
                    content.get("teaching_note_fa"),
                    content.get("learner_trap_fa"),
                    _pages(pages, "printed"),
                    _pages(pages, "pdf"),
                    row["source_ref"],
                    "ADV_CANONICAL_BOOK_DERIVED",
                    "PROJECT_TRANSLATION_V1",
                    row["content_version"],
                ),
            )

        for row in tags:
            cur.execute(
                """
                INSERT INTO tags(
                  id,code,slug,tag_group,display_name_fr,display_name_fa,
                  membership_rule_fa,status,taxonomy_version
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,'ACTIVE',%s)
                ON CONFLICT(id) DO UPDATE SET
                  code=EXCLUDED.code,slug=EXCLUDED.slug,tag_group=EXCLUDED.tag_group,
                  display_name_fr=EXCLUDED.display_name_fr,display_name_fa=EXCLUDED.display_name_fa,
                  membership_rule_fa=EXCLUDED.membership_rule_fa,status='ACTIVE',
                  taxonomy_version=EXCLUDED.taxonomy_version
                """,
                (
                    stable_uuid("tag", row["tag_id"]),
                    row["tag_id"].replace("-", "_"),
                    row["token"],
                    row.get("scope"),
                    row["label_fr"],
                    row.get("label_fa"),
                    "Controlled Advanced tag. Exact token is the runtime membership key.",
                    TAXONOMY_VERSION,
                ),
            )

        for order, row in enumerate(lesson_tags, start=1):
            tag = tag_by_token[row["tag_token"]]
            cur.execute(
                """
                INSERT INTO lesson_tags(lesson_id,tag_id,assignment_order,assignment_basis,taxonomy_version)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT(lesson_id,tag_id) DO UPDATE SET
                  assignment_order=EXCLUDED.assignment_order,
                  assignment_basis=EXCLUDED.assignment_basis,
                  taxonomy_version=EXCLUDED.taxonomy_version
                """,
                (
                    stable_uuid("lesson", row["lesson_id"]),
                    stable_uuid("tag", tag["tag_id"]),
                    order,
                    row.get("mapping_basis"),
                    TAXONOMY_VERSION,
                ),
            )

        for row in qtypes:
            token = row["question_type"]
            cur.execute(
                """
                INSERT INTO question_types(
                  id,code,name_fa,system_name_en,cognitive_level,response_mode,active,catalogue_version
                ) VALUES (%s,%s,%s,%s,%s,'SINGLE_CHOICE_4',true,%s)
                ON CONFLICT(id) DO UPDATE SET
                  code=EXCLUDED.code,name_fa=EXCLUDED.name_fa,system_name_en=EXCLUDED.system_name_en,
                  cognitive_level=EXCLUDED.cognitive_level,response_mode='SINGLE_CHOICE_4',
                  active=true,catalogue_version=EXCLUDED.catalogue_version
                """,
                (
                    stable_uuid("question_type", token),
                    token,
                    QUESTION_TYPE_FA[token],
                    token,
                    COGNITIVE_LEVEL[token],
                    QUESTION_TYPE_VERSION,
                ),
            )

        for row in misconceptions:
            cur.execute(
                """
                INSERT INTO misconceptions(
                  id,subtopic_id,family,name_fa,statement_fa,diagnostic_interpretation_fa,
                  distractor_authoring_hint_fa,priority,status,empirical_commonness,
                  catalogue_version,source_ref
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVE',NULL,%s,%s)
                ON CONFLICT(id) DO UPDATE SET
                  subtopic_id=EXCLUDED.subtopic_id,family=EXCLUDED.family,name_fa=EXCLUDED.name_fa,
                  statement_fa=EXCLUDED.statement_fa,
                  diagnostic_interpretation_fa=EXCLUDED.diagnostic_interpretation_fa,
                  distractor_authoring_hint_fa=EXCLUDED.distractor_authoring_hint_fa,
                  priority=EXCLUDED.priority,status='ACTIVE',
                  catalogue_version=EXCLUDED.catalogue_version,source_ref=EXCLUDED.source_ref
                """,
                (
                    stable_uuid("misconception", row["misconception_id"]),
                    stable_uuid("subtopic", row["home_subtopic_id"]),
                    lesson_by_id[row["lesson_id"]]["lesson_code"],
                    f"{subtopic_by_id[row['home_subtopic_id']]['title_fa']} — خطای اصلی",
                    row["description"],
                    row.get("diagnostic_interpretation"),
                    row.get("distractor_authoring_hint"),
                    row.get("priority"),
                    MISCONCEPTION_VERSION,
                    row.get("source_ref"),
                ),
            )

        actors = [
            ("openai-gpt-5.6-sol", "AI_GENERATOR", "OpenAI GPT-5.6 Sol — ADV authoring"),
            ("openai-gpt-5.6-sol-qa", "REVIEWER", "OpenAI GPT-5.6 Sol — ADV QA"),
        ]
        for external_id, actor_type, display_name in actors:
            cur.execute(
                """
                INSERT INTO actors(id,external_actor_id,actor_type,display_name,active)
                VALUES (%s,%s,%s,%s,true)
                ON CONFLICT(id) DO UPDATE SET
                  external_actor_id=EXCLUDED.external_actor_id,actor_type=EXCLUDED.actor_type,
                  display_name=EXCLUDED.display_name,active=true
                """,
                (stable_uuid("actor", external_id), external_id, actor_type, display_name),
            )

        # Preserve source-derived cross references exactly as directed pairs.
        for row in cross_refs:
            cur.execute(
                """
                INSERT INTO lesson_related_references(
                  relation_id,lesson_id,related_lesson_id,relation_type,strength,
                  evidence_type,status,note_fa
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT(relation_id) DO UPDATE SET
                  lesson_id=EXCLUDED.lesson_id,related_lesson_id=EXCLUDED.related_lesson_id,
                  relation_type=EXCLUDED.relation_type,strength=EXCLUDED.strength,
                  evidence_type=EXCLUDED.evidence_type,status=EXCLUDED.status,note_fa=EXCLUDED.note_fa
                """,
                (
                    stable_uuid("related_reference", row["cross_reference_id"]),
                    stable_uuid("lesson", row["lesson_a_id"]),
                    stable_uuid("lesson", row["lesson_b_id"]),
                    row["relation_type"],
                    3,
                    row.get("source_basis"),
                    "ACTIVE",
                    "Book-derived related-topic record; direction preserved from canonical source map.",
                ),
            )

        # Technical dependencies are intentionally NOT inserted into lesson_prerequisites:
        # canonical records explicitly say is_book_declared_prerequisite=false.
        for row in dependencies:
            cur.execute(
                """
                INSERT INTO lesson_related_references(
                  relation_id,lesson_id,related_lesson_id,relation_type,strength,
                  evidence_type,status,note_fa
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT(relation_id) DO UPDATE SET
                  lesson_id=EXCLUDED.lesson_id,related_lesson_id=EXCLUDED.related_lesson_id,
                  relation_type=EXCLUDED.relation_type,strength=EXCLUDED.strength,
                  evidence_type=EXCLUDED.evidence_type,status=EXCLUDED.status,note_fa=EXCLUDED.note_fa
                """,
                (
                    stable_uuid("related_reference", row["dependency_id"]),
                    stable_uuid("lesson", row["from_lesson_id"]),
                    stable_uuid("lesson", row["to_lesson_id"]),
                    f"TECHNICAL_{row['relation_type']}",
                    5 if row["relation_type"] == "STRONG_SUPPORT" else 3,
                    row.get("basis"),
                    row.get("status"),
                    "Application-derived support edge; not a book-declared prerequisite.",
                ),
            )

        # Subtopic compatibility.
        for record in compat_records:
            for item in record["compatibility_by_type"]:
                status, factor = COMPAT_STATUS[item["status"]]
                type_id = stable_uuid("question_type", item["question_type"])
                cur.execute(
                    """
                    INSERT INTO subtopic_question_type_compatibility(
                      id,subtopic_id,question_type_id,compatibility_status,allocation_factor,
                      conditional_guardrail_required,guardrail_text,compatibility_version
                    ) VALUES (%s,%s,%s,%s,%s,false,%s,%s)
                    ON CONFLICT(subtopic_id,question_type_id,compatibility_version) DO UPDATE SET
                      compatibility_status=EXCLUDED.compatibility_status,
                      allocation_factor=EXCLUDED.allocation_factor,
                      conditional_guardrail_required=false,
                      guardrail_text=EXCLUDED.guardrail_text
                    """,
                    (
                        stable_uuid(
                            "subtopic_qtype_compat",
                            f"{record['subtopic_id']}:{item['question_type']}",
                        ),
                        stable_uuid("subtopic", record["subtopic_id"]),
                        type_id,
                        status,
                        factor,
                        item.get("rationale"),
                        COMPATIBILITY_VERSION,
                    ),
                )

        # Aggregate lesson compatibility from canonical subtopics.
        grouped: dict[tuple[str, str], list[str]] = {}
        for record in compat_records:
            for item in record["compatibility_by_type"]:
                grouped.setdefault(
                    (record["lesson_id"], item["question_type"]), []
                ).append(item["status"])
        rank = {"NOT_COMPATIBLE": 0, "COMPATIBLE": 1, "RECOMMENDED": 2}
        for (lesson_id, qtype), statuses in grouped.items():
            best = max(statuses, key=rank.__getitem__)
            status, factor = COMPAT_STATUS[best]
            cur.execute(
                """
                INSERT INTO lesson_question_type_compatibility(
                  id,lesson_id,question_type_id,compatibility_status,allocation_factor,
                  conditional_guardrail_required,rationale,compatibility_version
                ) VALUES (%s,%s,%s,%s,%s,false,%s,%s)
                ON CONFLICT(lesson_id,question_type_id,compatibility_version) DO UPDATE SET
                  compatibility_status=EXCLUDED.compatibility_status,
                  allocation_factor=EXCLUDED.allocation_factor,
                  conditional_guardrail_required=false,rationale=EXCLUDED.rationale
                """,
                (
                    stable_uuid("lesson_qtype_compat", f"{lesson_id}:{qtype}"),
                    stable_uuid("lesson", lesson_id),
                    stable_uuid("question_type", qtype),
                    status,
                    factor,
                    "Derived as the strongest canonical subtopic compatibility within the lesson.",
                    COMPATIBILITY_VERSION,
                ),
            )

        # Full-bank targets. No separate MVP/expanded canonical tiers exist, so all
        # three physical columns are set equal to the source-backed full target.
        for row in qtypes:
            target = int(row["global_target"])
            cur.execute(
                """
                INSERT INTO question_type_global_targets(
                  question_type_id,policy_version,target_full,target_expanded,target_mvp
                ) VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT(question_type_id,policy_version) DO UPDATE SET
                  target_full=EXCLUDED.target_full,target_expanded=EXCLUDED.target_expanded,
                  target_mvp=EXCLUDED.target_mvp
                """,
                (
                    stable_uuid("question_type", row["question_type"]),
                    QUESTION_TYPE_VERSION,
                    target, target, target,
                ),
            )

        for row in lessons:
            target = int(row["target_question_count"])
            cur.execute(
                """
                INSERT INTO lesson_capacity_targets(
                  lesson_id,capacity_model_version,target_full,target_expanded,target_mvp
                ) VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT(lesson_id,capacity_model_version) DO UPDATE SET
                  target_full=EXCLUDED.target_full,target_expanded=EXCLUDED.target_expanded,
                  target_mvp=EXCLUDED.target_mvp
                """,
                (
                    stable_uuid("lesson", row["lesson_id"]),
                    "ADV-CAPACITY-v1.0",
                    target, target, target,
                ),
            )

        props = difficulty["global_target"]["proportions"]
        profile_code = "ADV_GLOBAL_20_40_30_10"
        cur.execute(
            """
            INSERT INTO difficulty_profiles(
              profile_code,easy_pct,medium_pct,hard_pct,very_hard_pct,policy_version
            ) VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT(profile_code) DO UPDATE SET
              easy_pct=EXCLUDED.easy_pct,medium_pct=EXCLUDED.medium_pct,
              hard_pct=EXCLUDED.hard_pct,very_hard_pct=EXCLUDED.very_hard_pct,
              policy_version=EXCLUDED.policy_version
            """,
            (
                profile_code, props["EASY"], props["MEDIUM"],
                props["HARD"], props["VERY_HARD"], DIFFICULTY_VERSION,
            ),
        )

        for row in difficulty["lesson_targets"]:
            counts = row["counts"]
            target = int(row["target"])
            cur.execute(
                """
                INSERT INTO lesson_difficulty_targets(
                  lesson_id,policy_version,profile_code,target_full,easy_full,medium_full,
                  hard_full,very_hard_full,target_expanded,target_mvp,rationale
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT(lesson_id,policy_version) DO UPDATE SET
                  profile_code=EXCLUDED.profile_code,target_full=EXCLUDED.target_full,
                  easy_full=EXCLUDED.easy_full,medium_full=EXCLUDED.medium_full,
                  hard_full=EXCLUDED.hard_full,very_hard_full=EXCLUDED.very_hard_full,
                  target_expanded=EXCLUDED.target_expanded,target_mvp=EXCLUDED.target_mvp,
                  rationale=EXCLUDED.rationale
                """,
                (
                    stable_uuid("lesson", row["lesson_id"]),
                    DIFFICULTY_VERSION,
                    profile_code,
                    target,
                    counts["EASY"], counts["MEDIUM"], counts["HARD"], counts["VERY_HARD"],
                    target, target,
                    "Canonical ADV difficulty allocation: 20% EASY, 40% MEDIUM, 30% HARD, 10% VERY_HARD.",
                ),
            )

        total = int(difficulty["global_target"]["total"])
        cur.execute(
            """
            INSERT INTO bank_targets(
              target_key,target_scope,target_full,target_expanded,target_mvp,policy_version,note
            ) VALUES ('ADV-QB','GLOBAL',%s,%s,%s,%s,%s)
            ON CONFLICT(target_key,target_scope,policy_version) DO UPDATE SET
              target_full=EXCLUDED.target_full,target_expanded=EXCLUDED.target_expanded,
              target_mvp=EXCLUDED.target_mvp,note=EXCLUDED.note
            """,
            (
                total, total, total, "ADV-BANK-TARGET-v1.0",
                "Canonical Advanced target. No separate MVP/expanded tier is source-defined.",
            ),
        )

        # Deliberate non-seed: lesson_weight_versions. The Advanced canonical
        # package does not contain verified TCF lesson weights.
        cur.execute(
            """
            INSERT INTO project_decisions(
              decision_code,scope,status,decision_fa,impact,owner,upstream_stage
            ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT(decision_code) DO UPDATE SET
              scope=EXCLUDED.scope,status=EXCLUDED.status,decision_fa=EXCLUDED.decision_fa,
              impact=EXCLUDED.impact,owner=EXCLUDED.owner,upstream_stage=EXCLUDED.upstream_stage
            """,
            (
                "ADV_NO_TCF_WEIGHT_INVENTION_V1",
                "ADV_REFERENCE_SEED",
                "ACCEPTED_TECHNICAL_GUARDRAIL",
                "برای درس‌های کتاب Advanced وزن TCF تأییدشده در منبع canonical وجود ندارد؛ tcf_weight برابر صفر نگه داشته می‌شود و lesson_weight_versions ساخته نمی‌شود.",
                "Prevents fabricated TCF weighting while preserving the existing physical schema.",
                "Iman",
                12,
            ),
        )

    return {
        "categories": len(categories),
        "subcategories": len(subcategories),
        "lessons": len(lessons),
        "subtopics": len(subtopics),
        "tags": len(tags),
        "lesson_tags": len(lesson_tags),
        "question_types": len(qtypes),
        "misconceptions": len(misconceptions),
        "subtopic_compatibility": len(compat_records) * len(qtypes),
        "cross_references": len(cross_refs),
        "technical_dependencies_as_related": len(dependencies),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed canonical Advanced reference data.")
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--repo-root", type=Path, default=repo_root())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = load_all(args.repo_root)
    validate_reference_package(data)
    if args.dry_run:
        print("PASS: Advanced canonical reference package validated.")
        return

    import psycopg

    with psycopg.connect(args.database_url) as conn:
        counts = seed(conn, args.repo_root)
        conn.commit()
    print("PASS: Advanced canonical reference seed applied.")
    for key, value in counts.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
