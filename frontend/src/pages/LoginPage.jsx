import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { user } = await login(form)
      toast.success(`Welcome back, ${user.username}! 🎵`)
      navigate(user.onboarding_completed ? '/app/dashboard' : '/onboarding')
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Invalid email or password'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      padding: '24px',
      background: 'radial-gradient(ellipse at 50% 30%, rgba(124,58,237,0.15) 0%, transparent 60%)',
    }}>
      <div style={{
        width: '100%', maxWidth: 440,
        background: 'rgba(26,26,53,0.8)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 'var(--radius-2xl)',
        padding: 48,
        backdropFilter: 'blur(24px)',
        boxShadow: '0 24px 64px rgba(0,0,0,0.5)',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{
            width: 56, height: 56, borderRadius: 16,
            background: 'linear-gradient(135deg, #7C3AED, #0EA5E9)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.75rem', margin: '0 auto 16px',
            boxShadow: '0 8px 24px rgba(124,58,237,0.4)',
          }}>🎵</div>
          <h2 style={{ marginBottom: 8 }}>Welcome back</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Sign in to your MoodSync account
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email address</label>
            <input
              className="form-input"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              className="form-input"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', marginTop: 8, padding: '14px' }}
          >
            {loading ? (
              <><div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Signing in...</>
            ) : 'Sign In →'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 28, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'var(--primary-light)', fontWeight: 600 }}>
            Create one free
          </Link>
        </div>
      </div>
    </div>
  )
}
