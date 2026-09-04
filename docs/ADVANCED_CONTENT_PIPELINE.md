# Advanced Content Pipeline

The repository starts with the application core but without book-specific canonical data.

## Required content sequence

### Stage 1 — Knowledge map
Extract the new book into lessons, atomic subtopics, dependencies, exceptions, source
references and stable IDs.

### Stage 2 — Taxonomy
Build the Advanced taxonomy and controlled tags from the new knowledge map. Do not
blindly inherit the Intermediate mapping.

### Stage 3 — Weights
Recalculate TCF/general importance weights for the Advanced lesson set. The final active
weights must be versioned and normalized.

### Stage 4 — Capacity
Recalculate question targets from the Advanced weights and production policy.

### Stage 5+ — Authoring and Question Bank
Create the Advanced inventory, authoring compatibility, misconception/distractor model,
difficulty distribution, canonical question rows and QA evidence.

## Bootstrap boundary

Only after Advanced Stage 1/2/3 canonical reference data exists should a new
`ops/stage12` reference seed be generated.

Only after the Advanced canonical Question Bank exists should a new
`ops/question_bank` bootstrap be generated.

Finally regenerate the Stage 26 operations contract/migration runner tests so release
gates reference the Advanced canonical versions rather than the old content pack.
