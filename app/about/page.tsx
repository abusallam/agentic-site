"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { brandConfig } from "@/lib/brand"
import { ArrowRight, Award, BookOpen, Briefcase, Calendar, CheckCircle, Code, FileText, GraduationCap, Mail, MapPin, Phone, User, Brain, Zap, Target, Users } from "lucide-react"
import Image from "next/image"

export default function AboutPage() {
  const { t, locale, isRTL } = useEnhancedTranslation()

  // Contact information from the image
  const contactInfo = {
    email: "consulting.sa",
    phone: "+966570707070",
    address: "Saudi Arabia",
    addressArabic: "المملكة العربية السعودية"
  }

  const services = [
    {
      title: "AI Consulting Services",
      titleArabic: "خدمات استشارات الذكاء الاصطناعي",
      description: "Strategic AI implementation and consulting for businesses",
      descriptionArabic: "تنفيذ استراتيجي للذكاء الاصطناعي واستشارات للشركات",
      icon: Brain
    },
    {
      title: "Chatbot Development",
      titleArabic: "تطوير روبوتات المحادثة",
      description: "Custom chatbot solutions for customer engagement",
      descriptionArabic: "حلول روبوتات محادثة مخصصة لتفاعل العملاء",
      icon: Zap
    },
    {
      title: "AI Agent Development",
      titleArabic: "تطوير وكلاء الذكاء الاصطناعي",
      description: "Intelligent agents for business process automation",
      descriptionArabic: "وكلاء أذكياء لأتمتة العمليات التجارية",
      icon: Target
    },
    {
      title: "Digital Transformation",
      titleArabic: "التحول الرقمي",
      description: "Complete digital transformation solutions",
      descriptionArabic: "حلول التحول الرقمي الشاملة",
      icon: Users
    }
  ]

  const achievements = [
    {
      number: "100+",
      label: "Projects Completed",
      labelArabic: "مشروع مكتمل"
    },
    {
      number: "50+",
      label: "Satisfied Clients",
      labelArabic: "عميل راضٍ"
    },
    {
      number: "5+",
      label: "Years Experience",
      labelArabic: "سنوات خبرة"
    },
    {
      number: "24/7",
      label: "Support",
      labelArabic: "دعم"
    }
  ]

  const expertise = [
    "Artificial Intelligence",
    "Machine Learning",
    "Natural Language Processing",
    "Computer Vision",
    "Deep Learning",
    "Data Analytics",
    "Cloud Computing",
    "Software Engineering"
  ]

  const expertiseArabic = [
    "الذكاء الاصطناعي",
    "تعلم الآلة",
    "معالجة اللغة الطبيعية",
    "رؤية الحاسوب",
    "التعلم العميق",
    "تحليل البيانات",
    "الحوسبة السحابية",
    "هندسة البرمجيات"
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
                {locale === "ar" ? "مستشار المهندس / عاصم أبو سلام" : "Consultant Eng / Asim Abu Sallam"}
              </h1>
              <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                {locale === "ar" 
                  ? "خبير في الذكاء الاصطناعي والتحول الرقمي، متخصص في تطوير حلول مبتكرة للشركات"
                  : "AI Expert & Digital Transformation Specialist, dedicated to developing innovative solutions for businesses"
                }
              </p>
            </div>
          </div>
        </section>

        {/* Profile Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                {/* Profile Card */}
                <div className="space-y-8">
                  <Card className="glass-effect border-0 bg-background/50 overflow-hidden">
                    <CardContent className="p-0">
                      <div className="aspect-square w-full bg-gradient-to-br from-primary/20 to-secondary/20 relative overflow-hidden">
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                            <User className="h-16 w-16 text-white" />
                          </div>
                        </div>
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4 text-white">
                          <h3 className="text-xl font-bold">
                            {locale === "ar" ? "م. عاصم أبو سلام" : "Eng. Asim Abu Sallam"}
                          </h3>
                          <p className="text-sm opacity-90">
                            {locale === "ar" ? "مستشار الذكاء الاصطناعي" : "AI Consultant"}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="glass-effect border-0 bg-background/50">
                    <CardContent className="p-6 space-y-4">
                      <h3 className="text-lg font-semibold">
                        {locale === "ar" ? "معلومات الاتصال" : "Contact Information"}
                      </h3>
                      <div className="space-y-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-full bg-primary/10">
                            <Mail className="h-4 w-4 text-primary" />
                          </div>
                          <span className="text-sm">{contactInfo.email}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-full bg-primary/10">
                            <Phone className="h-4 w-4 text-primary" />
                          </div>
                          <span className="text-sm">{contactInfo.phone}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-full bg-primary/10">
                            <MapPin className="h-4 w-4 text-primary" />
                          </div>
                          <span className="text-sm">
                            {locale === "ar" ? contactInfo.addressArabic : contactInfo.address}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="glass-effect border-0 bg-background/50">
                    <CardContent className="p-6 space-y-4">
                      <h3 className="text-lg font-semibold">
                        {locale === "ar" ? "مجالات الخبرة" : "Areas of Expertise"}
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {(locale === "ar" ? expertiseArabic : expertise).map((skill, index) => (
                          <Badge key={index} variant="secondary" className="bg-primary/10 hover:bg-primary/20 transition-colors">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Main Content */}
                <div className="lg:col-span-2 space-y-8">
                  <Card className="glass-effect border-0 bg-background/50">
                    <CardContent className="p-6 space-y-6">
                      <div>
                        <h2 className="text-2xl font-bold font-heading mb-4">
                          {locale === "ar" ? "نبذة عني" : "About Me"}
                        </h2>
                        <p className="text-muted-foreground leading-relaxed">
                          {locale === "ar" 
                            ? "مستشار ذكاء اصطناعي ومهندس برمجيات ذو خبرة واسعة في مجال تطوير وتنفيذ حلول الذكاء الاصطناعي للشركات. متخصص في تحويل التحديات التجارية المعقدة إلى حلول تقنية مبتكرة. أقدم خدمات استشارية شاملة في مجال الذكاء الاصطناعي، تطوير روبوتات المحادثة، وكلاء الذكاء الاصطناعي، والتحول الرقمي للمؤسسات."
                            : "AI consultant and software engineer with extensive experience in developing and implementing AI solutions for businesses. Specialized in transforming complex business challenges into innovative technical solutions. I provide comprehensive consulting services in artificial intelligence, chatbot development, AI agents, and digital transformation for organizations."
                          }
                        </p>
                      </div>

                      <div>
                        <h3 className="text-xl font-semibold mb-4 flex items-center">
                          <Briefcase className="mr-2 h-5 w-5 text-primary" />
                          {locale === "ar" ? "الخدمات المقدمة" : "Services Offered"}
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {services.map((service, index) => (
                            <div key={index} className="p-4 rounded-lg bg-muted/20 border border-muted/40">
                              <div className="flex items-center gap-3 mb-2">
                                <service.icon className="h-5 w-5 text-primary" />
                                <h4 className="font-semibold">
                                  {locale === "ar" ? service.titleArabic : service.title}
                                </h4>
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {locale === "ar" ? service.descriptionArabic : service.description}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Achievements */}
                  <Card className="glass-effect border-0 bg-background/50">
                    <CardContent className="p-6">
                      <h3 className="text-xl font-semibold mb-6 text-center">
                        {locale === "ar" ? "الإنجازات" : "Achievements"}
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        {achievements.map((achievement, index) => (
                          <div key={index} className="text-center">
                            <div className="text-2xl font-bold text-primary mb-1">
                              {achievement.number}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {locale === "ar" ? achievement.labelArabic : achievement.label}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center space-y-8">
              <h2 className="text-3xl sm:text-4xl font-bold font-heading">
                {locale === "ar" ? "هل أنت مستعد للتعاون معي؟" : "Ready to Work With Me?"}
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                {locale === "ar" 
                  ? "دعني أساعدك في تحقيق أهدافك من خلال حلول الذكاء الاصطناعي المبتكرة"
                  : "Let me help you achieve your goals with innovative AI solutions"
                }
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button size="lg" className="btn-gradient">
                  <Mail className="mr-2 h-4 w-4" />
                  {locale === "ar" ? "تواصل معي" : "Contact Me"}
                </Button>
                <Button size="lg" variant="outline" className="bg-background/50">
                  <ArrowRight className="mr-2 h-4 w-4" />
                  {locale === "ar" ? "استعرض خدماتي" : "View My Services"}
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
