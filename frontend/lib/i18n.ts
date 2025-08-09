"use client"

import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react"

export type Locale = "en" | "ar"

// Static translations object
const translations = {
  en: {
    nav: {
      home: "Home",
      aiAgents: "AI Agents",
      chatbots: "Chatbots",
      consulting: "Consulting",
      getStarted: "Get Started",
    },
    hero: {
      badge: "Next-Generation AI Solutions",
      title: "Transform Your Business with",
      titleHighlight: "AI Agents",
      description:
        "Powerful AI chatbots and intelligent agents that automate workflows, enhance customer experience, and drive business growth with cutting-edge technology.",
      startTrial: "Start Free Trial",
      watchDemo: "Watch Demo",
      smartAgents: "Smart AI Agents",
      smartAgentsDesc: "Intelligent automation that learns and adapts to your business needs",
      enterpriseSecurity: "Enterprise Security",
      enterpriseSecurityDesc: "Bank-level security with SSL encryption and data protection",
      lightningFast: "Lightning Fast",
      lightningFastDesc: "Deploy AI solutions in minutes, not months",
    },
    consulting: {
      badge: "Expert AI Consultant",
      title: "Asim Abu Salam",
      subtitle: "AI Strategy & Implementation Expert",
      description:
        "Transform your business with strategic AI consulting. Get expert guidance on AI implementation, automation strategies, and digital transformation from a seasoned professional with proven results.",
      scheduleConsultation: "Schedule Consultation",
      viewPortfolio: "View Portfolio",
      yearsExperience: "Years of AI Experience",
      successfulProjects: "Successful Projects",
      averageROI: "Average ROI Increase",
    },
  },
  ar: {
    nav: {
      home: "الرئيسية",
      aiAgents: "وكلاء الذكاء الاصطناعي",
      chatbots: "روبوتات المحادثة",
      consulting: "الاستشارات",
      getStarted: "ابدأ الآن",
    },
    hero: {
      badge: "حلول الذكاء الاصطناعي من الجيل التالي",
      title: "حوّل عملك مع",
      titleHighlight: "وكلاء الذكاء الاصطناعي",
      description:
        "روبوتات محادثة قوية ووكلاء ذكيون يؤتمتون سير العمل ويعززون تجربة العملاء ويدفعون نمو الأعمال بتقنية متطورة.",
      startTrial: "ابدأ التجربة المجانية",
      watchDemo: "شاهد العرض التوضيحي",
      smartAgents: "وكلاء ذكيون",
      smartAgentsDesc: "أتمتة ذكية تتعلم وتتكيف مع احتياجات عملك",
      enterpriseSecurity: "أمان المؤسسات",
      enterpriseSecurityDesc: "أمان على مستوى البنوك مع تشفير SSL وحماية البيانات",
      lightningFast: "سريع البرق",
      lightningFastDesc: "انشر حلول الذكاء الاصطناعي في دقائق وليس شهور",
    },
    consulting: {
      badge: "خبير استشاري في الذكاء الاصطناعي",
      title: "عاصم أبو سلام",
      subtitle: "خبير استراتيجية وتنفيذ الذكاء الاصطناعي",
      description:
        "حوّل عملك مع الاستشارات الاستراتيجية في الذكاء الاصطناعي. احصل على إرشادات خبيرة في تنفيذ الذكاء الاصطناعي واستراتيجيات الأتمتة والتحول الرقمي من محترف متمرس بنتائج مثبتة.",
      scheduleConsultation: "احجز استشارة",
      viewPortfolio: "اعرض الأعمال",
      yearsExperience: "سنوات من الخبرة في الذكاء الاصطناعي",
      successfulProjects: "مشاريع ناجحة",
      averageROI: "متوسط زيادة العائد على الاستثمار",
    },
  },
} as const

interface I18nContextType {
  locale: Locale
  t: (key: string) => string
  changeLanguage: (newLocale: Locale) => void
}

const I18nContext = createContext<I18nContextType | undefined>(undefined)

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>("en")
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
    // Get locale from localStorage or browser language
    try {
      const savedLocale = localStorage.getItem("locale") as Locale
      const browserLocale = navigator.language.startsWith("ar") ? "ar" : "en"
      const initialLocale = savedLocale || browserLocale

      if (initialLocale === "ar" || initialLocale === "en") {
        setLocale(initialLocale)
        document.documentElement.lang = initialLocale
        document.documentElement.dir = initialLocale === "ar" ? "rtl" : "ltr"
      }
    } catch (error) {
      console.warn("Error setting initial locale:", error)
      setLocale("en")
    }
  }, [])

  const t = (key: string): string => {
    try {
      const keys = key.split(".")
      let value: any = translations[locale]

      for (const k of keys) {
        value = value?.[k]
      }

      return value || key
    } catch (error) {
      console.warn("Translation error for key:", key, error)
      return key
    }
  }

  const changeLanguage = (newLocale: Locale) => {
    try {
      setLocale(newLocale)
      if (isClient) {
        localStorage.setItem("locale", newLocale)
        document.documentElement.lang = newLocale
        document.documentElement.dir = newLocale === "ar" ? "rtl" : "ltr"
      }
    } catch (error) {
      console.warn("Error changing language:", error)
    }
  }

  return React.createElement(I18nContext.Provider, { value: { locale, t, changeLanguage } }, children)
}

export function useTranslation() {
  const context = useContext(I18nContext)
  if (context === undefined) {
    // Return a safe fallback instead of throwing
    return {
      locale: "en" as Locale,
      t: (key: string) => key,
      changeLanguage: () => {},
    }
  }
  return context
}

// For server-side usage
export function getStaticTranslations(locale: Locale) {
  return translations[locale] || translations.en
}
