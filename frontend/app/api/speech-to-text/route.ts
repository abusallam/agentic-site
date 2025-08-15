import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const audioFile = formData.get('audio') as File
    const language = formData.get('language') as string || 'en'

    if (!audioFile) {
      return NextResponse.json(
        { error: 'No audio file provided' },
        { status: 400 }
      )
    }

    // For now, we'll use a mock response
    // In production, you would integrate with Google Speech-to-Text API or similar
    const mockTranscriptions = {
      en: [
        "Hello, I need help with AI services",
        "Can you help me with workflow automation?",
        "I want to build a custom AI agent",
        "I need strategic consulting for my business"
      ],
      ar: [
        "مرحباً، أحتاج مساعدة في خدمات الذكاء الاصطناعي",
        "هل يمكنك مساعدتي في أتمتة سير العمل؟",
        "أريد بناء وكيل ذكي مخصص",
        "أحتاج استشارة استراتيجية لعملي"
      ]
    }

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    const transcriptions = mockTranscriptions[language as keyof typeof mockTranscriptions] || mockTranscriptions.en
    const randomText = transcriptions[Math.floor(Math.random() * transcriptions.length)]

    return NextResponse.json({
      success: true,
      text: randomText,
      language: language,
      confidence: 0.95
    })

  } catch (error) {
    console.error('Speech-to-text error:', error)
    return NextResponse.json(
      { error: 'Failed to process audio' },
      { status: 500 }
    )
  }
}