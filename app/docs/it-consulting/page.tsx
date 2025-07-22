"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"

export default function ItConsultingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-4xl font-bold mb-8">IT Consulting</h1>
          <div className="prose dark:prose-invert max-w-none">
            <p>
              The POTS Portal offers IT consulting services to help you navigate the complexities of digital
              transformation. Our team of experts can help you with everything from developing a technology roadmap to
              implementing new systems and processes.
            </p>
            <h2 id="our-services">Our Services</h2>
            <p>We offer a wide range of IT consulting services, including:</p>
            <ul>
              <li>Technology strategy and roadmap development</li>
              <li>IT infrastructure assessment and design</li>
              <li>Cloud migration and management</li>
              <li>Cybersecurity assessment and planning</li>
              <li>Software selection and implementation</li>
            </ul>
            <h2 id="our-approach">Our Approach</h2>
            <p>
              We take a collaborative approach to IT consulting. We work closely with you to understand your business
              goals and challenges, and we develop a customized solution that meets your specific needs.
            </p>
            <h2 id="get-in-touch">Get in Touch</h2>
            <p>
              If you would like to learn more about our IT consulting services, please contact us to schedule a
              consultation.
            </p>
          </div>
        </div>
      </main>
      <EnhancedFooter />
    </div>
  )
}
