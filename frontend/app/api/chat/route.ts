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
      response: response.message,
      agent_type: agentType,
      confidence: response.confidence,
      next_action: response.next_action,
      actions: response.actions || [],
      language: language,
      model: response.model,
      usage: response.usage
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
    // Enhanced context for initial customer agent with guardrails
    const enhancedContext = {
      ...context,
      guardrails_active: true,
      rate_limiting: true,
      content_filtering: true,
      user_profile: context?.user_profile || null
    }

    // Try to use real LLM first
    const llmResponse = await llmService.generateResponse({
      message,
      agent_type: 'initial_customer',
      customer_id: customerId,
      context: enhancedContext,
      language
    })

    if (llmResponse.success && llmResponse.response) {
      return {
        message: llmResponse.response,
        confidence: 0.9,
        next_action: 'collect_customer_info',
        agent_type: 'initial_customer',
        model: llmResponse.model,
        usage: llmResponse.usage,
        guardrails_applied: true,
        capabilities: ['voice_interaction', 'text_to_speech', 'info_collection', 'service_routing']
      }
    }
  } catch (error) {
    console.error('LLM service error for initial customer agent:', error)
  }

  // Enhanced fallback responses with guardrails
  const responses = {
    en: {
      greeting: "🛡️ Hello! Welcome to consulting.sa! I'm your secure AI assistant with voice capabilities. I can help you get started safely. Try speaking to me or type your message!",
      info_collection: "📋 To better assist you, I'd like to collect some basic information:\n\n• Your name\n• Email address\n• Phone number\n• Preferred service (Quick/Coded/Consulting)\n\n🎤 You can speak or type your response. What's your name?",
      services_overview: "🚀 We offer comprehensive AI solutions:\n\n• 🧠 AI Consulting & Strategy\n• 💻 Custom AI Agent Development  \n• ⚡ Workflow Automation with n8n\n• 🤖 Chatbot Development\n\n🎯 I can connect you with the right specialist. What interests you most?",
      human_handoff: "👥 I'd be happy to connect you with one of our human specialists for a detailed discussion. Would you like to schedule a live video consultation?",
      voice_enabled: "🎤 Voice interaction is now enabled! You can speak to me in Arabic or English. How can I help you today?",
      file_upload: "📁 I can help you with file uploads for analysis. What type of file would you like to share?",
      default: "🌟 Thank you for contacting consulting.sa! I'm your secure AI assistant with voice and file capabilities. I can collect your information, explain our services, or connect you with a specialist. What would you like to do first?"
    },
    ar: {
      greeting: "🛡️ مرحباً! أهلاً بك في consulting.sa! أنا مساعدك الذكي الآمن مع إمكانيات صوتية. يمكنني مساعدتك في البدء بأمان. جرب التحدث معي أو اكتب رسالتك!",
      info_collection: "📋 لمساعدتك بشكل أفضل، أود جمع بعض المعلومات الأساسية:\n\n• اسمك\n• عنوان البريد الإلكتروني\n• رقم الهاتف\n• الخدمة المفضلة (سريع/مبرمج/استشاري)\n\n🎤 يمكنك التحدث أو الكتابة. ما اسمك؟",
      services_overview: "🚀 نحن نقدم حلول ذكاء اصطناعي شاملة:\n\n• 🧠 استشارات واستراتيجية الذكاء الاصطناعي\n• 💻 تطوير وكلاء ذكاء اصطناعي مخصصة\n• ⚡ أتمتة سير العمل باستخدام n8n\n• 🤖 تطوير روبوتات المحادثة\n\n🎯 يمكنني ربطك بالمختص المناسب. ما الذي يهمك أكثر؟",
      human_handoff: "👥 سأكون سعيداً لربطك بأحد المختصين البشريين لمناقشة مفصلة. هل تود جدولة استشارة فيديو مباشرة؟",
      voice_enabled: "🎤 تم تفعيل التفاعل الصوتي! يمكنك التحدث معي بالعربية أو الإنجليزية. كيف يمكنني مساعدتك اليوم؟",
      file_upload: "📁 يمكنني مساعدتك في رفع الملفات للتحليل. ما نوع الملف الذي تود مشاركته؟",
      default: "🌟 شكراً لتواصلك مع consulting.sa! أنا مساعدك الذكي الآمن مع إمكانيات صوتية وملفات. يمكنني جمع معلوماتك، أو شرح خدماتنا، أو ربطك بمختص. ماذا تود أن تفعل أولاً؟"
    }
  }

  // Enhanced message type detection
  const messageType = message.toLowerCase().includes('hello') || message.includes('مرحبا') || message.includes('السلام') ? 'greeting' :
                     message.toLowerCase().includes('info') || message.includes('معلومات') ? 'info_collection' :
                     message.toLowerCase().includes('service') || message.includes('خدمة') ? 'services_overview' :
                     message.toLowerCase().includes('human') || message.includes('شخص') || message.includes('إنسان') ? 'human_handoff' :
                     message.toLowerCase().includes('voice') || message.includes('صوت') ? 'voice_enabled' :
                     message.toLowerCase().includes('file') || message.includes('ملف') ? 'file_upload' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.9,
    next_action: 'collect_customer_info',
    agent_type: 'initial_customer',
    guardrails_applied: true,
    capabilities: ['voice_interaction', 'text_to_speech', 'info_collection', 'service_routing', 'file_upload', 'guardrails']
  }
}

