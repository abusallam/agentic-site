import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { message, conversation_id } = await request.json()
    
    // Demo response for development environment
    const demoResponses = [
      "Thank you for your interest in our AI consulting services! How can I help you today?",
      "I understand you're looking for AI solutions. Let me connect you with our specialized team.",
      "Our AI consulting services include custom chatbots, workflow automation, and intelligent data analysis. What specific area interests you?",
      "I can help you explore our services. Would you like to schedule a consultation with our experts?",
      "Based on your inquiry, I recommend our enterprise AI solutions. Shall I provide more details?"
    ]
    
    // Simple demo logic
    const response = demoResponses[Math.floor(Math.random() * demoResponses.length)]
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    return NextResponse.json({
      response,
      type: 'text',
      handoff_required: message.toLowerCase().includes('human') || message.toLowerCase().includes('agent'),
      conversation_id
    })
    
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Failed to process chat message' },
      { status: 500 }
    )
  }
}