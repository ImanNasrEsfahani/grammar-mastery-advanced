# Static grammar lesson HTML — Advanced

This directory is the runtime home for authored grammar lesson HTML files.
The Next.js frontend serves files from `frontend/public/` at same-origin URLs.

## Canonical book

Book slug:

`grammaire-progressive-francais-avance`

Repository directory:

`frontend/public/grammar/grammaire-progressive-francais-avance/`

Runtime URL root:

`/grammar/grammaire-progressive-francais-avance/`

## Lesson naming contract

The Advanced canonical dataset contains exactly 27 lessons:

- Lesson 1 -> `L01.html`
- ...
- Lesson 27 -> `L27.html`

The learner route remains UUID-based:

`/{locale}/lessons/{lessonId}?book=grammaire-progressive-francais-avance`

The UI reads `lesson_no` from the canonical lesson API and resolves the matching static
lesson file. The physical database UUID remains the stable application key; the
filename is only a presentation lookup.

## Content policy

The Advanced HTML fragments in this repository are generated from
`data/product/ADV_lesson_content_v1.0.json`. Their pedagogical examples are original
project examples, not transcriptions of book exercises.

Do not add JavaScript to lesson HTML. Keep styles scoped under `.adv-lesson`.