async function handleN8nWorkflowAgent(message: string, customerId?: string, language = 'en', context?: any): Promise<ChatResponse> {
  try {
    // Enhanced context for n8n workflow agent
    const enhancedContext = {
      ...context,
      authenticated_user: customerId ? true : false,
      oauth_enabled: true,
      composio_integration: true,
      user_profile: context?.user_profile || null
    }

    // Try to use real LLM first
    const llmResponse = await llmService.generateResponse({
      message,
      agent_type: 'n8n_workflow',
      customer_id: customerId,
      context: enhancedContext,
      language
    })

    if (llmResponse.success && llmResponse.response) {
      return {
        message: llmResponse.response,
        confidence: 0.95,
        next_action: 'workflow_assistance',
        agent_type: 'n8n_workflow',
        model: llmResponse.model,
        usage: llmResponse.usage,
        capabilities: ['voice_interaction', 'file_upload', 'workflow_creation', 'oauth_integration', 'template_library']
      }
    }
  } catch (error) {
    console.error('LLM service error for n8n workflow agent:', error)
  }

  // Enhanced fallback responses with advanced capabilities
  const responses = {
    en: {
      templates: "🔧 I have several ready-to-use workflow templates for you:\n\n• 📧 Email Automation (15 min setup)\n• 📊 Data Processing Pipeline (20 min setup)\n• 🔗 System Integration (30 min setup)\n• 🔔 Automated Notifications (10 min setup)\n• 💭 Sentiment Analysis (25 min setup)\n• 📁 File Processing Workflows (20 min setup)\n• 🎤 Voice-triggered Automations (25 min setup)\n\n🎯 Which template interests you, or would you like a custom workflow? You can also upload files for analysis!",
      execute: "⚡ To execute a workflow, I need to verify your authentication first. Are you an existing customer with an active account?\n\n🔐 Authentication options:\n• Customer ID or email\n• OAuth via Composio\n• Voice verification available\n\nHow would you like to authenticate?",
      create: "🚀 I can help you create a custom n8n workflow with advanced capabilities!\n\n📋 Let me understand your needs:\n• What process do you want to automate?\n• What systems need to be connected?\n• How often should it run?\n• What's the expected input/output?\n• Do you need voice triggers?\n• Any file processing requirements?\n\n🎤 You can speak or type your automation requirements!",
      status: "📊 I can check the status of your workflows with real-time monitoring:\n\n🔍 Please provide:\n• Workflow ID or name\n• Customer account information\n\n📈 I'll show you:\n• Execution history\n• Performance metrics\n• Error logs and issues\n• Resource usage\n• Success rates\n\n🎤 You can also ask me verbally about specific workflows!",
      file_processing: "📁 I can help you create file processing workflows!\n\n🔧 Supported file types:\n• Documents (PDF, Word, Excel)\n• Images (JPG, PNG, GIF)\n• Data files (CSV, JSON, XML)\n• Code files (Python, JavaScript, etc.)\n\n📤 Upload your file and I'll create a custom workflow to process it automatically!",
      oauth_setup: "🔐 I can help you set up OAuth integrations via Composio:\n\n🌐 Supported services:\n• Google Workspace\n• Microsoft 365\n• Slack\n• Salesforce\n• And 100+ more!\n\n🎯 Which service would you like to connect?",
      default: "🤖 I'm your advanced n8n workflow automation specialist with voice and file capabilities!\n\n✨ I can help authenticated customers with:\n• 🔧 Creating workflows from templates\n• ⚡ Executing existing workflows\n• 📊 Monitoring workflow performance\n• 🎤 Voice-controlled automation\n• 📁 File processing workflows\n• 🔐 OAuth integrations via Composio\n• 🚀 Custom automation solutions\n\n🛡️ Note: Authentication required for workflow services. How can I help you today?"
    },
    ar: {
      templates: "🔧 لدي عدة قوالب سير عمل جاهزة للاستخدام:\n\n• 📧 أتمتة البريد الإلكتروني (إعداد 15 دقيقة)\n• 📊 خط معالجة البيانات (إعداد 20 دقيقة)\n• 🔗 تكامل الأنظمة (إعداد 30 دقيقة)\n• 🔔 إشعارات تلقائية (إعداد 10 دقائق)\n• 💭 تحليل المشاعر (إعداد 25 دقيقة)\n• 📁 سير عمل معالجة الملفات (إعداد 20 دقيقة)\n• 🎤 أتمتة مفعلة بالصوت (إعداد 25 دقيقة)\n\n🎯 أي قالب يهمك، أم تريد سير عمل مخصص؟ يمكنك أيضاً رفع ملفات للتحليل!",
      execute: "⚡ لتنفيذ سير العمل، أحتاج للتحقق من صحة هويتك أولاً. هل أنت عميل حالي لديك حساب نشط؟\n\n🔐 خيارات المصادقة:\n• معرف العميل أو البريد الإلكتروني\n• OAuth عبر Composio\n• التحقق الصوتي متاح\n\nكيف تود المصادقة؟",
      create: "🚀 يمكنني مساعدتك في إنشاء سير عمل n8n مخصص مع إمكانيات متقدمة!\n\n📋 دعني أفهم احتياجاتك:\n• ما العملية التي تريد أتمتتها؟\n• ما الأنظمة التي تحتاج للربط؟\n• كم مرة يجب أن يعمل؟\n• ما المدخلات والمخرجات المتوقعة؟\n• هل تحتاج مشغلات صوتية؟\n• أي متطلبات لمعالجة الملفات؟\n\n🎤 يمكنك التحدث أو الكتابة عن متطلبات الأتمتة!",
      status: "📊 يمكنني التحقق من حالة سير العمل مع المراقبة في الوقت الفعلي:\n\n🔍 يرجى تقديم:\n• معرف أو اسم سير العمل\n• معلومات حساب العميل\n\n📈 سأعرض لك:\n• تاريخ التنفيذ\n• مقاييس الأداء\n• سجلات الأخطاء والمشاكل\n• استخدام الموارد\n• معدلات النجاح\n\n🎤 يمكنك أيضاً سؤالي شفهياً عن سير عمل محدد!",
      file_processing: "📁 يمكنني مساعدتك في إنشاء سير عمل لمعالجة الملفات!\n\n🔧 أنواع الملفات المدعومة:\n• المستندات (PDF، Word، Excel)\n• الصور (JPG، PNG، GIF)\n• ملفات البيانات (CSV، JSON، XML)\n• ملفات الكود (Python، JavaScript، إلخ)\n\n📤 ارفع ملفك وسأنشئ سير عمل مخصص لمعالجته تلقائياً!",
      oauth_setup: "🔐 يمكنني مساعدتك في إعداد تكاملات OAuth عبر Composio:\n\n🌐 الخدمات المدعومة:\n• Google Workspace\n• Microsoft 365\n• Slack\n• Salesforce\n• وأكثر من 100 خدمة أخرى!\n\n🎯 أي خدمة تود ربطها؟",
      default: "🤖 أنا متخصص أتمتة سير العمل n8n المتقدم مع إمكانيات صوتية وملفات!\n\n✨ يمكنني مساعدة العملاء المصرح لهم في:\n• 🔧 إنشاء سير عمل من القوالب\n• ⚡ تنفيذ سير العمل الحالي\n• 📊 مراقبة أداء سير العمل\n• 🎤 أتمتة مُتحكم بها بالصوت\n• 📁 سير عمل معالجة الملفات\n• 🔐 تكاملات OAuth عبر Composio\n• 🚀 حلول الأتمتة المخصصة\n\n🛡️ ملاحظة: المصادقة مطلوبة لخدمات سير العمل. كيف يمكنني مساعدتك اليوم؟"
    }
  }

  const messageType = message.toLowerCase().includes('template') || message.includes('قالب') ? 'templates' :
                     message.toLowerCase().includes('execute') || message.includes('تنفيذ') || message.includes('تشغيل') ? 'execute' :
                     message.toLowerCase().includes('create') || message.includes('إنشاء') || message.includes('بناء') ? 'create' :
                     message.toLowerCase().includes('status') || message.includes('حالة') || message.includes('وضع') ? 'status' :
                     message.toLowerCase().includes('file') || message.includes('ملف') ? 'file_processing' :
                     message.toLowerCase().includes('oauth') || message.includes('تكامل') ? 'oauth_setup' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.95,
    next_action: 'workflow_assistance',
    agent_type: 'n8n_workflow',
    capabilities: ['voice_interaction', 'file_upload', 'workflow_creation', 'oauth_integration', 'template_library', 'real_time_monitoring']
  }
}

