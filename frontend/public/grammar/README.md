# Static grammar lesson HTML — Advanced instance

This directory is the runtime home for authored grammar lesson HTML files.

## Current state

No canonical Advanced book is registered yet.

Do not place copied Intermediate lesson HTML here. The real Advanced book slug,
lesson count, titles, edition and source provenance must be frozen from Stage 1
before learner lesson content is enabled.

## When Stage 1 is frozen

1. Choose one stable ASCII book slug.
2. Add the real book entry to `frontend/src/lib/grammar-content/books.ts`.
3. Set `ready: true` and the exact `lessonCount`.
4. Create `frontend/public/grammar/<book-slug>/`.
5. Save lesson HTML as `L01.html`, `L02.html`, ... using the canonical lesson
   number from the Advanced lesson map.
6. Rebuild/redeploy the frontend.

The learner route stays UUID-based. The lesson UUID is the stable application
identifier; `LNN.html` is only the presentation lookup for authored lesson
content.

## HTML authoring contract

- HTML is fetched same-origin and rendered inside the lesson page.
- The frontend sanitizer removes `script`, `iframe`, `object`, `embed`,
  event-handler attributes and `javascript:` URLs.
- Do not add JavaScript to authored lesson HTML.
- Keep CSS scoped to the lesson wrapper.
- Mixed Persian RTL and French LTR content must remain explicit.
- Relative images/media belong under the same book directory, e.g. `assets/`.

Do not use the display title as a storage key. The stable slug is the storage
and routing key.
