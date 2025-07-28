import type { Metadata } from "next"
import PrivacyPolicyClientPage from "./PrivacyPolicyClientPage"

export const metadata: Metadata = {
  title: "Privacy Policy - Main Consulting",
  description: "Privacy Policy for Main Consulting - Learn how we protect and handle your personal information.",
}

export default function PrivacyPolicyPage() {
  return <PrivacyPolicyClientPage />
}