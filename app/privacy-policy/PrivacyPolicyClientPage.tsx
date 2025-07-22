"use client"

import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { Card, CardContent } from "@/components/ui/card"
import { Shield, Lock, Eye, Users, Globe, FileText, AlertTriangle, Phone, Mail, MapPin } from "lucide-react"
import { cn } from "@/lib/utils"

export default function PrivacyPolicyClientPage() {
  const sections = [
    {
      icon: Eye,
      title: "1. Information We Collect",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>At consulting.sa (المستشار.السعودية), we collect information you provide directly to us, such as when you:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Contact us through our website forms</li>
            <li>Subscribe to our newsletter</li>
            <li>Request consulting services</li>
            <li>Participate in surveys or feedback</li>
          </ul>
          <p>This may include your name, email address, phone number, company information, and any other information you choose to provide.</p>
        </div>
      )
    },
    {
      icon: Shield,
      title: "2. How We Use Your Information",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>We use the information we collect to:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Provide, maintain, and improve our services</li>
            <li>Respond to your inquiries and provide customer support</li>
            <li>Send you technical notices, updates, and administrative messages</li>
            <li>Communicate with you about products, services, and events</li>
            <li>Process transactions and send related information</li>
            <li>Monitor and analyze trends and usage</li>
          </ul>
        </div>
      )
    },
    {
      icon: Users,
      title: "3. Information Sharing",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>With service providers who assist us in operating our website and conducting business</li>
            <li>When required by law or to protect our rights</li>
            <li>In connection with a merger, acquisition, or sale of assets</li>
          </ul>
        </div>
      )
    },
    {
      icon: Lock,
      title: "4. Data Security",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. However, no method of transmission over the internet is 100% secure.</p>
        </div>
      )
    },
    {
      icon: Globe,
      title: "5. Cookies and Tracking",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>Our website uses cookies and similar tracking technologies to enhance your experience. You can control cookie settings through your browser preferences.</p>
        </div>
      )
    },
    {
      icon: FileText,
      title: "6. Your Rights",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>You have the right to:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Access and update your personal information</li>
            <li>Request deletion of your personal information</li>
            <li>Opt-out of marketing communications</li>
            <li>Request a copy of your data</li>
          </ul>
        </div>
      )
    },
    {
      icon: Globe,
      title: "7. International Transfers",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place to protect your information.</p>
        </div>
      )
    },
    {
      icon: AlertTriangle,
      title: "8. Children's Privacy",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>Our services are not intended for children under 13. We do not knowingly collect personal information from children under 13.</p>
        </div>
      )
    },
    {
      icon: FileText,
      title: "9. Changes to This Policy",
      content: (
        <div className="space-y-4 text-muted-foreground">
          <p>We may update this privacy policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last updated" date.</p>
        </div>
      )
    }
  ]

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 bg-gradient-to-br from-background via-background to-muted/20">
          {/* Background */}
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
                Privacy Policy
              </h1>
              <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Your privacy is important to us. Learn how we protect and handle your personal information.
              </p>
              <p className="text-sm text-muted-foreground">
                Last updated: January 2025
              </p>
            </div>
          </div>
        </section>

        {/* Content Sections */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto space-y-8">
              {sections.map((section, index) => (
                <Card
                  key={index}
                  className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden animate-fade-in-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <CardContent className="p-8">
                    <div className="flex items-start gap-4 mb-6">
                      <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                        <section.icon className="h-6 w-6 text-primary" />
                      </div>
                      <h2 className="text-2xl font-semibold group-hover:text-primary transition-colors flex-1">
                        {section.title}
                      </h2>
                    </div>
                    {section.content}
                  </CardContent>
                  {/* Hover Glow Effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                </Card>
              ))}

              {/* Contact Section */}
              <Card className="group hover-lift glass-effect border-0 bg-background/50 relative overflow-hidden">
                <CardContent className="p-8">
                  <div className="flex items-start gap-4 mb-6">
                    <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                      <Phone className="h-6 w-6 text-primary" />
                    </div>
                    <h2 className="text-2xl font-semibold group-hover:text-primary transition-colors flex-1">
                      10. Contact Us
                    </h2>
                  </div>
                  <div className="space-y-4 text-muted-foreground">
                    <p>If you have any questions about this Privacy Policy, please contact us:</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                      <div className="flex items-center gap-3">
                        <Mail className="h-5 w-5 text-primary" />
                        <div>
                          <p className="font-medium text-foreground">Email</p>
                          <p className="text-sm">privacy@consulting.sa</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Globe className="h-5 w-5 text-primary" />
                        <div>
                          <p className="font-medium text-foreground">Website</p>
                          <p className="text-sm">consulting.sa</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <MapPin className="h-5 w-5 text-primary" />
                        <div>
                          <p className="font-medium text-foreground">Location</p>
                          <p className="text-sm">Saudi Arabia</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
                {/* Hover Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </Card>
            </div>
          </div>
        </section>
      </main>
      <EnhancedFooter />
    </div>
  )
}