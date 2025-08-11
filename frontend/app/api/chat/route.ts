import { NextRequest, NextResponse } from 'next/server'

interface ChatRequest {
  message: string
  customer_id?: string
  context?: {
    session_id?: string
    current_agent?: string
    language?: string
    timestamp?: string
  }
}

interface ChatResponse {
  message: string
  confidence: number
  next_action: string
  agent_type: string
  transfer_to?: string
  context?: any
}

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json()
    const { message, customer_id, context } = body

    // Detect language from message
    const isArabic = /[\u0600-\u06FF]/.test(message)
    const language = isArabic ? 'ar' : 'en'

    // Simple agent routing logic based on message content
    let agentType = 'welcoming'
    let response: ChatResponse

    // Analyze message intent
    const messageLower = message.toLowerCase()
    const arabicMessage = message

    // Check for billing-related queries
    if (
      messageLower.includes('bill') || 
      messageLower.includes('invoice') || 
      messageLower.includes('cost') || 
      messageLower.includes('price') || 
      messageLower.includes('payment') ||
      arabicMessage.includes('فاتورة') ||
      arabicMessage.includes('تكلفة') ||
      arabicMessage.includes('دفع') ||
      arabicMessage.includes('سعر')
    ) {
      agentType = 'billing'
      response = await handleBillingAgent(message, customer_id, language)
    }
    // Check for consulting queries
    else if (
      messageLower.includes('consult') || 
      messageLower.includes('meeting') || 
      messageLower.includes('schedule') ||
      arabicMessage.includes('استشارة') ||
      arabicMessage.includes('موعد') ||
      arabicMessage.includes('جدولة')
    ) {
      agentType = 'consulting'
      response = await handleConsultingAgent(message, customer_id, language)
    }
    // Check for workflow/automation queries
    else if (
      messageLower.includes('automat') || 
      messageLower.includes('workflow') || 
      messageLower.includes('n8n') ||
      arabicMessage.includes('أتمتة') ||
      arabicMessage.includes('سير العمل')
    ) {
      agentType = 'workflow'
      response = await handleWorkflowAgent(message, customer_id, language)
    }
    // Default to welcoming agent
    else {
      response = await handleWelcomingAgent(message, customer_id, language)
    }

    return NextResponse.json({
      success: true,
      response: {
        ...response,
        agent_type: agentType
      }
    })

  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to process message',
        response: {
          message: 'I apologize, but I\'m experiencing technical difficulties. Please try again.',
          confidence: 0.5,
          next_action: 'retry',
          agent_type: 'error'
        }
      },
      { status: 500 }
    )
  }
}

async function handleWelcomingAgent(message: string, customerId?: string, language = 'en'): Promise<ChatResponse> {
  // Simulate welcoming agent response
  const responses = {
    en: {
      greeting: "Hello! I'm your AI assistant. I can help you with AI consulting, billing inquiries, workflow automation, and scheduling consultations. How can I assist you today?",
      help: "I can help you with:\n• AI Consulting Services\n• Billing and Payment Information\n• Workflow Automation\n• Schedule Consultations\n• Technical Support\n\nWhat would you like to know more about?",
      default: "Thank you for your message! I'm here to help you with our AI consulting services. Would you like to learn about our services, check billing information, or schedule a consultation?"
    },
    ar: {
      greeting: "مرحباً! أنا مساعدك الذكي. يمكنني مساعدتك في استشارات الذكاء الاصطناعي، استفسارات الفوترة، أتمتة سير العمل، وجدولة الاستشارات. كيف يمكنني مساعدتك اليوم؟",
      help: "يمكنني مساعدتك في:\n• خدمات استشارات الذكاء الاصطناعي\n• معلومات الفوترة والدفع\n• أتمتة سير العمل\n• جدولة الاستشارات\n• الدعم التقني\n\nماذا تود أن تعرف أكثر؟",
      default: "شكراً لرسالتك! أنا هنا لمساعدتك في خدمات استشارات الذكاء الاصطناعي. هل تود التعرف على خدماتنا، أو التحقق من معلومات الفوترة، أو جدولة استشارة؟"
    }
  }

  const messageType = message.toLowerCase().includes('hello') || message.includes('مرحبا') ? 'greeting' :
                     message.toLowerCase().includes('help') || message.includes('مساعدة') ? 'help' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.9,
    next_action: 'await_user_choice',
    agent_type: 'welcoming'
  }
}

