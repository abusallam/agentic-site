"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { Code, Rocket, Settings, Users, FileText, Video, MessageSquare, ExternalLink } from "lucide-react"

export default function DocumentationPage() {

  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <section className="py-20 bg-gradient-to-br from-background via-background to-muted/20">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center space-y-6">
              <h1 className="text-4xl sm:text-5xl font-bold font-heading gradient-text">Documentation</h1>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Welcome to the documentation for the POTS Portal. Here you will find everything you need to know to get started with the project.
              </p>
            </div>
          </div>
        </section>

        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-2xl font-bold font-heading mb-8 text-center">Getting Started</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card
                  icon={Rocket}
                  title="Installation"
                  description="Learn how to install the project and get it running on your local machine."
                  href="/docs/installation"
                />
                <Card
                  icon={Settings}
                  title="Configuration"
                  description="Find out how to configure the project, including the Supabase integration."
                  href="/docs/configuration"
                />
                <Card
                  icon={Users}
                  title="Contributing"
                  description="Read our contribution guidelines and learn how you can help improve the project."
                  href="/docs/contributing"
                />
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-2xl font-bold font-heading mb-8 text-center">Services</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card
                  icon={Code}
                  title="AI Agents"
                  description="Learn how to create and manage AI agents to automate your workflows."
                  href="/docs/ai-agents"
                />
                <Card
                  icon={MessageSquare}
                  title="Chatbots"
                  description="Find out how to build and deploy intelligent chatbots for your business."
                  href="/docs/chatbots"
                />
                <Card
                  icon={FileText}
                  title="IT Consulting"
                  description="Get expert advice on how to leverage technology to achieve your business goals."
                  href="/docs/it-consulting"
                />
              </div>
            </div>
          </div>
        </section>

        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-2xl font-bold font-heading mb-8 text-center">Additional Resources</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <ResourceCard
                  icon={FileText}
                  title="PDF Guides"
                  description="Downloadable comprehensive guides"
                  action="Download"
                  href="/resources/guides.pdf"
                />
                <ResourceCard
                  icon={Video}
                  title="Video Tutorials"
                  description="Step-by-step video walkthroughs"
                  action="Watch"
                  href="/resources/videos"
                />
                <ResourceCard
                  icon={MessageSquare}
                  title="Community Forum"
                  description="Get help from the community"
                  action="Join"
                  href="/community"
                />
                <ResourceCard
                  icon={ExternalLink}
                  title="GitHub Repository"
                  description="Source code and examples"
                  action="View"
                  href="https://github.com/main-consulting"
                />
              </div>
            </div>
          </div>
        </section>
      </main>
      <EnhancedFooter />
    </div>
  )
}

interface CardProps {
  icon: React.ComponentType<{ className?: string }>
  title: string
  description: string
  href: string
}

function Card({ icon: Icon, title, description, href }: CardProps) {
  return (
    <a href={href} className="block p-6 rounded-lg border bg-background/50 hover:bg-background transition-colors group">
      <div className="flex items-center gap-4 mb-4">
        <div className="p-3 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
          <Icon className="h-6 w-6 text-primary" />
        </div>
        <h3 className="text-lg font-bold">{title}</h3>
      </div>
      <p className="text-muted-foreground">{description}</p>
    </a>
  )
}

interface ResourceCardProps {
  icon: React.ComponentType<{ className?: string }>
  title: string
  description: string
  action: string
  href: string
}

function ResourceCard({ icon: Icon, title, description, action, href }: ResourceCardProps) {
  return (
    <a href={href} className="block p-6 rounded-lg border bg-background/50 hover:bg-background transition-colors group text-center">
      <div className="p-3 rounded-lg bg-primary/10 w-fit mx-auto mb-3">
        <Icon className="h-6 w-6 text-primary" />
      </div>
      <h3 className="text-lg font-bold">{title}</h3>
      <p className="text-muted-foreground mb-4">{description}</p>
      <button className="w-full bg-primary text-primary-foreground py-2 rounded-lg">{action}</button>
    </a>
  )
}
