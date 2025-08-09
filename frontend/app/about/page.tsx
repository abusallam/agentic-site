"use client"

import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { UniversalHero } from "@/components/layout/universal-hero"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { Users, Target, Award, Globe, ArrowRight, Heart, Lightbulb, Shield } from "lucide-react"

export default function AboutPage() {
  const { t } = useEnhancedTranslation()
  const values = [
    {
      icon: Target,
      title: "Innovation",
      description: "We stay at the forefront of AI technology to deliver cutting-edge solutions."
    },
    {
      icon: Users,
      title: "Partnership",
      description: "We work closely with our clients as trusted partners in their digital transformation."
    },
    {
      icon: Award,
      title: "Excellence",
      description: "We maintain the highest standards of quality in everything we do."
    },
    {
      icon: Globe,
      title: "Impact",
      description: "We create solutions that make a meaningful difference for businesses and society."
    }
  ]

  const stats = [
    { number: "500+", label: "Happy Clients" },
    { number: "1000+", label: "Projects Completed" },
    { number: "10+", label: "Years Experience" },
    { number: "98%", label: "Client Satisfaction" }
  ]

  const heroActions = [
    {
      label: "Get Started",
      href: "/contact",
      variant: "default" as const,
      icon: ArrowRight,
    },
    {
      label: "Learn More",
      href: "/services",
      variant: "outline" as const,
    },
  ]

  const heroStats = [
    {
      icon: Heart,
      value: "500+",
      label: "Happy Clients",
    },
    {
      icon: Lightbulb,
      value: "1000+",
      label: "Projects",
    },
    {
      icon: Shield,
      value: "10+",
      label: "Years Experience",
    },
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <UniversalHero
          title={`About ${t("contact.name")}`}
          subtitle="We are passionate about helping businesses harness the power of artificial intelligence to transform their operations and achieve unprecedented growth."
          actions={heroActions}
          stats={heroStats}
        />

        {/* Mission Section */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-3xl font-bold mb-8">Our Mission</h2>
              <p className="text-lg text-muted-foreground mb-8">
                To democratize artificial intelligence by making advanced AI solutions accessible 
                to businesses of all sizes, helping them innovate, grow, and compete in the digital economy.
              </p>
              <div className="grid md:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                  <Card key={index} className="text-center">
                    <CardContent className="pt-6">
                      <div className="text-3xl font-bold text-primary mb-2">{stat.number}</div>
                      <div className="text-sm text-muted-foreground">{stat.label}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Founder Section */}
        <section className="py-16 bg-muted/50">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <div className="grid md:grid-cols-2 gap-12 items-center">
                <div>
                  <h2 className="text-3xl font-bold mb-6">Meet Our Founder</h2>
                  <h3 className="text-xl font-semibold mb-2">Asim Abu Salam</h3>
                  <Badge variant="secondary" className="mb-4">Founder & AI Consultant</Badge>
                  <p className="text-muted-foreground mb-4">
                    With over 10 years of experience in artificial intelligence and digital transformation, 
                    Asim has helped hundreds of businesses successfully implement AI solutions that drive 
                    real business value.
                  </p>
                  <p className="text-muted-foreground mb-6">
                    His expertise spans machine learning, natural language processing, computer vision, 
                    and AI strategy development. Asim is passionate about making AI accessible and 
                    practical for businesses across all industries.
                  </p>
                  <Button variant="outline">
                    Connect on LinkedIn
                  </Button>
                </div>
                <div className="text-center">
                  <div className="w-64 h-64 mx-auto bg-gradient-to-br from-primary/20 to-secondary/20 rounded-full flex items-center justify-center">
                    <Users className="h-24 w-24 text-primary" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Values Section */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Our Values</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                These core values guide everything we do and shape how we work with our clients.
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {values.map((value, index) => (
                <Card key={index} className="text-center hover-lift">
                  <CardHeader>
                    <value.icon className="h-12 w-12 text-primary mx-auto mb-4" />
                    <CardTitle className="text-lg">{value.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground text-sm">{value.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Story Section */}
        <section className="py-16 bg-muted/50">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold text-center mb-8">Our Story</h2>
              <div className="prose prose-lg mx-auto text-muted-foreground">
                <p>
                  consulting.sa was founded with a simple yet ambitious vision: to bridge the gap 
                  between cutting-edge AI research and practical business applications. We recognized 
                  that while AI technology was advancing rapidly, many businesses struggled to 
                  understand how to leverage these innovations effectively.
                </p>
                <p>
                  Starting as a small consulting practice in Saudi Arabia, we've grown into a 
                  trusted partner for businesses across the region and beyond. Our success is 
                  built on a foundation of deep technical expertise, practical business acumen, 
                  and an unwavering commitment to our clients' success.
                </p>
                <p>
                  Today, we continue to push the boundaries of what's possible with AI, helping 
                  our clients not just adopt new technologies, but transform their entire approach 
                  to business in the digital age.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-primary/5">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Business?</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
              Let's discuss how we can help you harness the power of AI to achieve your business goals.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="btn-primary">
                Get Started
              </Button>
              <Button size="lg" variant="outline">
                Learn More
              </Button>
            </div>
          </div>
        </section>
      </main>
      <EnhancedFooter />
    </div>
  )
}