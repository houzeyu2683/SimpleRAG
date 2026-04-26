import { apiClient } from './client'
import type { Document } from '@/types'

export const documentsApi = {
  list: (collectionId?: number) =>
    apiClient.get<Document[]>('/documents', { params: collectionId ? { collection_id: collectionId } : {} }).then((r) => r.data),

  upload: (file: File, collectionId: number, onProgress?: (pct: number) => void) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post<Document>(`/documents/upload?collection_id=${collectionId}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => onProgress?.(Math.round((e.loaded / (e.total ?? 1)) * 100)),
    }).then((r) => r.data)
  },

  getStatus: (fileId: string) =>
    apiClient.get<{ id: string; status: string; page_count: number | null; chunk_count: number | null; error_message: string | null }>(
      `/documents/${fileId}/status`,
    ).then((r) => r.data),

  delete: (fileId: string) => apiClient.delete(`/documents/${fileId}`),
}
