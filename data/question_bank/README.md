# Advanced Question Bank — v1.0

This package consolidates the Advanced question-bank batches from the project Google Drive into canonical lesson-level CSV files for `grammar-mastery-advanced`.

## Scope

- Active batches scanned and used: **130** (`ADV-B001` through `ADV-B130`)
- Raw question rows: **6,130**
- Unique valid questions written: **6,130**
- Lessons: **27**
- Exact duplicate rows removed: **0**
- Revision conflicts: **0**
- Invalid rows after required metadata normalization: **0**

Archived/legacy batch folders were not imported into the active bank. They were used only for version/history awareness.

## Canonical layout

- `lessons/ADV_L01_questions_v1.0.csv` … `lessons/ADV_L27_questions_v1.0.csv`
- `ADV_question_bank_manifest_v1.0.json`
- `ADV_question_bank_inventory_v1.0.csv`
- `ADV_question_bank_validation_report_v1.0.json`

Each lesson CSV uses the repository's frozen **46-column** canonical order from
`data/question_authoring/ADV_question_import_template_v1.0.csv`.

Questions are sorted deterministically by:

1. lesson sequence
2. canonical subtopic sequence
3. `external_id`
4. `question_revision`

No stem, option, answer key, explanation, difficulty label, or `source_ref` was rewritten.

## Metadata normalization

A current-contract version normalization was applied to **1,250** rows:

- `difficulty_model_version`: `ADV-DIFF-v1.0` → `ADV-DIFFICULTY-v1.0`

This changes metadata only. It is required to align those rows with the repository's current
`ADV_difficulty_plan_v1.0.json` / baseline version contract. The affected IDs and batches are
recorded in `ADV_question_bank_validation_report_v1.0.json`.

## Duplicate policy

No active rows share the same `external_id`, and no `(external_id, question_revision)` duplicates
exist. No non-identical row was automatically removed.

The final cumulative batch registry contains a small number of signature collisions. Potential
semantic duplicate candidates with different `external_id` values are retained and reported in
the validation report, following the conservative consolidation policy.

## Transformer compatibility

The current repository transformer is:

`ops/question_bank/transform_advanced_batch.py`

Current usage:

```bash
PYTHONPATH=. python ops/question_bank/transform_advanced_batch.py \
  data/question_bank/lessons/ADV_L01_questions_v1.0.csv \
  /tmp/ADV_L01_stage23_transport.csv \
  --repo-root .
```

In a clean direct-script invocation test, `PYTHONPATH=.` was required so Python could resolve
`src.backend.advanced_content`. If the project is installed as a package or your environment
already places the repository root on `sys.path`, an explicit `PYTHONPATH` may not be necessary.

All **27** lesson CSVs were passed through the current transformer logic successfully:
**6,130 / 6,130 rows transformed without schema/adapter errors**.

## Validation

The consolidation checked:

- exact 46-column header/order
- canonical lesson/subtopic IDs and codes
- subtopic parent relationship
- secondary-subtopic references
- question-type catalogue membership and compatibility
- four non-empty distinct options
- `correct_option`
- full/per-option explanations
- misconception foreign keys and correct-option misconception rule
- difficulty label/score bands
- locales
- canonical version fields
- source type and canonical `source_ref`
- active Batch package/validation/checkpoint consistency
- global ID uniqueness
- round-trip CSV parsing, UTF-8 encoding, quoting, and multiline fields
- lesson isolation and final count reconciliation
- compatibility with the current repository transformer

Final status: **PASS**.

## Reconciliation

`6,130 raw rows - 0 exact duplicates - 0 invalid rows = 6,130 unique valid questions`

`6,130 unique valid questions = 6,130 rows written`

Generated: `2026-09-06T02:31:06+00:00`
