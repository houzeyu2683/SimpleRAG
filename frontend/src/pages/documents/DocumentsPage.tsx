import { useEffect, useState } from 'react'
import { Trash2 } from 'lucide-react'
import { documentsApi } from '@/lib/api/documents'
import { collectionsApi } from '@/lib/api/collections'
import { useWebSocket } from '@/hooks/useWebSocket'
import { DocumentUploader } from '@/components/documents/DocumentUploader'
import { IngestStatusBadge } from '@/components/documents/IngestStatusBadge'
import type { Collection, Document } from '@/types'

export function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [collections, setCollections] = useState<Collection[]>([])
  const [selectedCollection, setSelectedCollection] = useState<number | null>(null)

  useEffect(() => {
    collectionsApi.list().then((cols) => {
      setCollections(cols)
      if (cols[0]) setSelectedCollection(cols[0].id)
    })
  }, [])

  useEffect(() => {
    documentsApi.list(selectedCollection ?? undefined).then(setDocuments).catch(console.error)
  }, [selectedCollection])

  // WebSocket: update document status in real time
  useWebSocket((event) => {
    setDocuments((prev) =>
      prev.map((d) =>
        d.id === event.file_id ? { ...d, status: event.status as Document['status'] } : d,
      ),
    )
  })

  const handleUpload = async (file: File) => {
    if (!selectedCollection) return
    const doc = await documentsApi.upload(file, selectedCollection)
    setDocuments((prev) => [doc, ...prev])
  }

  const handleDelete = async (fileId: string) => {
    await documentsApi.delete(fileId)
    setDocuments((prev) => prev.filter((d) => d.id !== fileId))
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">Documents</h1>
        <p className="text-sm text-gray-500 mt-0.5">Upload PDFs to index into your knowledge base</p>
      </div>

      {collections.length > 0 ? (
        <>
          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-600 font-medium">Collection</label>
            <select
              value={selectedCollection ?? ''}
              onChange={(e) => setSelectedCollection(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {collections.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <DocumentUploader onUpload={handleUpload} />

          <div className="space-y-2">
            {documents.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-8">No documents yet</p>
            ) : (
              documents.map((doc) => (
                <div key={doc.id} className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{doc.filename}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {doc.page_count != null && `${doc.page_count} pages · `}
                      {doc.chunk_count != null && `${doc.chunk_count} chunks`}
                    </p>
                  </div>
                  <IngestStatusBadge status={doc.status} />
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              ))
            )}
          </div>
        </>
      ) : (
        <div className="text-sm text-gray-500 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          Create a collection first before uploading documents.
        </div>
      )}
    </div>
  )
}
