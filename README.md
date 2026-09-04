# Grammar Mastery Advanced

Advanced-level instance of the Grammar Mastery Platform.

## Repository status

The software core is initialized from the existing Grammar Mastery Platform, while
book-specific canonical content starts intentionally empty.

Source platform snapshot:

- Repository: `ImanNasrEsfahani/grammar-mastery-platform`
- Commit: `a52d206b9bb1a6c07ae4afd185c9c8d9c4b8df4f`

## Content policy

Do not import or reuse the Intermediate book's lesson, subtopic, taxonomy, weighting,
question-bank, provenance, or canonical seed data as Advanced canonical content.

Advanced content must be regenerated from the new source book through the staged content
pipeline:

1. Knowledge map
2. Taxonomy
3. TCF weighting
4. Question capacity/targets
5. Master content inventory
6. Question type compatibility
7. Distractor/misconception model
8. Difficulty
9. Difficulty distribution
10. Canonical question schema and bank

After the Advanced canonical data is frozen, regenerate the canonical reference seed,
Question Bank bootstrap configuration, validation gates, tests, and Stage 26 release
contract against the Advanced data.

## Runtime core

This seed contains the reusable application/runtime core only. The `data/` tree is an
empty versioned content scaffold by design.
