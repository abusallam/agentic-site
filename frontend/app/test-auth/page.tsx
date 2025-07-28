"use client"

import { useState, useEffect } from "react"
import { supabase } from "@/lib/supabase"

export default function TestAuthPage() {
  const [result, setResult] = useState<any>(null)

  useEffect(() => {
    const testAuth = async () => {
      const email = `testuser-${Date.now()}@example.com`
      const password = "TestPassword123"

      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      })

      setResult({ data, error })
    }

    testAuth()
  }, [])

  return (
    <div>
      <h1>Auth Test</h1>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  )
}
