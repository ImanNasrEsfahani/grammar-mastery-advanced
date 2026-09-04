import {describe, expect, test} from "vitest";
import {
  DEFAULT_GRAMMAR_BOOK_SLUG,
  GRAMMAR_BOOKS,
  grammarLessonUrl,
  lessonHtmlFileName,
  resolveGrammarBookSlug,
} from "./books";

describe("advanced grammar content registry", () => {
  test("fails closed while Advanced canonical content is pending", () => {
    expect(DEFAULT_GRAMMAR_BOOK_SLUG).toBe("advanced-content-pending");
    expect(resolveGrammarBookSlug()).toBeNull();
    expect(GRAMMAR_BOOKS[DEFAULT_GRAMMAR_BOOK_SLUG].ready).toBe(false);
  });

  test("rejects unknown and legacy book slugs", () => {
    expect(resolveGrammarBookSlug("unknown-book")).toBeNull();
    expect(
      resolveGrammarBookSlug("grammaire-progressive-francais-intermediaire-3e"),
    ).toBeNull();
  });

  test("maps lesson numbers to stable zero-padded HTML filenames", () => {
    expect(lessonHtmlFileName(1)).toBe("L01.html");
    expect(lessonHtmlFileName(9)).toBe("L09.html");
    expect(lessonHtmlFileName(100)).toBe("L100.html");
  });

  test("does not build lesson URLs before the Advanced book is registered", () => {
    expect(() => grammarLessonUrl(DEFAULT_GRAMMAR_BOOK_SLUG, 1)).toThrow(
      /not registered/i,
    );
  });

  test("rejects invalid lesson numbers", () => {
    expect(() => lessonHtmlFileName(0)).toThrow(RangeError);
    expect(() => lessonHtmlFileName(1000)).toThrow(RangeError);
  });
});
