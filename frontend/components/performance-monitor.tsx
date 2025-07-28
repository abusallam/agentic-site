"use client"

import { useEffect } from "react"

export function PerformanceMonitor() {
  useEffect(() => {
    // Only run in browser environment
    if (typeof window === "undefined") {
      return
    }

    // Simple performance logging for development
    if (process.env.NODE_ENV === "development") {
      console.log("Performance Monitor: Initialized")
    }
  }, [])

  return null // This component doesn't render anything
}

export default PerformanceMonitor