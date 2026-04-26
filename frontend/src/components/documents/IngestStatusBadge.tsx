import { clsx } from 'clsx'
import type { Document } from '@/types'

const config: Record<Document['status'], { label: string; className: string }> = {
  pending:   { label: 'Pending',   className: 'bg-gray-100 text-gray-600' },
  parsing:   { label: 'Parsing',   className: 'bg-yellow-100 text-yellow-700' },
  chunking:  { label: 'Chunking',  className: 'bg-yellow-100 text-yellow-700' },
  embedding: { label: 'Embedding', className: 'bg-blue-100 text-blue-700' },
  indexing:  { label: 'Indexing',  className: 'bg-blue-100 text-blue-700' },
  done:      { label: 'Ready',     className: 'bg-green-100 text-green-700' },
  failed:    { label: 'Failed',    className: 'bg-red-100 text-red-700' },
}

export function IngestStatusBadge({ status }: { status: Document['status'] }) {
  const { label, className } = config[status] ?? config.pending
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium', className)}>
      {['parsing', 'chunking', 'embedding', 'indexing'].includes(status) && (
        <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 animate-pulse" />
      )}
      {label}
    </span>
  )
}
