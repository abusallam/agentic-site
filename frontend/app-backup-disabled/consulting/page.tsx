import type { Metadata } from "next"
import ConsultingClientPage from "./ConsultingClientPage"
// Removed unused translations import

export const metadata: Metadata = {
  title: "Consulting - Main Consulting",
  description: "Expert AI consulting services to help transform your business with artificial intelligence solutions.",
}

export default function ConsultingPage() {
  return <ConsultingClientPage />
}
