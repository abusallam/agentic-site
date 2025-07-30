"use client"

import * as React from "react"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { brandConfig } from "@/lib/brand"
import { authHelpers } from "@/lib/supabase"
import { Eye, EyeOff, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

export default function LoginPage() {
  const { t, isRTL } = useEnhancedTranslation()
  const [showPassword, setShowPassword] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState("")

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string

    try {
      const { error } = await authHelpers.signIn(email, password)

      if (error) {
        setError(error.message)
      } else {
        // Redirect to dashboard or home page
        window.location.href = "/"
      }
    } catch {
      setError("An unexpected error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/20 p-4">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="w-full max-w-md relative z-10">
        <Card className="glass-effect border-0 bg-background/80 backdrop-blur-md">
          <CardHeader className="text-center space-y-4">
            {/* Logo */}
            <Link href="/" className="flex items-center justify-center gap-3 mb-4">
              <Image src={brandConfig.logo.image || "/placeholder.svg"} alt={brandConfig.name} width={48} height={48} />
              <span className="text-xl font-bold font-heading">{brandConfig.name}</span>
            </Link>

            <div className="space-y-2">
              <CardTitle className="text-2xl font-bold">{t("auth.login.title")}</CardTitle>
              <CardDescription>{t("auth.login.subtitle")}</CardDescription>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {error && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">{t("auth.login.email")}</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="focus-ring"
                  placeholder="you@example.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">{t("auth.login.password")}</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    required
                    className={cn("focus-ring", isRTL ? "pl-10 pr-4" : "pr-10 pl-4")}
                    placeholder="••••••••"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className={cn("absolute top-1/2 -translate-y-1/2 h-8 w-8", isRTL ? "left-2" : "right-2")}
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Checkbox id="remember" />
                  <Label htmlFor="remember" className="text-sm">
                    {t("auth.login.remember")}
                  </Label>
                </div>
                <Link href="/auth/forgot-password" className="text-sm text-primary hover:underline">
                  {t("auth.login.forgot")}
                </Link>
              </div>

              <Button type="submit" className="w-full btn-gradient" disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {t("auth.login.submit")}
              </Button>
            </form>

            <div className="text-center text-sm text-muted-foreground">
              {t("auth.login.noAccount")}{" "}
              <Link href="/auth/signup" className="text-primary hover:underline font-medium">
                {t("auth.login.signUp")}
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
