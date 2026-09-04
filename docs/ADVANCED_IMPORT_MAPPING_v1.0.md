# Advanced canonical -> repository mapping v1.0

This document is the human-readable companion to
`data/advanced/v1.0/ADV_REPOSITORY_MAPPING_v1.0.json`.

## Boundary rule

Canonical Advanced data is immutable at integration time. Database-specific conversion is
performed by `src/backend/advanced_content/adapter.py`.

## Stable ID mapping

Namespace UUID: `2ff38ec0-7fd9-5f16-9864-8976e9a7ac06`

Examples:

- `lesson:ADV-L01` -> `1b38d180-a2d3-5814-a596-544d1739bc84`
- `subtopic:ADV-L01-ST01` -> `a360607b-45a2-5bd6-910f-d44da9d93b83`
- `misconception:ADV-L01-MC01` -> `0c566754-4424-5bee-bb8e-c7d531d1b110`

## Reference seed

Run a structural check without a database:

```bash
python ops/stage12/seed_advanced_reference.py --database-url postgresql://unused --dry-run
```

Apply to a database:

```bash
python ops/stage12/seed_advanced_reference.py --database-url "$DATABASE_URL"
```

## Transform a canonical question batch

```bash
python ops/question_bank/transform_advanced_batch.py \
  path/to/ADV_B001_questions_v1.0.csv \
  /tmp/ADV_B001_stage23.csv
```

The output remains the same frozen 46-column transport shape expected by Stage23, with
repository UUIDs/enums and Advanced version constants.
