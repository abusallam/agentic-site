import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { EnhancedServicesSection } from "@/components/features/services-section-enhanced"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"

export default function ServicesPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Our AI Services</h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Comprehensive AI solutions to transform your business and accelerate digital innovation
            </p>
          </div>
          <EnhancedServicesSection />
        </div>
      </main>
      <EnhancedFooter />
    </div>
  )
}