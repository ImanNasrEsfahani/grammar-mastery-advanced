# Advanced Repository Compatibility Report v1.0

Repository: `ImanNasrEsfahani/grammar-mastery-advanced`  
Inspected branch: `main`  
Inspected commit: `f9a1df1fd3575d8eb09306ec57c80aa076c55b5f`  
Canonical content contract: `ADV-QB-SCHEMA-v1.0`  
Target physical PostgreSQL contract: `relational-schema-v0.9.0`

## Result

**COMPATIBLE WITH ADAPTER — no destructive database schema migration is required.**

The repository can host the 27-lesson Advanced canonical dataset. The main mismatch is
at the content/database boundary: canonical stable IDs and several canonical enums use
a deliberately database-independent representation, while the repository requires UUIDs,
regional locales, Stage23 draft status, physical source enums, and 1–4 difficulty scores.

The patch therefore adds a versioned adapter instead of rewriting canonical question data.

## Canonical scope used

- 27 lessons
- 116 subtopics
- 8 technical site categories
- 27 lesson-shaped subcategories
- 58 controlled tags
- 98 lesson-tag assignments
- 116 misconceptions
- 15 question types
- 116 subtopic compatibility records
- 43 application-derived dependency/support edges
- 68 book-derived cross references
- 8 Bilan review sections
- 12 non-lesson/support sections
- 6,130 question target
- difficulty plan: 20% EASY / 40% MEDIUM / 30% HARD / 10% VERY_HARD

## Repository findings

### Database and migrations

The existing PostgreSQL reference model already has the tables required for:
`grammar_categories`, `grammar_lessons`, `grammar_subtopics`, `tags`, `lesson_tags`,
`question_types`, `misconceptions`, question compatibility, capacity/difficulty targets,
actors, questions, options, secondary subtopics and question tags.

No canonical Advanced identifier should be forced into these UUID columns directly.
The patch uses deterministic UUIDv5 mappings with namespace:

`2ff38ec0-7fd9-5f16-9864-8976e9a7ac06`

Rule:

`uuid5(namespace, "<kind>:<canonical_stable_id>")`

This keeps canonical IDs intact while giving the database stable UUIDs.

### Import pipeline

The existing frozen Stage23 import transport already uses the same 46 column names and
the same 15 question-type tokens as the current Advanced Question Bank. The adapter only
changes boundary representations.

| Canonical ADV | Repository transport |
|---|---|
| `ADV-L01`, `ADV-L01-ST01`, misconception IDs | deterministic UUIDv5 |
| `fr`, `fa` | `fr-FR`, `fa-IR` |
| JSON arrays | pipe-delimited UUID/token lists |
| difficulty score `0..1` | `1..4` using `1 + 3*x` |
| `READY_FOR_IMPORT` | `DRAFT` |
| `BOOK_RULE_DERIVED*` | `PROJECT_SYNTHETIC_FROM_RULE` |
| `BOOK_RULE_PLUS_SUPPORT_CONFIRMED` | `EXTERNAL_REVIEWED` |
| blank media type | `NONE` |
| raw batch tags | controlled tags only + canonical lesson tags |
| `ADV-QB-SCHEMA-v1.0` | transport `ADV-QB-IMPORT-v1.0` |

The repository validator's four Advanced version constants must be changed from the old
v0.9 values to the canonical Advanced versions. This is a **versioned import-contract
change**, not a silent canonical schema change.

### TCF weight

The Advanced canonical package does not provide verified lesson-level TCF weights.
`grammar_lessons.tcf_weight` is therefore seeded as `0` and `lesson_weight_versions`
is intentionally not populated. No TCF weighting is invented.

### Dependencies

All 43 dependency records explicitly state that they are **not book-declared prerequisites**.
They are therefore stored as technical `lesson_related_references`, not as
`lesson_prerequisites`.

### Frontend

The current registry points to an Intermediate 52-lesson book. The patch replaces the
registry with:

- slug: `grammaire-progressive-francais-avance`
- 27 lessons
- Advanced title
- runtime root: `/grammar/grammaire-progressive-francais-avance`

It also includes 27 generated `L01.html` ... `L27.html` lesson fragments built from the
canonical project lesson-content layer. Their examples are original pedagogical examples,
not copied book exercises.

### API contracts

The core and import APIs are UUID/content driven. No OpenAPI path or response shape change
is required solely to switch from the Intermediate content set to the Advanced content set.

## Versioned changes included in this patch

1. Canonical Advanced data copied into the repository's existing `data/` domains.
2. Deterministic UUID adapter layer.
3. Advanced Stage12 reference seed.
4. Canonical-question -> Stage23 transport transformer.
5. Validator/import version upgrade to:
   - `ADV-QB-IMPORT-v1.0`
   - `ADV-TAXONOMY-v1.0`
   - `ADV-QTYPE-v1.0`
   - `ADV-COMPAT-v1.0`
   - `ADV-DISTRACTOR-v1.0`
6. Advanced frontend book registration and tests.
7. 27 Advanced static lesson HTML files.
8. Stage16/Stage17 authoritative book identity update.
9. Stage17 source hash updated to the actual supplied Advanced PDF SHA-256:
   `e591fea7ed499aadf59f4ed35ac041653257f4b813a2c936aad6671db187edb0`
10. Docker data allow-list update for Advanced canonical files.

## Validation performed on the patch

The real canonical B001 CSV (50 rows) was transformed through the new adapter.

Result: **PASS**

- 50/50 rows transformed
- all primary IDs became valid deterministic UUIDs
- all distractor misconception IDs resolved
- correct-option misconception remained empty
- locales resolved to repository enums
- status became `DRAFT`
- source type resolved to repository enum
- tags resolved exclusively to controlled tokens
- author/reviewer actors resolved to distinct UUIDs
- media type resolved to `NONE`
- Advanced version constants preserved at the transport/database boundary

## Remaining Question Bank gate

The Drive structure audit verifies all 130 canonical batch folders and reports 6,130
completed questions, but it separately marks project-wide global content/semantic
validation as pending. The integration patch therefore prepares the reference seed and
batch adapter but does **not** bulk publish the 6,130 questions.

Bulk import/publication should occur only after the global Question Bank validation gate
is PASS.
