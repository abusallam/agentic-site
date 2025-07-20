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
  ]

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-muted/20">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: "url('/bg1.webp')",
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
      </div>

      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl animate-pulse delay-1000" />
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
              {t("hero.title")}
            </h1>

            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              {t("hero.subtitle")}
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              size="lg"
              className="group bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary"
            >
              {t("hero.cta.primary")}
              <ArrowRight
                className={cn(
                  "ml-2 h-4 w-4 transition-transform group-hover:translate-x-1",
                  isRTL && "ml-0 mr-2 group-hover:-translate-x-1",
                )}
              />
            </Button>
            <Button size="lg" variant="outline" className="hover-lift bg-transparent">
              {t("hero.cta.secondary")}
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
