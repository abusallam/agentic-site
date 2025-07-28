"use client"

import Link from "next/link"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export function EnhancedConsultingContact() {
  const { t, locale, isRTL } = useEnhancedTranslation()

  return (
    <section className={cn("py-12 md:py-24 lg:py-32 bg-gray-100 dark:bg-gray-800", isRTL && "text-right")}>
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">{t("consultingPage.contact.title")}</h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              {t("consultingPage.contact.subtitle")}
            </p>
          </div>
          <Button asChild>
            <Link href={`/${locale}/contact`}>{t("consultingPage.contact.cta")}</Link>
          </Button>
        </div>
      </div>
    </section>
  )
}
