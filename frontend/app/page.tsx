"use client"

import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { UniversalHero } from "@/components/layout/universal-hero"
import { EnhancedServicesSection } from "@/components/features/services-section-enhanced"
import { EnhancedTestimonialsSection } from "@/components/features/testimonials-section-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { EnhancedChatWidget } from "@/components/chatbot/enhanced-chat-widget"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { ArrowRight, Users, CheckCircle, Clock, Star } from "lucide-react"

export default function HomePage() {
  const { t } = useEnhancedTranslation()

  const heroStats = [
    {
      icon: Users,
      value: "500+",
      label: t("hero.stats.clients"),
    },
    {
      icon: CheckCircle,
      value: "1000+",
      label: t("hero.stats.projects"),
    },
    {
      icon: Clock,
      value: "10+",
      label: t("hero.stats.experience"),
    },
    {
      icon: Star,
      value: "98%",
      label: t("hero.stats.satisfaction"),
    },
    {
      icon: ArrowRight,
      value: "24/7",
      label: t("hero.stats.support"),
    },
  ]

  const heroActions = [
    {
      label: t("hero.cta.primary"),
      href: "/contact",
      variant: "default" as const,
      icon: ArrowRight,
    },
    {
      label: t("hero.cta.secondary"),
      href: "/services",
      variant: "outline" as const,
    },
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <UniversalHero
          title={t("hero.title")}
          subtitle={t("hero.subtitle")}
          actions={heroActions}
          stats={heroStats}
          showScrollIndicator={true}
        />
        <EnhancedServicesSection />
        <EnhancedTestimonialsSection />
      </main>
      <EnhancedFooter />
      
      {/* Enhanced AI Chat Widget */}
      <EnhancedChatWidget 
        position="bottom-right"
        theme="auto"
      />
    </div>
  )
}