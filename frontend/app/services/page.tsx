"use client"

import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { UniversalHero } from "@/components/layout/universal-hero"
import { EnhancedServicesSection } from "@/components/features/services-section-enhanced"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { ArrowRight, Zap, Bot, Brain } from "lucide-react"

export default function ServicesPage() {
  const { t } = useEnhancedTranslation()

  const heroActions = [
    {
      label: t("services.consulting.cta"),
      href: "/contact",
      variant: "default" as const,
      icon: ArrowRight,
    },
    {
      label: t("ui.learnMore"),
      href: "/consulting",
      variant: "outline" as const,
    },
  ]

  const heroStats = [
    {
      icon: Zap,
      value: "50+",
      label: t("services.aiAgents.title"),
    },
    {
      icon: Bot,
      value: "100+",
      label: t("services.chatbots.title"),
    },
    {
      icon: Brain,
      value: "200+",
      label: "AI Solutions",
    },
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <UniversalHero
          title={t("services.title")}
          subtitle={t("services.subtitle")}
          actions={heroActions}
          stats={heroStats}
        />
        <EnhancedServicesSection />
      </main>
      <EnhancedFooter />
    </div>
  )
}