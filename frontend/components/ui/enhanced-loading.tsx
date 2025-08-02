import * as React from "react"
import { cn } from "@/lib/utils"
import { Loader2, RefreshCw } from "lucide-react"

// Enhanced Skeleton Component
interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "circular" | "rectangular" | "text"
  animation?: "pulse" | "wave" | "none"
}

const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, variant = "default", animation = "pulse", ...props }, ref) => {
    const baseClasses = "bg-muted rounded-md"
    
    const variantClasses = {
      default: "h-4 w-full",
      circular: "rounded-full aspect-square",
      rectangular: "w-full h-20",
      text: "h-4 w-3/4"
    }
    
    const animationClasses = {
      pulse: "animate-pulse",
      wave: "loading-shimmer",
      none: ""
    }
    
    return (
      <div
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          animationClasses[animation],
          className
        )}
        {...props}
      />
    )
  }
)
Skeleton.displayName = "Skeleton"

// Loading Spinner Component
interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "xl"
  variant?: "default" | "dots" | "bars" | "ring"
  className?: string
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = "md", 
  variant = "default",
  className 
}) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6", 
    lg: "h-8 w-8",
    xl: "h-12 w-12"
  }
  
  if (variant === "dots") {
    return (
      <div className={cn("flex space-x-1", className)}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={cn(
              "bg-primary rounded-full animate-bounce",
              size === "sm" ? "h-2 w-2" : size === "lg" ? "h-4 w-4" : "h-3 w-3"
            )}
            style={{ animationDelay: `${i * 0.1}s` }}
          />
        ))}
      </div>
    )
  }
  
  if (variant === "bars") {
    return (
      <div className={cn("flex space-x-1", className)}>
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={cn(
              "bg-primary animate-pulse",
              size === "sm" ? "h-4 w-1" : size === "lg" ? "h-8 w-2" : "h-6 w-1.5"
            )}
            style={{ 
              animationDelay: `${i * 0.15}s`,
              animationDuration: "1s"
            }}
          />
        ))}
      </div>
    )
  }
  
  if (variant === "ring") {
    return (
      <div className={cn("relative", sizeClasses[size], className)}>
        <div className="absolute inset-0 rounded-full border-2 border-muted"></div>
        <div className="absolute inset-0 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
      </div>
    )
  }
  
  return (
    <Loader2 className={cn("animate-spin text-primary", sizeClasses[size], className)} />
  )
}

// Page Loading Component
interface PageLoadingProps {
  message?: string
  showProgress?: boolean
  progress?: number
}

const PageLoading: React.FC<PageLoadingProps> = ({ 
  message = "Loading...", 
  showProgress = false,
  progress = 0
}) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
      <LoadingSpinner size="xl" variant="ring" />
      <div className="text-center space-y-2">
        <p className="text-lg font-medium text-foreground">{message}</p>
        {showProgress && (
          <div className="w-64 bg-muted rounded-full h-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  )
}

// Card Loading Skeleton
const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn("p-6 space-y-4", className)}>
      <div className="flex items-center space-x-4">
        <Skeleton variant="circular" className="h-12 w-12" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-4/6" />
      </div>
    </div>
  )
}

// Table Loading Skeleton
const TableSkeleton: React.FC<{ rows?: number; columns?: number }> = ({ 
  rows = 5, 
  columns = 4 
}) => {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} className="h-8 flex-1" />
          ))}
        </div>
      ))}
    </div>
  )
}

// List Loading Skeleton
const ListSkeleton: React.FC<{ items?: number }> = ({ items = 6 }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center space-x-4">
          <Skeleton variant="circular" className="h-10 w-10" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
}

// Refresh Button with Loading State
interface RefreshButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
  onRefresh?: () => void
}

const RefreshButton: React.FC<RefreshButtonProps> = ({ 
  loading = false, 
  onRefresh,
  className,
  children,
  ...props 
}) => {
  return (
    <button
      onClick={onRefresh}
      disabled={loading}
      className={cn(
        "inline-flex items-center px-3 py-2 text-sm font-medium rounded-md",
        "bg-background border border-input hover:bg-accent hover:text-accent-foreground",
        "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        "transition-all duration-200",
        className
      )}
      {...props}
    >
      <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
      {children || "Refresh"}
    </button>
  )
}

export {
  Skeleton,
  LoadingSpinner,
  PageLoading,
  CardSkeleton,
  TableSkeleton,
  ListSkeleton,
  RefreshButton
}