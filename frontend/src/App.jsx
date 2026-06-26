import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/authStore'
import Navbar from './components/shared/Navbar'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import OnboardingPage from './pages/OnboardingPage'
import DashboardPage from './pages/DashboardPage'
import AssessmentPage from './pages/AssessmentPage'
import RecommendationPage from './pages/RecommendationPage'
import AnalyticsPage from './pages/AnalyticsPage'
import PlaylistsPage from './pages/PlaylistsPage'
import SettingsPage from './pages/SettingsPage'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  if (isAuthenticated) return <Navigate to="/app/dashboard" replace />
  return children
}

export default function App() {
  const { fetchMe, isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) fetchMe()
  }, [])

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-base)' }}>

      {isAuthenticated && <Navbar />}
      <Routes>
        {/* Public */}
        <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
        <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />

        {/* Protected App Routes */}
        <Route path="/onboarding" element={<ProtectedRoute><OnboardingPage /></ProtectedRoute>} />
        <Route path="/app/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/app/assess" element={<ProtectedRoute><AssessmentPage /></ProtectedRoute>} />
        <Route path="/app/recommend" element={<ProtectedRoute><RecommendationPage /></ProtectedRoute>} />
        <Route path="/app/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
        <Route path="/app/playlists" element={<ProtectedRoute><PlaylistsPage /></ProtectedRoute>} />
        <Route path="/app/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to={isAuthenticated ? "/app/dashboard" : "/"} replace />} />
      </Routes>
    </div>
  )
}
