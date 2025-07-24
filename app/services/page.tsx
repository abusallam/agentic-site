"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { HeroBackground } from "@/components/layout/hero-background"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Bot, Brain, Code, Cpu, Database, Globe, MessageSquare, Settings, Smartphone, Users, Zap } from "lucide-react"

export default function ServicesPage() {
  const { t, locale, isRTL } = useEnhancedTranslation()

  const mainServices = [
    {
      icon: Brain,
      title: "AI Consulting",
      titleArabic: "استشارات الذكاء الاصطناعي",
      description: "Strategic AI implementation and planning for your business transformation",
      descriptionArabic: "تنفيذ وتخطيط الذكاء الاصطناعي الاستراتيجي لتحويل أعمالك",
      features: ["AI Strategy Development", "Feasibility Studies", "Implementation Planning", "ROI Analysis"],
      featuresArabic: ["تطوير استراتيجية الذكاء الاصطناعي", "دراسات الجدوى", "تخطيط التنفيذ", "تحليل العائد على الاستثمار"],
      price: "Custom",
      priceArabic: "مخصص",
    },
    {
      icon: MessageSquare,
      title: "Chatbot Development",
      titleArabic: "تطوير روبوتات المحادثة",
      description: "Intelligent conversational AI systems for customer engagement",
      descriptionArabic: "أنظمة ذكاء اصطناعي تحاورية ذكية لتفاعل العملاء",
      features: ["Natural Language Processing", "Multi-platform Integration", "24/7 Customer Support", "Analytics Dashboard"],
      featuresArabic: ["معالجة اللغة الطبيعية", "تكامل متعدد المنصات", "دعم العملاء على مدار الساعة", "لوحة التحليلات"],
      price: "From $2,999",
      priceArabic: "من 2,999 دولار",
    },
    {
      icon: Bot,
      title: "AI Agents",
      titleArabic: "وكلاء الذكاء الاصطناعي",
      description: "Autonomous AI agents for business process automation",
      descriptionArabic: "وكلاء ذكاء اصطناعي مستقلون لأتمتة العمليات التجارية",
      features: ["Process Automation", "Decision Making", "Task Scheduling", "Performance Monitoring"],
      featuresArabic: ["أتمتة العمليات", "اتخاذ القرارات", "جدولة المهام", "مراقبة الأداء"],
      price: "From $4,999",
      priceArabic: "من 4,999 دولار",
    },
  ]

  const additionalServices = [
    {
      icon: Database,
      title: "Data Analytics",
      titleArabic: "تحليل البيانات",
      description: "Advanced data analysis and business intelligence",
      descriptionArabic: "تحليل البيانات المتقدم وذكاء الأعمال",
    },
    {
      icon: Code,
      title: "Custom Development",
      titleArabic: "التطوير المخصص",
      description: "Tailored software solutions for your specific needs",
      descriptionArabic: "حلول برمجية مخصصة لاحتياجاتك المحددة",
    },
    {
      icon: Globe,
      title: "Cloud Integration",
      titleArabic: "تكامل السحابة",
      description: "Seamless cloud migration and integration services",
      descriptionArabic: "خدمات الهجرة والتكامل السحابي السلس",
    },
    {
      icon: Settings,
      title: "System Optimization",
      titleArabic: "تحسين النظام",
      description: "Performance optimization and system enhancement",
      descriptionArabic: "تحسين الأداء وتعزيز النظام",
    },
    {
      icon: Smartphone,
      title: "Mobile Solutions",
      titleArabic: "الحلول المحمولة",
      description: "Mobile app development with AI integration",
      descriptionArabic: "تطوير تطبيقات الهاتف المحمول مع تكامل الذكاء الاصطناعي",
    },
    {
      icon: Users,
      title: "Team Training",
      titleArabic: "تدريب الفريق",
      description: "Comprehensive AI training programs for your team",
      descriptionArabic: "برامج تدريب شاملة للذكاء الاصطناعي لفريقك",
    },
  ]

  const processSteps = [
    {
      step: "01",
      title: "Discovery",
      titleArabic: "الاستكشاف",
      description: "We analyze your business needs and identify AI opportunities",
      descriptionArabic: "نحلل احتياجات عملك ونحدد فرص الذكاء الاصطناعي",
    },
    {
      step: "02",
      title: "Strategy",
      titleArabic: "الاستراتيجية",
      description: "Develop a comprehensive AI implementation strategy",
      descriptionArabic: "تطوير استراتيجية شاملة لتنفيذ الذكاء الاصطناعي",
    },
    {
      step: "03",
      title: "Development",
      titleArabic: "التطوير",
      description: "Build and customize AI solutions for your specific needs",
      descriptionArabic: "بناء وتخصيص حلول الذكاء الاصطناعي لاحتياجاتك المحددة",
    },
    {
      step: "04",
      title: "Deployment",
      titleArabic: "النشر",
      description: "Deploy and integrate solutions into your existing systems",
      descriptionArabic: "نشر ودمج الحلول في أنظمتك الحالية",
    },
    {
      step: "05",
      title: "Support",
      titleArabic: "الدعم",
      description: "Ongoing support and optimization for maximum performance",
      descriptionArabic: "الدعم المستمر والتحسين للحصول على أقصى أداء",
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
              {locale === "ar" ? "خدماتنا" : "Our Services"}
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              {locale === "ar" 
                ? "حلول شاملة للذكاء الاصطناعي لتحويل أعمالك وتسريع نموك"
                : "Comprehensive AI solutions to transform your business and accelerate growth"
              }
            </p>
          </div>
        </HeroBackground>

        {/* Main Services */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                  {locale === "ar" ? "خدماتنا الأساسية" : "Core Services"}
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  {locale === "ar" 
                    ? "خدمات متخصصة مصممة لتلبية احتياجاتك في مجال الذكاء الاصطناعي"
                    : "Specialized services designed to meet your AI transformation needs"
                  }
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {mainServices.map((service, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardHeader className="pb-4">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-3 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <service.icon className="h-8 w-8 text-primary" />
                        </div>
                        <Badge variant="secondary" className="bg-primary/10">
                          {locale === "ar" ? service.priceArabic : service.price}
                        </Badge>
                      </div>
                      <CardTitle className="text-2xl group-hover:text-primary transition-colors">
                        {locale === "ar" ? service.titleArabic : service.title}
                      </CardTitle>
                      <CardDescription className="text-base">
                        {locale === "ar" ? service.descriptionArabic : service.description}
                      </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-6">
                      <ul className="space-y-3">
                        {(locale === "ar" ? service.featuresArabic : service.features).map((feature, featureIndex) => (
                          <li key={featureIndex} className="flex items-center gap-3 text-sm">
                            <div className="w-2 h-2 rounded-full bg-primary flex-shrink-0" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                      <Button className="w-full btn-gradient group">
                        {locale === "ar" ? "اعرف المزيد" : "Learn More"}
                        <ArrowRight className={cn("h-4 w-4 transition-transform group-hover:translate-x-1", isRTL ? "mr-2 group-hover:-translate-x-1" : "ml-2")} />
                      </Button>
                    </CardContent>

                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Additional Services */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                  {locale === "ar" ? "خدمات إضافية" : "Additional Services"}
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  {locale === "ar" 
                    ? "خدمات متكاملة لدعم رحلتك الرقمية بالكامل"
                    : "Comprehensive services to support your complete digital journey"
                  }
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {additionalServices.map((service, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <service.icon className="h-6 w-6 text-primary" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg group-hover:text-primary transition-colors mb-2">
                            {locale === "ar" ? service.titleArabic : service.title}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {locale === "ar" ? service.descriptionArabic : service.description}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Process Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                  {locale === "ar" ? "عمليتنا" : "Our Process"}
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  {locale === "ar" 
                    ? "منهجية مثبتة لضمان نجاح مشاريع الذكاء الاصطناعي"
                    : "A proven methodology to ensure successful AI project delivery"
                  }
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
                {processSteps.map((step, index) => (
                  <div
                    key={index}
                    className="text-center animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="relative mb-6">
                      <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center text-white font-bold text-lg">
                        {step.step}
                      </div>
                      {index < processSteps.length - 1 && (
                        <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-primary/50 to-transparent" />
                      )}
                    </div>
                    <h3 className="font-semibold text-lg mb-2">
                      {locale === "ar" ? step.titleArabic : step.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {locale === "ar" ? step.descriptionArabic : step.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center space-y-8">
              <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                {locale === "ar" ? "هل أنت مستعد للبدء؟" : "Ready to Get Started?"}
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                {locale === "ar" 
                  ? "دعنا نساعدك في تحويل أعمالك بحلول الذكاء الاصطناعي المبتكرة"
                  : "Let us help you transform your business with innovative AI solutions"
                }
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button size="lg" className="btn-gradient">
                  {locale === "ar" ? "احجز استشارة مجانية" : "Book Free Consultation"}
                  <ArrowRight className={cn("h-4 w-4", isRTL ? "mr-2" : "ml-2")} />
                </Button>
                <Button size="lg" variant="outline" className="bg-background/50">
                  {locale === "ar" ? "تواصل معنا" : "Contact Us"}
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