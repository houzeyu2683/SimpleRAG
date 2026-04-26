import { apiClient } from './client'
import type { ChatMessage, ChatSession } from '@/types'

export const chatApi = {
  createSession: (title: string, collection_id: number) =>
    apiClient.post<ChatSession>('/chat/sessions', { title, collection_id }).then((r) => r.data),

  listSessions: () =>
    apiClient.get<ChatSession[]>('/chat/sessions').then((r) => r.data),

  getMessages: (sessionId: number) =>
    apiClient.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`).then((r) => r.data),

  deleteSession: (sessionId: number) =>
    apiClient.delete(`/chat/sessions/${sessionId}`),

  streamMessage: (sessionId: number, content: string, onEvent: (event: SSEEvent) => void): Promise<void> => {
    return new Promise((resolve, reject) => {
      const token = localStorage.getItem('access_token')
      const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

      fetch(`${BASE_URL}/api/v1/chat/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content }),
      })
        .then((res) => {
          if (!res.ok) return reject(new Error(`HTTP ${res.status}`))
          if (!res.body) return reject(new Error('No body'))

          const reader = res.body.getReader()
          const decoder = new TextDecoder()
          let buffer = ''

          const pump = () =>
            reader.read().then(({ done, value }) => {
              if (done) return resolve()
              buffer += decoder.decode(value, { stream: true })
              const lines = buffer.split('\n')
              buffer = lines.pop() ?? ''
              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const parsed = JSON.parse(line.slice(6))
                    onEvent(parsed)
                  } catch { /* skip malformed */ }
                }
              }
              pump()
            })

          pump()
        })
        .catch(reject)
    })
  },
}

export interface SSEEvent {
  type: 'token' | 'citations' | 'done' | 'error'
  data?: string | object[]
}
