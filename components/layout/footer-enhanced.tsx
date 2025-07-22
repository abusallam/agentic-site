"use client"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { brandConfig } from "@/lib/brand"
import { Mail, Phone, MapPin, Clock, Linkedin, Twitter, Github } from "lucide-react"
import { cn } from "@/lib/utils"

export function EnhancedFooter() {
  const { t, isRTL } = useEnhancedTranslation()

  const footerSections = [
    {
      title: t("footer.company"),
      links: [
        { label: "About Us", href: "/about" },
        { label: "Our Team", href: "/team" },
        { label: "Careers", href: "/careers" },
        { label: "News", href: "/news" },
      ],
    },
    {
      title: t("footer.services"),
      links: [
        { label: t("services.aiAgents.title"), href: "/ai-agents" },
        { label: t("services.chatbots.title"), href: "/chatbots" },
        { label: t("services.consulting.title"), href: "/consulting" },
        { label: "Custom Solutions", href: "/custom" },
      ],
    },
    {
      title: t("footer.resources"),
      links: [
        { label: t("nav.documentation"), href: "/documentation" },
        { label: "Blog", href: "/blog" },
        { label: "Case Studies", href: "/case-studies" },
        { label: "Support", href: "/support" },
      ],
    },
  ]

  const contactInfo = [
    {
      icon: Mail,
      label: brandConfig.contact.email,
      href: `mailto:${brandConfig.contact.email}`,
    },
    {
      icon: Phone,
      label: brandConfig.contact.phone,
      href: `tel:${brandConfig.contact.phone}`,
    },
    {
      icon: MapPin,
      label: brandConfig.contact.address,
      href: "#",
    },
    {
      icon: Clock,
      label: brandConfig.contact.hours,
      href: "#",
    },
  ]

  const socialLinks = [
    {
      icon: Linkedin,
      href: brandConfig.social.linkedin,
      label: "LinkedIn",
    },
    {
      icon: Twitter,
      href: brandConfig.social.twitter,
      label: "Twitter",
    },
    {
      icon: Github,
      href: brandConfig.social.github,
      label: "GitHub",
    },
  ]

  return (
    <footer className="bg-background border-t">
      <div className="container mx-auto px-4">
        {/* Main Footer Content */}
        <div className="py-16">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Brand Section */}
            <div className="lg:col-span-1 space-y-6">
              <Link href="/" className="flex items-center gap-3">
                <Image
                  src={brandConfig.logo.image || "/placeholder.svg"}
                  alt={brandConfig.name}
                  width={40}
                  height={40}
                />
                <span className="text-lg font-bold font-heading">{brandConfig.name}</span>
              </Link>

              <p className="text-muted-foreground text-sm leading-relaxed">{brandConfig.description}</p>

              {/* Social Links */}
              <div className="flex gap-3">
                {socialLinks.map((social, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="icon"
                    asChild
                    className="hover:bg-primary hover:text-primary-foreground transition-colors bg-transparent"
                  >
                    <Link href={social.href} target="_blank" rel="noopener noreferrer">
                      <social.icon className="h-4 w-4" />
                      <span className="sr-only">{social.label}</span>
                    </Link>
                  </Button>
                ))}
              </div>
            </div>

            {/* Footer Links */}
            {footerSections.map((section, index) => (
              <div key={index} className="space-y-4">
                <h3 className="font-semibold text-foreground">{section.title}</h3>
                <ul className="space-y-2">
                  {section.links.map((link, linkIndex) => (
                    <li key={linkIndex}>
                      <Link
                        href={link.href}
                        className="text-sm text-muted-foreground hover:text-primary transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Contact Section */}
        <div className="py-8 border-t">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h3 className="font-semibold text-foreground mb-4">{t("footer.contact")}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {contactInfo.map((info, index) => (
                  <Link
                    key={index}
                    href={info.href}
                    className="flex items-center gap-3 text-sm text-muted-foreground hover:text-primary transition-colors group"
                  >
                    <info.icon className="h-4 w-4 flex-shrink-0 group-hover:text-primary" />
                    <span>{info.label}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Newsletter Signup */}
            <div>
              <h3 className="font-semibold text-foreground mb-4">Stay Updated</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Subscribe to our newsletter for the latest AI insights and updates.
              </p>
              <div className="flex gap-2">
                <Input type="email" placeholder="Enter your email" className="flex-1" />
                <Button>Subscribe</Button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div
          className={cn(
            "py-6 border-t flex flex-col sm:flex-row justify-between items-center gap-4",
            isRTL && "sm:flex-row-reverse",
          )}
        >
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} {brandConfig.name}. {t("footer.rights")}
          </p>
          <div className="flex gap-6">
            <Link href="/privacy" className="text-sm text-muted-foreground hover:text-primary transition-colors">
              {t("footer.privacy")}
            </Link>
            <Link href="/terms" className="text-sm text-muted-foreground hover:text-primary transition-colors">
              {t("footer.terms")}
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
