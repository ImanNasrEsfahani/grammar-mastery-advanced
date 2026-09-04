# Advanced Bootstrap Status

The Advanced repository intentionally has no canonical lesson/taxonomy/question
data yet.

## What is available now

- Reusable application/runtime core.
- A schema-only PostgreSQL migration plan.
- A fail-closed release gate.
- Empty versioned Advanced data scaffolding.

## What is intentionally disabled

- Intermediate canonical reference seed.
- Intermediate Question Bank bootstrap/publication.
- Production release of this Advanced instance.

Those pieces must be regenerated after the new Advanced book has completed the
content pipeline.

## Safe schema workflow

Dry-run/verify:

```bash
python ops/stage26/migration_runner.py --target staging
```

Apply only to a dedicated development/staging PostgreSQL after PG connection
variables are injected:

```bash
python ops/stage26/migration_runner.py \
  --target staging \
  --execute \
  --confirm-release-id advanced-schema-001
```

The runner applies only the explicitly pinned canonical SQL sequence. It never
runs `database/postgres/*.sql` by wildcard and never loads lessons, taxonomy or
questions.

Production execution is deliberately blocked until Advanced canonical content is
frozen and Stage 26 is regenerated.

## After Advanced content is frozen

Regenerate, in order:

1. canonical reference seed from Advanced Stage 1/2/3 outputs;
2. Advanced Question Bank bootstrap;
3. content-bound validation/test gates;
4. production Stage 26 contract and release evidence.

Do not reuse Intermediate IDs or canonical seed manifests.
