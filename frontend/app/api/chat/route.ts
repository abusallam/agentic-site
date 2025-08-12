import { NextRequest, NextResponse } from 'next/server'
import { llmService } from '@/lib/llm-integration'

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

    // Enhanced agent routing with four specialized agents
    
    // Check for consulting queries FIRST (high-level strategic) - HIGHEST PRIORITY
    if (
      messageLower.includes('consult') || 
      messageLower.includes('strategy') ||
      messageLower.includes('strategic') ||
      messageLower.includes('expert') ||
      messageLower.includes('meeting') || 
      messageLower.includes('schedule') ||
      messageLower.includes('feasibility') ||
      messageLower.includes('brainstorm') ||
      messageLower.includes('market research') ||
      messageLower.includes('business plan') ||
      messageLower.includes('video consultation') ||
      arabicMessage.includes('استشارة') ||
      arabicMessage.includes('استراتيجية') ||
      arabicMessage.includes('خبير') ||
      arabicMessage.includes('موعد') ||
      arabicMessage.includes('جدولة') ||
      arabicMessage.includes('جدوى') ||
      arabicMessage.includes('شركتي') ||
      arabicMessage.includes('شركة') ||
      arabicMessage.includes('مؤسسة') ||
      arabicMessage.includes('تطبيق الذكاء الاصطناعي') ||
      arabicMessage.includes('عصف ذهني') ||
      arabicMessage.includes('تحليل السوق') ||
      arabicMessage.includes('خطة العمل') ||
      arabicMessage.includes('خطة التنفيذ')
    ) {
      agentType = 'consulting'
      response = await handleConsultingAgent(message, customer_id, language, context)
    }
    // Check for n8n workflow automation queries (authenticated customers) - SPECIFIC WORKFLOW TERMS ONLY
    else if (
      messageLower.includes('workflow') || 
      messageLower.includes('n8n') || 
      (messageLower.includes('automat') && !arabicMessage.includes('استشارة')) ||
      messageLower.includes('template') ||
      (messageLower.includes('execute') && !arabicMessage.includes('استشارة')) ||
      arabicMessage.includes('سير العمل') ||
      (arabicMessage.includes('أتمتة') && !arabicMessage.includes('استشارة')) ||
      arabicMessage.includes('قالب') ||
      (arabicMessage.includes('تنفيذ') && arabicMessage.includes('سير العمل')) ||
      arabicMessage.includes('تشغيل')
    ) {
      agentType = 'n8n_workflow'
      response = await handleN8nWorkflowAgent(message, customer_id, language, context)
    }
    // Check for code generation queries (medium complexity)
    else if (
      messageLower.includes('code') || 
      messageLower.includes('develop') || 
      messageLower.includes('build') ||
      messageLower.includes('project') ||
      messageLower.includes('application') ||
      messageLower.includes('system') ||
      arabicMessage.includes('كود') ||
      arabicMessage.includes('برمجة') ||
      arabicMessage.includes('تطوير') ||
      arabicMessage.includes('مشروع') ||
      (arabicMessage.includes('تطبيق') && !arabicMessage.includes('تطبيق الذكاء الاصطناعي')) ||
      arabicMessage.includes('نظام')
    ) {
      agentType = 'code_generation'
      response = await handleCodeGenerationAgent(message, customer_id, language, context)
    }
    // Check for billing-related queries
    else if (
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
    // Default to initial customer agent (new customers)
    else {
      agentType = 'initial_customer'
      response = await handleInitialCustomerAgent(message, customer_id, language, context)
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



// New specialized agent handlers for our four-agent system

async function handleInitialCustomerAgent(message: string, customerId?: string, language = 'en', context?: any): Promise<ChatResponse> {
  try {
    // Try to use real LLM first
    const llmResponse = await llmService.generateResponse({
      message,
      agent_type: 'initial_customer',
      customer_id: customerId,
      context,
      language
    })

    if (llmResponse.success && llmResponse.response) {
      return {
        message: llmResponse.response,
        confidence: 0.9,
        next_action: 'collect_customer_info',
        agent_type: 'initial_customer',
        model: llmResponse.model,
        usage: llmResponse.usage
      }
    }
  } catch (error) {
    console.error('LLM service error for initial customer agent:', error)
  }

  // Fallback to mock responses
  const responses = {
    en: {
      greeting: "Hello! Welcome to consulting.sa! I'm your AI assistant and I'm here to help you get started. I can collect your information and connect you with the right specialist. How can I assist you today?",
      info_collection: "To better assist you, I'd like to collect some basic information:\n\n• Your name\n• Email address\n• Phone number\n• How you'd like us to help you\n\nWhat's your name?",
      services_overview: "We offer comprehensive AI solutions:\n\n• AI Consulting & Strategy\n• Custom AI Agent Development\n• Workflow Automation with n8n\n• Chatbot Development\n\nI can also connect you with a human specialist if needed. What interests you most?",
      human_handoff: "I'd be happy to connect you with one of our human specialists for a more detailed discussion. Would you like to schedule a live consultation via video call?",
      default: "Thank you for contacting consulting.sa! I'm here to help you with our AI services. I can collect your information, explain our services, or connect you with a specialist. What would you like to do first?"
    },
    ar: {
      greeting: "مرحباً! أهلاً بك في consulting.sa! أنا مساعدك الذكي وأنا هنا لمساعدتك في البدء. يمكنني جمع معلوماتك وربطك بالمختص المناسب. كيف يمكنني مساعدتك اليوم؟",
      info_collection: "لمساعدتك بشكل أفضل، أود جمع بعض المعلومات الأساسية:\n\n• اسمك\n• عنوان البريد الإلكتروني\n• رقم الهاتف\n• كيف تود أن نساعدك\n\nما اسمك؟",
      services_overview: "نحن نقدم حلول ذكاء اصطناعي شاملة:\n\n• استشارات واستراتيجية الذكاء الاصطناعي\n• تطوير وكلاء ذكاء اصطناعي مخصصة\n• أتمتة سير العمل باستخدام n8n\n• تطوير روبوتات المحادثة\n\nيمكنني أيضاً ربطك بمختص بشري عند الحاجة. ما الذي يهمك أكثر؟",
      human_handoff: "سأكون سعيداً لربطك بأحد المختصين البشريين لمناقشة أكثر تفصيلاً. هل تود جدولة استشارة مباشرة عبر مكالمة فيديو؟",
      default: "شكراً لتواصلك مع consulting.sa! أنا هنا لمساعدتك في خدمات الذكاء الاصطناعي. يمكنني جمع معلوماتك، أو شرح خدماتنا، أو ربطك بمختص. ماذا تود أن تفعل أولاً؟"
    }
  }

  const messageType = message.toLowerCase().includes('hello') || message.includes('مرحبا') || message.includes('السلام') ? 'greeting' :
                     message.toLowerCase().includes('info') || message.includes('معلومات') ? 'info_collection' :
                     message.toLowerCase().includes('service') || message.includes('خدمة') ? 'services_overview' :
                     message.toLowerCase().includes('human') || message.includes('شخص') || message.includes('إنسان') ? 'human_handoff' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.9,
    next_action: 'collect_customer_info',
    agent_type: 'initial_customer'
  }
}

async function handleN8nWorkflowAgent(message: string, customerId?: string, language = 'en', context?: any): Promise<ChatResponse> {
  try {
    // Try to use real LLM first
    const llmResponse = await llmService.generateResponse({
      message,
      agent_type: 'n8n_workflow',
      customer_id: customerId,
      context,
      language
    })

    if (llmResponse.success && llmResponse.response) {
      return {
        message: llmResponse.response,
        confidence: 0.95,
        next_action: 'workflow_assistance',
        agent_type: 'n8n_workflow',
        model: llmResponse.model,
        usage: llmResponse.usage
      }
    }
  } catch (error) {
    console.error('LLM service error for n8n workflow agent:', error)
  }

  // Fallback to mock responses
  const responses = {
    en: {
      templates: "I have several ready-to-use workflow templates for you:\n\n• Email Automation (15 min setup)\n• Data Processing Pipeline (20 min setup)\n• System Integration (30 min setup)\n• Automated Notifications (10 min setup)\n• Sentiment Analysis (25 min setup)\n\nWhich template interests you, or would you like a custom workflow?",
      execute: "To execute a workflow, I need to verify your authentication first. Are you an existing customer with an active account? If yes, please provide your customer ID or email.",
      create: "I can help you create a custom n8n workflow! Let me understand your needs:\n\n• What process do you want to automate?\n• What systems need to be connected?\n• How often should it run?\n• What's the expected input/output?\n\nTell me about your automation requirements.",
      status: "I can check the status of your workflows. Please provide:\n\n• Workflow ID or name\n• Customer account information\n\nI'll show you execution history, performance metrics, and any issues.",
      default: "I'm your n8n workflow automation specialist! I can help authenticated customers with:\n\n• Creating workflows from templates\n• Executing existing workflows\n• Monitoring workflow performance\n• Custom automation solutions\n\nNote: You need to be authenticated to use workflow services. How can I help you today?"
    },
    ar: {
      templates: "لدي عدة قوالب سير عمل جاهزة للاستخدام:\n\n• أتمتة البريد الإلكتروني (إعداد 15 دقيقة)\n• خط معالجة البيانات (إعداد 20 دقيقة)\n• تكامل الأنظمة (إعداد 30 دقيقة)\n• إشعارات تلقائية (إعداد 10 دقائق)\n• تحليل المشاعر (إعداد 25 دقيقة)\n\nأي قالب يهمك، أم تريد سير عمل مخصص؟",
      execute: "لتنفيذ سير العمل، أحتاج للتحقق من صحة هويتك أولاً. هل أنت عميل حالي لديك حساب نشط؟ إذا كان الجواب نعم، يرجى تقديم معرف العميل أو البريد الإلكتروني.",
      create: "يمكنني مساعدتك في إنشاء سير عمل n8n مخصص! دعني أفهم احتياجاتك:\n\n• ما العملية التي تريد أتمتتها؟\n• ما الأنظمة التي تحتاج للربط؟\n• كم مرة يجب أن يعمل؟\n• ما المدخلات/المخرجات المتوقعة؟\n\nأخبرني عن متطلبات الأتمتة.",
      status: "يمكنني التحقق من حالة سير العمل الخاص بك. يرجى تقديم:\n\n• معرف أو اسم سير العمل\n• معلومات حساب العميل\n\nسأعرض لك تاريخ التنفيذ ومقاييس الأداء وأي مشاكل.",
      default: "أنا متخصص أتمتة سير العمل n8n! يمكنني مساعدة العملاء المصرح لهم في:\n\n• إنشاء سير عمل من القوالب\n• تنفيذ سير العمل الحالي\n• مراقبة أداء سير العمل\n• حلول الأتمتة المخصصة\n\nملاحظة: تحتاج للمصادقة لاستخدام خدمات سير العمل. كيف يمكنني مساعدتك اليوم؟"
    }
  }

  const messageType = message.toLowerCase().includes('template') || message.includes('قالب') ? 'templates' :
                     message.toLowerCase().includes('execute') || message.includes('تنفيذ') || message.includes('تشغيل') ? 'execute' :
                     message.toLowerCase().includes('create') || message.includes('إنشاء') || message.includes('بناء') ? 'create' :
                     message.toLowerCase().includes('status') || message.includes('حالة') || message.includes('وضع') ? 'status' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.95,
    next_action: 'workflow_assistance',
    agent_type: 'n8n_workflow'
  }
}

