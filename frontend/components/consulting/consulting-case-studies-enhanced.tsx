"use client"

import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export function EnhancedConsultingCaseStudies() {
  const { t, isRTL } = useEnhancedTranslation()

  const caseStudies = [
    {
      title: t("consultingPage.caseStudies.case1.title"),
      description: t("consultingPage.caseStudies.case1.description"),
      image: "/placeholder.svg",
    },
    {
      title: t("consultingPage.caseStudies.case2.title"),
      description: t("consultingPage.caseStudies.case2.description"),
      image: "/placeholder.svg",
    },
    {
      title: t("consultingPage.caseStudies.case3.title"),
      description: t("consultingPage.caseStudies.case3.description"),
      image: "/placeholder.svg",
    },
  ]

  return (
    <section className={cn("w-full py-12 md:py-24 lg:py-32 bg-white dark:bg-gray-900", isRTL && "rtl text-right")}>
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">{t("consultingPage.caseStudies.title")}</h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              {t("consultingPage.caseStudies.subtitle")}
            </p>
          </div>
        </div>
        <div className="mx-auto grid max-w-5xl items-start gap-8 py-12 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {caseStudies.map((study, index) => (
            <Card key={index} className="overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300">
              <Image
                alt={study.title}
                className="aspect-video w-full overflow-hidden rounded-t-xl object-cover"
                height={200}
                src={study.image || "/placeholder.svg"}
                width={350}
              />
              <CardHeader>
                <CardTitle className="text-xl font-bold text-gray-900 dark:text-white">{study.title}</CardTitle>
                <CardDescription className="text-gray-600 dark:text-gray-400 mb-4">{study.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="outline">
                  <Link href="#">{t("ui.learnMore")}</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
