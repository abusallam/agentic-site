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
        <div className="space-y-8 animate-fade-in-up">
          <h1
            className={cn(
              "hero-title text-4xl sm:text-5xl lg:text-7xl xl:text-8xl font-bold leading-tight tracking-tight",
              "drop-shadow-2xl"
            )}
          >
            {title}
          </h1>

          <p className="text-lg sm:text-xl lg:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed animate-fade-in-up stagger-2 font-light">
            {subtitle}
          </p>
        </div>

        {/* CTA Buttons */}
        {actions.length > 0 && (
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center animate-fade-in-up stagger-3">
            {actions.map((action, index) => (
              <Button
                key={index}
                size="lg"
                variant={action.variant || "default"}
                className={cn(
                  "group relative overflow-hidden px-8 py-4 text-lg font-semibold transition-all duration-300",
                  "hover:scale-105 hover:shadow-2xl",
                  action.variant === "default" && [
                    "bg-gradient-to-r from-primary via-primary/90 to-secondary",
                    "hover:from-primary/90 hover:via-primary hover:to-secondary/90",
                    "shadow-lg shadow-primary/25 hover:shadow-primary/40",
                    "interactive-glow"
                  ],
                  action.variant === "outline" && [
                    "hover-lift bg-transparent border-2 border-primary/50",
                    "hover:border-primary hover:bg-primary/10",
                    "backdrop-blur-sm"
                  ]
                )}
                onClick={action.onClick}
                asChild={!!action.href}
              >
                {action.href ? (
                  <a href={action.href} className="flex items-center">
                    {action.label}
                    {action.icon && (
                      <action.icon
                        className={cn(
                          "ml-3 h-5 w-5 transition-all duration-300 group-hover:translate-x-1 group-hover:scale-110",
                          isRTL && "ml-0 mr-3 group-hover:-translate-x-1",
                        )}
                      />
                    )}
                  </a>
                ) : (
                  <span className="flex items-center">
                    {action.label}
                    {action.icon && (
                      <action.icon
                        className={cn(
                          "ml-3 h-5 w-5 transition-all duration-300 group-hover:translate-x-1 group-hover:scale-110",
                          isRTL && "ml-0 mr-3 group-hover:-translate-x-1",
                        )}
                      />
                    )}
                  </span>
                )}
              </Button>
            ))}
          </div>
        )}

        {/* Enhanced Stats Cards */}
        {stats.length > 0 && (
          <div className={cn(
            "grid gap-6 mt-20 animate-fade-in-up stagger-4",
            stats.length <= 3 ? "grid-cols-1 md:grid-cols-3" : 
            stats.length <= 4 ? "grid-cols-2 md:grid-cols-4" : 
            "grid-cols-2 md:grid-cols-3 lg:grid-cols-5"
          )}>
            {stats.map((stat, index) => (
              <Card
                key={index}
                className={cn(
                  "group relative overflow-hidden",
                  "hover-lift glass-effect border-0 bg-background/40 backdrop-blur-md",
                  "hover:bg-background/60 hover:shadow-xl hover:shadow-primary/10",
                  "transition-all duration-500 animate-scale-in",
                  "before:absolute before:inset-0 before:bg-gradient-to-br before:from-primary/5 before:to-secondary/5",
                  "before:opacity-0 before:transition-opacity before:duration-300 hover:before:opacity-100"
                )}
                style={{ animationDelay: `${(index + 4) * 150}ms` }}
              >
                <CardContent className="relative p-8 text-center">
                  <div className="relative">
                    <stat.icon className={cn(
                      "h-10 w-10 mx-auto mb-4 transition-all duration-300",
                      "text-primary group-hover:text-primary/80 group-hover:scale-110",
                      "drop-shadow-sm"
                    )} />
                    
                    <div className={cn(
                      "text-3xl font-bold text-foreground mb-2 transition-all duration-300",
                      "group-hover:scale-105 bg-gradient-to-br from-foreground to-foreground/80 bg-clip-text"
                    )}>
                      {stat.value}
                    </div>
                    
                    <div className={cn(
                      "text-sm text-muted-foreground font-medium transition-colors duration-300",
                      "group-hover:text-muted-foreground/80"
                    )}>
                      {stat.label}
                    </div>
                  </div>
                  
                  {/* Subtle glow effect on hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-secondary/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-lg" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </HeroBackground>
  )
}