import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import type { ChatMessage, Citation } from '@/types'

interface Props {
  messages: ChatMessage[]
  streaming: { content: string; citations: Citation[] } | null
  streamError: string | null
}

export function ChatWindow({ messages, streaming, streamError }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streaming?.content, streamError])

  if (messages.length === 0 && !streaming && !streamError) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
        Ask a question to get started
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {streaming && (
        <MessageBubble
          message={{
            id: -1,
            session_id: -1,
            role: 'assistant',
            content: streaming.content + '▍',
            citations: streaming.citations.length > 0 ? streaming.citations : null,
            created_at: new Date().toISOString(),
          }}
        />
      )}

      {streamError && (
        <div className="flex items-start gap-2 rounded-lg px-4 py-3 text-sm text-red-400"
          style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)' }}>
          <span className="mt-0.5 shrink-0">⚠</span>
          <span>{streamError}</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
