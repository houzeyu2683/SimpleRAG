import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { AppLayout } from '@/components/layout/AppLayout'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RegisterPage } from '@/pages/auth/RegisterPage'
import { ChatPage } from '@/pages/chat/ChatPage'
import { DocumentsPage } from '@/pages/documents/DocumentsPage'
import { CollectionsPage } from '@/pages/collections/CollectionsPage'
import { AdminPage } from '@/pages/admin/AdminPage'

function BackgroundSystem() {
  return (
    <div className="background-system">
      <div className="floating-orb floating-orb-1" />
      <div className="floating-orb floating-orb-2" />
      <div className="floating-orb floating-orb-3" />
      <div className="floating-orb floating-orb-4" />
      <div className="geometric-decorations">
        <div className="geometric-line geometric-line-1" />
        <div className="geometric-line geometric-line-2" />
        <div className="geometric-line geometric-line-3" />
        <div className="geometric-polygon geometric-polygon-1" />
        <div className="geometric-polygon geometric-polygon-2" />
        <div className="geometric-circle geometric-circle-1" />
        <div className="geometric-circle geometric-circle-2" />
      </div>
      <div className="particle-system">
        {Array.from({ length: 15 }).map((_, i) => (
          <div key={i} className={`particle particle-${i + 1}`} />
        ))}
      </div>
      <div className="light-beams">
        <div className="light-beam light-beam-1" />
        <div className="light-beam light-beam-2" />
        <div className="light-beam light-beam-3" />
      </div>
      <div className="grid-overlay" />
    </div>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated())
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function GuestRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated())
  return isAuthenticated ? <Navigate to="/chat" replace /> : <>{children}</>
}

export default function App() {
  return (
    <div className="relative min-h-screen" style={{ background: '#0a0b1e', color: '#e2e8f0' }}>
      <BackgroundSystem />
      <div className="relative z-10 h-screen flex flex-col">
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
            <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />

            <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
              <Route index element={<Navigate to="/chat" replace />} />
              <Route path="chat" element={<ChatPage />} />
              <Route path="documents" element={<DocumentsPage />} />
              <Route path="collections" element={<CollectionsPage />} />
              <Route path="admin" element={<AdminPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </div>
    </div>
  )
}