async function handleCodeGenerationAgent(message: string, customerId?: string, language = 'en', context?: any): Promise<ChatResponse> {
  try {
    // Try to use real LLM first
    const llmResponse = await llmService.generateResponse({
      message,
      agent_type: 'code_generation',
      customer_id: customerId,
      context,
      language
    })

    if (llmResponse.success && llmResponse.response) {
      return {
        message: llmResponse.response,
        confidence: 0.9,
        next_action: 'analyze_requirements',
        agent_type: 'code_generation',
        model: llmResponse.model,
        usage: llmResponse.usage
      }
    }
  } catch (error) {
    console.error('LLM service error for code generation agent:', error)
  }

  // Fallback to mock responses
  const responses = {
    en: {
      frameworks: "I can help you build AI agents using different frameworks:\n\n• Google ADK - Best for simple, production-ready agents\n• LangGraph - Perfect for complex multi-agent workflows\n• Pydantic AI - Ideal for structured, type-safe applications\n\nWhat type of agent do you want to build? Describe your requirements and I'll recommend the best framework.",
      requirements: "Great! Let me analyze your requirements to build the perfect AI agent. Please tell me:\n\n• What should your agent do? (main functionality)\n• What data sources will it use?\n• What systems should it integrate with?\n• How complex should the workflow be?\n• Any specific technical requirements?\n\nThe more details you provide, the better I can help!",
      architecture: "Based on your requirements, I'll create a complete project structure including:\n\n• Full source code with best practices\n• Database schema and models\n• API endpoints and integrations\n• Comprehensive tests\n• Documentation and setup guides\n• Deployment instructions\n\nThis usually takes 15-30 minutes. Ready to proceed?",
      default: "I'm your AI agent development specialist! I build complete, production-ready AI agents using:\n\n• Google ADK (simple agents)\n• LangGraph (complex workflows)\n• Pydantic AI (structured apps)\n\nI provide full code, tests, documentation, and deployment guides. What kind of AI agent do you want to build?"
    },
    ar: {
      frameworks: "يمكنني مساعدتك في بناء وكلاء ذكاء اصطناعي باستخدام أطر عمل مختلفة:\n\n• Google ADK - الأفضل للوكلاء البسيطة الجاهزة للإنتاج\n• LangGraph - مثالي لسير العمل المعقد متعدد الوكلاء\n• Pydantic AI - مثالي للتطبيقات المنظمة وآمنة الأنواع\n\nما نوع الوكيل الذي تريد بناءه؟ اوصف متطلباتك وسأوصي بأفضل إطار عمل.",
      requirements: "ممتاز! دعني أحلل متطلباتك لبناء الوكيل الذكي المثالي. يرجى إخباري:\n\n• ماذا يجب أن يفعل وكيلك؟ (الوظيفة الأساسية)\n• ما مصادر البيانات التي سيستخدمها؟\n• ما الأنظمة التي يجب أن يتكامل معها؟\n• ما مدى تعقيد سير العمل؟\n• أي متطلبات تقنية محددة؟\n\nكلما قدمت تفاصيل أكثر، كلما تمكنت من مساعدتك بشكل أفضل!",
      architecture: "بناءً على متطلباتك، سأنشئ هيكل مشروع كامل يتضمن:\n\n• كود مصدري كامل مع أفضل الممارسات\n• مخطط قاعدة البيانات والنماذج\n• نقاط API والتكاملات\n• اختبارات شاملة\n• وثائق وأدلة الإعداد\n• تعليمات النشر\n\nهذا عادة يستغرق 15-30 دقيقة. هل أنت مستعد للمتابعة؟",
      default: "أنا متخصص تطوير وكلاء الذكاء الاصطناعي! أبني وكلاء كاملة وجاهزة للإنتاج باستخدام:\n\n• Google ADK (وكلاء بسيطة)\n• LangGraph (سير عمل معقد)\n• Pydantic AI (تطبيقات منظمة)\n\nأقدم كود كامل واختبارات ووثائق وأدلة نشر. ما نوع الوكيل الذكي الذي تريد بناءه؟"
    }
  }

  const messageType = message.toLowerCase().includes('framework') || message.includes('إطار') || message.includes('أداة') ? 'frameworks' :
                     message.toLowerCase().includes('requirement') || message.includes('متطلب') || message.includes('احتياج') ? 'requirements' :
                     message.toLowerCase().includes('architecture') || message.includes('هيكل') || message.includes('تصميم') ? 'architecture' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.9,
    next_action: 'analyze_requirements',
    agent_type: 'code_generation'
  }
}

