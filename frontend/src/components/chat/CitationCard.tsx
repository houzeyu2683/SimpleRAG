import { useState } from 'react'
import { FileText, ChevronDown, ChevronUp } from 'lucide-react'
import type { Citation } from '@/types'
import { useAuthStore } from '@/store/authStore'

interface Props {
  citation: Citation
  index: number
}

export function CitationCard({ citation, index }: Props) {
  const [open, setOpen] = useState(false)
  const [imgError, setImgError] = useState(false)
  const accessToken = useAuthStore((s) => s.accessToken)

  const previewSrc = citation.preview_url && accessToken
    ? `${citation.preview_url}&token=${accessToken}`
    : citation.preview_url

  return (
    <div className="rounded-lg overflow-hidden text-xs"
      style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(148,163,184,0.15)' }}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left transition-colors hover:bg-slate-700/30"
      >
        <FileText size={13} className="text-slate-500 shrink-0" />
        <span className="flex-1 text-slate-400 truncate">
          [{index + 1}] Page {citation.page}
          {citation.chunk_type === 'table' && <span className="ml-1 text-blue-400">[Table]</span>}
        </span>
        <span className="text-slate-500 text-[10px] mr-1">{Math.round(citation.score * 100)}%</span>
        {open ? <ChevronUp size={13} className="text-slate-500" /> : <ChevronDown size={13} className="text-slate-500" />}
      </button>

      {open && (
        <div className="p-3 space-y-2" style={{ borderTop: '1px solid rgba(148,163,184,0.1)' }}>
          <p className="text-slate-400 leading-relaxed">{citation.snippet}</p>
          {!imgError && previewSrc && (
            <img
              src={previewSrc}
              alt={`Page ${citation.page}`}
              className="w-full rounded"
              style={{ border: '1px solid rgba(148,163,184,0.15)' }}
              onError={() => setImgError(true)}
            />
          )}
        </div>
      )}
    </div>
  )
}
