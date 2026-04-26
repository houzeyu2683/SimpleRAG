import { useState, useRef, type KeyboardEvent } from 'react'
import { Send } from 'lucide-react'

interface Props {
  onSend: (content: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const onInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }

  return (
    <div className="flex items-end gap-2 p-4 border-t border-slate-700/50"
      style={{ background: 'rgba(15,23,42,0.7)', backdropFilter: 'blur(12px)' }}>
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        onInput={onInput}
        placeholder="Ask a question… (Shift+Enter for newline)"
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none rounded-xl px-3 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:opacity-50 overflow-hidden transition-all"
        style={{ background: 'rgba(51,65,85,0.5)', border: '1px solid rgba(148,163,184,0.2)' }}
      />
      <button
        onClick={submit}
        disabled={disabled || !value.trim()}
        className="shrink-0 w-9 h-9 flex items-center justify-center bg-blue-600 hover:bg-blue-500 text-white rounded-xl disabled:opacity-40 transition-all duration-200"
        style={{ boxShadow: '0 0 12px rgba(59,130,246,0.3)' }}
      >
        <Send size={15} />
      </button>
    </div>
  )
}