async function handleBillingAgent(message: string, customerId?: string, language = 'en'): Promise<ChatResponse> {
  // Simulate billing agent response
  const responses = {
    en: {
      usage: "Here's your current resource usage summary:\n\n• Compute Resources: 25 hours - 1.25 SAR\n• Storage Usage: 10 GB - 1.00 SAR\n• AI Token Usage: 5K tokens - 0.01 SAR\n\nTotal Cost: 2.26 SAR\n\nWould you like me to generate a detailed invoice?",
      invoice: "I can generate an invoice for you. Your current usage includes compute resources, storage, and AI tokens. The total amount is 2.26 SAR including 15% VAT. Would you like me to proceed with invoice generation?",
      payment: "For payment information, you can use credit card, bank transfer, or digital wallets. All payments are processed securely. Do you need help with a specific payment method?",
      default: "I'm your billing assistant. I can help you with:\n• Current usage and costs\n• Invoice generation\n• Payment information\n• Billing history\n\nWhat would you like to know about your billing?"
    },
    ar: {
      usage: "إليك ملخص استخدام الموارد الحالي:\n\n• موارد المعالجة: 25 ساعة - 1.25 ريال\n• استخدام التخزين: 10 جيجابايت - 1.00 ريال\n• استخدام رموز الذكاء الاصطناعي: 5 آلاف رمز - 0.01 ريال\n\nإجمالي التكلفة: 2.26 ريال\n\nهل تود أن أقوم بإنشاء فاتورة مفصلة؟",
      invoice: "يمكنني إنشاء فاتورة لك. استخدامك الحالي يشمل موارد المعالجة والتخزين ورموز الذكاء الاصطناعي. المبلغ الإجمالي هو 2.26 ريال شاملاً ضريبة القيمة المضافة 15%. هل تود أن أتابع مع إنشاء الفاتورة؟",
      payment: "لمعلومات الدفع، يمكنك استخدام بطاقة ائتمان، أو تحويل بنكي، أو محافظ رقمية. جميع المدفوعات تتم بشكل آمن. هل تحتاج مساعدة في طريقة دفع معينة؟",
      default: "أنا مساعد الفوترة الخاص بك. يمكنني مساعدتك في:\n• الاستخدام والتكاليف الحالية\n• إنشاء الفواتير\n• معلومات الدفع\n• تاريخ الفوترة\n\nماذا تود أن تعرف عن فوترتك؟"
    }
  }

  const messageType = message.toLowerCase().includes('usage') || message.includes('استخدام') ? 'usage' :
                     message.toLowerCase().includes('invoice') || message.includes('فاتورة') ? 'invoice' :
                     message.toLowerCase().includes('payment') || message.includes('دفع') ? 'payment' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.95,
    next_action: 'show_billing_options',
    agent_type: 'billing'
  }
}

async function handleConsultingAgent(message: string, customerId?: string, language = 'en'): Promise<ChatResponse> {
  const responses = {
    en: {
      schedule: "I'd be happy to help you schedule a consultation! Our AI consulting sessions include:\n\n• Strategy Development\n• Technical Implementation\n• Performance Optimization\n• Custom AI Solutions\n\nWould you prefer a video call or in-person meeting? What time works best for you?",
      services: "Our consulting services include:\n\n• AI Strategy & Planning\n• Technical Feasibility Studies\n• Implementation Support\n• AI Ethics & Governance\n• Performance Optimization\n\nWhich area interests you most?",
      default: "I'm here to help with AI consulting services. I can schedule consultations, explain our services, or connect you with our specialists. How can I assist you today?"
    },
    ar: {
      schedule: "سأكون سعيداً لمساعدتك في جدولة استشارة! جلسات استشارات الذكاء الاصطناعي تشمل:\n\n• تطوير الاستراتيجية\n• التنفيذ التقني\n• تحسين الأداء\n• حلول الذكاء الاصطناعي المخصصة\n\nهل تفضل مكالمة فيديو أم اجتماع شخصي؟ ما هو الوقت الأنسب لك؟",
      services: "خدماتنا الاستشارية تشمل:\n\n• استراتيجية وتخطيط الذكاء الاصطناعي\n• دراسات الجدوى التقنية\n• دعم التنفيذ\n• أخلاقيات وحوكمة الذكاء الاصطناعي\n• تحسين الأداء\n\nأي مجال يهمك أكثر؟",
      default: "أنا هنا للمساعدة في خدمات استشارات الذكاء الاصطناعي. يمكنني جدولة الاستشارات، أو شرح خدماتنا، أو ربطك بمتخصصينا. كيف يمكنني مساعدتك اليوم؟"
    }
  }

  const messageType = message.toLowerCase().includes('schedule') || message.includes('جدولة') ? 'schedule' :
                     message.toLowerCase().includes('service') || message.includes('خدمة') ? 'services' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.9,
    next_action: 'schedule_consultation',
    agent_type: 'consulting'
  }
}

async function handleWorkflowAgent(message: string, customerId?: string, language = 'en'): Promise<ChatResponse> {
  const responses = {
    en: {
      automation: "I can help you with workflow automation! Our services include:\n\n• N8N Workflow Creation\n• Process Automation\n• API Integrations\n• Data Processing Pipelines\n• Custom Automation Solutions\n\nWhat type of workflow would you like to automate?",
      n8n: "N8N is a powerful workflow automation tool we use to create custom automation solutions. We can help you:\n\n• Design automated workflows\n• Connect different services and APIs\n• Process data automatically\n• Create custom integrations\n\nWhat would you like to automate?",
      default: "I'm your workflow automation specialist. I can help you automate repetitive tasks, create custom workflows, and integrate different systems. What processes would you like to automate?"
    },
    ar: {
      automation: "يمكنني مساعدتك في أتمتة سير العمل! خدماتنا تشمل:\n\n• إنشاء سير عمل N8N\n• أتمتة العمليات\n• تكامل واجهات برمجة التطبيقات\n• خطوط معالجة البيانات\n• حلول الأتمتة المخصصة\n\nما نوع سير العمل الذي تود أتمتته؟",
      n8n: "N8N هو أداة قوية لأتمتة سير العمل نستخدمها لإنشاء حلول أتمتة مخصصة. يمكننا مساعدتك في:\n\n• تصميم سير عمل آلي\n• ربط خدمات وواجهات برمجة مختلفة\n• معالجة البيانات تلقائياً\n• إنشاء تكاملات مخصصة\n\nماذا تود أن تؤتمت؟",
      default: "أنا متخصص أتمتة سير العمل. يمكنني مساعدتك في أتمتة المهام المتكررة، وإنشاء سير عمل مخصص، ودمج أنظمة مختلفة. ما العمليات التي تود أتمتتها؟"
    }
  }

  const messageType = message.toLowerCase().includes('automat') || message.includes('أتمتة') ? 'automation' :
                     message.toLowerCase().includes('n8n') ? 'n8n' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.9,
    next_action: 'design_workflow',
    agent_type: 'workflow'
  }
}