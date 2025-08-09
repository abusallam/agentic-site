import type React from "react"
import type { Metadata } from "next"
import { Bitter, Noto_Sans_Arabic } from "next/font/google"
import "./globals.css"

const bitter = Bitter({
  subsets: ["latin"],
  variable: "--font-bitter",
  weight: ["400", "600"],
  display: 'swap',
})

const notoSansArabic = Noto_Sans_Arabic({
  subsets: ["arabic"],
  variable: "--font-noto-arabic",
  weight: ["400", "600"],
  display: 'swap',
})

export const metadata: Metadata = {
  title: "consulting.sa - AI Consulting Services",
  description: "Professional AI consulting services in Saudi Arabia",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${bitter.variable} ${notoSansArabic.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  )
}