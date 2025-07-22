"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { ArrowRight, Users, CheckCircle, Clock, Star, Brain, Target, Lightbulb, Shield, BarChart3, Cog, Users2, MessageSquare, Award, Code, Database, Globe, Settings, TrendingUp, Cpu } from "lucide-react"
import { cn } from "@/lib/utils"

export default function ConsultingClientPage() {
  const { t, isRTL } = useEnhancedTranslation()

  const stats = [
    {
      icon: Users,
      value: "500+",
      label: t("hero.stats.clients"),
    },
    {
      icon: CheckCircle,
      value: "1000+",
      label: t("hero.stats.projects"),
    },
    {
      icon: Clock,
      value: "10+",
      label: t("hero.stats.experience"),
    },
    {
      icon: Star,
      value: "98%",
      label: t("hero.stats.satisfaction"),
    },
  ]

  const consultingServices = [
    {
      icon: Brain,
      title: t("consultingPage.services.strategy.title"),
      description: t("consultingPage.services.strategy.description"),
      features: ["Business Analysis", "AI Roadmap", "ROI Assessment", "Risk Evaluation"],
    },
    {
      icon: Target,
      title: t("consultingPage.services.feasibility.title"),
      description: t("consultingPage.services.feasibility.description"),
      features: ["Technical Assessment", "Market Analysis", "Cost-Benefit Analysis", "Timeline Planning"],
    },
    {
      icon: Cog,
      title: t("consultingPage.services.implementation.title"),
      description: t("consultingPage.services.implementation.description"),
      features: ["Project Management", "Technical Support", "Team Training", "Quality Assurance"],
    },
    {
      icon: Shield,
      title: t("consultingPage.services.ethics.title"),
      description: t("consultingPage.services.ethics.description"),
      features: ["Ethical Guidelines", "Compliance Review", "Bias Detection", "Governance Framework"],
    },
  ]

  const caseStudies = [
    {
      title: t("consultingPage.caseStudies.case1.title"),
      description: t("consultingPage.caseStudies.case1.description"),
      icon: BarChart3,
      metric: "40%",
      metricLabel: "Efficiency Increase",
    },
    {
      title: t("consultingPage.caseStudies.case2.title"),
      description: t("consultingPage.caseStudies.case2.description"),
      icon: Target,
      metric: "25%",
      metricLabel: "Accuracy Improvement",
    },
    {
      title: t("consultingPage.caseStudies.case3.title"),
      description: t("consultingPage.caseStudies.case3.description"),
      icon: MessageSquare,
      metric: "60%",
      metricLabel: "Response Time Reduction",
    },
  ]

  const saasServices = [
    {
      icon: Database,
      title: "Data Analytics Platform",
      description: "Advanced analytics and business intelligence solutions for data-driven decision making.",
      features: ["Real-time Analytics", "Custom Dashboards", "Predictive Modeling", "Data Visualization"],
    },
    {
      icon: Cpu,
      title: "AI Model Development",
      description: "Custom AI model development and deployment for specific business needs.",
      features: ["Machine Learning", "Deep Learning", "Model Training", "API Integration"],
    },
    {
      icon: Globe,
      title: "Cloud Integration",
      description: "Seamless cloud integration and migration services for scalable solutions.",
      features: ["AWS/Azure Setup", "Cloud Migration", "Scalability", "Security"],
    },
    {
      icon: Settings,
      title: "Process Automation",
      description: "Intelligent automation solutions to streamline business processes.",
      features: ["Workflow Automation", "RPA Solutions", "Integration", "Monitoring"],
    },
  ]

  const achievements = [
    {
      icon: Award,
      title: "Certified AI Consultant",
      description: "Advanced certification in AI and machine learning technologies",
      year: "2023",
    },
    {
      icon: Code,
      title: "Full Stack Developer",
      description: "Expert in modern web technologies and frameworks",
      year: "2022",
    },
    {
      icon: TrendingUp,
      title: "Project Manager",
      description: "Certified project management professional with proven track record",
      year: "2021",
    },
    {
      icon: Users2,
      title: "AI Specialist",
      description: "Specialized in artificial intelligence and automation solutions",
      year: "2020",
    },
  ]

  const insights = [
    {
      title: "AI Implementation Strategy",
      description: "Best practices for implementing AI solutions in enterprise environments with focus on ROI and scalability.",
      readTime: "5 min read",
    },
    {
      title: "Digital Transformation Roadmap",
      description: "Step-by-step guide to successful digital transformation initiatives for modern businesses.",
      readTime: "8 min read",
    },
    {
      title: "Automation Success Stories",
      description: "Real-world case studies showcasing successful automation implementations across industries.",
      readTime: "6 min read",
    },
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
          {/* Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-muted/20">
            <div
              className="absolute inset-0 opacity-10"
              style={{
                backgroundImage: "url('/bg1.webp')",
                backgroundSize: "cover",
                backgroundPosition: "center",
              }}
            />
          </div>

          {/* Floating Elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/5 rounded-full blur-3xl animate-pulse" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl animate-pulse delay-1000" />
          </div>

          <div className="container mx-auto px-4 relative z-10">
            <div className="max-w-4xl mx-auto text-center space-y-8">
              {/* Main Content */}
              <div className="space-y-6 animate-fade-in-up">
                <h1
                  className={cn(
                    "text-4xl sm:text-5xl lg:text-6xl font-bold font-heading leading-tight",
                    "bg-gradient-to-r from-foreground via-primary to-secondary bg-clip-text text-transparent",
                  )}
                >
                  {t("hero.title")}
                </h1>

                <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                  {t("hero.subtitle")}
                </p>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button
                  size="lg"
                  className="group bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary"
                >
                  {t("services.consulting.cta")}
                  <ArrowRight
                    className={cn(
                      "ml-2 h-4 w-4 transition-transform group-hover:translate-x-1",
                      isRTL && "ml-0 mr-2 group-hover:-translate-x-1",
                    )}
                  />
                </Button>
                <Button size="lg" variant="outline" className="hover-lift bg-transparent">
                  {t("ui.learnMore")}
                </Button>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-16">
                {stats.map((stat, index) => (
                  <Card
                    key={index}
                    className="hover-lift glass-effect border-0 bg-background/50 animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardContent className="p-6 text-center">
                      <stat.icon className="h-8 w-8 mx-auto mb-3 text-primary" />
                      <div className="text-2xl font-bold text-foreground mb-1">{stat.value}</div>
                      <div className="text-sm text-muted-foreground">{stat.label}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          {/* Scroll Indicator */}
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
            <div className="w-6 h-10 border-2 border-muted-foreground/30 rounded-full flex justify-center">
              <div className="w-1 h-3 bg-muted-foreground/50 rounded-full mt-2 animate-pulse" />
            </div>
          </div>
        </section>

        {/* About Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center space-y-8">
              <h2 className="text-3xl sm:text-4xl font-bold font-heading">{t("consultingPage.about.title")}</h2>
              <div className="space-y-6 text-lg text-muted-foreground">
                <p>{t("consultingPage.about.paragraph1")}</p>
                <p>{t("consultingPage.about.paragraph2")}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Consulting Services Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              {/* Header */}
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">{t("consultingPage.services.title")}</h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">{t("consultingPage.services.subtitle")}</p>
              </div>

              {/* Services Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {consultingServices.map((service, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardHeader className="pb-4">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <service.icon className="h-6 w-6 text-primary" />
                        </div>
                      </div>
                      <CardTitle className="text-xl group-hover:text-primary transition-colors">{service.title}</CardTitle>
                      <CardDescription className="text-base">{service.description}</CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                      {/* Features List */}
                      <ul className="space-y-2">
                        {service.features.map((feature, featureIndex) => (
                          <li key={featureIndex} className="flex items-center gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-primary flex-shrink-0" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>

                    {/* Hover Glow Effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Case Studies Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              {/* Header */}
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">{t("consultingPage.caseStudies.title")}</h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">{t("consultingPage.caseStudies.subtitle")}</p>
              </div>

              {/* Case Studies Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {caseStudies.map((caseStudy, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardHeader className="pb-4">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <caseStudy.icon className="h-6 w-6 text-primary" />
                        </div>
                        <Badge variant="secondary">{caseStudy.metric}</Badge>
                      </div>
                      <CardTitle className="text-lg group-hover:text-primary transition-colors">{caseStudy.title}</CardTitle>
                      <CardDescription className="text-sm">{caseStudy.description}</CardDescription>
                    </CardHeader>

                    <CardContent>
                      <div className="text-xs text-muted-foreground">{caseStudy.metricLabel}</div>
                    </CardContent>

                    {/* Hover Glow Effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* SaaS Services Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              {/* Header */}
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">SaaS Services To Offer</h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  Comprehensive software-as-a-service solutions designed to accelerate your digital transformation
                </p>
              </div>

              {/* SaaS Services Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {saasServices.map((service, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardHeader className="pb-4">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <service.icon className="h-6 w-6 text-primary" />
                        </div>
                      </div>
                      <CardTitle className="text-xl group-hover:text-primary transition-colors">{service.title}</CardTitle>
                      <CardDescription className="text-base">{service.description}</CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                      {/* Features List */}
                      <ul className="space-y-2">
                        {service.features.map((feature, featureIndex) => (
                          <li key={featureIndex} className="flex items-center gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-primary flex-shrink-0" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>

                    {/* Hover Glow Effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Insights Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              {/* Header */}
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">Insights</h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  Expert insights and thought leadership on AI, automation, and digital transformation
                </p>
              </div>

              {/* Insights Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {insights.map((insight, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardHeader className="pb-4">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <Lightbulb className="h-6 w-6 text-primary" />
                        </div>
                        <Badge variant="outline">{insight.readTime}</Badge>
                      </div>
                      <CardTitle className="text-lg group-hover:text-primary transition-colors">{insight.title}</CardTitle>
                      <CardDescription className="text-sm">{insight.description}</CardDescription>
                    </CardHeader>

                    <CardContent>
                      <Button variant="ghost" size="sm" className="p-0 h-auto text-primary hover:text-primary/80">
                        Read More <ArrowRight className="ml-1 h-3 w-3" />
                      </Button>
                    </CardContent>

                    {/* Hover Glow Effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Achievements Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              {/* Header */}
              <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl sm:text-4xl font-bold font-heading">My Achievements</h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  Professional certifications and expertise that drive exceptional results
                </p>
              </div>

              {/* Achievements Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {achievements.map((achievement, index) => (
                  <Card
                    key={index}
                    className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up text-center"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardContent className="p-6">
                      <div className="flex flex-col items-center space-y-4">
                        <div className="p-3 rounded-full bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <achievement.icon className="h-8 w-8 text-primary" />
                        </div>
                        <div className="space-y-2">
                          <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                            {achievement.title}
                          </h3>
                          <p className="text-sm text-muted-foreground">{achievement.description}</p>
                          <Badge variant="secondary" className="text-xs">
                            {achievement.year}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>

                    {/* Hover Glow Effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center space-y-8">
              <h2 className="text-3xl sm:text-4xl font-bold font-heading">{t("consultingPage.contact.title")}</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">{t("consultingPage.contact.subtitle")}</p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button
                  size="lg"
                  className="group bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary"
                >
                  {t("consultingPage.contact.cta")}
                  <ArrowRight
                    className={cn(
                      "ml-2 h-4 w-4 transition-transform group-hover:translate-x-1",
                      isRTL && "ml-0 mr-2 group-hover:-translate-x-1",
                    )}
                  />
                </Button>
                <Button size="lg" variant="outline" className="hover-lift bg-transparent">
                  {t("ui.learnMore")}
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
