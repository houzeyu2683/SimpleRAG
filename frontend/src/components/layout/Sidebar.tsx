import { NavLink } from 'react-router-dom'
import { MessageSquare, FileText, Database, Shield } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { clsx } from 'clsx'

const navItems = [
  { to: '/chat', icon: MessageSquare, label: 'Chat' },
  { to: '/documents', icon: FileText, label: 'Documents' },
  { to: '/collections', icon: Database, label: 'Collections' },
]

export function Sidebar() {
  const user = useAuthStore((s) => s.user)

  return (
    <aside className="w-56 flex flex-col glass-panel-strong rounded-none border-r border-slate-700/50">
      <div className="h-14 flex items-center px-4 border-b border-slate-700/50">
        <span className="font-semibold text-gradient text-sm tracking-wide">RAG System</span>
      </div>

      <nav className="flex-1 p-2 space-y-0.5">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all duration-200',
                isActive
                  ? 'bg-blue-600/20 text-blue-400 font-medium border border-blue-500/30'
                  : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200',
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}

        {user?.role === 'admin' && (
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all duration-200',
                isActive
                  ? 'bg-blue-600/20 text-blue-400 font-medium border border-blue-500/30'
                  : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200',
              )
            }
          >
            <Shield size={16} />
            Admin
          </NavLink>
        )}
      </nav>

      <div className="p-3 border-t border-slate-700/50">
        <div className="text-xs text-slate-300 truncate">{user?.email}</div>
        <div className="text-xs text-slate-500 capitalize">{user?.role}</div>
      </div>
    </aside>
  )
}
