import { create } from 'zustand'
import type { ChatMessage, ChatSession, Citation } from '@/types'

interface StreamingMessage {
  content: string
  citations: Citation[]
}

interface ChatStore {
  sessions: ChatSession[]
  activeSessionId: number | null
  messages: ChatMessage[]
  streaming: StreamingMessage | null
  streamError: string | null

  setSessions: (sessions: ChatSession[]) => void
  addSession: (session: ChatSession) => void
  removeSession: (id: number) => void
  setActiveSession: (id: number | null) => void
  setMessages: (messages: ChatMessage[]) => void
  appendToken: (token: string) => void
  setCitations: (citations: Citation[]) => void
  commitStreaming: (message: ChatMessage) => void
  clearStreaming: () => void
  setStreamError: (error: string | null) => void
}

export const useChatStore = create<ChatStore>((set) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  streaming: null,
  streamError: null,

  setSessions: (sessions) => set({ sessions }),
  addSession: (session) => set((s) => ({ sessions: [session, ...s.sessions] })),
  removeSession: (id) => set((s) => ({ sessions: s.sessions.filter((x) => x.id !== id) })),
  setActiveSession: (id) => set({ activeSessionId: id, messages: [], streaming: null, streamError: null }),
  setMessages: (messages) => set({ messages }),
  appendToken: (token) =>
    set((s) => ({
      streaming: {
        content: (s.streaming?.content ?? '') + token,
        citations: s.streaming?.citations ?? [],
      },
    })),
  setCitations: (citations) =>
    set((s) => ({
      streaming: { content: s.streaming?.content ?? '', citations },
    })),
  commitStreaming: (message) =>
    set((s) => ({ messages: [...s.messages, message], streaming: null, streamError: null })),
  clearStreaming: () => set({ streaming: null }),
  setStreamError: (error) => set({ streaming: null, streamError: error }),
}))
