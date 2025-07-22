"use client"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { ArrowRight, Users, CheckCircle, Clock, Star } from "lucide-react"
import { cn } from "@/lib/utils"

export function EnhancedHeroSection() {
  const { t, isRTL } = useEnhancedTranslation()

  const stats = [
    {
      icon: Users,
      value: "500+",
      label: "Happy Clients",
    },
    {
      icon: CheckCircle,
      value: "1000+",
      label: "Projects Completed",
    },
    {
      icon: Clock,
      value: "10+",
      label: "Years Experience",
    },
    {
      icon: Star,
      value: "98%",
      label: "Client Satisfaction",
    },
  ]

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden hero-background">
      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/10 rounded-full blur-3xl animate-float-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-float-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/2 right-1/3 w-32 h-32 bg-accent/10 rounded-full blur-2xl animate-float" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {/* Main Content */}
          <div className="space-y-6 animate-fade-in-up">
            <h1
              className={cn(
                "hero-title text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight",
                "bg-gradient-to-r from-foreground via-primary to-secondary bg-clip-text text-transparent",
              )}
            >
              Transform Your Business with AI Solutions
            </h1>

            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Professional AI consulting services and cutting-edge SaaS solutions for modern businesses
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              size="lg"
              className="group bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary"
            >
              Get Started
              <ArrowRight
                className={cn(
                  "ml-2 h-4 w-4 transition-transform group-hover:translate-x-1",
                  isRTL && "ml-0 mr-2 group-hover:-translate-x-1",
                )}
              />
            </Button>
            <Button size="lg" variant="outline" className="hover-lift bg-transparent">
              Learn More
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-16">
            {stats.map((stat, index) => (
              <Card
                key={index}
                className="hover-lift glass-effect border-0 bg-background/50 animate-fade-in-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <CardContent className="p-6 text-center">
                  <stat.icon className="h-8 w-8 mx-auto mb-3 text-primary" />
                  <div className="text-2xl font-bold text-foreground mb-1">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-muted-foreground/30 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-muted-foreground/50 rounded-full mt-2 animate-pulse" />
        </div>
      </div>
    </section>
  )
}
