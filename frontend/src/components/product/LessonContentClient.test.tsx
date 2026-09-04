import {render, screen} from "@testing-library/react";
import {afterEach, expect, test, vi} from "vitest";
import {apiRequest} from "@/lib/api/client";
import {LessonContentClient} from "./LessonContentClient";

vi.mock("@/lib/api/client", async (importOriginal) => {
  const original = await importOriginal<typeof import("@/lib/api/client")>();
  return {...original, apiRequest: vi.fn()};
});

vi.mock("@/lib/grammar-content/books", async (importOriginal) => {
  const original =
    await importOriginal<typeof import("@/lib/grammar-content/books")>();
  return {
    ...original,
    getGrammarBook: vi.fn(() => ({
      slug: "advanced-content-pending",
      titleFr: "Advanced test content",
      titleFa: "محتوای آزمایشی پیشرفته",
      edition: "test",
      lessonCount: 999,
      publicRoot: "/grammar/advanced-test",
      ready: true,
    })),
    grammarLessonUrl: vi.fn(
      (_slug: "advanced-content-pending", lessonNo: number) =>
        `/grammar/advanced-test/L${String(lessonNo).padStart(2, "0")}.html`,
    ),
  };
});

const LESSON_ID = "22222222-2222-4222-8222-222222222222";
const SUBTOPIC_ID = "33333333-3333-4333-8333-333333333333";
const REVIEW_ID = "55555555-5555-4555-8555-555555555555";

function lessonEnvelope() {
  return {
    data: {
      id: LESSON_ID,
      lesson_no: 32,
      title_fr: "ADVANCED TEST LESSON",
      short_title: "Advanced test",
      category_id: "66666666-6666-4666-8666-666666666666",
      subcategory_id: "77777777-7777-4777-8777-777777777777",
      category_title_fr: "Advanced grammar",
      category_title_fa: "گرامر پیشرفته",
      subcategory_title_fr: "Advanced synthetic fixture",
      subcategory_title_fa: "نمونه آزمایشی پیشرفته",
      tcf_weight: 1,
      active: true,
      question_count: 42,
      subtopics: [
        {
          id: SUBTOPIC_ID,
          code: "ADV-T01",
          title_fr: "Synthetic advanced subtopic",
          title_fa: "زیرموضوع آزمایشی پیشرفته",
          short_definition_fa: "این داده فقط برای تست رابط کاربری است.",
          active: true,
        },
      ],
      book_reference: {book_pages: "test", pdf_pages: "test"},
      learning: {
        overview: {
          mastery_score_pct: 63,
          confidence: 0.52,
          coverage_ratio: 0.71,
          evidence_count: 18,
          mastery_band: "DEVELOPING",
          model_version: "mastery-evidence-v0.9.0",
          source: "AGGREGATED_SUBTOPICS",
        },
        subtopics: [
          {
            id: SUBTOPIC_ID,
            question_count: 42,
            mistake_count: 3,
            mastery: {
              mastery_score_pct: 78,
              confidence: 0.72,
              coverage_ratio: 1,
              evidence_count: 8,
              mastery_band: "DEVELOPING",
              model_version: "mastery-evidence-v0.9.0",
              source: "PERSISTED_SUBTOPIC",
            },
          },
        ],
        unresolved_mistake_count: 12,
        review_item_id: REVIEW_ID,
        misconceptions: [
          {
            id: "88888888-8888-4888-8888-888888888888",
            family: "ADVANCED_SYNTHETIC",
            name_fa: "خطای آزمایشی",
            statement_fa: "این misconception صرفاً fixture تست است.",
            diagnostic_interpretation_fa: null,
            subtopic_id: SUBTOPIC_ID,
            subtopic_title_fr: "Synthetic advanced subtopic",
            subtopic_title_fa: "زیرموضوع آزمایشی پیشرفته",
            repeat_count: 5,
            last_wrong_at: "2026-08-24T18:00:00Z",
          },
        ],
        recent_activity: [
          {
            attempt_id: "99999999-9999-4999-8999-999999999999",
            test_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            mode: "adaptive",
            question_count: 18,
            answered_count: 18,
            correct_count: 14,
            accuracy_pct: 77.8,
            duration_seconds: 660,
            completed_at: "2026-08-24T18:00:00Z",
          },
        ],
      },
    },
    meta: {request_id: "test-request", api_version: "v1"},
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

test("renders the lesson dashboard with a synthetic Advanced fixture", async () => {
  vi.mocked(apiRequest).mockResolvedValue(lessonEnvelope());
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () => "<article><p>Advanced test lesson body</p></article>",
    }),
  );

  render(
    <LessonContentClient
      locale="fa"
      lessonId={LESSON_ID}
      bookSlug="advanced-content-pending"
    />,
  );

  expect(
    await screen.findByRole("heading", {name: "ADVANCED TEST LESSON"}),
  ).toBeInTheDocument();
  expect(screen.getByText("63%")).toBeInTheDocument();
  expect(screen.getByText("52%")).toBeInTheDocument();
  expect(screen.getByText("71%")).toBeInTheDocument();
  expect(screen.getAllByText("Synthetic advanced subtopic").length).toBeGreaterThan(0);
  expect(screen.getByText("خطای آزمایشی")).toBeInTheDocument();
  expect(screen.getByRole("link", {name: "شروع تمرین درس"})).toHaveAttribute(
    "href",
    `/fa/tests/new?lesson=${LESSON_ID}`,
  );
  expect(screen.getByRole("link", {name: /مرور اشتباهات/})).toHaveAttribute(
    "href",
    `/fa/review/${REVIEW_ID}`,
  );
});
