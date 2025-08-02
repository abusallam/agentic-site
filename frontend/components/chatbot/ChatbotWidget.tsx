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
  Calendar
} from 'lucide-react'

interface Message {
  id: string
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
  type?: 'text' | 'action' | 'handoff'
}

interface ChatbotWidgetProps {
  position?: 'bottom-right' | 'bottom-left' | 'embedded'
  theme?: 'light' | 'dark'
  initialMessage?: string
}

export default function ChatbotWidget({ 
  position = 'bottom-right',
  theme = 'light',
  initialMessage
}: ChatbotWidgetProps) {
  const { t, locale, isRTL } = useEnhancedTranslation()
  const [isOpen, setIsOpen] = useState(false)
  
  // Debug logging
  const handleToggleOpen = () => {
    console.log('Chatbot toggle clicked, current state:', isOpen)
    setIsOpen(!isOpen)
    
    // Add initial message if opening for first time
    if (!isOpen && messages.length === 0) {
      const welcomeMessage: Message = {
        id: Date.now().toString(),
        content: initialMessage || 'Hello! How can I help you today?',
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages([welcomeMessage])
    }
  }
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isConnected, setIsConnected] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initialize with welcome message using translation
    const welcomeMessage = initialMessage || t('chatbot.initialMessage')
    setMessages([{
      id: '1',
      content: welcomeMessage,
      sender: 'bot',
      timestamp: new Date()
    }])
  }, [initialMessage, t])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessage = async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      // Simulate API call to agent
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          conversation_id: 'chat-' + Date.now()
        }),
      })

      const data = await response.json()
      
      setTimeout(() => {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response || t('chatbot.defaultResponse') || "I understand you're interested in our AI services. Let me help you with that!",
          sender: 'bot',
          timestamp: new Date(),
          type: data.type || 'text'
        }

        setMessages(prev => [...prev, botMessage])
        setIsTyping(false)

        // Check if handoff is needed
        if (data.handoff_required) {
          setTimeout(() => {
            const handoffMessage: Message = {
              id: (Date.now() + 2).toString(),
              content: t('chatbot.handoffMessage'),
              sender: 'bot',
              timestamp: new Date(),
              type: 'handoff'
            }
            setMessages(prev => [...prev, handoffMessage])
          }, 1000)
        }
      }, 1500)

    } catch (error) {
      setIsTyping(false)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: t('chatbot.errorMessage'),
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
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
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
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
                <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-4 w-4" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
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
            className="rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-shadow"
            size="lg"
          >
            <MessageCircle className="h-6 w-6" />
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
                        className={`max-w-[85%] rounded-lg p-3 ${
                          message.sender === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
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
                      <div className="bg-gray-100 rounded-lg p-2 max-w-[85%]">
                        <div className="flex items-center space-x-1">
                          <Bot className="h-3 w-3" />
                          <div className="flex space-x-1">
                            <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
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