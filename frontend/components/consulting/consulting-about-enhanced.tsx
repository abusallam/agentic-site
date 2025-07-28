"use client"

import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"

export function EnhancedConsultingAbout() {
  const { t, isRTL } = useEnhancedTranslation()

  return (
    <section className={cn("py-12 md:py-24 lg:py-32", isRTL && "text-right")}>
      <div className="container px-4 md:px-6">
        <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 xl:grid-cols-2">
          <div className="flex flex-col justify-center space-y-4">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">{t("consultingPage.about.title")}</h2>
              <p className="max-w-[600px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
                {t("consultingPage.about.paragraph1")}
              </p>
              <p className="max-w-[600px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
                {t("consultingPage.about.paragraph2")}
              </p>
            </div>
          </div>
          <div className="flex justify-center">
            <img
              alt="About Us"
              className="mx-auto aspect-video overflow-hidden rounded-xl object-cover sm:w-full lg:order-last"
              height="310"
              src="/placeholder.svg"
              width="550"
            />
          </div>
        </div>
      </div>
    </section>
  )
}
