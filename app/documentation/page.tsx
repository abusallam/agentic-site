"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { HeroBackground } from "@/components/layout/hero-background"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight, Book, Code, Cpu, Database, FileText, Globe, Lightbulb, Settings, Zap } from "lucide-react"

export default function DocumentationPage() {
  const { locale, isRTL } = useEnhancedTranslation()

  const documentationSections = [
    {
      icon: Book,
      title: "Getting Started",
      titleArabic: "البدء",
      description: "Learn the basics of our AI platform and how to get started",
      descriptionArabic: "تعلم أساسيات منصة الذكاء الاصطناعي وكيفية البدء",
      articles: ["Quick Start Guide", "Platform Overview", "Account Setup"],
      articlesArabic: ["دليل البدء السريع", "نظرة عامة على المنصة", "إعداد الحساب"],
    },
    {
      icon: Code,
      title: "API Documentation",
      titleArabic: "توثيق API",
      description: "Complete API reference and integration guides",
      descriptionArabic: "مرجع API كامل وأدلة التكامل",
      articles: ["REST API", "Authentication", "Rate Limits", "SDKs"],
      articlesArabic: ["REST API", "المصادقة", "حدود المعدل", "مجموعات التطوير"],
    },
    {
      icon: Cpu,
      title: "AI Agents",
      titleArabic: "وكلاء الذكاء الاصطناعي",
      description: "Build and deploy intelligent AI agents",
      descriptionArabic: "بناء ونشر وكلاء الذكاء الاصطناعي الذكية",
      articles: ["Agent Architecture", "Training Models", "Deployment", "Monitoring"],
      articlesArabic: ["هندسة الوكيل", "تدريب النماذج", "النشر", "المراقبة"],
    },
    {
      icon: Zap,
      title: "Chatbots",
      titleArabic: "روبوتات المحادثة",
      description: "Create conversational AI interfaces",
      descriptionArabic: "إنشاء واجهات الذكاء الاصطناعي التحاورية",
      articles: ["Bot Builder", "Natural Language Processing", "Integration", "Analytics"],
      articlesArabic: ["منشئ البوت", "معالجة اللغة الطبيعية", "التكامل", "التحليلات"],
    },
    {
      icon: Database,
      title: "Data Management",
      titleArabic: "إدارة البيانات",
      description: "Manage and process your data effectively",
      descriptionArabic: "إدارة ومعالجة بياناتك بفعالية",
      articles: ["Data Import", "Processing Pipelines", "Storage", "Security"],
      articlesArabic: ["استيراد البيانات", "خطوط المعالجة", "التخزين", "الأمان"],
    },
    {
      icon: Settings,
      title: "Configuration",
      titleArabic: "التكوين",
      description: "Configure and customize your AI solutions",
      descriptionArabic: "تكوين وتخصيص حلول الذكاء الاصطناعي",
      articles: ["Environment Setup", "Custom Models", "Workflows", "Integrations"],
      articlesArabic: ["إعداد البيئة", "النماذج المخصصة", "سير العمل", "التكاملات"],
    },
  ]

  const quickLinks = [
    {
      title: "API Reference",
      titleArabic: "مرجع API",
      description: "Complete API documentation",
      descriptionArabic: "توثيق API كامل",
      href: "/docs/api",
      icon: Code,
    },
    {
      title: "Tutorials",
      titleArabic: "الدروس التعليمية",
      description: "Step-by-step guides",
      descriptionArabic: "أدلة خطوة بخطوة",
      href: "/docs/tutorials",
      icon: Book,
    },
    {
      title: "Examples",
      titleArabic: "الأمثلة",
      description: "Code examples and samples",
      descriptionArabic: "أمثلة الكود والعينات",
      href: "/docs/examples",
      icon: FileText,
    },
    {
      title: "Support",
      titleArabic: "الدعم",
      description: "Get help and support",
      descriptionArabic: "احصل على المساعدة والدعم",
      href: "/contact",
      icon: Lightbulb,
    },
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        {/* Hero Section */}
        <HeroBackground className="py-20">
          <div className="max-w-4xl mx-auto text-center space-y-6">
            <h1 className={cn(
              "text-4xl sm:text-5xl lg:text-6xl font-bold font-heading leading-tight",
              "bg-gradient-to-r from-foreground via-primary to-secondary bg-clip-text text-transparent"
            )}>
              {locale === "ar" ? "التوثيق" : "Documentation"}
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              {locale === "ar" 
                ? "دليل شامل لمنصة الذكاء الاصطناعي الخاصة بنا، بما في ذلك واجهات برمجة التطبيقات والأدلة والأمثلة"
                : "Comprehensive guide to our AI platform, including APIs, guides, and examples"
              }
            </p>
          </div>
        </HeroBackground>

        {/* Quick Links */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                  {locale === "ar" ? "روابط سريعة" : "Quick Links"}
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  {locale === "ar" 
                    ? "ابدأ بهذه الموارد الأساسية"
                    : "Get started with these essential resources"
                  }
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
                {quickLinks.map((link, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up text-center"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardContent className="p-6">
                      <div className="flex flex-col items-center space-y-4">
                        <div className="p-3 rounded-full bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <link.icon className="h-6 w-6 text-primary" />
                        </div>
                        <div className="space-y-2">
                          <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                            {locale === "ar" ? link.titleArabic : link.title}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {locale === "ar" ? link.descriptionArabic : link.description}
                          </p>
                        </div>
                        <Button variant="ghost" size="sm" className="text-primary hover:text-primary/80">
                          {locale === "ar" ? "اعرف المزيد" : "Learn More"}
                          <ArrowRight className={cn("h-3 w-3", isRTL ? "mr-1" : "ml-1")} />
                        </Button>
                      </div>
                    </CardContent>
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Documentation Sections */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                  {locale === "ar" ? "أقسام التوثيق" : "Documentation Sections"}
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  {locale === "ar" 
                    ? "استكشف دليلنا الشامل لجميع ميزات المنصة"
                    : "Explore our comprehensive guide to all platform features"
                  }
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {documentationSections.map((section, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardHeader className="pb-4">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <section.icon className="h-6 w-6 text-primary" />
                        </div>
                      </div>
                      <CardTitle className="text-xl group-hover:text-primary transition-colors">
                        {locale === "ar" ? section.titleArabic : section.title}
                      </CardTitle>
                      <CardDescription className="text-base">
                        {locale === "ar" ? section.descriptionArabic : section.description}
                      </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <h4 className="font-medium text-sm text-muted-foreground">
                          {locale === "ar" ? "المقالات:" : "Articles:"}
                        </h4>
                        <ul className="space-y-1">
                          {(locale === "ar" ? section.articlesArabic : section.articles).map((article, articleIndex) => (
                            <li key={articleIndex} className="text-sm text-muted-foreground hover:text-primary transition-colors cursor-pointer">
                              • {article}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <Button variant="ghost" size="sm" className="w-full text-primary hover:text-primary/80">
                        {locale === "ar" ? "استكشف القسم" : "Explore Section"}
                        <ArrowRight className={cn("h-3 w-3", isRTL ? "mr-1" : "ml-1")} />
                      </Button>
                    </CardContent>

                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center space-y-8">
              <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                {locale === "ar" ? "هل تحتاج إلى مساعدة؟" : "Need Help?"}
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                {locale === "ar" 
                  ? "لا يمكنك العثور على ما تبحث عنه؟ فريق الدعم لدينا هنا لمساعدتك."
                  : "Can't find what you're looking for? Our support team is here to help."
                }
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button size="lg" className="btn-gradient">
                  {locale === "ar" ? "اتصل بالدعم" : "Contact Support"}
                  <ArrowRight className={cn("h-4 w-4", isRTL ? "mr-2" : "ml-2")} />
                </Button>
                <Button size="lg" variant="outline" className="bg-background/50">
                  {locale === "ar" ? "انضم إلى المجتمع" : "Join Community"}
                  <Globe className={cn("h-4 w-4", isRTL ? "mr-2" : "ml-2")} />
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>
      <EnhancedFooter />
    </div>
  )
}