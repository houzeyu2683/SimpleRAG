import { apiClient } from './client'
import type { Collection } from '@/types'

export const collectionsApi = {
  list: () => apiClient.get<Collection[]>('/collections').then((r) => r.data),
  create: (name: string, description?: string) =>
    apiClient.post<Collection>('/collections', { name, description }).then((r) => r.data),
  delete: (id: number) => apiClient.delete(`/collections/${id}`),
}
