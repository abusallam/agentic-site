"use client"

import * as React from "react"
import Link from "next/link"
import Image from "next/image"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { brandConfig } from "@/lib/brand"
import { cn } from "@/lib/utils"

interface EnhancedLogoProps {
  variant?: "horizontal" | "vertical"
  size?: "sm" | "md" | "lg" | "xl"
  showText?: boolean
  className?: string
}

export function EnhancedLogo({ 
  variant = "vertical", 
  size = "md", 
  showText = true,
  className 
}: EnhancedLogoProps) {
  const { locale } = useEnhancedTranslation()

  const sizeConfig = {
    sm: { width: 24, height: 24, textSize: "text-sm" },
    md: { width: 40, height: 40, textSize: "text-base" },
    lg: { width: 56, height: 56, textSize: "text-lg" },
    xl: { width: 72, height: 72, textSize: "text-xl" }
  }

  const config = sizeConfig[size]
  const brandName = locale === "ar" ? brandConfig.nameArabic : brandConfig.name

  return (
    <Link 
      href="/" 
      className={cn(
        "group transition-all duration-300 hover:scale-105",
        variant === "vertical" ? "flex flex-col items-center gap-2" : "flex items-center gap-3",
        className
      )}
    >
      {/* Logo Image */}
      <div className="relative">
        <Image
          src="/pics/logo-main-512.webp"
          alt={brandConfig.name}
          width={config.width}
          height={config.height}
          className="transition-transform duration-300 group-hover:scale-110 drop-shadow-sm"
          priority
        />
      </div>
      
      {/* Brand Text */}
      {showText && (
        <div className={cn(
          "font-bold font-heading bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent transition-all duration-300",
          config.textSize,
          variant === "vertical" ? "text-center" : "whitespace-nowrap"
        )}>
          {brandName}
        </div>
      )}
    </Link>
  )
}