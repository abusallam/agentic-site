"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"

export default function InstallationPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-4xl font-bold mb-8">Installation</h1>
          <div className="prose dark:prose-invert max-w-none">
            <p>
              To get started with the POTS Portal, you'll need to have Node.js and npm (or yarn) installed on your
              machine. Once you have those, you can follow these steps to get the project up and running:
            </p>
            <ol>
              <li>
                <p>Clone the repository from GitHub:</p>
                <pre>
                  <code>git clone https://github.com/main-consulting/website.git</code>
                </pre>
              </li>
              <li>
                <p>Navigate into the project directory:</p>
                <pre>
                  <code>cd website</code>
                </pre>
              </li>
              <li>
                <p>Install the dependencies:</p>
                <pre>
                  <code>npm install</code>
                </pre>
              </li>
              <li>
                <p>
                  Create a <code>.env.local</code> file in the root of the project and add the following environment
                  variables:
                </p>
                <pre>
                  <code>
                    NEXT_PUBLIC_SUPABASE_URL=YOUR_SUPABASE_URL
                    <br />
                    NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
                  </code>
                </pre>
                <p>
                  You can find these values in your Supabase project's settings, under the "API" section.
                </p>
              </li>
              <li>
                <p>Start the development server:</p>
                <pre>
                  <code>npm run dev</code>
                </pre>
              </li>
            </ol>
            <p>
              Once the development server is running, you can open your browser and navigate to{" "}
              <a href="http://localhost:3000">http://localhost:3000</a> to see the application in action.
            </p>
          </div>
        </div>
      </main>
      <EnhancedFooter />
    </div>
  )
}
