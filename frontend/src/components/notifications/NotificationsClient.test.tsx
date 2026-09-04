import {render, screen, waitFor, within} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {beforeEach, expect, test, vi} from "vitest";
import {apiRequest} from "@/lib/api/client";
import {NotificationsClient} from "./NotificationsClient";

const router = vi.hoisted(() => ({push: vi.fn()}));

vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));

vi.mock("@/lib/api/client", async (importOriginal) => {
  const original = await importOriginal<typeof import("@/lib/api/client")>();
  return {...original, apiRequest: vi.fn()};
});

const items = [
  {
    id: "n-review",
    kind: "learning",
    tone: "review",
    action_required: true,
    title_fa: "مرور امروز",
    title_en: "Review due",
    body_fa: "یک مرور واقعی برای امروز دارید.",
    body_en: "You have a real review due today.",
    href: "/review/review-1",
    cta_fa: "شروع مرور",
    cta_en: "Start review",
    french_scope: "les relatifs",
    source_type: "REVIEW_DUE",
    source_key: "review-1",
    payload: {},
    seen_at: null,
    read_at: null,
    created_at: "2026-09-04T18:00:00Z",
    unread: true,
  },
  {
    id: "n-system",
    kind: "system",
    tone: "system",
    action_required: false,
    title_fa: "تنظیمات حساب",
    title_en: "Account settings",
    body_fa: "تنظیمات اعلان‌های خود را بررسی کنید.",
    body_en: "Review your notification settings.",
    href: "/settings",
    cta_fa: "باز کردن تنظیمات",
    cta_en: "Open settings",
    french_scope: null,
    source_type: "SYSTEM_NOTICE",
    source_key: "system-1",
    payload: {},
    seen_at: null,
    read_at: null,
    created_at: "2026-09-04T17:00:00Z",
    unread: true,
  },
  {
    id: "n-result",
    kind: "general",
    tone: "result",
    action_required: false,
    title_fa: "نتیجه ثبت شد",
    title_en: "Result recorded",
    body_fa: "نتیجه قبلی شما ثبت شده است.",
    body_en: "Your previous result has been recorded.",
    href: null,
    cta_fa: null,
    cta_en: null,
    french_scope: null,
    source_type: "ATTEMPT_RESULT",
    source_key: "attempt-1",
    payload: {},
    seen_at: "2026-09-04T16:00:00Z",
    read_at: "2026-09-04T16:05:00Z",
    created_at: "2026-09-04T16:00:00Z",
    unread: false,
  },
] as const;

const notificationEnvelope = {
  data: {
    items: items.map((item) => ({...item})),
    unread_count: 2,
    provider_version: "notifications-v1",
  },
  meta: {request_id: "notifications-request", api_version: "v1"},
};

function mutationEnvelope(unreadCount: number) {
  return {
    data: {unread_count: unreadCount},
    meta: {request_id: "mutation-request", api_version: "v1"},
  };
}

function installApiMock() {
  vi.mocked(apiRequest).mockImplementation(async (path) => {
    if (path === "/api/backend/notifications") {
      return structuredClone(notificationEnvelope) as never;
    }
    if (path === "/api/backend/notifications/seen") {
      return mutationEnvelope(2) as never;
    }
    if (path === "/api/backend/notifications/read-all") {
      return mutationEnvelope(0) as never;
    }
    if (path === "/api/backend/notifications/n-review/read") {
      return mutationEnvelope(1) as never;
    }
    if (path === "/api/backend/notifications/n-system/read") {
      return mutationEnvelope(1) as never;
    }
    throw new Error(`Unexpected notification request: ${path}`);
  });
}

beforeEach(() => {
  router.push.mockReset();
  vi.mocked(apiRequest).mockReset();
  installApiMock();
});

test("renders API-backed notifications and navigates through the real CTA", async () => {
  const user = userEvent.setup();
  render(<NotificationsClient locale="fa" />);

  expect(await screen.findByRole("heading", {name: "اعلان‌ها"})).toBeInTheDocument();
  expect(screen.getByText("۲ خوانده‌نشده")).toBeInTheDocument();
  expect(screen.getByText("۳ اعلان واقعی")).toBeInTheDocument();

  const reviewCard = screen.getByRole("heading", {name: /مرور امروز/}).closest("article");
  expect(reviewCard).not.toBeNull();
  await user.click(within(reviewCard!).getByRole("button", {name: "شروع مرور"}));

  await waitFor(() => {
    expect(apiRequest).toHaveBeenCalledWith(
      "/api/backend/notifications/n-review/read",
      {method: "POST"},
    );
  });
  expect(router.push).toHaveBeenCalledWith("/fa/review/review-1");
});

test("filters unread notifications and persists mark-all-read through the API", async () => {
  const user = userEvent.setup();
  render(<NotificationsClient locale="fa" />);
  await screen.findByRole("heading", {name: "اعلان‌ها"});

  await user.click(screen.getByRole("button", {name: /خوانده‌نشده/}));
  expect(screen.getByRole("heading", {name: /مرور امروز/})).toBeInTheDocument();
  expect(screen.getByRole("heading", {name: "تنظیمات حساب"})).toBeInTheDocument();
  expect(screen.queryByRole("heading", {name: "نتیجه ثبت شد"})).not.toBeInTheDocument();

  await user.click(screen.getByRole("button", {name: "همه را خواندم"}));
  await waitFor(() => expect(screen.getByText("۰ خوانده‌نشده")).toBeInTheDocument());
  expect(apiRequest).toHaveBeenCalledWith(
    "/api/backend/notifications/read-all",
    {method: "POST"},
  );
});

test("marks one notification read through its current card action", async () => {
  const user = userEvent.setup();
  render(<NotificationsClient locale="en" />);
  await screen.findByRole("heading", {name: "Notifications"});

  const reviewCard = screen.getByRole("heading", {name: /Review due/}).closest("article");
  expect(reviewCard).not.toBeNull();
  await user.click(within(reviewCard!).getByRole("button", {name: "Mark read"}));

  await waitFor(() => {
    expect(within(reviewCard!).getByText(/Read/)).toBeInTheDocument();
  });
  expect(screen.getByText("1 unread")).toBeInTheDocument();
  expect(apiRequest).toHaveBeenCalledWith(
    "/api/backend/notifications/n-review/read",
    {method: "POST"},
  );
});
