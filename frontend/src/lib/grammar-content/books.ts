export type GrammarBookDefinition = {
  slug: string;
  titleFr: string;
  titleFa: string;
  edition: string;
  lessonCount: number;
  publicRoot: string;
  ready: boolean;
};

/**
 * Advanced starts intentionally without a registered canonical book.
 *
 * Replace this placeholder only after Stage 1 has frozen the Advanced book
 * identity and lesson inventory. Keeping a typed placeholder prevents the
 * frontend from silently falling back to the Intermediate book.
 */
export const GRAMMAR_BOOKS = {
  "advanced-content-pending": {
    slug: "advanced-content-pending",
    titleFr: "Contenu avancé en préparation",
    titleFa: "محتوای سطح پیشرفته در حال آماده‌سازی",
    edition: "pending",
    lessonCount: 0,
    publicRoot: "/grammar/advanced-content-pending",
    ready: false,
  },
} as const satisfies Record<string, GrammarBookDefinition>;

export type GrammarBookSlug = keyof typeof GRAMMAR_BOOKS;

export const DEFAULT_GRAMMAR_BOOK_SLUG: GrammarBookSlug =
  "advanced-content-pending";

export function isGrammarBookSlug(value: string): value is GrammarBookSlug {
  return Object.prototype.hasOwnProperty.call(GRAMMAR_BOOKS, value);
}

/**
 * Fail closed until a real Advanced book is registered.
 * This deliberately makes learner lesson-content routes return 404 rather
 * than serving copied Intermediate HTML.
 */
export function resolveGrammarBookSlug(
  value?: string | null,
): GrammarBookSlug | null {
  const candidate = value || DEFAULT_GRAMMAR_BOOK_SLUG;
  if (!isGrammarBookSlug(candidate)) return null;
  return GRAMMAR_BOOKS[candidate].ready ? candidate : null;
}

export function getGrammarBook(slug: GrammarBookSlug) {
  return GRAMMAR_BOOKS[slug];
}

export function lessonHtmlFileName(lessonNo: number): string {
  if (!Number.isInteger(lessonNo) || lessonNo < 1 || lessonNo > 999) {
    throw new RangeError("lessonNo must be an integer from 1 to 999.");
  }
  return `L${String(lessonNo).padStart(2, "0")}.html`;
}

export function grammarLessonUrl(
  slug: GrammarBookSlug,
  lessonNo: number,
): string {
  const book = getGrammarBook(slug);

  if (!book.ready || book.lessonCount < 1) {
    throw new Error(
      "Advanced grammar content is not registered yet. Complete Stage 1 and register the canonical book before serving lesson HTML.",
    );
  }

  if (lessonNo > book.lessonCount) {
    throw new RangeError(
      `Lesson ${lessonNo} is outside the configured ${book.lessonCount}-lesson book.`,
    );
  }

  return `${book.publicRoot}/${lessonHtmlFileName(lessonNo)}`;
}
