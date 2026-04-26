import { useRef, useState } from 'react'
import { Upload } from 'lucide-react'
import { clsx } from 'clsx'

interface Props {
  onUpload: (file: File) => Promise<void>
  disabled?: boolean
}

export function DocumentUploader({ onUpload, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState<number | null>(null)

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.pdf')) return
    setProgress(0)
    try {
      await onUpload(file)
    } finally {
      setProgress(null)
    }
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      className={clsx(
        'border-2 border-dashed rounded-xl p-8 flex flex-col items-center gap-2 cursor-pointer transition-colors',
        dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400 bg-white',
        disabled && 'opacity-50 cursor-not-allowed',
      )}
    >
      <Upload size={24} className="text-gray-400" />
      <p className="text-sm text-gray-600 font-medium">Drop PDF here or click to browse</p>
      <p className="text-xs text-gray-400">Max 50 MB</p>
      {progress !== null && (
        <div className="w-full max-w-xs mt-2">
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 transition-all" style={{ width: `${progress}%` }} />
          </div>
          <p className="text-xs text-gray-500 text-center mt-1">{progress}%</p>
        </div>
      )}
      <input ref={inputRef} type="file" accept=".pdf" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f) }} />
    </div>
  )
}
