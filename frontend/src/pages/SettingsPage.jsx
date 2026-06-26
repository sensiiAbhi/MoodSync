import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import { authApi } from '../api'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const { user, fetchMe } = useAuthStore()
  const [form, setForm] = useState({ full_name: '', username: '', age_range: '', occupation: '', timezone: '' })
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState('profile')

  useEffect(() => {
    if (user) {
      setForm(prev => ({
        ...prev,
        full_name: user.full_name || '',
        username: user.username || '',
      }))
    }
  }, [user])

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await authApi.updateMe(form)
      await fetchMe()
      toast.success('Profile updated successfully!')
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to update profile'
      toast.error(typeof msg === 'string' ? msg : 'Update failed')
    }
    setSaving(false)
  }

  const TABS = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'preferences', label: 'Preferences', icon: '⚙️' },
    { id: 'privacy', label: 'Privacy & Data', icon: '🔒' },
  ]

  const AGE_RANGES = ['Under 18', '18-24', '25-34', '35-44', '45-54', '55+']
  const OCCUPATIONS = ['Student', 'Developer/Engineer', 'Creative Professional', 'Office Worker', 'Healthcare Worker', 'Educator', 'Entrepreneur', 'Other']

  return (
    <div className="page-layout">
      <div className="main-content" style={{ maxWidth: 900, margin: '0 auto' }}>
        <div style={{ marginBottom: 40 }}>
          <h1 style={{ marginBottom: 8 }}>Settings</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage your account and preferences</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: 24, alignItems: 'start' }}>
          {/* Tab Nav */}
          <div className="card" style={{ padding: 8, position: 'sticky', top: 88 }}>
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  width: '100%', display: 'flex', alignItems: 'center', gap: 10,
                  padding: '10px 14px', borderRadius: 8, border: 'none', cursor: 'pointer',
                  background: activeTab === tab.id ? 'rgba(124,58,237,0.15)' : 'transparent',
                  color: activeTab === tab.id ? 'var(--primary-light)' : 'var(--text-secondary)',
                  fontWeight: activeTab === tab.id ? 600 : 400,
                  fontSize: '0.875rem', marginBottom: 2,
                  transition: 'all 0.15s ease',
                  textAlign: 'left',
                }}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content */}
          <div>
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="card">
                {/* Avatar */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 32, paddingBottom: 32, borderBottom: '1px solid var(--border)' }}>
                  <div style={{
                    width: 80, height: 80, borderRadius: '50%',
                    background: 'linear-gradient(135deg, #7C3AED, #0EA5E9)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '2rem', fontWeight: 800, color: 'white',
                    boxShadow: '0 0 20px rgba(124,58,237,0.3)',
                    flexShrink: 0,
                  }}>
                    {user?.username?.[0]?.toUpperCase() || 'U'}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: 4 }}>{user?.full_name || user?.username}</div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: 8 }}>{user?.email}</div>
                    <div style={{
                      display: 'inline-flex', alignItems: 'center', gap: 4,
                      background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)',
                      color: '#6EE7B7', padding: '3px 10px', borderRadius: 99, fontSize: '0.75rem', fontWeight: 600,
                    }}>
                      ✓ Verified
                    </div>
                  </div>
                </div>

                <form onSubmit={handleSave}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
                    <div className="form-group" style={{ margin: 0 }}>
                      <label className="form-label">Full Name</label>
                      <input
                        className="form-input"
                        value={form.full_name}
                        onChange={e => setForm({ ...form, full_name: e.target.value })}
                        placeholder="Your full name"
                      />
                    </div>
                    <div className="form-group" style={{ margin: 0 }}>
                      <label className="form-label">Username</label>
                      <input
                        className="form-input"
                        value={form.username}
                        onChange={e => setForm({ ...form, username: e.target.value })}
                        placeholder="username"
                        disabled
                        style={{ opacity: 0.6, cursor: 'not-allowed' }}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Email</label>
                    <input
                      className="form-input"
                      value={user?.email || ''}
                      disabled
                      style={{ opacity: 0.6, cursor: 'not-allowed' }}
                    />
                  </div>

                  <div style={{ marginBottom: 24 }}>
                    <label className="form-label" style={{ display: 'block', marginBottom: 12 }}>Age Range</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {AGE_RANGES.map(age => (
                        <button
                          type="button"
                          key={age}
                          className={`btn btn-sm ${form.age_range === age ? 'btn-primary' : 'btn-ghost'}`}
                          onClick={() => setForm({ ...form, age_range: age })}
                        >
                          {age}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div style={{ marginBottom: 32 }}>
                    <label className="form-label" style={{ display: 'block', marginBottom: 12 }}>Occupation</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {OCCUPATIONS.map(occ => (
                        <button
                          type="button"
                          key={occ}
                          className={`btn btn-sm ${form.occupation === occ ? 'btn-primary' : 'btn-ghost'}`}
                          onClick={() => setForm({ ...form, occupation: occ })}
                        >
                          {occ}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={saving}
                  >
                    {saving ? <><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Saving...</> : 'Save Changes'}
                  </button>
                </form>
              </div>
            )}

            {/* Preferences Tab */}
            {activeTab === 'preferences' && (
              <div className="card">
                <h3 style={{ marginBottom: 24 }}>Listening Preferences</h3>

                {[
                  { label: 'Daily Mood Reminders', desc: 'Get notified to complete your daily mood check-in', enabled: true },
                  { label: 'Weekly Mood Report', desc: 'Receive a weekly summary of your mood patterns', enabled: false },
                  { label: 'Recommendation Explanations', desc: 'Show why each track was recommended', enabled: true },
                  { label: 'Explicit Content', desc: 'Include explicit tracks in recommendations', enabled: false },
                ].map(pref => (
                  <div key={pref.label} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '18px 0', borderBottom: '1px solid var(--border)',
                  }}>
                    <div>
                      <div style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: '0.9rem' }}>{pref.label}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 2 }}>{pref.desc}</div>
                    </div>
                    <div style={{
                      width: 48, height: 26, borderRadius: 99,
                      background: pref.enabled ? 'var(--primary)' : 'rgba(255,255,255,0.1)',
                      cursor: 'pointer', position: 'relative', flexShrink: 0,
                      transition: 'background 0.2s ease',
                    }}>
                      <div style={{
                        position: 'absolute', top: 3, left: pref.enabled ? 25 : 3,
                        width: 20, height: 20, borderRadius: '50%',
                        background: 'white', transition: 'left 0.2s ease',
                        boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
                      }} />
                    </div>
                  </div>
                ))}

                <div style={{ marginTop: 24 }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Note: Preference changes in this beta version are displayed only — persistence coming in v2.
                  </p>
                </div>
              </div>
            )}

            {/* Privacy Tab */}
            {activeTab === 'privacy' && (
              <div className="card">
                <h3 style={{ marginBottom: 24 }}>Privacy & Data</h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                  {[
                    {
                      icon: '🔒', title: 'Data Encryption',
                      desc: 'All your psychological assessment data is encrypted at rest and in transit using AES-256.',
                      status: 'Active', statusColor: '#10B981',
                    },
                    {
                      icon: '🛡️', title: 'GDPR Compliance',
                      desc: 'MoodSync is fully GDPR compliant. You have the right to access, export, or delete your data at any time.',
                      status: 'Compliant', statusColor: '#10B981',
                    },
                    {
                      icon: '🔑', title: 'JWT Authentication',
                      desc: 'Your sessions use short-lived access tokens (15min) with secure HttpOnly refresh token rotation.',
                      status: 'Active', statusColor: '#10B981',
                    },
                  ].map(item => (
                    <div key={item.title} style={{
                      display: 'flex', gap: 16, padding: '16px 20px',
                      background: 'rgba(16,185,129,0.05)',
                      border: '1px solid rgba(16,185,129,0.15)',
                      borderRadius: 12,
                    }}>
                      <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>{item.icon}</span>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                          <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{item.title}</span>
                          <span style={{
                            fontSize: '0.7rem', fontWeight: 700,
                            color: item.statusColor, background: `${item.statusColor}20`,
                            padding: '2px 8px', borderRadius: 99,
                          }}>{item.status}</span>
                        </div>
                        <p style={{ fontSize: '0.8rem', lineHeight: 1.6, margin: 0 }}>{item.desc}</p>
                      </div>
                    </div>
                  ))}

                  <div style={{
                    marginTop: 12, padding: '20px', border: '1px solid rgba(239,68,68,0.2)',
                    borderRadius: 12, background: 'rgba(239,68,68,0.04)',
                  }}>
                    <h4 style={{ color: '#FCA5A5', marginBottom: 8, fontSize: '0.95rem' }}>Danger Zone</h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 16 }}>
                      Permanently delete your account and all associated data including mood history, playlists, and recommendations. This action cannot be undone.
                    </p>
                    <button className="btn btn-danger btn-sm" onClick={() => toast.error('Please contact support to delete your account.')}>
                      Delete My Account
                    </button>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  )
}
