"use client"
import { EnhancedNavigation } from "@/components/layout/navigation-enhanced"
import { EnhancedFooter } from "@/components/layout/footer-enhanced"

export default function ContributingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <EnhancedNavigation />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-4xl font-bold mb-8">Contributing</h1>
          <div className="prose dark:prose-invert max-w-none">
            <p>
              We welcome contributions from the community to help us improve the POTS Portal. If you would like to
              contribute, please follow these guidelines:
            </p>
            <h2 id="bug-reports">Bug Reports</h2>
            <p>
              If you find a bug in the application, please open an issue on our GitHub repository. Please include a
              detailed description of the bug, including steps to reproduce it.
            </p>
            <h2 id="feature-requests">Feature Requests</h2>
            <p>
              If you have an idea for a new feature, please open an issue on our GitHub repository. Please include a
              detailed description of the feature and why you think it would be a good addition to the project.
            </p>
            <h2 id="pull-requests">Pull Requests</h2>
            <p>
              If you would like to contribute code to the project, please open a pull request on our GitHub repository.
              Please make sure that your code follows our coding style and that all tests pass.
            </p>
          </div>
        </div>
      </main>
      <EnhancedFooter />
    </div>
  )
}
