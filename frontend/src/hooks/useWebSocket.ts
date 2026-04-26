import { useEffect, useRef } from 'react'
import { useAuthStore } from '@/store/authStore'

export interface IngestEvent {
  file_id: string
  status: string
  detail: string
}

export function useWebSocket(onEvent: (event: IngestEvent) => void) {
  const token = useAuthStore((s) => s.accessToken)
  const wsRef = useRef<WebSocket | null>(null)
  const onEventRef = useRef(onEvent)
  onEventRef.current = onEvent

  useEffect(() => {
    if (!token) return

    const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
    const wsUrl = BASE_URL.replace(/^http/, 'ws') || `ws://${window.location.host}`
    const ws = new WebSocket(`${wsUrl}/ws/notifications?token=${token}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as IngestEvent
        onEventRef.current(data)
      } catch { /* skip */ }
    }

    ws.onclose = () => { wsRef.current = null }

    return () => { ws.close() }
  }, [token])
}
