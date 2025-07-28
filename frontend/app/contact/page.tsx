"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { HeroBackground } from "@/components/layout/hero-background"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { brandConfig } from "@/lib/brand"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Mail, Phone, MapPin, Clock, Send, MessageSquare, Users, Headphones } from "lucide-react"
import { cn } from "@/lib/utils"

export default function ContactPage() {
  const { t, locale, isRTL } = useEnhancedTranslation()

  const contactMethods = [
    {
      icon: Mail,
      title: "Email Us",
      titleArabic: "راسلنا",
      description: "Get in touch via email for detailed inquiries",
      descriptionArabic: "تواصل معنا عبر البريد الإلكتروني للاستفسارات التفصيلية",
      contact: brandConfig.contact.email,
      action: `mailto:${brandConfig.contact.email}`,
    },
    {
      icon: Phone,
      title: "Call Us",
      titleArabic: "اتصل بنا",
      description: "Speak directly with our AI consulting experts",
      descriptionArabic: "تحدث مباشرة مع خبراء استشارات الذكاء الاصطناعي",
      contact: brandConfig.contact.phone,
      action: `tel:${brandConfig.contact.phone}`,
    },
    {
      icon: MapPin,
      title: "Visit Us",
      titleArabic: "زرنا",
      description: "Located in the heart of Saudi Arabia",
      descriptionArabic: "نقع في قلب المملكة العربية السعودية",
      contact: locale === "ar" ? brandConfig.contact.addressArabic : brandConfig.contact.address,
      action: "#",
    },
    {
      icon: Clock,
      title: "Business Hours",
      titleArabic: "ساعات العمل",
      description: "Available for consultations and support",
      descriptionArabic: "متاح للاستشارات والدعم",
      contact: locale === "ar" ? brandConfig.contact.hoursArabic : brandConfig.contact.hours,
      action: "#",
    },
  ]

  const services = [
    {
      icon: MessageSquare,
      title: "AI Consulting",
      titleArabic: "استشارات الذكاء الاصطناعي",
      description: "Strategic AI implementation and planning",
      descriptionArabic: "تنفيذ وتخطيط الذكاء الاصطناعي الاستراتيجي",
    },
    {
      icon: Users,
      title: "Team Training",
      titleArabic: "تدريب الفرق",
      description: "Comprehensive AI training programs",
      descriptionArabic: "برامج تدريب شاملة للذكاء الاصطناعي",
    },
    {
      icon: Headphones,
      title: "24/7 Support",
      titleArabic: "دعم على مدار الساعة",
      description: "Round-the-clock technical assistance",
      descriptionArabic: "مساعدة تقنية على مدار الساعة",
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
              {locale === "ar" ? "تواصل معنا" : "Contact Us"}
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              {locale === "ar" 
                ? "نحن هنا لمساعدتك في رحلتك نحو الذكاء الاصطناعي. تواصل معنا اليوم لمناقشة احتياجاتك."
                : "We're here to help you on your AI journey. Get in touch today to discuss your needs."
              }
            </p>
          </div>
        </HeroBackground>

        {/* Contact Methods */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
                {contactMethods.map((method, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up text-center"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardContent className="p-6">
                      <div className="flex flex-col items-center space-y-4">
                        <div className="p-3 rounded-full bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <method.icon className="h-6 w-6 text-primary" />
                        </div>
                        <div className="space-y-2">
                          <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                            {locale === "ar" ? method.titleArabic : method.title}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {locale === "ar" ? method.descriptionArabic : method.description}
                          </p>
                          <p className="text-sm font-medium text-foreground">
                            {method.contact}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>

              {/* Contact Form and Services */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                {/* Contact Form */}
                <Card className="glass-effect border-0 bg-background/50">
                  <CardHeader>
                    <CardTitle className="text-2xl font-heading">
                      {locale === "ar" ? "أرسل لنا رسالة" : "Send us a Message"}
                    </CardTitle>
                    <CardDescription>
                      {locale === "ar" 
                        ? "املأ النموذج أدناه وسنتواصل معك قريباً"
                        : "Fill out the form below and we'll get back to you soon"
                      }
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="firstName">
                          {locale === "ar" ? "الاسم الأول" : "First Name"}
                        </Label>
                        <Input id="firstName" placeholder={locale === "ar" ? "أدخل اسمك الأول" : "Enter your first name"} />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="lastName">
                          {locale === "ar" ? "اسم العائلة" : "Last Name"}
                        </Label>
                        <Input id="lastName" placeholder={locale === "ar" ? "أدخل اسم العائلة" : "Enter your last name"} />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">
                        {locale === "ar" ? "البريد الإلكتروني" : "Email"}
                      </Label>
                      <Input id="email" type="email" placeholder={locale === "ar" ? "أدخل بريدك الإلكتروني" : "Enter your email"} />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="company">
                        {locale === "ar" ? "الشركة" : "Company"}
                      </Label>
                      <Input id="company" placeholder={locale === "ar" ? "أدخل اسم شركتك" : "Enter your company name"} />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="message">
                        {locale === "ar" ? "الرسالة" : "Message"}
                      </Label>
                      <Textarea 
                        id="message" 
                        rows={5}
                        placeholder={locale === "ar" ? "أخبرنا عن مشروعك أو استفسارك" : "Tell us about your project or inquiry"} 
                      />
                    </div>
                    <Button className="w-full btn-gradient">
                      <Send className={cn("h-4 w-4", isRTL ? "ml-2" : "mr-2")} />
                      {locale === "ar" ? "إرسال الرسالة" : "Send Message"}
                    </Button>
                  </CardContent>
                </Card>

                {/* Services Overview */}
                <div className="space-y-6">
                  <div>
                    <h2 className="text-3xl font-bold font-heading mb-4">
                      {locale === "ar" ? "كيف يمكننا مساعدتك" : "How We Can Help"}
                    </h2>
                    <p className="text-muted-foreground">
                      {locale === "ar" 
                        ? "نقدم مجموعة شاملة من خدمات الذكاء الاصطناعي لمساعدتك في تحقيق أهدافك التجارية."
                        : "We offer a comprehensive range of AI services to help you achieve your business goals."
                      }
                    </p>
                  </div>

                  <div className="space-y-4">
                    {services.map((service, index) => (
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

                  <Card className="glass-effect border-0 bg-primary/5">
                    <CardContent className="p-6 text-center">
                      <h3 className="font-semibold text-lg mb-2">
                        {locale === "ar" ? "استشارة مجانية" : "Free Consultation"}
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        {locale === "ar" 
                          ? "احجز استشارة مجانية لمناقشة احتياجاتك من الذكاء الاصطناعي"
                          : "Book a free consultation to discuss your AI needs"
                        }
                      </p>
                      <Button variant="outline" className="bg-background/50">
                        {locale === "ar" ? "احجز الآن" : "Book Now"}
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <EnhancedFooter />
    </div>
  )
}
