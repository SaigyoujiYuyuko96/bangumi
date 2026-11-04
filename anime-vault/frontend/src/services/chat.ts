import api from './api'

export interface ChatMessage {
  id: number
  session_id: string
  role: string
  content: string
  metadata: Record<string, any> | null
  tokens_used: number
  created_at: string
}

export interface ChatResponse {
  message: string
  session_id: string
  metadata: Record<string, any> | null
}

export interface ChatSession {
  session_id: string
  title: string
  last_message: string | null
  updated_at: string
}

export async function sendMessage(message: string, sessionId?: string) {
  const { data } = await api.post<ChatResponse>('/chat/send', { message, session_id: sessionId })
  return data
}

export async function getChatHistory(sessionId: string) {
  const { data } = await api.get(`/chat/history/${sessionId}`)
  return data
}

export async function getSessions() {
  const { data } = await api.get<{ sessions: ChatSession[] }>('/chat/sessions')
  return data
}

export async function deleteSession(sessionId: string) {
  const { data } = await api.delete(`/chat/sessions/${sessionId}`)
  return data
}

export async function sendMessageStream(
  message: string,
  sessionId: string | undefined,
  onChunk: (chunk: string) => void,
  onComplete: (fullMessage: string, sessionId: string) => void,
  onError: (error: string) => void
) {
  try {
    const response = await fetch(
      `${api.defaults.baseURL}/chat/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
        body: JSON.stringify({ message, session_id: sessionId }),
      }
    )

    if (!response.ok) {
      throw new Error('Network response was not ok')
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No reader available')
    }

    const decoder = new TextDecoder()
    let fullMessage = ''
    let currentSessionId = sessionId || ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            onComplete(fullMessage, currentSessionId)
            return
          }
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'content') {
              fullMessage += parsed.content
              onChunk(parsed.content)
            } else if (parsed.type === 'session_id') {
              currentSessionId = parsed.session_id
            }
          } catch (e) {
            fullMessage += data
            onChunk(data)
          }
        }
      }
    }

    onComplete(fullMessage, currentSessionId)
  } catch (error: any) {
    onError(error.message || 'An error occurred')
  }
}
