import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '@/lib/api/auth'
import { useAuthStore } from '@/store/authStore'

export function useAuth() {
  const { user, setTokens, setUser, logout: storeLogout, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await authApi.login(email, password)
    setTokens(tokens.access_token, tokens.refresh_token)
    const me = await authApi.me()
    setUser(me)
    navigate('/chat')
  }, [setTokens, setUser, navigate])

  const register = useCallback(async (username: string, email: string, password: string) => {
    await authApi.register(username, email, password)
    await login(email, password)
  }, [login])

  const logout = useCallback(async () => {
    try { await authApi.logout() } catch { /* ignore */ }
    storeLogout()
    navigate('/login')
  }, [storeLogout, navigate])

  return { user, login, register, logout, isAuthenticated }
}
