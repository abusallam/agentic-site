"use client"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import Image from "next/image"
import { Star } from "lucide-react"

function EnhancedTestimonialsSection() {
  const { t } = useEnhancedTranslation()

  const testimonials = [
    {
      name: "John Doe",
      title: "CEO, Example Inc.",
      quote: "consulting.sa has been a game-changer for our business. Their AI-powered solutions have helped us automate our workflows and improve our efficiency.",
      avatar: "/placeholder-user.jpg",
    },
    {
      name: "Jane Smith",
      title: "CTO, Another Co.",
      quote: "The team at consulting.sa is top-notch. They are experts in their field and have been a pleasure to work with. I would highly recommend them to anyone looking for AI consulting services.",
      avatar: "/placeholder-user.jpg",
    },
    {
      name: "Sam Wilson",
      title: "Founder, Startup LLC",
      quote: "We were looking for a way to engage with our customers more effectively, and consulting.sa delivered. Their chatbots have helped us improve our customer satisfaction and increase our sales.",
      avatar: "/placeholder-user.jpg",
    },
  ]

  return (
    <section className="section-padding bg-background">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <h2 className="text-3xl sm:text-4xl font-bold font-heading gradient-text">What Our Clients Say</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            We are proud to have helped so many businesses succeed. Here's what some of our clients have to say about us.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="testimonial-card p-8 rounded-xl animate-fade-in-up" style={{ animationDelay: `${index * 200}ms` }}>
              <div className="flex items-center mb-4">
                <Image
                  src={testimonial.avatar}
                  alt={testimonial.name}
                  width={48}
                  height={48}
                  className="rounded-full mr-4"
                />
                <div>
                  <h3 className="font-bold">{testimonial.name}</h3>
                  <p className="text-sm text-muted-foreground">{testimonial.title}</p>
                </div>
              </div>
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 text-primary" fill="currentColor" />
                ))}
              </div>
              <p className="text-muted-foreground">{testimonial.quote}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
export { EnhancedTestimonialsSection }
export default EnhancedTestimonialsSection