"use client"

import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { UniversalHero } from "@/components/layout/universal-hero"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { CheckCircle, Users, TrendingUp, Shield, ArrowRight, Target, Award, Clock } from "lucide-react"

export default function ConsultingPage() {
  const { t } = useEnhancedTranslation()
  const services = [
    {
      icon: TrendingUp,
      title: "AI Strategy Development",
      description: "Develop comprehensive AI strategies aligned with your business goals and market opportunities."
    },
    {
      icon: Users,
      title: "Implementation Support",
      description: "Expert guidance and hands-on support during AI solution implementation and deployment."
    },
    {
      icon: CheckCircle,
      title: "Feasibility Studies",
      description: "Assess technical and business feasibility of AI projects before investment."
    },
    {
      icon: Shield,
      title: "AI Ethics & Governance",
      description: "Ensure responsible AI development with proper ethics and governance frameworks."
    }
  ]

  const caseStudies = [
    {
      title: "Retail Automation Success",
      description: "Increased operational efficiency by 40% through AI-powered inventory management.",
      industry: "Retail"
    },
    {
      title: "Financial Risk Assessment",
      description: "Improved risk assessment accuracy by 25% with predictive analytics models.",
      industry: "Finance"
    },
    {
      title: "Customer Support Enhancement",
      description: "Reduced response times by 60% with NLP-powered chatbot implementation.",
      industry: "Technology"
    }
  ]

  const heroActions = [
    {
      label: t("consultingPage.contact.cta"),
      href: "/contact",
      variant: "default" as const,
      icon: ArrowRight,
    },
    {
      label: t("ui.learnMore"),
      href: "/services",
      variant: "outline" as const,
    },
  ]

  const heroStats = [
    {
      icon: Target,
      value: "95%",
      label: "Success Rate",
    },
    {
      icon: Award,
      value: "50+",
      label: "Projects",
    },
    {
      icon: Clock,
      value: "10+",
      label: "Years Experience",
    },
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <UniversalHero
          title={t("services.consulting.title")}
          subtitle={t("consultingPage.about.paragraph1")}
          actions={heroActions}
          stats={heroStats}
        />

        {/* About Section */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold text-center mb-8">About Our Consulting Services</h2>
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <p className="text-muted-foreground mb-4">
                    We are a team of experienced AI consultants dedicated to helping businesses 
                    leverage the power of artificial intelligence. Our mission is to provide you 
                    with the expertise and guidance you need to succeed in the digital age.
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">
                    With a focus on practical solutions and measurable results, we partner with 
                    you to develop and implement AI strategies that drive growth, improve efficiency, 
                    and create a competitive advantage.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Services Section */}
        <section className="py-16 bg-muted/50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Our Consulting Services</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                We offer a range of consulting services to help you at every stage of your AI journey.
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {services.map((service, index) => (
                <Card key={index} className="hover-lift">
                  <CardHeader>
                    <service.icon className="h-12 w-12 text-primary mb-4" />
                    <CardTitle className="text-lg">{service.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground text-sm">{service.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Case Studies Section */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Case Studies</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                See how we've helped other businesses succeed with our AI consulting services.
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-6">
              {caseStudies.map((study, index) => (
                <Card key={index} className="hover-lift">
                  <CardHeader>
                    <div className="flex justify-between items-start mb-2">
                      <CardTitle className="text-lg">{study.title}</CardTitle>
                      <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                        {study.industry}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground text-sm">{study.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-primary/5">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
              Contact us today to learn more about our AI consulting services and how we can help your business succeed.
            </p>
            <Button size="lg" className="btn-primary">
              Contact Us
            </Button>
          </div>
        </section>
      </main>
      <EnhancedFooter />
    </div>
  )
}