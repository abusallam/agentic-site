import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, Brain, Workflow, BarChart3, Lock, Rocket } from "lucide-react"

export function FeaturesSection() {
  const features = [
    {
      icon: MessageSquare,
      title: "Advanced Chatbots",
      description: "Natural language processing with context awareness and multi-language support",
      badge: "Popular",
    },
    {
      icon: Brain,
      title: "AI Agents",
      description: "Autonomous agents that can perform complex tasks and make intelligent decisions",
      badge: "New",
    },
    {
      icon: Workflow,
      title: "Workflow Automation",
      description: "Streamline business processes with intelligent automation and integration",
      badge: null,
    },
    {
      icon: BarChart3,
      title: "Analytics Dashboard",
      description: "Real-time insights and performance metrics for your AI implementations",
      badge: null,
    },
    {
      icon: Lock,
      title: "Enterprise Security",
      description: "End-to-end encryption, OAuth authentication, and compliance-ready infrastructure",
      badge: null,
    },
    {
      icon: Rocket,
      title: "Rapid Deployment",
      description: "Get your AI solutions live in minutes with our cloud-native platform",
      badge: null,
    },
  ]

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Powerful Features for Modern Businesses</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Everything you need to build, deploy, and scale AI solutions that drive real business results
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="relative overflow-hidden hover:shadow-lg transition-shadow duration-300">
              {feature.badge && (
                <Badge className="absolute top-4 right-4" variant={feature.badge === "New" ? "default" : "secondary"}>
                  {feature.badge}
                </Badge>
              )}
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
