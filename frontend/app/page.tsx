import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedHeroSection } from "@/components/layout/hero-section-enhanced"
import { EnhancedServicesSection } from "@/components/features/services-section-enhanced"
import { EnhancedTestimonialsSection } from "@/components/features/testimonials-section-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <EnhancedHeroSection />
        <EnhancedServicesSection />
        <EnhancedTestimonialsSection />
      </main>
      <EnhancedFooter />
    </div>
  )
}