async function handleCodeGenerationAgent(message: string, customerId?: string, language = 'en', context?: any): Promise<ChatResponse> {
  try {
    // Enhanced context for code generation agent
    const enhancedContext = {
      ...context,
      code_generation_enabled: true,
      file_processing: true,
      voice_interaction: true,
      user_profile: context?.user_profile || null
    }

    // Try to use real LLM first
    const llmResponse = await llmService.generateResponse({
      message,
      agent_type: 'code_generation',
      customer_id: customerId,
      context: enhancedContext,
      language
    })

    if (llmResponse.success && llmResponse.response) {
      return {
        message: llmResponse.response,
        confidence: 0.9,
        next_action: 'analyze_requirements',
        agent_type: 'code_generation',
        model: llmResponse.model,
        usage: llmResponse.usage,
        capabilities: ['voice_interaction', 'file_upload', 'code_generation', 'architecture_design', 'testing_framework']
      }
    }
  } catch (error) {
    console.error('LLM service error for code generation agent:', error)
  }

  // Enhanced fallback responses with advanced capabilities
  const responses = {
    en: {
      frameworks: "💻 I can help you build AI agents using different frameworks with voice and file capabilities:\n\n• 🚀 Google ADK - Best for simple, production-ready agents\n• 🔄 LangGraph - Perfect for complex multi-agent workflows\n• 🛡️ Pydantic AI - Ideal for structured, type-safe applications\n\n🎤 You can describe your requirements by voice or upload specification files!\n\nWhat type of agent do you want to build? Describe your requirements and I'll recommend the best framework.",
      requirements: "🎯 Great! Let me analyze your requirements to build the perfect AI agent with advanced capabilities:\n\n📋 Please tell me:\n• What should your agent do? (main functionality)\n• What data sources will it use?\n• What systems should it integrate with?\n• How complex should the workflow be?\n• Any specific technical requirements?\n• Do you need voice interaction?\n• File processing capabilities?\n\n🎤 You can speak your requirements or upload specification documents!\n\nThe more details you provide, the better I can help!",
      architecture: "🏗️ Based on your requirements, I'll create a complete project structure with advanced features:\n\n📦 Full Package Includes:\n• 💻 Full source code with best practices\n• 🗄️ Database schema and models\n• 🔌 API endpoints and integrations\n• 🧪 Comprehensive tests\n• 📚 Documentation and setup guides\n• 🚀 Deployment instructions\n• 🎤 Voice interaction capabilities\n• 📁 File processing features\n• 🛡️ Security implementations\n\n⏱️ This usually takes 15-30 minutes. Ready to proceed?",
      file_analysis: "📁 I can analyze your uploaded files to understand your code requirements!\n\n🔍 Supported file types:\n• Code files (Python, JavaScript, TypeScript, etc.)\n• Architecture diagrams\n• Requirements documents\n• API specifications (OpenAPI, GraphQL)\n• Database schemas\n\n📤 Upload your files and I'll create a custom AI agent based on your specifications!",
      voice_coding: "🎤 Voice-powered coding is available! You can:\n\n• Describe your agent requirements verbally\n• Explain complex workflows by speaking\n• Request code modifications through voice\n• Get audio explanations of generated code\n\n🗣️ Try saying: 'Create a customer service agent with voice capabilities'",
      testing: "🧪 I provide comprehensive testing frameworks:\n\n• Unit tests for all components\n• Integration tests for API endpoints\n• Voice interaction testing\n• File processing validation\n• Performance benchmarks\n• Security testing\n\n🎯 All generated code comes with complete test coverage!",
      default: "💻 I'm your advanced AI agent development specialist with voice and file capabilities!\n\n✨ I build complete, production-ready AI agents using:\n• 🚀 Google ADK (simple agents)\n• 🔄 LangGraph (complex workflows)\n• 🛡️ Pydantic AI (structured apps)\n\n🎤 Advanced Features:\n• Voice interaction support\n• File upload and processing\n• Complete testing frameworks\n• Security implementations\n• Documentation generation\n• Deployment automation\n\n📁 Upload files or 🎤 speak your requirements! What kind of AI agent do you want to build?"
    },
    ar: {
      frameworks: "💻 يمكنني مساعدتك في بناء وكلاء ذكاء اصطناعي باستخدام أطر عمل مختلفة مع إمكانيات صوتية وملفات:\n\n• 🚀 Google ADK - الأفضل للوكلاء البسيطة الجاهزة للإنتاج\n• 🔄 LangGraph - مثالي لسير العمل المعقد متعدد الوكلاء\n• 🛡️ Pydantic AI - مثالي للتطبيقات المنظمة وآمنة الأنواع\n\n🎤 يمكنك وصف متطلباتك بالصوت أو رفع ملفات المواصفات!\n\nما نوع الوكيل الذي تريد بناءه؟ اوصف متطلباتك وسأوصي بأفضل إطار عمل.",
      requirements: "🎯 ممتاز! دعني أحلل متطلباتك لبناء الوكيل الذكي المثالي مع إمكانيات متقدمة:\n\n📋 يرجى إخباري:\n• ماذا يجب أن يفعل وكيلك؟ (الوظيفة الأساسية)\n• ما مصادر البيانات التي سيستخدمها؟\n• ما الأنظمة التي يجب أن يتكامل معها؟\n• ما مدى تعقيد سير العمل؟\n• أي متطلبات تقنية محددة؟\n• هل تحتاج تفاعل صوتي؟\n• إمكانيات معالجة الملفات؟\n\n🎤 يمكنك نطق متطلباتك أو رفع مستندات المواصفات!\n\nكلما قدمت تفاصيل أكثر، كلما تمكنت من مساعدتك بشكل أفضل!",
      architecture: "🏗️ بناءً على متطلباتك، سأنشئ هيكل مشروع كامل مع ميزات متقدمة:\n\n📦 الحزمة الكاملة تشمل:\n• 💻 كود مصدري كامل مع أفضل الممارسات\n• 🗄️ مخطط قاعدة البيانات والنماذج\n• 🔌 نقاط API والتكاملات\n• 🧪 اختبارات شاملة\n• 📚 وثائق وأدلة الإعداد\n• 🚀 تعليمات النشر\n• 🎤 إمكانيات التفاعل الصوتي\n• 📁 ميزات معالجة الملفات\n• 🛡️ تطبيقات الأمان\n\n⏱️ هذا عادة يستغرق 15-30 دقيقة. هل أنت مستعد للمتابعة؟",
      file_analysis: "📁 يمكنني تحليل الملفات المرفوعة لفهم متطلبات الكود الخاصة بك!\n\n🔍 أنواع الملفات المدعومة:\n• ملفات الكود (Python، JavaScript، TypeScript، إلخ)\n• مخططات الهيكل\n• مستندات المتطلبات\n• مواصفات API (OpenAPI، GraphQL)\n• مخططات قاعدة البيانات\n\n📤 ارفع ملفاتك وسأنشئ وكيل ذكي مخصص بناءً على مواصفاتك!",
      voice_coding: "🎤 البرمجة بالصوت متاحة! يمكنك:\n\n• وصف متطلبات الوكيل شفهياً\n• شرح سير العمل المعقد بالكلام\n• طلب تعديلات الكود عبر الصوت\n• الحصول على شروحات صوتية للكود المُولد\n\n🗣️ جرب قول: 'أنشئ وكيل خدمة عملاء مع إمكانيات صوتية'",
      testing: "🧪 أقدم أطر اختبار شاملة:\n\n• اختبارات الوحدة لجميع المكونات\n• اختبارات التكامل لنقاط API\n• اختبار التفاعل الصوتي\n• التحقق من معالجة الملفات\n• معايير الأداء\n• اختبار الأمان\n\n🎯 جميع الأكواد المُولدة تأتي مع تغطية اختبار كاملة!",
      default: "💻 أنا متخصص تطوير وكلاء الذكاء الاصطناعي المتقدم مع إمكانيات صوتية وملفات!\n\n✨ أبني وكلاء كاملة وجاهزة للإنتاج باستخدام:\n• 🚀 Google ADK (وكلاء بسيطة)\n• 🔄 LangGraph (سير عمل معقد)\n• 🛡️ Pydantic AI (تطبيقات منظمة)\n\n🎤 الميزات المتقدمة:\n• دعم التفاعل الصوتي\n• رفع ومعالجة الملفات\n• أطر اختبار كاملة\n• تطبيقات الأمان\n• توليد الوثائق\n• أتمتة النشر\n\n📁 ارفع الملفات أو 🎤 انطق متطلباتك! ما نوع الوكيل الذكي الذي تريد بناءه؟"
    }
  }

  const messageType = message.toLowerCase().includes('framework') || message.includes('إطار') || message.includes('أداة') ? 'frameworks' :
                     message.toLowerCase().includes('requirement') || message.includes('متطلب') || message.includes('احتياج') ? 'requirements' :
                     message.toLowerCase().includes('architecture') || message.includes('هيكل') || message.includes('تصميم') ? 'architecture' :
                     message.toLowerCase().includes('file') || message.includes('ملف') ? 'file_analysis' :
                     message.toLowerCase().includes('voice') || message.includes('صوت') ? 'voice_coding' :
                     message.toLowerCase().includes('test') || message.includes('اختبار') ? 'testing' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.9,
    next_action: 'analyze_requirements',
    agent_type: 'code_generation',
    capabilities: ['voice_interaction', 'file_upload', 'code_generation', 'architecture_design', 'testing_framework', 'security_implementation']
  }
}

