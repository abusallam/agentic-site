import type React from "react"
import type { Metadata } from "next"
import "./globals.css"

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
    <html lang="en">
      <body className="font-sans antialiased">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900">consulting.sa</h1>
              </div>
              <div className="flex items-center space-x-4">
                <a href="/" className="text-gray-700 hover:text-gray-900">Home</a>
                <a href="/about" className="text-gray-700 hover:text-gray-900">About</a>
                <a href="/services" className="text-gray-700 hover:text-gray-900">Services</a>
                <a href="/contact" className="text-gray-700 hover:text-gray-900">Contact</a>
              </div>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  )
}