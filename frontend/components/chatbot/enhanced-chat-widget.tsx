"use client"

import * as React from "react"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { 
  MessageCircle, 
  Send, 
  X, 
  Minimize2, 
  Maximize2, 
  Bot, 
  User,
  Loader2,
  Sparkles,
  ArrowRight
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"

interface ChatMessage {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: Date
  confidence?: number
  next_action?: string
  agent_type?: string
}

interface EnhancedChatWidgetProps {
  className?: string
  position?: "bottom-right" | "bottom-left" | "bottom-center"
  theme?: "light" | "dark" | "auto"
}

export function EnhancedChatWidget({ 
  className, 
  position = "bottom-right",
  theme = "auto" 
}: EnhancedChatWidgetProps) {
  const { t } = useEnhancedTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "system",
      content: t("chat.welcome", "Welcome! I'm your AI assistant. How can I help you today?"),
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [currentAgent, setCurrentAgent] = useState<string>("welcoming")
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus()
    }
  }, [isOpen, isMinimized])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: "user",
      content: inputValue.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      // Send to our enhanced agentic backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          customer_id: sessionId,
          context: {
            session_id: sessionId,
            current_agent: currentAgent,
            timestamp: new Date().toISOString()
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      
      // Handle direct response from our chat API
      if (data.success && data.response) {
        const assistantMessage: ChatMessage = {
          id: `assistant_${Date.now()}`,
          role: "assistant",
          content: data.response.message || "I'm here to help! How can I assist you?",
          timestamp: new Date(),
          confidence: data.response.confidence,
          next_action: data.response.next_action,
          agent_type: data.response.agent_type
        }

        setMessages(prev => [...prev, assistantMessage])
        
        // Update current agent if routing occurred
        if (data.response.transfer_to) {
          setCurrentAgent(data.response.transfer_to)
        } else if (data.response.agent_type) {
          setCurrentAgent(data.response.agent_type)
        }
      } else {
        throw new Error(data.error || 'Failed to get response')
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        role: "assistant",
        content: "I apologize, but I'm experiencing some technical difficulties. Please try again in a moment.",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const pollTaskResult = async (taskId: string, maxAttempts = 10): Promise<any> => {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await fetch(`/api/v1/tasks/${taskId}/status`)
        const data = await response.json()
        
        if (data.status === 'success') {
          return data
        } else if (data.status === 'failure') {
          throw new Error(data.error || 'Task failed')
        }
        
        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, 1000))
      } catch (error) {
        console.error('Polling error:', error)
        break
      }
    }
    return null
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getPositionClasses = () => {
    switch (position) {
      case "bottom-left":
        return "bottom-4 left-4"
      case "bottom-center":
        return "bottom-4 left-1/2 transform -translate-x-1/2"
      case "bottom-right":
      default:
        return "bottom-4 right-4"
    }
  }

  const getAgentBadgeColor = (agentType?: string) => {
    switch (agentType) {
      case "welcoming":
        return "bg-blue-500/10 text-blue-600 border-blue-500/20"
      case "workflow":
        return "bg-green-500/10 text-green-600 border-green-500/20"
      case "professional":
        return "bg-purple-500/10 text-purple-600 border-purple-500/20"
      case "consulting":
        return "bg-orange-500/10 text-orange-600 border-orange-500/20"
      default:
        return "bg-primary/10 text-primary border-primary/20"
    }
  }

  if (!isOpen) {
    return (
      <div className={cn("fixed z-50", getPositionClasses(), className)}>
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className={cn(
            "group relative overflow-hidden rounded-full w-16 h-16 shadow-2xl",
            "bg-gradient-to-r from-primary via-primary/90 to-secondary",
            "hover:from-primary/90 hover:via-primary hover:to-secondary/90",
            "hover:scale-110 transition-all duration-300",
            "animate-pulse-glow"
          )}
        >
          <MessageCircle className="h-6 w-6 transition-transform group-hover:scale-110" />
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-secondary/20 rounded-full animate-ping" />
        </Button>
      </div>
    )
  }

  return (
    <div className={cn("fixed z-50", getPositionClasses(), className)}>
      <Card className={cn(
        "w-96 h-[600px] shadow-2xl border-0 bg-background/95 backdrop-blur-md",
        "animate-scale-in transition-all duration-300",
        isMinimized && "h-16"
      )}>
        {/* Header */}
        <CardHeader className="flex flex-row items-center justify-between p-4 border-b bg-gradient-to-r from-primary/5 to-secondary/5">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Bot className="h-6 w-6 text-primary" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            </div>
            <div>
              <h3 className="font-semibold text-sm">AI Assistant</h3>
              <p className="text-xs text-muted-foreground">
                {currentAgent === "welcoming" ? "Welcoming Agent" :
                 currentAgent === "workflow" ? "Workflow Agent" :
                 currentAgent === "professional" ? "Professional Agent" :
                 currentAgent === "consulting" ? "Consulting Agent" : "AI Agent"}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(!isMinimized)}
              className="h-8 w-8 p-0"
            >
              {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        {!isMinimized && (
          <CardContent className="p-0 flex flex-col h-[calc(600px-80px)]">
            {/* Messages */}
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex items-start space-x-3 animate-fade-in-up",
                      message.role === "user" && "flex-row-reverse space-x-reverse"
                    )}
                  >
                    <div className={cn(
                      "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
                      message.role === "user" 
                        ? "bg-primary text-primary-foreground" 
                        : "bg-secondary text-secondary-foreground"
                    )}>
                      {message.role === "user" ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                    </div>
                    
                    <div className={cn(
                      "flex-1 max-w-[80%]",
                      message.role === "user" && "flex flex-col items-end"
                    )}>
                      <div className={cn(
                        "rounded-2xl px-4 py-3 text-sm",
                        message.role === "user"
                          ? "bg-primary text-primary-foreground ml-auto"
                          : "bg-muted"
                      )}>
                        {message.content}
                      </div>
                      
                      <div className="flex items-center space-x-2 mt-2">
                        <span className="text-xs text-muted-foreground">
                          {message.timestamp.toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </span>
                        
                        {message.agent_type && (
                          <Badge 
                            variant="outline" 
                            className={cn("text-xs", getAgentBadgeColor(message.agent_type))}
                          >
                            {message.agent_type}
                          </Badge>
                        )}
                        
                        {message.confidence && (
                          <Badge variant="outline" className="text-xs">
                            {Math.round(message.confidence * 100)}%
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex items-start space-x-3 animate-fade-in-up">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="bg-muted rounded-2xl px-4 py-3 flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm text-muted-foreground">Thinking...</span>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </ScrollArea>

            {/* Input */}
            <div className="p-4 border-t bg-background/50">
              <div className="flex items-center space-x-2">
                <Input
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={t("chat.placeholder", "Type your message...")}
                  disabled={isLoading}
                  className="flex-1 border-0 bg-muted/50 focus:bg-muted"
                />
                <Button
                  onClick={sendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  size="sm"
                  className="px-3"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              
              <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                <span>Powered by AI Agents</span>
                <div className="flex items-center space-x-1">
                  <Sparkles className="h-3 w-3" />
                  <span>Enhanced</span>
                </div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  )
}