import { Metadata } from 'next'
import { UniversalHero } from '@/components/layout/universal-hero'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Login - consulting.sa',
  description: 'Sign in to your consulting.sa account',
}

export default function LoginPage() {
  return (
    <div className="min-h-screen">
      <UniversalHero
        title="Welcome Back"
        subtitle="Sign in to your account to access our AI consulting services"
        showActions={false}
      />
      
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-md mx-auto">
          <Card>
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl text-center">Sign In</CardTitle>
              <CardDescription className="text-center">
                Enter your credentials to access your account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  required
                />
              </div>
              <Button className="w-full btn-primary">
                Sign In
              </Button>
              <div className="text-center text-sm">
                <Link href="/auth/forgot-password" className="text-primary hover:underline">
                  Forgot your password?
                </Link>
              </div>
              <div className="text-center text-sm">
                Don't have an account?{' '}
                <Link href="/auth/signup" className="text-primary hover:underline">
                  Sign up
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}