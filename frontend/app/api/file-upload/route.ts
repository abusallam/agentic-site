import { NextRequest, NextResponse } from 'next/server'
import { writeFile, mkdir } from 'fs/promises'
import { join } from 'path'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const agentType = formData.get('agent_type') as string
    const userId = formData.get('user_id') as string

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    // Validate file type and size
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: 'File too large. Maximum size is 10MB.' },
        { status: 400 }
      )
    }

    const allowedTypes = [
      'text/plain',
      'application/pdf',
      'image/jpeg',
      'image/png',
      'image/gif',
      'application/json',
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'File type not supported' },
        { status: 400 }
      )
    }

    // Create upload directory
    const uploadDir = join(process.cwd(), 'public', 'uploads', agentType)
    try {
      await mkdir(uploadDir, { recursive: true })
    } catch (error) {
      // Directory might already exist
    }

    // Generate unique filename
    const timestamp = Date.now()
    const fileName = `${userId}_${timestamp}_${file.name}`
    const filePath = join(uploadDir, fileName)

    // Save file
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    await writeFile(filePath, buffer)

    const fileUrl = `/uploads/${agentType}/${fileName}`

    // Process file based on agent type
    let processingResult = null
    switch (agentType) {
      case 'code_generation':
        processingResult = await processCodeFile(file, buffer)
        break
      case 'n8n_workflow':
        processingResult = await processWorkflowFile(file, buffer)
        break
      case 'consulting':
        processingResult = await processConsultingFile(file, buffer)
        break
      default:
        processingResult = await processGeneralFile(file, buffer)
    }

    return NextResponse.json({
      success: true,
      fileUrl,
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      processing: processingResult
    })

  } catch (error) {
    console.error('File upload error:', error)
    return NextResponse.json(
      { error: 'Failed to upload file' },
      { status: 500 }
    )
  }
}

async function processCodeFile(file: File, buffer: Buffer) {
  // Process code files for code generation agent
  const content = buffer.toString('utf-8')
  
  return {
    type: 'code_analysis',
    language: detectCodeLanguage(file.name),
    lines: content.split('\n').length,
    size: buffer.length,
    preview: content.substring(0, 200) + '...'
  }
}

async function processWorkflowFile(file: File, buffer: Buffer) {
  // Process workflow files for n8n agent
  if (file.type === 'application/json') {
    try {
      const content = JSON.parse(buffer.toString('utf-8'))
      return {
        type: 'workflow_definition',
        nodes: content.nodes?.length || 0,
        connections: Object.keys(content.connections || {}).length,
        valid: true
      }
    } catch {
      return {
        type: 'invalid_json',
        valid: false
      }
    }
  }
  
  return {
    type: 'general_file',
    size: buffer.length
  }
}

async function processConsultingFile(file: File, buffer: Buffer) {
  // Process consulting files
  return {
    type: 'consulting_document',
    size: buffer.length,
    pages: file.type === 'application/pdf' ? 'estimated' : 1,
    ready_for_analysis: true
  }
}

async function processGeneralFile(file: File, buffer: Buffer) {
  return {
    type: 'general_file',
    size: buffer.length,
    processed: true
  }
}

function detectCodeLanguage(filename: string): string {
  const extension = filename.split('.').pop()?.toLowerCase()
  
  const languageMap: { [key: string]: string } = {
    'js': 'javascript',
    'ts': 'typescript',
    'py': 'python',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'c',
    'cs': 'csharp',
    'php': 'php',
    'rb': 'ruby',
    'go': 'go',
    'rs': 'rust',
    'swift': 'swift',
    'kt': 'kotlin',
    'scala': 'scala',
    'html': 'html',
    'css': 'css',
    'sql': 'sql',
    'json': 'json',
    'xml': 'xml',
    'yaml': 'yaml',
    'yml': 'yaml'
  }
  
  return languageMap[extension || ''] || 'text'
}