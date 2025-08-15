'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useEnhancedTranslation } from '@/lib/i18n-enhanced'
import { 
  MessageCircle, 
  X, 
  Send, 
  Bot, 
  User,
  Minimize2,
  Maximize2,
  Phone,
  Calendar,
  Mic,
  MicOff,
  Upload,
  Volume2,
  VolumeX,
  Video,
  Shield,
  FileText,
  Code,
  Briefcase,
  UserPlus
} from 'lucide-react'

interface Message {
  id: string
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
  type?: 'text' | 'action' | 'handoff' | 'file' | 'voice' | 'code' | 'guardrail'
  agentType?: 'initial_customer' | 'n8n_workflow' | 'code_generation' | 'consulting'
  fileUrl?: string
  fileName?: string
  voiceUrl?: string
  codeLanguage?: string
}

interface UserProfile {
  id: string
  name?: string
  email?: string
  phone?: string
  preferredService?: 'quick' | 'coded' | 'consulting'
  serviceHistory: string[]
  conversationHistory: Message[]
  language: 'ar' | 'en'
  registrationDate: Date
}

interface ChatbotWidgetProps {
  position?: 'bottom-right' | 'bottom-left' | 'embedded'
  theme?: 'light' | 'dark'
  initialMessage?: string
  userId?: string
  userProfile?: UserProfile
  agentType?: 'initial_customer' | 'n8n_workflow' | 'code_generation' | 'consulting'
}

