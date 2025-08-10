"use client"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"

interface HeroBackgroundProps {
  children: React.ReactNode
  className?: string
  showScrollIndicator?: boolean
}

export function HeroBackground({ children, className, showScrollIndicator = false }: HeroBackgroundProps) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
    
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100,
      })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <section className={cn("relative min-h-screen flex items-center justify-center overflow-hidden hero-background", className)}>
      {/* Enhanced Background with Parallax Effect */}
      <div className="absolute inset-0">
        <div
          className="absolute inset-0 opacity-50 bg-cover bg-center bg-no-repeat transition-transform duration-1000 ease-out"
          style={{
            backgroundImage: "url('/bg1.webp')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
            transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02}px) scale(1.05)`,
          }}
        />
        
        {/* Enhanced Gradient Overlays */}
        <div className="absolute inset-0 bg-gradient-to-br from-background/85 via-background/65 to-background/85" />
        <div className="absolute inset-0 bg-gradient-to-t from-background/95 via-transparent to-background/60" />
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-secondary/5" />
      </div>
      
      {/* Enhanced Floating Elements with Interactive Movement */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Primary floating orbs */}
        <div 
          className="absolute top-1/4 left-1/4 w-72 h-72 bg-gradient-to-br from-primary/15 to-primary/5 rounded-full blur-3xl animate-float-slow transition-transform duration-300"
          style={{
            transform: `translate(${mousePosition.x * 0.05}px, ${mousePosition.y * 0.05}px)`,
          }}
        />
        <div 
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-to-br from-secondary/15 to-secondary/5 rounded-full blur-3xl animate-float-slow transition-transform duration-500"
          style={{ 
            animationDelay: '2s',
            transform: `translate(${mousePosition.x * -0.03}px, ${mousePosition.y * -0.03}px)`,
          }}
        />
        
        {/* Secondary floating elements */}
        <div 
          className="absolute top-1/2 right-1/3 w-40 h-40 bg-gradient-to-br from-accent/20 to-accent/5 rounded-full blur-2xl animate-float transition-transform duration-700"
          style={{
            transform: `translate(${mousePosition.x * 0.08}px, ${mousePosition.y * 0.08}px)`,
          }}
        />
        <div 
          className="absolute top-3/4 left-1/3 w-56 h-56 bg-gradient-to-br from-primary/10 to-primary/2 rounded-full blur-2xl animate-float-slow transition-transform duration-400"
          style={{ 
            animationDelay: '4s',
            transform: `translate(${mousePosition.x * -0.06}px, ${mousePosition.y * -0.06}px)`,
          }}
        />
        
        {/* Additional ambient elements */}
        <div 
          className="absolute top-1/6 right-1/6 w-24 h-24 bg-gradient-to-br from-secondary/25 to-secondary/5 rounded-full blur-xl animate-pulse transition-transform duration-600"
          style={{
            transform: `translate(${mousePosition.x * 0.1}px, ${mousePosition.y * 0.1}px)`,
          }}
        />
        <div 
          className="absolute bottom-1/6 left-1/6 w-32 h-32 bg-gradient-to-br from-accent/15 to-accent/3 rounded-full blur-xl animate-pulse transition-transform duration-800"
          style={{ 
            animationDelay: '1s',
            transform: `translate(${mousePosition.x * -0.04}px, ${mousePosition.y * -0.04}px)`,
          }}
        />
      </div>

      {/* Animated Grid Pattern */}
      <div className="absolute inset-0 opacity-[0.02] pointer-events-none">
        <div 
          className="absolute inset-0 bg-grid-pattern animate-grid-flow"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      {/* Enhanced Gradient Overlay for better text readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/25 to-background/50" />
      <div className="absolute inset-0 bg-radial-gradient from-transparent via-background/10 to-background/30" />

      {/* Content with enhanced entrance animation */}
      <div className={cn(
        "container mx-auto px-4 relative z-10 transition-all duration-1000",
        isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      )}>
        {children}
      </div>

      {/* Enhanced Scroll Indicator */}
      {showScrollIndicator && (
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-20">
          <div className="flex flex-col items-center space-y-2 animate-bounce">
            <div className="w-6 h-10 border-2 border-muted-foreground/40 rounded-full flex justify-center relative overflow-hidden">
              <div className="w-1 h-3 bg-gradient-to-b from-primary to-secondary rounded-full mt-2 animate-scroll-indicator" />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/20 to-transparent animate-pulse" />
            </div>
            <div className="text-xs text-muted-foreground/60 font-medium tracking-wider uppercase">
              Scroll
            </div>
          </div>
        </div>
      )}

      {/* Ambient Light Effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 w-96 h-96 bg-gradient-radial from-primary/10 via-primary/5 to-transparent blur-3xl transform -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 right-0 w-80 h-80 bg-gradient-radial from-secondary/10 via-secondary/5 to-transparent blur-3xl transform translate-x-1/4 translate-y-1/4" />
      </div>
    </section>
  )
}