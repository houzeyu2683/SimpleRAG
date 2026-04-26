import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CitationCard } from './CitationCard'
import type { ChatMessage } from '@/types'
import { clsx } from 'clsx'
import { useAuthStore } from '@/store/authStore'

interface Props {
  message: ChatMessage
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'
  const accessToken = useAuthStore((s) => s.accessToken)

  function tokenizeApiUrl(src: string | undefined): string | undefined {
    if (!src || !accessToken) return src
    if (!src.startsWith('/api/')) return src
    return src.includes('?') ? `${src}&token=${accessToken}` : `${src}?token=${accessToken}`
  }

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div className={clsx('max-w-[75%] space-y-2', isUser ? 'items-end' : 'items-start')}>
        <div
          className={clsx('px-4 py-3 rounded-2xl text-sm leading-relaxed', isUser ? 'rounded-br-sm' : 'rounded-bl-sm')}
          style={
            isUser
              ? { background: 'rgba(59,130,246,0.85)', color: '#fff', boxShadow: '0 0 16px rgba(59,130,246,0.3)' }
              : { background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(148,163,184,0.15)', color: '#cbd5e1', backdropFilter: 'blur(12px)' }
          }
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                img({ src, alt }) {
                  return (
                    <img
                      src={tokenizeApiUrl(src)}
                      alt={alt ?? ''}
                      className="max-w-full rounded my-3"
                      style={{ border: '1px solid rgba(148,163,184,0.15)', display: 'block' }}
                    />
                  )
                },
                code({ children, className }) {
                  const isBlock = className?.includes('language-')
                  return isBlock ? (
                    <pre className="rounded p-3 overflow-x-auto text-xs my-2"
                      style={{ background: 'rgba(2,6,23,0.6)', border: '1px solid rgba(148,163,184,0.15)' }}>
                      <code className="text-slate-300">{children}</code>
                    </pre>
                  ) : (
                    <code className="px-1.5 py-0.5 rounded text-xs text-blue-300"
                      style={{ background: 'rgba(59,130,246,0.15)' }}>{children}</code>
                  )
                },
                table({ children }) {
                  return (
                    <div className="overflow-x-auto my-2">
                      <table className="text-xs border-collapse" style={{ borderColor: 'rgba(148,163,184,0.2)' }}>{children}</table>
                    </div>
                  )
                },
                th({ children }) {
                  return <th className="px-2 py-1 text-slate-300 font-medium"
                    style={{ border: '1px solid rgba(148,163,184,0.2)', background: 'rgba(51,65,85,0.4)' }}>{children}</th>
                },
                td({ children }) {
                  return <td className="px-2 py-1 text-slate-400"
                    style={{ border: '1px solid rgba(148,163,184,0.2)' }}>{children}</td>
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="space-y-1 w-full">
            {message.citations.map((c, i) => (
              <CitationCard key={c.citation_id} citation={c} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
