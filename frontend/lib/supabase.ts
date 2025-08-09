import { createClient } from '@supabase/supabase-js'

// Mock Supabase client for development when environment variables are not available
const createMockClient = () => ({
  auth: {
    signUp: async () => ({ data: null, error: { message: "Supabase not configured" } }),
    signInWithPassword: async () => ({ data: null, error: { message: "Supabase not configured" } }),
    signOut: async () => ({ error: { message: "Supabase not configured" } }),
    getUser: async () => ({ data: { user: null }, error: { message: "Supabase not configured" } }),
    resetPasswordForEmail: async () => ({ data: null, error: { message: "Supabase not configured" } }),
  },
  from: () => ({
    insert: () => ({ select: () => ({ data: null, error: { message: "Supabase not configured" } }) }),
    select: () => ({ eq: () => ({ single: () => ({ data: null, error: { message: "Supabase not configured" } }) }) }),
    update: () => ({ eq: () => ({ select: () => ({ data: null, error: { message: "Supabase not configured" } }) }) }),
  }),
})

let supabase: any

try {
  if (
    process.env.NEXT_PUBLIC_SUPABASE_URL &&
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  ) {
    supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
  } else {
    console.warn("Supabase environment variables not configured, using mock client")
    supabase = createMockClient()
  }
} catch (error) {
  console.warn("Supabase client creation failed, using mock client:", error)
  supabase = createMockClient()
}

export { supabase }

// Types for our database
export interface ContactSubmission {
  id?: string
  first_name: string
  last_name: string
  email: string
  company?: string
  service_interest?: string
  message: string
  created_at?: string
}

export interface NewsletterSubscription {
  id?: string
  email: string
  created_at?: string
}

export interface User {
  id?: string
  email: string
  first_name: string
  last_name: string
  company?: string
  role?: string
  created_at?: string
  updated_at?: string
}

// Auth helper functions with error handling
export const authHelpers = {
  async signUp(email: string, password: string, userData: Partial<User>) {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: userData,
        },
      })
      return { data, error }
    } catch {
      return { data: null, error: { message: "Authentication service unavailable" } }
    }
  },

  async signIn(email: string, password: string) {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })
      return { data, error }
    } catch {
      return { data: null, error: { message: "Authentication service unavailable" } }
    }
  },

  async signOut() {
    try {
      const { error } = await supabase.auth.signOut()
      return { error }
    } catch {
      return { error: { message: "Authentication service unavailable" } }
    }
  },

  async getCurrentUser() {
    try {
      const {
        data: { user },
        error,
      } = await supabase.auth.getUser()
      return { user, error }
    } catch {
      return { user: null, error: { message: "Authentication service unavailable" } }
    }
  },

  async resetPassword(email: string) {
    try {
      const { data, error } = await supabase.auth.resetPasswordForEmail(email)
      return { data, error }
    } catch {
      return { data: null, error: { message: "Authentication service unavailable" } }
    }
  },
}

// Database helper functions with error handling
export const dbHelpers = {
  async submitContact(submission: ContactSubmission) {
    try {
      const { data, error } = await supabase.from("contact_submissions").insert([submission]).select()
      return { data, error }
    } catch {
      return { data: null, error: { message: "Database service unavailable" } }
    }
  },

  async subscribeNewsletter(email: string) {
    try {
      const { data, error } = await supabase.from("newsletter_subscriptions").insert([{ email }]).select()
      return { data, error }
    } catch {
      return { data: null, error: { message: "Database service unavailable" } }
    }
  },

  async getUserProfile(userId: string) {
    try {
      const { data, error } = await supabase.from("user_profiles").select("*").eq("id", userId).single()
      return { data, error }
    } catch {
      return { data: null, error: { message: "Database service unavailable" } }
    }
  },

  async updateUserProfile(userId: string, updates: Partial<User>) {
    try {
      const { data, error } = await supabase.from("user_profiles").update(updates).eq("id", userId).select()
      return { data, error }
    } catch {
      return { data: null, error: { message: "Database service unavailable" } }
    }
  },
}
