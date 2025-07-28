import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function GET() {
  try {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (!supabaseUrl || !supabaseKey) {
      return NextResponse.json(
        {
          connected: false,
          error: 'Supabase configuration missing',
          timestamp: new Date().toISOString(),
        },
        { status: 500 }
      )
    }

    const supabase = createClient(supabaseUrl, supabaseKey)
    
    // Simple query to test connection
    const { data, error } = await supabase
      .from('health_check')
      .select('*')
      .limit(1)

    if (error && error.code !== 'PGRST116') { // PGRST116 is "table not found" which is ok for health check
      return NextResponse.json(
        {
          connected: false,
          error: error.message,
          timestamp: new Date().toISOString(),
        },
        { status: 500 }
      )
    }

    return NextResponse.json({
      connected: true,
      timestamp: new Date().toISOString(),
      database: 'supabase',
    })
  } catch (error) {
    return NextResponse.json(
      {
        connected: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}