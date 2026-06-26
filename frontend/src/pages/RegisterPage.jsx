import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', username: '', password: '', full_name: '' })
  const [loading, setLoading] = useState(false)
  const { register, login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      await register(form)
      toast.success('Account created! Let\'s set up your profile 🎵')
      // Auto-login after register
      const { user } = await login({ email: form.email, password: form.password })
      navigate('/onboarding')
    } catch (err) {
      const detail = err?.response?.data?.detail
      toast.error(typeof detail === 'string' ? detail : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      padding: '24px',
      background: 'radial-gradient(ellipse at 50% 30%, rgba(14,165,233,0.12) 0%, transparent 60%)',
    }}>
      <div style={{
        width: '100%', maxWidth: 460,
        background: 'rgba(26,26,53,0.8)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 'var(--radius-2xl)',
        padding: 48,
        backdropFilter: 'blur(24px)',
        boxShadow: '0 24px 64px rgba(0,0,0,0.5)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{
            width: 56, height: 56, borderRadius: 16,
            background: 'linear-gradient(135deg, #7C3AED, #0EA5E9)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.75rem', margin: '0 auto 16px',
            boxShadow: '0 8px 24px rgba(124,58,237,0.4)',
          }}>🎵</div>
          <h2 style={{ marginBottom: 8 }}>Create your account</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Join MoodSync and discover music for your mind
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Full name</label>
              <input
                className="form-input"
                type="text"
                placeholder="Alex Johnson"
                value={form.full_name}
                onChange={e => setForm({ ...form, full_name: e.target.value })}
              />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Username</label>
              <input
                className="form-input"
                type="text"
                placeholder="musiclover42"
                value={form.username}
                onChange={e => setForm({ ...form, username: e.target.value })}
                required
              />
            </div>
          </div>

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
              placeholder="At least 8 characters"
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
              <><div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Creating account...</>
            ) : 'Create Account →'}
          </button>
        </form>

        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: 16 }}>
          By creating an account you agree to our terms. Your psychological data is private and secure.
        </p>

        <div style={{ textAlign: 'center', marginTop: 24, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--primary-light)', fontWeight: 600 }}>
            Sign in
          </Link>
        </div>
      </div>
    </div>
  )
}
