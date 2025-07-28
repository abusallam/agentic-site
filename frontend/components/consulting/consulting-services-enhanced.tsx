"use client"

import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"
import { Brain, Lightbulb, TrendingUp, ShieldCheck } from "lucide-react"

export function EnhancedConsultingServices() {
  const { t, isRTL } = useEnhancedTranslation()

  const services = [
    {
      icon: Brain,
      title: t("consultingPage.services.strategy.title"),
      description: t("consultingPage.services.strategy.description"),
    },
    {
      icon: Lightbulb,
      title: t("consultingPage.services.feasibility.title"),
      description: t("consultingPage.services.feasibility.description"),
    },
    {
      icon: TrendingUp,
      title: t("consultingPage.services.implementation.title"),
      description: t("consultingPage.services.implementation.description"),
    },
    {
      icon: ShieldCheck,
      title: t("consultingPage.services.ethics.title"),
      description: t("consultingPage.services.ethics.description"),
    },
  ]

  return (
    <section className={cn("py-12 md:py-24 lg:py-32 bg-gray-100 dark:bg-gray-800", isRTL && "text-right")}>
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">{t("consultingPage.services.title")}</h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              {t("consultingPage.services.subtitle")}
            </p>
          </div>
        </div>
        <div className="mx-auto grid max-w-5xl items-start gap-8 py-12 sm:grid-cols-2 lg:grid-cols-4">
          {services.map((service, index) => (
            <div key={index} className="grid gap-1">
              <div className="flex items-center justify-center rounded-full bg-primary-100 p-3 text-primary-600 dark:bg-primary-900 dark:text-primary-300">
                <service.icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">{service.title}</h3>
              <p className="text-gray-500 dark:text-gray-400">{service.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
