export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user' | 'viewer'
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Collection {
  id: number
  name: string
  description: string | null
  qdrant_collection: string
  owner_id: number
  created_at: string
}

export interface Document {
  id: string
  filename: string
  collection_id: number
  owner_id: number
  page_count: number | null
  chunk_count: number | null
  status: 'pending' | 'parsing' | 'chunking' | 'embedding' | 'indexing' | 'done' | 'failed'
  error_message: string | null
  created_at: string
}

export interface Citation {
  citation_id: string
  file_id: string
  page: number
  snippet: string
  score: number
  chunk_type: string
  preview_url: string
}

export interface ChatSession {
  id: number
  title: string
  collection_id: number
  owner_id: number
  created_at: string
}

export interface ChatMessage {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  citations: Citation[] | null
  created_at: string
}