// Keep the existing consulting agent but enhance it
async function handleConsultingAgent(message: string, customerId?: string, language = 'en', context?: any): Promise<ChatResponse> {
  try {
    // Try to use real LLM first
    const llmResponse = await llmService.generateResponse({
      message,
      agent_type: 'consulting',
      customer_id: customerId,
      context,
      language
    })

    if (llmResponse.success && llmResponse.response) {
      return {
        message: llmResponse.response,
        confidence: 0.95,
        next_action: 'offer_consultation',
        agent_type: 'consulting',
        model: llmResponse.model,
        usage: llmResponse.usage
      }
    }
  } catch (error) {
    console.error('LLM service error for consulting agent:', error)
  }

  // Fallback to mock responses
  const responses = {
    en: {
      strategy: "I'd love to help you develop an AI strategy! Our strategic consulting includes:\n\n• AI Readiness Assessment (2000-3000 SAR)\n• Strategic Roadmap Development (3000-5000 SAR)\n• ROI Analysis & Business Case (2500-4000 SAR)\n• Implementation Planning (2000-4000 SAR)\n\nWould you like to schedule a consultation to discuss your specific needs?",
      feasibility: "Feasibility studies are crucial for AI success! Our comprehensive studies include:\n\n• Technical Feasibility Analysis (3000-5000 SAR)\n• Business Impact Assessment (2500-4000 SAR)\n• Cost-Benefit Analysis (2000-3500 SAR)\n• Risk Assessment (2000-3000 SAR)\n\nThis typically takes 1-2 weeks. Shall we schedule a consultation to get started?",
      implementation: "Implementation support ensures your AI project succeeds! Our services include:\n\n• Project Management (1500-2500 SAR/month)\n• Technical Guidance (2000-3000 SAR/month)\n• Team Training (1000-2000 SAR/session)\n• Quality Assurance (1500-2500 SAR/month)\n\nWould you like to discuss your implementation needs?",
      schedule: "I'd be happy to schedule a consultation with our AI experts! We offer:\n\n• 30-min Quick Consultation (500-800 SAR)\n• 1-hour Strategy Session (1000-1500 SAR)\n• 2-hour Deep Dive (2000-3000 SAR)\n• Full-day Workshop (5000-8000 SAR)\n\nWhat type of consultation would work best for you?",
      default: "I'm your AI consulting specialist! I provide strategic guidance for AI implementation. Our services include strategy development, feasibility studies, implementation support, and expert consultations. I can also connect you with our human consultants via video call. How can I help you succeed with AI?"
    },
    ar: {
      strategy: "سأكون سعيداً لمساعدتك في تطوير استراتيجية الذكاء الاصطناعي! استشاراتنا الاستراتيجية تشمل:\n\n• تقييم الجاهزية للذكاء الاصطناعي (2000-3000 ريال)\n• تطوير خارطة طريق استراتيجية (3000-5000 ريال)\n• تحليل العائد على الاستثمار (2500-4000 ريال)\n• تخطيط التنفيذ (2000-4000 ريال)\n\nهل تود جدولة استشارة لمناقشة احتياجاتك المحددة؟",
      feasibility: "دراسات الجدوى ضرورية لنجاح الذكاء الاصطناعي! دراساتنا الشاملة تشمل:\n\n• تحليل الجدوى التقنية (3000-5000 ريال)\n• تقييم الأثر التجاري (2500-4000 ريال)\n• تحليل التكلفة والفائدة (2000-3500 ريال)\n• تقييم المخاطر (2000-3000 ريال)\n\nهذا عادة يستغرق 1-2 أسبوع. هل نجدول استشارة للبدء؟",
      implementation: "دعم التنفيذ يضمن نجاح مشروع الذكاء الاصطناعي! خدماتنا تشمل:\n\n• إدارة المشاريع (1500-2500 ريال/شهر)\n• التوجيه التقني (2000-3000 ريال/شهر)\n• تدريب الفريق (1000-2000 ريال/جلسة)\n• ضمان الجودة (1500-2500 ريال/شهر)\n\nهل تود مناقشة احتياجات التنفيذ؟",
      schedule: "سأكون سعيداً لجدولة استشارة مع خبراء الذكاء الاصطناعي! نقدم:\n\n• استشارة سريعة 30 دقيقة (500-800 ريال)\n• جلسة استراتيجية ساعة واحدة (1000-1500 ريال)\n• جلسة تفصيلية ساعتان (2000-3000 ريال)\n• ورشة عمل يوم كامل (5000-8000 ريال)\n\nما نوع الاستشارة الأنسب لك؟",
      default: "أنا متخصص استشارات الذكاء الاصطناعي! أقدم التوجيه الاستراتيجي لتطبيق الذكاء الاصطناعي. خدماتنا تشمل تطوير الاستراتيجية، ودراسات الجدوى، ودعم التنفيذ، والاستشارات الخبيرة. يمكنني أيضاً ربطك بمستشارينا البشريين عبر مكالمة فيديو. كيف يمكنني مساعدتك للنجاح مع الذكاء الاصطناعي؟"
    }
  }

  const messageType = message.toLowerCase().includes('strategy') || message.includes('استراتيجية') ? 'strategy' :
                     message.toLowerCase().includes('feasibility') || message.includes('جدوى') ? 'feasibility' :
                     message.toLowerCase().includes('implementation') || message.includes('تنفيذ') ? 'implementation' :
                     message.toLowerCase().includes('schedule') || message.includes('جدولة') || message.includes('موعد') ? 'schedule' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.95,
    next_action: 'offer_consultation',
    agent_type: 'consulting'
  }
}