import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <div className="min-h-screen">
      {/* Navigation skeleton */}
      <div className="sticky top-0 z-50 w-full border-b bg-background/95">
        <div className="container flex h-16 items-center justify-between">
          <Skeleton className="h-10 w-48" />
          <div className="hidden md:flex items-center space-x-6">
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-24" />
          </div>
        </div>
      </div>

      {/* Hero skeleton */}
      <div className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-5xl mx-auto">
            <Skeleton className="h-8 w-64 mx-auto mb-6" />
            <Skeleton className="h-16 w-full mb-6" />
            <Skeleton className="h-6 w-3/4 mx-auto mb-8" />
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Skeleton className="h-12 w-40" />
              <Skeleton className="h-12 w-40" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
