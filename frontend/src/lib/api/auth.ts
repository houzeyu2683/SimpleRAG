import { apiClient } from './client'
import type { TokenResponse, User } from '@/types'

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<TokenResponse>('/auth/login', { email, password }).then((r) => r.data),

  register: (username: string, email: string, password: string) =>
    apiClient.post<User>('/auth/register', { username, email, password }).then((r) => r.data),

  logout: () => apiClient.post('/auth/logout'),

  refreshToken: (refresh_token: string) =>
    apiClient.post<TokenResponse>('/auth/refresh', { refresh_token }).then((r) => r.data),

  me: () => apiClient.get<User>('/users/me').then((r) => r.data),
}
