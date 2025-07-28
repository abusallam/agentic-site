import type { Metadata } from "next"
import AiAgentsClientPage from "./AIAgentsClientPage"
// Removed unused translations import

export const metadata: Metadata = {
  title: "AI Agents - Main Consulting",
  description: "Learn about AI agents and how they can transform your business processes.",
}

export default function AiAgentsPage() {
  return <AiAgentsClientPage />
}
