import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Development Environment - consulting.sa',
  description: 'Development environment for consulting.sa AI platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'Arial, sans-serif' }}>
        {children}
      </body>
    </html>
  )
}