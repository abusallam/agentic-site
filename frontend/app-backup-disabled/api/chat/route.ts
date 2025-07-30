import { NextRequest, NextResponse } from 'next/server'

// This would connect to your Python agents
async function callPythonAgent(message: string, conversationId: string) {
  try {
    // In production, this would call your Python agent API
    // For now, we'll simulate the agent response
    
    const response = await fetch('http://localhost:8080/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        agent_type: 'root_agent'
      }),
    })

    if (response.ok) {
      return await response.json()
    } else {
      throw new Error('Agent API unavailable')
    }
  } catch (error) {
    // Fallback response when agent is not available
    return generateFallbackResponse(message)
  }
}

function generateFallbackResponse(message: string) {
  const lowerMessage = message.toLowerCase()
  
  // Service type detection
  if (lowerMessage.includes('chatbot') || lowerMessage.includes('chat bot')) {
    return {
      response: "I can help you with AI chatbot development! Our chatbots can handle customer support, lead generation, and more. They support multiple languages and integrate with your existing systems. Would you like to know more about pricing or see a demo?",
      type: "service_info",
      service_type: "chatbot",
      handoff_required: lowerMessage.includes('demo') || lowerMessage.includes('call') || lowerMessage.includes('speak')
    }
  }
  
  if (lowerMessage.includes('ai agent') || lowerMessage.includes('artificial intelligence')) {
    return {
      response: "Our AI agents can automate complex workflows, handle customer inquiries, and integrate with your business systems. They learn from your data and improve over time. What specific tasks would you like to automate?",
      type: "service_info",
      service_type: "ai_agent",
      handoff_required: lowerMessage.includes('complex') || lowerMessage.includes('custom')
    }
  }
  
  if (lowerMessage.includes('workflow') || lowerMessage.includes('automation')) {
    return {
      response: "We can help automate your business workflows! This includes order processing, inventory management, email automation, and more. Our solutions integrate with popular tools like CRM systems, databases, and APIs. What processes would you like to automate?",
      type: "service_info",
      service_type: "workflow_automation",
      handoff_required: lowerMessage.includes('integrate') || lowerMessage.includes('complex')
    }
  }
  
  // Pricing inquiries
  if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('pricing')) {
    return {
      response: "Our pricing varies based on your specific needs:\n\n• AI Chatbots: Starting at $299/month\n• AI Agents: Starting at $599/month\n• Workflow Automation: Starting at $399/month\n\nAll plans include setup, training, and ongoing support. Would you like a custom quote based on your requirements?",
      type: "pricing_info",
      handoff_required: true
    }
  }
  
  // Contact/demo requests
  if (lowerMessage.includes('demo') || lowerMessage.includes('call') || lowerMessage.includes('speak') || lowerMessage.includes('human')) {
    return {
      response: "I'd be happy to connect you with one of our specialists for a personalized demo! They can show you exactly how our solutions work for your specific use case.",
      type: "handoff",
      handoff_required: true
    }
  }
  
  // General greeting
  if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
    return {
      response: "Hello! I'm your AI assistant from consulting.sa. We specialize in:\n\n🤖 AI Chatbots for customer support\n🧠 AI Agents for workflow automation\n⚙️ Custom automation solutions\n\nWhat can I help you with today?",
      type: "greeting"
    }
  }
  
  // Default response
  return {
    response: "I understand you're interested in our AI services. We offer chatbots, AI agents, and workflow automation solutions. Could you tell me more about what you're looking for? Or would you prefer to speak with one of our specialists?",
    type: "general",
    handoff_required: false
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, conversation_id } = body

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    // Call the Python agent
    const agentResponse = await callPythonAgent(message, conversation_id || 'default')

    return NextResponse.json(agentResponse)

  } catch (error) {
    console.error('Chat API error:', error)
    
    return NextResponse.json(
      { 
        response: "I'm having trouble processing your request right now. Please try again in a moment, or contact our support team directly.",
        type: "error"
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Chat API is running',
    endpoints: {
      POST: '/api/chat - Send a message to the AI assistant'
    }
  })
}