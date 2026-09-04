import type {Metadata} from "next";
import {notFound} from "next/navigation";
import {PasswordRecoveryClient} from "@/components/auth/PasswordRecoveryClient";
import {isLocale} from "@/lib/i18n";

export const metadata: Metadata = {
  robots: {index: false, follow: false},
  referrer: "no-referrer",
};

export default async function ForgotPasswordPage({params}: {params: Promise<{locale: string}>}) {
  const {locale} = await params;
  if (!isLocale(locale)) notFound();
  return <PasswordRecoveryClient locale={locale} mode="request" />;
}
