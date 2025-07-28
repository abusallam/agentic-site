"use client"

import React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle, RefreshCw, Home, Bug, Mail } from "lucide-react"

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
  errorId?: string
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error: Error; resetError: () => void }>
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

// Error logging service
const logErrorToService = (error: Error, errorInfo: React.ErrorInfo, errorId: string) => {
  const errorData = {
    message: error.message,
    stack: error.stack,
    componentStack: errorInfo.componentStack,
    errorId,
    timestamp: new Date().toISOString(),
    userAgent: typeof window !== "undefined" ? window.navigator.userAgent : "unknown",
    url: typeof window !== "undefined" ? window.location.href : "unknown",
  }

  if (process.env.NODE_ENV === "development") {
    console.group("🚨 Error Boundary")
    console.error("Error:", error)
    console.error("Error Info:", errorInfo)
    console.error("Error Data:", errorData)
    console.groupEnd()
  }
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    return {
      hasError: true,
      error,
      errorId,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const errorId = this.state.errorId || `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    this.setState({
      error,
      errorInfo,
      errorId,
    })

    logErrorToService(error, errorInfo, errorId)
    
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  resetError = () => {
    this.setState({ 
      hasError: false, 
      error: undefined, 
      errorInfo: undefined,
      errorId: undefined 
    })
  }

  reportError = () => {
    const { error, errorId } = this.state
    const subject = `Error Report - ${errorId}`
    const body = `Error ID: ${errorId}
Error Message: ${error?.message}
Timestamp: ${new Date().toISOString()}
URL: ${typeof window !== "undefined" ? window.location.href : "unknown"}

Please describe what you were doing when this error occurred:
`
    
    const mailtoLink = `mailto:asim@main.consulting.sa?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
    if (typeof window !== "undefined") {
      window.open(mailtoLink)
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback
        return <FallbackComponent error={this.state.error!} resetError={this.resetError} />
      }

      return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-background">
          <Card className="w-full max-w-lg">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
                <AlertTriangle className="h-8 w-8 text-destructive" />
              </div>
              <CardTitle className="text-2xl">Oops! Something went wrong</CardTitle>
              <CardDescription className="text-base">
                We apologize for the inconvenience. An unexpected error has occurred.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {this.state.errorId && (
                <div className="rounded-lg bg-muted/50 p-4 border">
                  <div className="flex items-center gap-2 mb-2">
                    <Bug className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Error ID</span>
                  </div>
                  <code className="text-xs font-mono text-muted-foreground break-all">
                    {this.state.errorId}
                  </code>
                </div>
              )}

              {process.env.NODE_ENV === "development" && this.state.error && (
                <div className="rounded-lg bg-destructive/5 border border-destructive/20 p-4">
                  <h4 className="text-sm font-semibold text-destructive mb-2">Development Error Details</h4>
                  <div className="space-y-2">
                    <div>
                      <span className="text-xs font-medium text-destructive">Message:</span>
                      <p className="text-xs font-mono text-destructive/80 mt-1">
                        {this.state.error.message}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Button onClick={this.resetError} className="w-full">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </Button>
                <Button variant="outline" onClick={() => typeof window !== "undefined" && (window.location.href = "/")} className="w-full">
                  <Home className="mr-2 h-4 w-4" />
                  Go Home
                </Button>
              </div>

              <Button 
                variant="ghost" 
                onClick={this.reportError} 
                className="w-full text-muted-foreground hover:text-foreground"
                size="sm"
              >
                <Mail className="mr-2 h-4 w-4" />
                Report this error
              </Button>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

export const useErrorHandler = () => {
  return (error: Error, errorInfo?: React.ErrorInfo) => {
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    logErrorToService(error, errorInfo || { componentStack: "" }, errorId)
  }
}
