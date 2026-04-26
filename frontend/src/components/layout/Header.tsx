import { LogOut } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

export function Header() {
  const { user, logout } = useAuth()

  return (
    <header className="h-14 border-b border-slate-700/50 flex items-center justify-between px-6"
      style={{ background: 'rgba(15,23,42,0.7)', backdropFilter: 'blur(12px)' }}>
      <div />
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-400">{user?.username}</span>
        <button
          onClick={logout}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-200 transition-colors"
        >
          <LogOut size={15} />
          Logout
        </button>
      </div>
    </header>
  )
}
