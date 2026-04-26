import { useEffect, useState } from 'react'
import { Trash2, Plus, Database } from 'lucide-react'
import { collectionsApi } from '@/lib/api/collections'
import type { Collection } from '@/types'

export function CollectionsPage() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    collectionsApi.list().then(setCollections).catch(console.error)
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setCreating(true)
    try {
      const col = await collectionsApi.create(name, description || undefined)
      setCollections((prev) => [...prev, col])
      setName('')
      setDescription('')
    } catch {
      setError('Failed to create collection. Name may already exist.')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id: number) => {
    await collectionsApi.delete(id)
    setCollections((prev) => prev.filter((c) => c.id !== id))
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">Collections</h1>
        <p className="text-sm text-gray-500 mt-0.5">Knowledge base collections backed by Qdrant</p>
      </div>

      <form onSubmit={handleCreate} className="bg-white border border-gray-200 rounded-xl p-4 space-y-3">
        <h2 className="text-sm font-medium text-gray-700">New collection</h2>
        <input
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Name"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {error && <p className="text-xs text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={creating}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Plus size={14} />
          Create
        </button>
      </form>

      <div className="space-y-2">
        {collections.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-8">No collections yet</p>
        ) : (
          collections.map((col) => (
            <div key={col.id} className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl">
              <Database size={18} className="text-blue-500 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{col.name}</p>
                {col.description && <p className="text-xs text-gray-500 mt-0.5">{col.description}</p>}
                <p className="text-xs text-gray-400 mt-0.5 font-mono">{col.qdrant_collection}</p>
              </div>
              <button
                onClick={() => handleDelete(col.id)}
                className="text-gray-400 hover:text-red-500 transition-colors"
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
