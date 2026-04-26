import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { chatApi } from '@/lib/api/chat'
import { apiClient } from '@/lib/api/client'
import { useChatStore } from '@/store/chatStore'
import { useChat } from '@/hooks/useChat'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { ChatInput } from '@/components/chat/ChatInput'
import type { Collection } from '@/types'
import { clsx } from 'clsx'

export function ChatPage() {
  const { sessions, activeSessionId, setSessions, addSession, removeSession, setActiveSession } = useChatStore()
  const { messages, streaming, streamError, sendMessage } = useChat(activeSessionId)
  const [collections, setCollections] = useState<Collection[]>([])
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    chatApi.listSessions().then(setSessions).catch(console.error)
    apiClient.get<Collection[]>('/collections').then((r) => setCollections(r.data)).catch(console.error)
  }, [setSessions])

  const createSession = async () => {
    if (!collections[0]) return
    setCreating(true)
    try {
      const session = await chatApi.createSession('New Chat', collections[0].id)
      addSession(session)
      setActiveSession(session.id)
    } finally {
      setCreating(false)
    }
  }

  const deleteSession = async (id: number) => {
    await chatApi.deleteSession(id)
    removeSession(id)
    if (activeSessionId === id) setActiveSession(null)
  }

  return (
    <div className="flex h-full -m-6 overflow-hidden">
      {/* Session sidebar */}
      <div className="w-56 flex flex-col border-r border-slate-700/50"
        style={{ background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(12px)' }}>
        <div className="p-3 border-b border-slate-700/50">
          <button
            onClick={createSession}
            disabled={creating || collections.length === 0}
            className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 text-xs bg-blue-600 hover:bg-blue-500 text-white rounded-lg disabled:opacity-40 transition-all duration-200"
            style={{ boxShadow: '0 0 12px rgba(59,130,246,0.3)' }}
          >
            <Plus size={13} />
            New Chat
          </button>
          {collections.length === 0 && (
            <p className="text-[10px] text-slate-500 mt-1.5 text-center">Create a collection first</p>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {sessions.map((s) => (
            <div
              key={s.id}
              className={clsx(
                'group flex items-center gap-1 px-2 py-1.5 rounded-lg cursor-pointer text-xs transition-all duration-200',
                activeSessionId === s.id
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200',
              )}
              onClick={() => setActiveSession(s.id)}
            >
              <span className="flex-1 truncate">{s.title}</span>
              <button
                onClick={(e) => { e.stopPropagation(); deleteSession(s.id) }}
                className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-all"
              >
                <Trash2 size={12} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {activeSessionId ? (
          <>
            <ChatWindow messages={messages} streaming={streaming} streamError={streamError} />
            <ChatInput onSend={sendMessage} disabled={!!streaming} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
            Select or create a chat session
          </div>
        )}
      </div>
    </div>
  )
}
