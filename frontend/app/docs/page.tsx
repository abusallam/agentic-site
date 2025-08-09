"use client"

import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { UniversalHero } from "@/components/layout/universal-hero"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { BookOpen, Code, Zap, Users, ArrowRight, FileText, Layers, Settings } from "lucide-react"

export default function DocsPage() {
  const { t } = useEnhancedTranslation()
  const docSections = [
    {
      title: "Getting Started",
      description: "Quick start guide to begin your AI journey",
      icon: Zap,
      items: ["Setup Guide", "First Steps", "Basic Configuration"],
      badge: "Essential"
    },
    {
      title: "API Documentation",
      description: "Complete API reference and integration guides",
      icon: Code,
      items: ["REST API", "Authentication", "Rate Limits", "Examples"],
      badge: "Technical"
    },
    {
      title: "AI Services",
      description: "Documentation for our AI consulting services",
      icon: BookOpen,
      items: ["Chatbot Development", "AI Agent Creation", "Custom Solutions"],
      badge: "Services"
    },
    {
      title: "Support",
      description: "Get help and connect with our team",
      icon: Users,
      items: ["FAQ", "Contact Support", "Community", "Training"],
      badge: "Help"
    }
  ]

  const heroActions = [
    {
      label: "Quick Start Guide",
      href: "#getting-started",
      variant: "default" as const,
      icon: ArrowRight,
    },
    {
      label: "API Reference",
      href: "#api",
      variant: "outline" as const,
    },
  ]

  const heroStats = [
    {
      icon: FileText,
      value: "50+",
      label: "Guides",
    },
    {
      icon: Layers,
      value: "20+",
      label: "APIs",
    },
    {
      icon: Settings,
      value: "100+",
      label: "Examples",
    },
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <UniversalHero
          title={t("nav.documentation")}
          subtitle="Everything you need to know about our AI consulting services and how to integrate them into your business."
          actions={heroActions}
          stats={heroStats}
        />

        {/* Documentation Sections */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {docSections.map((section, index) => (
                <Card key={index} className="hover-lift">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                          <section.icon className="h-6 w-6 text-primary" />
                        </div>
                        <CardTitle className="text-xl">{section.title}</CardTitle>
                      </div>
                      <Badge variant="secondary">{section.badge}</Badge>
                    </div>
                    <p className="text-muted-foreground">{section.description}</p>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {section.items.map((item, itemIndex) => (
                        <li key={itemIndex} className="flex items-center gap-2 text-sm">
                          <ArrowRight className="h-3 w-3 text-primary" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                    <Button variant="outline" className="w-full mt-4">
                      Explore {section.title}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Coming Soon Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-2xl mx-auto text-center space-y-6">
              <h2 className="text-3xl font-bold">More Documentation Coming Soon</h2>
              <p className="text-muted-foreground">
                We're continuously expanding our documentation to help you get the most out of our AI services.
                Check back regularly for updates and new guides.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild>
                  <a href="/contact">Request Documentation</a>
                </Button>
                <Button variant="outline" asChild>
                  <a href="/services">View Services</a>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>
      <EnhancedFooter />
    </div>
  )
}