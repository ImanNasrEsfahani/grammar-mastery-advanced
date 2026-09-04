import {describe, expect, test} from "vitest";
import {
  DEFAULT_GRAMMAR_BOOK_SLUG,
  grammarLessonUrl,
  lessonHtmlFileName,
  resolveGrammarBookSlug,
} from "./books";

describe("grammar content registry", () => {
  test("uses the canonical Advanced book by default", () => {
    expect(resolveGrammarBookSlug()).toBe(DEFAULT_GRAMMAR_BOOK_SLUG);
    expect(DEFAULT_GRAMMAR_BOOK_SLUG).toBe(
      "grammaire-progressive-francais-avance",
    );
  });

  test("rejects an unknown book slug", () => {
    expect(resolveGrammarBookSlug("unknown-book")).toBeNull();
  });

  test("maps lesson numbers to zero-padded HTML filenames", () => {
    expect(lessonHtmlFileName(1)).toBe("L01.html");
    expect(lessonHtmlFileName(9)).toBe("L09.html");
    expect(lessonHtmlFileName(27)).toBe("L27.html");
  });

  test("builds a static same-origin Advanced lesson URL", () => {
    expect(grammarLessonUrl(DEFAULT_GRAMMAR_BOOK_SLUG, 1)).toBe(
      "/grammar/grammaire-progressive-francais-avance/L01.html",
    );
  });

  test("fails closed outside the configured Advanced book range", () => {
    expect(() => grammarLessonUrl(DEFAULT_GRAMMAR_BOOK_SLUG, 28)).toThrow(
      RangeError,
    );
    expect(() => lessonHtmlFileName(0)).toThrow(RangeError);
  });
});
