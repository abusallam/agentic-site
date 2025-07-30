"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"

export default function AiAgentsClientPage() {
  const { t } = useEnhancedTranslation()
  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-4xl font-bold mb-8">{t("services.aiAgents.title")}</h1>
          <div className="prose dark:prose-invert max-w-none">
            <p>
              The POTS Portal allows you to create and manage AI agents to automate your workflows. AI agents are
              intelligent bots that can perform a variety of tasks, such as collecting data, sending emails, and
              interacting with other applications.
            </p>
            <h2 id="creating-an-agent">Creating an Agent</h2>
            <p>
              To create an AI agent, navigate to the "AI Agents" page and click the "Create Agent" button. You will be
              prompted to give your agent a name and a description.
            </p>
            <h2 id="configuring-an-agent">Configuring an Agent</h2>
            <p>
              Once you have created an agent, you can configure it to perform a variety of tasks. You can add actions
              to your agent, such as sending an email, calling an API, or running a script. You can also set up
              triggers to run your agent at a specific time or when a certain event occurs.
            </p>
            <h2 id="monitoring-an-agent">Monitoring an Agent</h2>
            <p>
              You can monitor the activity of your AI agents from the "AI Agents" page. You can see when your agents
              have run, what actions they have performed, and whether they have encountered any errors.
            </p>
          </div>
        </div>
      </main>
      <EnhancedFooter />
    </div>
  )
}
