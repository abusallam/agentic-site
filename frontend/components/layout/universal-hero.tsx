"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { HeroBackground } from "./hero-background"
import { ArrowRight, LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface HeroAction {
  label: string
  href?: string
  onClick?: () => void
  variant?: "default" | "outline" | "ghost"
  icon?: LucideIcon
}

interface HeroStat {
  icon: LucideIcon
  value: string
  label: string
}

interface UniversalHeroProps {
  title: string
  subtitle: string
  actions?: HeroAction[]
  stats?: HeroStat[]
  showScrollIndicator?: boolean
  className?: string
}

export function UniversalHero({
  title,
  subtitle,
  actions = [],
  stats = [],
  showScrollIndicator = false,
  className
}: UniversalHeroProps) {
  const { isRTL } = useEnhancedTranslation()

  return (
    <HeroBackground showScrollIndicator={showScrollIndicator} className={className}>
      <div className="max-w-4xl mx-auto text-center space-y-8">
        {/* Main Content */}
        <div className="space-y-6 animate-fade-in-up">
          <h1
            className={cn(
              "hero-title text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight",
              "bg-gradient-to-r from-foreground via-primary to-secondary bg-clip-text text-transparent",
            )}
          >
            {title}
          </h1>

          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            {subtitle}
          </p>
        </div>

        {/* CTA Buttons */}
        {actions.length > 0 && (
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            {actions.map((action, index) => (
              <Button
                key={index}
                size="lg"
                variant={action.variant || "default"}
                className={cn(
                  "group",
                  action.variant === "default" && "bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary",
                  action.variant === "outline" && "hover-lift bg-transparent"
                )}
                onClick={action.onClick}
                asChild={!!action.href}
              >
                {action.href ? (
                  <a href={action.href}>
                    {action.label}
                    {action.icon && (
                      <action.icon
                        className={cn(
                          "ml-2 h-4 w-4 transition-transform group-hover:translate-x-1",
                          isRTL && "ml-0 mr-2 group-hover:-translate-x-1",
                        )}
                      />
                    )}
                  </a>
                ) : (
                  <>
                    {action.label}
                    {action.icon && (
                      <action.icon
                        className={cn(
                          "ml-2 h-4 w-4 transition-transform group-hover:translate-x-1",
                          isRTL && "ml-0 mr-2 group-hover:-translate-x-1",
                        )}
                      />
                    )}
                  </>
                )}
              </Button>
            ))}
          </div>
        )}

        {/* Stats Cards */}
        {stats.length > 0 && (
          <div className={cn(
            "grid gap-4 mt-16",
            stats.length <= 3 ? "grid-cols-1 md:grid-cols-3" : 
            stats.length <= 4 ? "grid-cols-2 md:grid-cols-4" : 
            "grid-cols-2 md:grid-cols-3 lg:grid-cols-5"
          )}>
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
        )}
      </div>
    </HeroBackground>
  )
}