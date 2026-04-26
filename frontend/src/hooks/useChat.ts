import { useCallback, useEffect } from 'react'
import { chatApi } from '@/lib/api/chat'
import { useChatStore } from '@/store/chatStore'
import type { Citation } from '@/types'

export function useChat(sessionId: number | null) {
  const {
    messages, streaming, streamError, setMessages, appendToken,
    setCitations, commitStreaming, clearStreaming, setStreamError,
  } = useChatStore()

  useEffect(() => {
    if (!sessionId) return
    chatApi.getMessages(sessionId).then(setMessages).catch(console.error)
  }, [sessionId, setMessages])

  const sendMessage = useCallback(async (content: string) => {
    if (!sessionId) return

    // Clear previous error and add optimistic user message
    setStreamError(null)
    const tempUserMsg = {
      id: Date.now(),
      session_id: sessionId,
      role: 'user' as const,
      content,
      citations: null,
      created_at: new Date().toISOString(),
    }
    setMessages([...messages, tempUserMsg])

    // Start streaming placeholder
    setCitations([])

    try {
      await chatApi.streamMessage(sessionId, content, (event) => {
        if (event.type === 'token') {
          appendToken(event.data as string)
        } else if (event.type === 'citations') {
          setCitations(event.data as Citation[])
        } else if (event.type === 'done') {
          useChatStore.getState().streaming &&
            commitStreaming({
              id: Date.now() + 1,
              session_id: sessionId,
              role: 'assistant',
              content: useChatStore.getState().streaming!.content,
              citations: useChatStore.getState().streaming!.citations,
              created_at: new Date().toISOString(),
            })
        } else if (event.type === 'error') {
          setStreamError(event.data as string ?? 'An error occurred. Please try again.')
        }
      })
    } catch (err) {
      console.error('Stream error:', err)
      setStreamError('Connection error. Please try again.')
    }
  }, [sessionId, messages, setMessages, appendToken, setCitations, commitStreaming, clearStreaming, setStreamError])

  return { messages, streaming, streamError, sendMessage }
}
