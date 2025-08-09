'use client'

import dynamic from 'next/dynamic'

// Client-side dynamic import for the chatbot
const ChatbotWidget = dynamic(() => import('./ChatbotWidget'), {
  ssr: false,
  loading: () => null
})

interface ChatbotWrapperProps {
  position?: 'bottom-right' | 'bottom-left'
}

export default function ChatbotWrapper({ position = 'bottom-right' }: ChatbotWrapperProps) {
  return <ChatbotWidget position={position} />
}