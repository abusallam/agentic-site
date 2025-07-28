"use client"

import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Bot, MessageSquare, Brain, Cpu, Database, Cloud, 
  Zap, Users, CheckCircle, ArrowRight, Star, 
  Target, Shield, BarChart3, Lightbulb, Settings,
  Headphones, Clock, Award
} from "lucide-react"

export default function ServicesClientPage() {
  const { t, locale, isRTL } = useEnhancedTranslation()

  const mainServices = [
    {
      icon: Bot,
      title: locale === "ar" ? "وكلاء الذكاء الاصطناعي" : "AI Agents",
      description: locale === "ar" 
        ? "وكلاء ذكيون مخصصون لأتمتة العمليات التجارية المعقدة وتحسين الكفاءة"
        : "Intelligent agents designed to automate complex business processes and enhance efficiency",
      features: [
        locale === "ar" ? "أتمتة العمليات" : "Process Automation",
        locale === "ar" ? "اتخاذ القرارات الذكية" : "Smart Decision Making", 
        locale === "ar" ? "التعلم المستمر" : "Continuous Learning",
        locale === "ar" ? "التكامل السلس" : "Seamless Integration"
      ],
      badge: locale === "ar" ? "الأكثر طلباً" : "Most Popular",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: MessageSquare,
      title: locale === "ar" ? "روبوتات المحادثة" : "Chatbots",
      description: locale === "ar"
        ? "روبوتات محادثة ذكية تدعم اللغة العربية والإنجليزية لتحسين خدمة العملاء"
        : "Intelligent chatbots with Arabic and English support to enhance customer service",
      features: [
        locale === "ar" ? "دعم متعدد اللغات" : "Multi-language Support",
        locale === "ar" ? "فهم السياق" : "Context Understanding",
        locale === "ar" ? "ردود فورية" : "Instant Responses",
        locale === "ar" ? "تحليل المشاعر" : "Sentiment Analysis"
      ],
      badge: locale === "ar" ? "جديد" : "New",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: Brain,
      title: locale === "ar" ? "استشارات الذكاء الاصطناعي" : "AI Consulting",
      description: locale === "ar"
        ? "استشارات استراتيجية شاملة لتطبيق الذكاء الاصطناعي في مؤسستك"
        : "Comprehensive strategic consulting for implementing AI in your organization",
      features: [
        locale === "ar" ? "تقييم الاحتياجات" : "Needs Assessment",
        locale === "ar" ? "استراتيجية التنفيذ" : "Implementation Strategy",
        locale === "ar" ? "تدريب الفرق" : "Team Training",
        locale === "ar" ? "الدعم المستمر" : "Ongoing Support"
      ],
      badge: locale === "ar" ? "مميز" : "Premium",
      color: "from-purple-500 to-pink-500"
    }
  ]

  const additionalServices = [
    {
      icon: Database,
      title: locale === "ar" ? "تحليل البيانات" : "Data Analytics",
      description: locale === "ar" ? "تحليل البيانات المتقدم والذكاء التجاري" : "Advanced data analysis and business intelligence"
    },
    {
      icon: Cloud,
      title: locale === "ar" ? "الحلول السحابية" : "Cloud Solutions", 
      description: locale === "ar" ? "نشر وإدارة حلول الذكاء الاصطناعي السحابية" : "Deploy and manage cloud-based AI solutions"
    },
    {
      icon: Shield,
      title: locale === "ar" ? "أمان الذكاء الاصطناعي" : "AI Security",
      description: locale === "ar" ? "حماية وأمان تطبيقات الذكاء الاصطناعي" : "Security and protection for AI applications"
    },
    {
      icon: Settings,
      title: locale === "ar" ? "التكامل المخصص" : "Custom Integration",
      description: locale === "ar" ? "تكامل مخصص مع الأنظمة الحالية" : "Custom integration with existing systems"
    }
  ]

  const processSteps = [
    {
      step: "01",
      title: locale === "ar" ? "التقييم" : "Assessment",
      description: locale === "ar" ? "تحليل احتياجاتك وأهدافك التجارية" : "Analyze your needs and business objectives"
    },
    {
      step: "02", 
      title: locale === "ar" ? "التخطيط" : "Planning",
      description: locale === "ar" ? "وضع استراتيجية مخصصة لتطبيق الذكاء الاصطناعي" : "Develop a custom AI implementation strategy"
    },
    {
      step: "03",
      title: locale === "ar" ? "التطوير" : "Development", 
      description: locale === "ar" ? "بناء وتطوير الحلول المخصصة" : "Build and develop custom solutions"
    },
    {
      step: "04",
      title: locale === "ar" ? "النشر" : "Deployment",
      description: locale === "ar" ? "نشر الحلول وضمان التشغيل السلس" : "Deploy solutions and ensure smooth operation"
    },
    {
      step: "05",
      title: locale === "ar" ? "الدعم" : "Support",
      description: locale === "ar" ? "دعم مستمر وتحسينات دورية" : "Ongoing support and regular improvements"
    }
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 bg-gradient-to-br from-background via-background to-muted/20">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/5 rounded-full blur-3xl animate-pulse" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl animate-pulse delay-1000" />
          </div>
          
          <div className="container mx-auto px-4 relative z-10">
            <div className="max-w-4xl mx-auto text-center space-y-6">
              <h1 className={cn(
                "text-4xl sm:text-5xl lg:text-6xl font-bold font-heading leading-tight",
                "bg-gradient-to-r from-foreground via-primary to-secondary bg-clip-text text-transparent"
              )}>
                {locale === "ar" ? "خدماتنا المتميزة" : "Our Premium Services"}
              </h1>
              <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                {locale === "ar" 
                  ? "نقدم حلول الذكاء الاصطناعي المتطورة لتحويل أعمالك وتحقيق النجاح في العصر الرقمي"
                  : "We provide cutting-edge AI solutions to transform your business and achieve success in the digital age"
                }
              </p>
            </div>
          </div>
        </section>

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
                    ? "خدمات شاملة مصممة لتلبية احتياجاتك في مجال الذكاء الاصطناعي"
                    : "Comprehensive services designed to meet your AI needs"
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
                    {service.badge && (
                      <Badge className="absolute top-4 right-4 z-10" variant="secondary">
                        {service.badge}
                      </Badge>
                    )}
                    
                    <CardHeader className="pb-4">
                      <div className="flex items-center gap-3 mb-4">
                        <div className={cn(
                          "p-3 rounded-xl bg-gradient-to-r group-hover:scale-110 transition-transform",
                          service.color
                        )}>
                          <service.icon className="h-6 w-6 text-white" />
                        </div>
                      </div>
                      <CardTitle className="text-xl group-hover:text-primary transition-colors">
                        {service.title}
                      </CardTitle>
                      <CardDescription className="text-base">
                        {service.description}
                      </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-6">
                      <ul className="space-y-3">
                        {service.features.map((feature, featureIndex) => (
                          <li key={featureIndex} className="flex items-center gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-primary flex-shrink-0" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>

                      <Button className="w-full group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                        {locale === "ar" ? "اعرف المزيد" : "Learn More"}
                        <ArrowRight className={cn("h-4 w-4 ml-2", isRTL && "ml-0 mr-2 rotate-180")} />
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
                    ? "خدمات متخصصة لتلبية احتياجاتك الفريدة"
                    : "Specialized services to meet your unique requirements"
                  }
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {additionalServices.map((service, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden"
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <service.icon className="h-5 w-5 text-primary" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg group-hover:text-primary transition-colors mb-2">
                            {service.title}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {service.description}
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

        {/* Process Steps */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                  {locale === "ar" ? "عملية العمل" : "Our Process"}
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  {locale === "ar" 
                    ? "منهجية مجربة لضمان نجاح مشروعك"
                    : "A proven methodology to ensure your project's success"
                  }
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                {processSteps.map((step, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden text-center"
                  >
                    <CardContent className="p-6">
                      <div className="space-y-4">
                        <div className="text-4xl font-bold text-primary/20 group-hover:text-primary/40 transition-colors">
                          {step.step}
                        </div>
                        <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                          {step.title}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {step.description}
                        </p>
                      </div>
                    </CardContent>
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
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
                  ? "تواصل معنا اليوم لمناقشة احتياجاتك وكيف يمكننا مساعدتك في تحقيق أهدافك"
                  : "Contact us today to discuss your needs and how we can help you achieve your goals"
                }
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button size="lg" className="btn-gradient">
                  <MessageSquare className={cn("h-4 w-4", isRTL ? "ml-2" : "mr-2")} />
                  {locale === "ar" ? "احجز استشارة مجانية" : "Book Free Consultation"}
                </Button>
                <Button size="lg" variant="outline" className="bg-background/50">
                  <ArrowRight className={cn("h-4 w-4", isRTL ? "ml-2 rotate-180" : "mr-2")} />
                  {locale === "ar" ? "تصفح أعمالنا" : "View Our Work"}
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
