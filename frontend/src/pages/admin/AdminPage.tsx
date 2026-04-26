import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api/client'
import type { User } from '@/types'

const ROLES = ['admin', 'user', 'viewer'] as const

export function AdminPage() {
  const [users, setUsers] = useState<User[]>([])
  const [total, setTotal] = useState(0)
  const [updating, setUpdating] = useState<number | null>(null)

  useEffect(() => {
    apiClient.get<{ items: User[]; total: number }>('/admin/users').then((r) => {
      setUsers(r.data.items)
      setTotal(r.data.total)
    }).catch(console.error)
  }, [])

  const updateRole = async (userId: number, role: string) => {
    setUpdating(userId)
    try {
      const { data } = await apiClient.patch<User>(`/admin/users/${userId}`, { role })
      setUsers((prev) => prev.map((u) => (u.id === data.id ? data : u)))
    } finally {
      setUpdating(null)
    }
  }

  const toggleActive = async (user: User) => {
    setUpdating(user.id)
    try {
      const { data } = await apiClient.patch<User>(`/admin/users/${user.id}`, { is_active: !user.is_active })
      setUsers((prev) => prev.map((u) => (u.id === data.id ? data : u)))
    } finally {
      setUpdating(null)
    }
  }

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">User Management</h1>
        <p className="text-sm text-gray-500 mt-0.5">{total} users total</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              {['Username', 'Email', 'Role', 'Status', 'Actions'].map((h) => (
                <th key={h} className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{user.username}</td>
                <td className="px-4 py-3 text-gray-500">{user.email}</td>
                <td className="px-4 py-3">
                  <select
                    value={user.role}
                    disabled={updating === user.id}
                    onChange={(e) => updateRole(user.id, e.target.value)}
                    className="border border-gray-300 rounded-md px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
                  </select>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${user.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => toggleActive(user)}
                    disabled={updating === user.id}
                    className="text-xs text-blue-600 hover:underline disabled:opacity-50"
                  >
                    {user.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