// Enhanced consulting agent with live session capabilities
async function handleConsultingAgent(message: string, customerId?: string, language = 'en', context?: any): Promise<ChatResponse> {
  try {
    // Enhanced context for consulting agent
    const enhancedContext = {
      ...context,
      live_session_enabled: true,
      livekit_integration: true,
      voice_consultation: true,
      user_profile: context?.user_profile || null
    }

    // Try to use real LLM first
    const llmResponse = await llmService.generateResponse({
      message,
      agent_type: 'consulting',
      customer_id: customerId,
      context: enhancedContext,
      language
    })

    if (llmResponse.success && llmResponse.response) {
      return {
        message: llmResponse.response,
        confidence: 0.95,
        next_action: 'offer_consultation',
        agent_type: 'consulting',
        model: llmResponse.model,
        usage: llmResponse.usage,
        capabilities: ['voice_interaction', 'live_sessions', 'strategic_consulting', 'file_analysis', 'video_consultation']
      }
    }
  } catch (error) {
    console.error('LLM service error for consulting agent:', error)
  }

  // Enhanced fallback responses with live session capabilities
  const responses = {
    en: {
      strategy: "🧠 I'd love to help you develop an AI strategy with live consultation support!\n\n💼 Our strategic consulting includes:\n• 📊 AI Readiness Assessment (2000-3000 SAR)\n• 🗺️ Strategic Roadmap Development (3000-5000 SAR)\n• 💰 ROI Analysis & Business Case (2500-4000 SAR)\n• 📋 Implementation Planning (2000-4000 SAR)\n• 🎤 Voice consultation sessions\n• 📹 Live video strategy sessions\n\n🎯 Would you like to schedule a live consultation to discuss your specific needs?",
      feasibility: "🔍 Feasibility studies are crucial for AI success with comprehensive analysis!\n\n📈 Our studies include:\n• 🔧 Technical Feasibility Analysis (3000-5000 SAR)\n• 📊 Business Impact Assessment (2500-4000 SAR)\n• 💹 Cost-Benefit Analysis (2000-3500 SAR)\n• ⚠️ Risk Assessment (2000-3000 SAR)\n• 🎤 Voice-guided analysis sessions\n• 📁 Document analysis and review\n\n⏱️ This typically takes 1-2 weeks. Shall we schedule a live consultation to get started?",
      implementation: "🚀 Implementation support ensures your AI project succeeds with hands-on guidance!\n\n🛠️ Our services include:\n• 📋 Project Management (1500-2500 SAR/month)\n• 🎯 Technical Guidance (2000-3000 SAR/month)\n• 👥 Team Training (1000-2000 SAR/session)\n• ✅ Quality Assurance (1500-2500 SAR/month)\n• 🎤 Voice coaching sessions\n• 📹 Live implementation reviews\n• 📁 Document and code reviews\n\n🎯 Would you like to discuss your implementation needs in a live session?",
      schedule: "📅 I'd be happy to schedule a consultation with our AI experts with multiple options!\n\n🎯 Consultation Types:\n• ⚡ 30-min Quick Consultation (500-800 SAR)\n• 🧠 1-hour Strategy Session (1000-1500 SAR)\n• 🔍 2-hour Deep Dive (2000-3000 SAR)\n• 🏢 Full-day Workshop (5000-8000 SAR)\n• 🎤 Voice-only consultation (20% discount)\n• 📹 Video consultation (premium experience)\n• 📁 Document review session (additional 500 SAR)\n\n🎯 What type of consultation would work best for you?",
      live_session: "🎥 Live session capabilities are available now!\n\n✨ Features include:\n• 📹 HD video consultation\n• 🎤 Crystal clear audio\n• 📱 Screen sharing for presentations\n• 📝 Real-time note taking\n• 📁 Document sharing and review\n• 🔄 Session recording for later review\n\n🚀 Ready to start a live session? I can connect you immediately!",
      file_analysis: "📁 I can analyze your business documents for strategic insights!\n\n🔍 Supported documents:\n• Business plans and strategies\n• Financial reports and projections\n• Technical specifications\n• Market research reports\n• Competitive analysis\n• Implementation roadmaps\n\n📤 Upload your documents and I'll provide strategic analysis during our consultation!",
      voice_consultation: "🎤 Voice-powered strategic consulting is available!\n\n🗣️ You can:\n• Describe your business challenges verbally\n• Explain complex strategies by speaking\n• Get audio strategic recommendations\n• Participate in voice-only consultation sessions\n• Record strategy sessions for team sharing\n\n🎯 Try saying: 'I need help with AI strategy for my retail business'",
      default: "🎯 I'm your advanced AI consulting specialist with live session capabilities!\n\n✨ I provide strategic guidance for AI implementation with:\n• 🧠 Strategy development and planning\n• 🔍 Feasibility studies and analysis\n• 🚀 Implementation support and guidance\n• 👥 Expert consultations and workshops\n• 🎤 Voice consultation sessions\n• 📹 Live video strategy sessions\n• 📁 Document analysis and review\n• 🔄 Ongoing strategic support\n\n🎥 I can also connect you with our human consultants via live video call. How can I help you succeed with AI?"
    },
    ar: {
      strategy: "🧠 سأكون سعيداً لمساعدتك في تطوير استراتيجية الذكاء الاصطناعي مع دعم الاستشارة المباشرة!\n\n💼 استشاراتنا الاستراتيجية تشمل:\n• 📊 تقييم الجاهزية للذكاء الاصطناعي (2000-3000 ريال)\n• 🗺️ تطوير خارطة طريق استراتيجية (3000-5000 ريال)\n• 💰 تحليل العائد على الاستثمار (2500-4000 ريال)\n• 📋 تخطيط التنفيذ (2000-4000 ريال)\n• 🎤 جلسات استشارة صوتية\n• 📹 جلسات استراتيجية مباشرة بالفيديو\n\n🎯 هل تود جدولة استشارة مباشرة لمناقشة احتياجاتك المحددة؟",
      feasibility: "🔍 دراسات الجدوى ضرورية لنجاح الذكاء الاصطناعي مع تحليل شامل!\n\n📈 دراساتنا تشمل:\n• 🔧 تحليل الجدوى التقنية (3000-5000 ريال)\n• 📊 تقييم الأثر التجاري (2500-4000 ريال)\n• 💹 تحليل التكلفة والفائدة (2000-3500 ريال)\n• ⚠️ تقييم المخاطر (2000-3000 ريال)\n• 🎤 جلسات تحليل موجهة بالصوت\n• 📁 تحليل ومراجعة المستندات\n\n⏱️ هذا عادة يستغرق 1-2 أسبوع. هل نجدول استشارة مباشرة للبدء؟",
      implementation: "🚀 دعم التنفيذ يضمن نجاح مشروع الذكاء الاصطناعي مع إرشاد عملي!\n\n🛠️ خدماتنا تشمل:\n• 📋 إدارة المشاريع (1500-2500 ريال/شهر)\n• 🎯 التوجيه التقني (2000-3000 ريال/شهر)\n• 👥 تدريب الفريق (1000-2000 ريال/جلسة)\n• ✅ ضمان الجودة (1500-2500 ريال/شهر)\n• 🎤 جلسات تدريب صوتية\n• 📹 مراجعات تنفيذ مباشرة\n• 📁 مراجعة المستندات والكود\n\n🎯 هل تود مناقشة احتياجات التنفيذ في جلسة مباشرة؟",
      schedule: "📅 سأكون سعيداً لجدولة استشارة مع خبراء الذكاء الاصطناعي مع خيارات متعددة!\n\n🎯 أنواع الاستشارات:\n• ⚡ استشارة سريعة 30 دقيقة (500-800 ريال)\n• 🧠 جلسة استراتيجية ساعة واحدة (1000-1500 ريال)\n• 🔍 جلسة تفصيلية ساعتان (2000-3000 ريال)\n• 🏢 ورشة عمل يوم كامل (5000-8000 ريال)\n• 🎤 استشارة صوتية فقط (خصم 20%)\n• 📹 استشارة فيديو (تجربة مميزة)\n• 📁 جلسة مراجعة مستندات (إضافية 500 ريال)\n\n🎯 ما نوع الاستشارة الأنسب لك؟",
      live_session: "🎥 إمكانيات الجلسة المباشرة متاحة الآن!\n\n✨ الميزات تشمل:\n• 📹 استشارة فيديو عالية الدقة\n• 🎤 صوت واضح كالكريستال\n• 📱 مشاركة الشاشة للعروض التقديمية\n• 📝 تدوين الملاحظات في الوقت الفعلي\n• 📁 مشاركة ومراجعة المستندات\n• 🔄 تسجيل الجلسة للمراجعة اللاحقة\n\n🚀 مستعد لبدء جلسة مباشرة؟ يمكنني ربطك فوراً!",
      file_analysis: "📁 يمكنني تحليل مستندات عملك للحصول على رؤى استراتيجية!\n\n🔍 المستندات المدعومة:\n• خطط العمل والاستراتيجيات\n• التقارير المالية والتوقعات\n• المواصفات التقنية\n• تقارير أبحاث السوق\n• التحليل التنافسي\n• خرائط طريق التنفيذ\n\n📤 ارفع مستنداتك وسأقدم تحليلاً استراتيجياً أثناء استشارتنا!",
      voice_consultation: "🎤 الاستشارة الاستراتيجية المدعومة بالصوت متاحة!\n\n🗣️ يمكنك:\n• وصف تحديات عملك شفهياً\n• شرح الاستراتيجيات المعقدة بالكلام\n• الحصول على توصيات استراتيجية صوتية\n• المشاركة في جلسات استشارة صوتية فقط\n• تسجيل جلسات الاستراتيجية لمشاركة الفريق\n\n🎯 جرب قول: 'أحتاج مساعدة في استراتيجية الذكاء الاصطناعي لعملي التجاري'",
      default: "🎯 أنا متخصص استشارات الذكاء الاصطناعي المتقدم مع إمكانيات الجلسات المباشرة!\n\n✨ أقدم التوجيه الاستراتيجي لتطبيق الذكاء الاصطناعي مع:\n• 🧠 تطوير وتخطيط الاستراتيجية\n• 🔍 دراسات الجدوى والتحليل\n• 🚀 دعم وإرشاد التنفيذ\n• 👥 استشارات خبيرة وورش عمل\n• 🎤 جلسات استشارة صوتية\n• 📹 جلسات استراتيجية مباشرة بالفيديو\n• 📁 تحليل ومراجعة المستندات\n• 🔄 الدعم الاستراتيجي المستمر\n\n🎥 يمكنني أيضاً ربطك بمستشارينا البشريين عبر مكالمة فيديو مباشرة. كيف يمكنني مساعدتك للنجاح مع الذكاء الاصطناعي؟"
    }
  }

  const messageType = message.toLowerCase().includes('strategy') || message.includes('استراتيجية') ? 'strategy' :
                     message.toLowerCase().includes('feasibility') || message.includes('جدوى') ? 'feasibility' :
                     message.toLowerCase().includes('implementation') || message.includes('تنفيذ') ? 'implementation' :
                     message.toLowerCase().includes('schedule') || message.includes('جدولة') || message.includes('موعد') ? 'schedule' :
                     message.toLowerCase().includes('live') || message.includes('مباشر') ? 'live_session' :
                     message.toLowerCase().includes('file') || message.includes('ملف') ? 'file_analysis' :
                     message.toLowerCase().includes('voice') || message.includes('صوت') ? 'voice_consultation' : 'default'

  return {
    message: responses[language as keyof typeof responses][messageType as keyof typeof responses.en],
    confidence: 0.95,
    next_action: 'offer_consultation',
    agent_type: 'consulting',
    capabilities: ['voice_interaction', 'live_sessions', 'strategic_consulting', 'file_analysis', 'video_consultation', 'document_review'],
    live_session_required: messageType === 'live_session' || messageType === 'schedule'
  }
} any): Promise<ChatResponse> {
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