export default function ChatbotWidget({ 
  position = 'bottom-right',
  theme = 'light',
  initialMessage,
  userId,
  userProfile,
  agentType = 'initial_customer'
}: ChatbotWidgetProps) {
  const { t, locale, isRTL } = useEnhancedTranslation()
  const [isOpen, setIsOpen] = useState(false)
  
  // Enhanced state management
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isConnected, setIsConnected] = useState(true)
  const [currentAgentType, setCurrentAgentType] = useState<string>(agentType)
  
  // Voice capabilities
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [audioChunks, setAudioChunks] = useState<Blob[]>([])
  
  // File upload capabilities
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Live session capabilities
  const [isLiveSession, setIsLiveSession] = useState(false)
  const [liveSessionId, setLiveSessionId] = useState<string | null>(null)
  
  // User profile and memory
  const [currentUserProfile, setCurrentUserProfile] = useState<UserProfile | null>(userProfile || null)
  const [guardrailsActive, setGuardrailsActive] = useState(agentType === 'initial_customer')
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const speechSynthesis = useRef<SpeechSynthesis | null>(null)
  
  // Debug logging
  const handleToggleOpen = () => {
    console.log('Chatbot toggle clicked, current state:', isOpen)
    setIsOpen(!isOpen)
    
    // Add initial message if opening for first time
    if (!isOpen && messages.length === 0) {
      loadUserContext()
    }
  }

  // Initialize speech synthesis
  useEffect(() => {
    if (typeof window !== 'undefined') {
      speechSynthesis.current = window.speechSynthesis
    }
  }, [])

  useEffect(() => {
    // Initialize with welcome message using translation
    if (messages.length === 0) {
      loadUserContext()
    }
  }, [initialMessage, t])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Load user context and conversation history
  const loadUserContext = async () => {
    try {
      let welcomeMessage = initialMessage || t('chatbot.initialMessage')
      
      // If user has profile, personalize welcome message
      if (currentUserProfile) {
        const userName = currentUserProfile.name || 'valued customer'
        const serviceHistory = currentUserProfile.serviceHistory.length > 0 
          ? `I see you've used our ${currentUserProfile.serviceHistory.join(', ')} services before.`
          : ''
        
        welcomeMessage = locale === 'ar' 
          ? `مرحباً ${userName}! ${serviceHistory} كيف يمكنني مساعدتك اليوم؟`
          : `Hello ${userName}! ${serviceHistory} How can I help you today?`
        
        // Load previous conversation if exists
        if (currentUserProfile.conversationHistory.length > 0) {
          setMessages(currentUserProfile.conversationHistory)
          return
        }
      }

      // Set agent-specific welcome message
      const agentWelcomes = {
        initial_customer: locale === 'ar' 
          ? 'مرحباً! أنا مساعدك لتسجيل العملاء الجدد. سأساعدك في جمع معلوماتك وربطك بالخدمة المناسبة.'
          : 'Hello! I\'m your new customer onboarding assistant. I\'ll help collect your information and connect you with the right service.',
        n8n_workflow: locale === 'ar'
          ? 'مرحباً! أنا متخصص أتمتة سير العمل. يمكنني مساعدتك في إنشاء وإدارة سير العمل باستخدام n8n.'
          : 'Hello! I\'m your workflow automation specialist. I can help you create and manage n8n workflows.',
        code_generation: locale === 'ar'
          ? 'مرحباً! أنا متخصص تطوير الوكلاء الأذكياء. سأساعدك في بناء حلول ذكاء اصطناعي مخصصة.'
          : 'Hello! I\'m your AI agent development specialist. I\'ll help you build custom AI solutions.',
        consulting: locale === 'ar'
          ? 'مرحباً! أنا مستشار الذكاء الاصطناعي. يمكنني تقديم الاستشارات الاستراتيجية وجدولة جلسات مباشرة.'
          : 'Hello! I\'m your AI consulting specialist. I can provide strategic guidance and schedule live sessions.'
      }

      const initialMsg: Message = {
        id: '1',
        content: agentWelcomes[agentType] || welcomeMessage,
        sender: 'bot',
        timestamp: new Date(),
        agentType: agentType
      }

      setMessages([initialMsg])
      
      // Speak welcome message if voice is enabled
      if (voiceEnabled && !isSpeaking) {
        speakMessage(initialMsg.content)
      }
      
    } catch (error) {
      console.error('Error loading user context:', error)
    }
  }

  // Voice interaction functions
  const speakMessage = (text: string) => {
    if (!voiceEnabled || !speechSynthesis.current || isSpeaking) return

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = locale === 'ar' ? 'ar-SA' : 'en-US'
    utterance.rate = 0.9
    utterance.pitch = 1.0
    
    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    speechSynthesis.current.speak(utterance)
  }

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          setAudioChunks(prev => [...prev, event.data])
        }
      }

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
        await processVoiceInput(audioBlob)
        setAudioChunks([])
        stream.getTracks().forEach(track => track.stop())
      }

      setMediaRecorder(recorder)
      recorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting voice recording:', error)
    }
  }

  const stopVoiceRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop()
      setIsRecording(false)
    }
  }

  const processVoiceInput = async (audioBlob: Blob) => {
    try {
      // Convert speech to text using Web Speech API or send to backend
      const formData = new FormData()
      formData.append('audio', audioBlob)
      formData.append('language', locale)

      const response = await fetch('/api/speech-to-text', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const { text } = await response.json()
        if (text) {
          sendMessage(text)
        }
      }
    } catch (error) {
      console.error('Error processing voice input:', error)
    }
  }

  // File upload functions
  const handleFileUpload = async (file: File) => {
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('agent_type', currentAgentType)
    formData.append('user_id', userId || 'anonymous')

    try {
      const response = await fetch('/api/file-upload', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const { fileUrl, fileName } = await response.json()
        
        const fileMessage: Message = {
          id: Date.now().toString(),
          content: `Uploaded file: ${fileName}`,
          sender: 'user',
          timestamp: new Date(),
          type: 'file',
          fileUrl,
          fileName
        }

        setMessages(prev => [...prev, fileMessage])
        
        // Process file with appropriate agent
        await processFileWithAgent(fileUrl, fileName, file.type)
      }
    } catch (error) {
      console.error('Error uploading file:', error)
    }
  }

  const processFileWithAgent = async (fileUrl: string, fileName: string, fileType: string) => {
    const context = {
      file_url: fileUrl,
      file_name: fileName,
      file_type: fileType,
      agent_type: currentAgentType,
      user_profile: currentUserProfile
    }

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `Process uploaded file: ${fileName}`,
          customer_id: userId,
          context
        })
      })

      const data = await response.json()
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response?.message || `I've processed your file ${fileName}. How can I help you with it?`,
        sender: 'bot',
        timestamp: new Date(),
        agentType: data.response?.agent_type
      }

      setMessages(prev => [...prev, botMessage])
      
      if (voiceEnabled) {
        speakMessage(botMessage.content)
      }
    } catch (error) {
      console.error('Error processing file with agent:', error)
    }
  }

  // Guardrails for new customer agent
  const applyGuardrails = (message: string): { allowed: boolean; reason?: string } => {
    if (!guardrailsActive) return { allowed: true }

    // Rate limiting check
    const recentMessages = messages.filter(m => 
      m.sender === 'user' && 
      Date.now() - m.timestamp.getTime() < 60000 // Last minute
    )
    
    if (recentMessages.length > 10) {
      return { allowed: false, reason: 'Rate limit exceeded. Please wait a moment.' }
    }

    // Content filtering
    const suspiciousPatterns = [
      /hack|exploit|vulnerability|injection|script/i,
      /(.)\1{10,}/, // Repeated characters
      /^\s*$/, // Empty message
    ]

    for (const pattern of suspiciousPatterns) {
      if (pattern.test(message)) {
        return { allowed: false, reason: 'Message contains inappropriate content.' }
      }
    }

    // Length check
    if (message.length > 1000) {
      return { allowed: false, reason: 'Message too long. Please keep it under 1000 characters.' }
    }

    return { allowed: true }
  }

  // Enhanced sendMessage with guardrails and agent capabilities
  const sendMessage = async (content: string, messageType: 'text' | 'voice' | 'file' = 'text') => {
    if (!content.trim()) return

    // Apply guardrails for new customer agent
    const guardrailCheck = applyGuardrails(content)
    if (!guardrailCheck.allowed) {
      const warningMessage: Message = {
        id: Date.now().toString(),
        content: guardrailCheck.reason || 'Message blocked by security filters.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'guardrail'
      }
      setMessages(prev => [...prev, warningMessage])
      return
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
      type: messageType
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    // Update user profile with conversation
    if (currentUserProfile) {
      const updatedProfile = {
        ...currentUserProfile,
        conversationHistory: [...messages, userMessage]
      }
      setCurrentUserProfile(updatedProfile)
      // Save to localStorage or backend
      localStorage.setItem(`user_profile_${userId}`, JSON.stringify(updatedProfile))
    }

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          customer_id: userId || 'anonymous',
          context: {
            session_id: `chat-${userId}-${Date.now()}`,
            language: locale,
            timestamp: new Date().toISOString(),
            use_real_llm: true,
            agent_type: currentAgentType,
            user_profile: currentUserProfile,
            message_type: messageType,
            guardrails_active: guardrailsActive
          }
        }),
      })

      const data = await response.json()
      
      setTimeout(() => {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response?.message || data.response || t('chatbot.defaultResponse') || "I understand you're interested in our AI services. Let me help you with that!",
          sender: 'bot',
          timestamp: new Date(),
          type: data.response?.type || 'text',
          agentType: data.response?.agent_type || currentAgentType
        }

        setMessages(prev => [...prev, botMessage])
        setIsTyping(false)

        // Speak response if voice is enabled
        if (voiceEnabled && !isSpeaking) {
          speakMessage(botMessage.content)
        }

        // Handle agent-specific responses
        handleAgentSpecificResponse(data.response, botMessage)

        // Update user profile
        if (currentUserProfile) {
          const updatedProfile = {
            ...currentUserProfile,
            conversationHistory: [...messages, userMessage, botMessage]
          }
          setCurrentUserProfile(updatedProfile)
          localStorage.setItem(`user_profile_${userId}`, JSON.stringify(updatedProfile))
        }

      }, 1500)

    } catch (error) {
      setIsTyping(false)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: t('chatbot.errorMessage') || 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  // Handle agent-specific responses and capabilities
  const handleAgentSpecificResponse = (response: any, botMessage: Message) => {
    if (!response) return

    // Handle handoff requests
    if (response.handoff_required || response.next_action === 'human_handoff') {
      setTimeout(() => {
        const handoffMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: t('chatbot.handoffMessage') || 'Let me connect you with a human specialist.',
          sender: 'bot',
          timestamp: new Date(),
          type: 'handoff'
        }
        setMessages(prev => [...prev, handoffMessage])
      }, 1000)
    }

    // Handle live session requests (for consulting agent)
    if (response.live_session_required && currentAgentType === 'consulting') {
      initiateLiveSession()
    }

    // Handle code generation requests
    if (response.code_generated && currentAgentType === 'code_generation') {
      const codeMessage: Message = {
        id: (Date.now() + 3).toString(),
        content: response.code_content || 'Here\'s your generated code:',
        sender: 'bot',
        timestamp: new Date(),
        type: 'code',
        codeLanguage: response.code_language || 'python'
      }
      setTimeout(() => {
        setMessages(prev => [...prev, codeMessage])
      }, 2000)
    }

    // Handle workflow creation (for n8n agent)
    if (response.workflow_created && currentAgentType === 'n8n_workflow') {
      const workflowMessage: Message = {
        id: (Date.now() + 4).toString(),
        content: `Workflow "${response.workflow_name}" has been created successfully!`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'action'
      }
      setTimeout(() => {
        setMessages(prev => [...prev, workflowMessage])
      }, 2000)
    }
  }

  // Live session functions
  const initiateLiveSession = async () => {
    try {
      const response = await fetch('/api/live-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          agent_type: currentAgentType,
          session_type: 'video_consultation'
        })
      })

      if (response.ok) {
        const { session_id, join_url } = await response.json()
        setLiveSessionId(session_id)
        setIsLiveSession(true)
        
        const sessionMessage: Message = {
          id: Date.now().toString(),
          content: `Live session initiated! Session ID: ${session_id}`,
          sender: 'bot',
          timestamp: new Date(),
          type: 'action'
        }
        setMessages(prev => [...prev, sessionMessage])
      }
    } catch (error) {
      console.error('Error initiating live session:', error)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(inputValue)
    }
  }

  const requestHandoff = () => {
    const handoffMessage: Message = {
      id: Date.now().toString(),
      content: t('chatbot.talkToHuman'),
      sender: 'user',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, handoffMessage])

    setTimeout(() => {
      const responseMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: t('chatbot.connectingMessage'),
        sender: 'bot',
        timestamp: new Date(),
        type: 'handoff'
      }
      setMessages(prev => [...prev, responseMessage])
      
      // Handle live agent handoff - would initiate LiveKit session
      console.log('Handoff requested - initiating live session with Root Agent')
    }, 1000)
  }

  const scheduleCall = () => {
    const scheduleMessage: Message = {
      id: Date.now().toString(),
      content: t('chatbot.scheduleCall'),
      sender: 'user',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, scheduleMessage])

    setTimeout(() => {
      const responseMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: t('chatbot.scheduleMessage'),
        sender: 'bot',
        timestamp: new Date(),
        type: 'action'
      }
      setMessages(prev => [...prev, responseMessage])
    }, 1000)
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (position === 'embedded') {
    return (
      <Card className="w-full h-[600px] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="flex items-center space-x-2">
            <Bot className="h-5 w-5 text-blue-600" />
            <span>{t('chatbot.title')}</span>
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Badge variant={isConnected ? "default" : "destructive"} className="text-xs">
              {isConnected ? t('chatbot.online') : t('chatbot.offline')}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col p-0">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 shadow-sm ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-800 border border-gray-200'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.sender === 'bot' && (
                      <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                  </div>
                  
                  {message.type === 'handoff' && (
                    <div className="mt-3 space-y-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="w-full"
                        onClick={requestHandoff}
                      >
                        <Phone className="h-4 w-4 mr-2" />
                        {t('chatbot.connectNow')}
                      </Button>
                    </div>
                  )}
                  
                  {message.type === 'action' && message.content.includes('schedule') && (
                    <div className="mt-3">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="w-full"
                        onClick={scheduleCall}
                      >
                        <Calendar className="h-4 w-4 mr-2" />
                        Schedule Now
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg p-3 max-w-[80%] shadow-sm">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-4 w-4 text-blue-600" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <div className="border-t p-4">
            <div className="flex space-x-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={t('chatbot.placeholder')}
                className="flex-1"
              />
              <Button 
                onClick={() => sendMessage(inputValue)}
                disabled={!inputValue.trim() || isTyping}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex justify-center space-x-2 mt-2">
              <Button variant="outline" size="sm" onClick={requestHandoff}>
                <Phone className="h-4 w-4 mr-2" />
                {t('chatbot.talkToHuman')}
              </Button>
              <Button variant="outline" size="sm" onClick={scheduleCall}>
                <Calendar className="h-4 w-4 mr-2" />
                {t('chatbot.scheduleCall')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      {/* Chat Widget Button */}
      {!isOpen && (
        <div className={`fixed ${position === 'bottom-right' ? 'bottom-6 right-6' : 'bottom-6 left-6'} z-50`}>
          <Button
            onClick={handleToggleOpen}
            className="rounded-full w-16 h-16 shadow-lg hover:shadow-xl transition-shadow text-lg"
            size="lg"
          >
            <MessageCircle className="h-8 w-8" />
          </Button>
        </div>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className={`fixed ${position === 'bottom-right' ? 'bottom-6 right-6' : 'bottom-6 left-6'} z-50`}>
          <Card className={`w-96 ${isMinimized ? 'h-14' : 'h-[500px]'} shadow-xl transition-all duration-300`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="flex items-center space-x-2 text-sm">
                <Bot className="h-4 w-4 text-blue-600" />
                <span>{t('chatbot.title')}</span>
                <Badge variant={isConnected ? "default" : "destructive"} className="text-xs">
                  {isConnected ? t('chatbot.online') : t('chatbot.offline')}
                </Badge>
              </CardTitle>
              <div className="flex items-center space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="h-6 w-6 p-0"
                >
                  {isMinimized ? <Maximize2 className="h-3 w-3" /> : <Minimize2 className="h-3 w-3" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </CardHeader>
            
            {!isMinimized && (
              <CardContent className="flex flex-col h-[440px] p-0">
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-lg p-3 shadow-sm ${
                          message.sender === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-800 border border-gray-200'
                        }`}
                      >
                        <div className="flex items-start space-x-1">
                          {message.sender === 'bot' && (
                            <Bot className="h-3 w-3 mt-0.5 flex-shrink-0" />
                          )}
                          <div className="flex-1">
                            <p className="text-sm">{message.content}</p>
                            <p className={`text-xs mt-1 ${
                              message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                            }`}>
                              {formatTime(message.timestamp)}
                            </p>
                          </div>
                        </div>
                        
                        {message.type === 'handoff' && (
                          <div className="mt-2">
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="w-full text-xs h-6"
                              onClick={requestHandoff}
                            >
                              <Phone className="h-3 w-3 mr-1" />
                              {t('chatbot.connectNow')}
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-white border border-gray-200 rounded-lg p-2 max-w-[85%] shadow-sm">
                        <div className="flex items-center space-x-1">
                          <Bot className="h-3 w-3 text-blue-600" />
                          <div className="flex space-x-1">
                            <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce"></div>
                            <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
                
                <div className="border-t p-2">
                  <div className="flex space-x-1">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder={t('chatbot.placeholder')}
                      className="flex-1 text-sm h-8"
                    />
                    <Button 
                      onClick={() => sendMessage(inputValue)}
                      disabled={!inputValue.trim() || isTyping}
                      size="sm"
                      className="h-8 w-8 p-0"
                    >
                      <Send className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>
        </div>
      )}
    </>
  )
}