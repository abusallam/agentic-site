"use client"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { Bot, MessageSquare, Brain, ArrowRight, Check } from "lucide-react"
import { cn } from "@/lib/utils"

export function EnhancedServicesSection() {
  const { t, isRTL } = useEnhancedTranslation()

  const services = [
    {
      icon: Bot,
      title: "AI Agents",
      description: "Intelligent automation solutions",
      href: "/ai-agents",
      features: [
        "Intelligent Process Automation",
        "Custom AI Workflows",
        "24/7 Autonomous Operations",
        "Advanced Analytics",
      ],
      badge: "Popular",
    },
    {
      icon: MessageSquare,
      title: "Chatbots",
      description: "Conversational AI interfaces",
      href: "/chatbots",
      features: ["Natural Language Processing", "Multi-language Support", "Integration Ready", "Real-time Learning"],
      badge: "New",
    },
    {
      icon: Brain,
      title: "AI Consulting",
      description: "Strategic AI implementation guidance",
      href: "/consulting",
      features: ["Strategic AI Planning", "Implementation Guidance", "Team Training", "Ongoing Support"],
      badge: "Premium",
    },
  ]

  return (
    <section className="section-padding bg-muted/20">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16 space-y-4">
            <h2 className="text-3xl sm:text-4xl font-bold font-heading gradient-text">Our AI Solutions</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">Comprehensive AI services to accelerate your digital transformation</p>
          </div>

          {/* Services Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <Card
                key={index}
                className="group service-card glass-effect-enhanced border-0 bg-background/60 relative overflow-hidden animate-fade-in-up"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                {/* Badge */}
                {service.badge && (
                  <Badge
                    className={cn("absolute top-4 z-10", isRTL ? "left-4" : "right-4")}
                    variant={
                      service.badge === "Popular" ? "default" : service.badge === "New" ? "secondary" : "outline"
                    }
                  >
                    {service.badge}
                  </Badge>
                )}

                <CardHeader className="pb-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                      <service.icon className="h-6 w-6 text-primary" />
                    </div>
                  </div>
                  <CardTitle className="text-xl group-hover:text-primary transition-colors">{service.title}</CardTitle>
                  <CardDescription className="text-base">{service.description}</CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Features List */}
                  <ul className="space-y-2">
                    {service.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center gap-2 text-sm">
                        <Check className="h-4 w-4 text-primary flex-shrink-0" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <Button
                    asChild
                    variant="outline"
                    className="w-full group-hover:bg-primary group-hover:text-primary-foreground transition-colors bg-transparent"
                  >
                    <Link href={service.href} className="flex items-center justify-center gap-2">
                      Learn More
                      <ArrowRight
                        className={cn(
                          "h-4 w-4 transition-transform group-hover:translate-x-1",
                          isRTL && "group-hover:-translate-x-1",
                        )}
                      />
                    </Link>
                  </Button>
                </CardContent>

                {/* Hover Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
