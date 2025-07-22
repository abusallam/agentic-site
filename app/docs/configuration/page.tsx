"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"

export default function ConfigurationPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-4xl font-bold mb-8">Configuration</h1>
          <div className="prose dark:prose-invert max-w-none">
            <p>
              The POTS Portal uses a few environment variables to configure the application. These variables are stored
              in a <code>.env.local</code> file in the root of the project.
            </p>
            <h2 id="supabase">Supabase</h2>
            <p>
              The application uses Supabase for authentication and database services. You will need to create a project
              on Supabase and obtain the URL and anon key. You can find these values in your Supabase project's
              settings, under the "API" section.
            </p>
            <p>
              Once you have the URL and anon key, you need to add them to your <code>.env.local</code> file:
            </p>
            <pre>
              <code>
                NEXT_PUBLIC_SUPABASE_URL=YOUR_SUPABASE_URL
                <br />
                NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
              </code>
            </pre>
            <h2 id="branding">Branding</h2>
            <p>
              The branding of the application can be configured in the <code>lib/brand.ts</code> file. This file
              contains the application name, logo, colors, and other branding-related information.
            </p>
            <h2 id="internationalization">Internationalization</h2>
            <p>
              The application uses a simple i18n implementation to support multiple languages. The translations are
              stored in the <code>lib/i18n-enhanced</code> file. You can add new languages and translations to this
              file to support additional locales.
            </p>
          </div>
        </div>
      </main>
      <EnhancedFooter />
    </div>
  )
}
