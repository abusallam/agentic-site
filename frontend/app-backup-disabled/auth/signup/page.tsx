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
import { Eye, EyeOff, Loader2, Check, X } from "lucide-react"
import { cn } from "@/lib/utils"

export default function SignupPage() {
  const { t, isRTL } = useEnhancedTranslation()
  const [showPassword, setShowPassword] = React.useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [confirmPassword, setConfirmPassword] = React.useState("")

  const passwordRequirements = [
    { label: "At least 8 characters", test: (pwd: string) => pwd.length >= 8 },
    { label: "Contains uppercase letter", test: (pwd: string) => /[A-Z]/.test(pwd) },
    { label: "Contains lowercase letter", test: (pwd: string) => /[a-z]/.test(pwd) },
    { label: "Contains number", test: (pwd: string) => /\d/.test(pwd) },
  ]

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const firstName = formData.get("firstName") as string
    const lastName = formData.get("lastName") as string
    const company = formData.get("company") as string

    if (password !== confirmPassword) {
      setError("Passwords do not match")
      setIsLoading(false)
      return
    }

    try {
      const { error } = await authHelpers.signUp(email, password, {
        first_name: firstName,
        last_name: lastName,
        company,
      })

      if (error) {
        setError(error.message)
      } else {
        // Redirect to verification page or dashboard
        window.location.href = "/auth/verify-email"
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
              <CardTitle className="text-2xl font-bold">{t("auth.signup.title")}</CardTitle>
              <CardDescription>{t("auth.signup.subtitle")}</CardDescription>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {error && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">{t("auth.signup.firstName")}</Label>
                  <Input id="firstName" name="firstName" required className="focus-ring" placeholder="John" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">{t("auth.signup.lastName")}</Label>
                  <Input id="lastName" name="lastName" required className="focus-ring" placeholder="Doe" />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">{t("auth.signup.email")}</Label>
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
                <Label htmlFor="company">{t("auth.signup.company")}</Label>
                <Input id="company" name="company" className="focus-ring" placeholder="Your Company" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">{t("auth.signup.password")}</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
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

                {/* Password Requirements */}
                {password && (
                  <div className="space-y-1 text-xs">
                    {passwordRequirements.map((req, index) => (
                      <div key={index} className="flex items-center gap-2">
                        {req.test(password) ? (
                          <Check className="h-3 w-3 text-green-500" />
                        ) : (
                          <X className="h-3 w-3 text-muted-foreground" />
                        )}
                        <span className={req.test(password) ? "text-green-600" : "text-muted-foreground"}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">{t("auth.signup.confirmPassword")}</Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className={cn("focus-ring", isRTL ? "pl-10 pr-4" : "pr-10 pl-4")}
                    placeholder="••••••••"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className={cn("absolute top-1/2 -translate-y-1/2 h-8 w-8", isRTL ? "left-2" : "right-2")}
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                {confirmPassword && password !== confirmPassword && (
                  <p className="text-xs text-destructive">Passwords do not match</p>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox id="terms" required />
                <Label htmlFor="terms" className="text-sm">
                  {t("auth.signup.agree")}{" "}
                  <Link href="/terms" className="text-primary hover:underline">
                    Terms of Service
                  </Link>
                </Label>
              </div>

              <Button
                type="submit"
                className="w-full btn-gradient"
                disabled={isLoading || password !== confirmPassword}
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {t("auth.signup.submit")}
              </Button>
            </form>

            <div className="text-center text-sm text-muted-foreground">
              {t("auth.signup.hasAccount")}{" "}
              <Link href="/auth/login" className="text-primary hover:underline font-medium">
                {t("auth.signup.signIn")}
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
