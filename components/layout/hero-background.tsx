"use client"
import { cn } from "@/lib/utils"

interface HeroBackgroundProps {
  children: React.ReactNode
  className?: string
  showScrollIndicator?: boolean
}

export function HeroBackground({ children, className, showScrollIndicator = false }: HeroBackgroundProps) {
  return (
    <section className={cn("relative min-h-screen flex items-center justify-center overflow-hidden hero-background", className)}>
      {/* Background with Image */}
      <div className="absolute inset-0">
        <div
          className="absolute inset-0 opacity-40 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: "url('/bg1.webp')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background/80 via-background/60 to-background/80" />
        <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-background/50" />
      </div>
      
      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/10 rounded-full blur-3xl animate-float-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-float-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/2 right-1/3 w-32 h-32 bg-accent/10 rounded-full blur-2xl animate-float" />
        <div className="absolute top-3/4 left-1/3 w-48 h-48 bg-primary/5 rounded-full blur-2xl animate-float-slow" style={{ animationDelay: '4s' }} />
      </div>

      {/* Gradient Overlay for better text readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/20 to-background/40" />

      {/* Content */}
      <div className="container mx-auto px-4 relative z-10">
        {children}
      </div>

      {/* Scroll Indicator */}
      {showScrollIndicator && (
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce z-20">
          <div className="w-6 h-10 border-2 border-muted-foreground/30 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-muted-foreground/50 rounded-full mt-2 animate-pulse" />
          </div>
        </div>
      )}
    </section>
  )
}