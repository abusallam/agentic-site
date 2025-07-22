"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"

export default function ChatbotsPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-4xl font-bold mb-8">Chatbots</h1>
          <div className="prose dark:prose-invert max-w-none">
            <p>
              The POTS Portal allows you to build and deploy intelligent chatbots for your business. Chatbots are a
              great way to engage with your customers, answer their questions, and provide them with support.
            </p>
            <h2 id="building-a-chatbot">Building a Chatbot</h2>
            <p>
              To build a chatbot, navigate to the "Chatbots" page and click the "Create Chatbot" button. You will be
              prompted to give your chatbot a name and a description.
            </p>
            <h2 id="training-a-chatbot">Training a Chatbot</h2>
            <p>
              Once you have created a chatbot, you will need to train it to understand and respond to user input. You
              can train your chatbot by providing it with a list of questions and answers. You can also use a
              pre-trained model to get started quickly.
            </p>
            <h2 id="deploying-a-chatbot">Deploying a Chatbot</h2>
            <p>
              Once you are happy with your chatbot, you can deploy it to your website or messaging platform. The POTS
              Portal provides a simple way to embed your chatbot on your website.
            </p>
          </div>
        </div>
      </main>
      <EnhancedFooter />
    </div>
  )
}
