import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import ThemePicker from './ThemePicker'
import toast from 'react-hot-toast'

const NAV_LINKS = [
  { path: '/app/dashboard', label: 'Home',      icon: '⊞' },
  { path: '/app/assess',    label: 'Check In',  icon: '◉' },
  { path: '/app/recommend', label: 'Discover',  icon: '✦' },
  { path: '/app/analytics', label: 'Analytics', icon: '▲' },
  { path: '/app/playlists', label: 'Playlists', icon: '♪' },
]

export default function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [avatarHover, setAvatarHover] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => { setMenuOpen(false) }, [location.pathname])

  const handleLogout = async () => {
    await logout()
    toast.success('See you soon! 👋')
    navigate('/')
  }

  const isActive = (path) => location.pathname === path

  return (
    <>
      <nav className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>
        <div className="navbar-inner">

          {/* ── Logo ── */}
          <Link to="/app/dashboard" className="nav-logo">
            <div className="nav-logo-icon">M</div>
            <span className="nav-logo-text">MoodSync</span>
          </Link>

          {/* ── Nav Links (desktop) ── */}
          <div className="nav-links desktop-only">
            {NAV_LINKS.map(link => (
              <Link
                key={link.path}
                to={link.path}
                className={`nav-link ${isActive(link.path) ? 'active' : ''}`}
              >
                <span className="nav-link-icon" style={{ fontSize: '0.8rem' }}>
                  {link.icon}
                </span>
                {link.label}
              </Link>
            ))}
          </div>

          {/* ── Right Side ── */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>

            {/* Theme Picker */}
            <div className="desktop-only">
              <ThemePicker />
            </div>

            {/* Check In CTA */}
            <Link
              to="/app/assess"
              className="btn btn-primary btn-sm desktop-only"
              style={{ textDecoration: 'none' }}
            >
              ◉ Check In
            </Link>

            {/* User Avatar dropdown */}
            <div style={{ position: 'relative' }}>
              <div
                onMouseEnter={() => setAvatarHover(true)}
                onMouseLeave={() => setAvatarHover(false)}
                style={{ position: 'relative' }}
              >
                <div
                  style={{
                    width: 34, height: 34, borderRadius: '50%',
                    background: 'var(--accent)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '0.85rem', fontWeight: 800,
                    color: '#000', cursor: 'pointer',
                    transition: 'transform 0.15s ease',
                    transform: avatarHover ? 'scale(1.08)' : 'scale(1)',
                    userSelect: 'none',
                  }}
                >
                  {user?.username?.[0]?.toUpperCase() || 'U'}
                </div>

                {/* Hover dropdown */}
                {avatarHover && (
                  <div style={{
                    position: 'absolute', top: '100%', right: 0,
                    marginTop: 8,
                    background: '#282828',
                    border: '1px solid rgba(255,255,255,0.12)',
                    borderRadius: 8,
                    padding: '6px',
                    minWidth: 180,
                    zIndex: 300,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
                    animation: 'fadeIn 0.15s ease',
                  }}>
                    <div style={{ padding: '8px 12px', borderBottom: '1px solid rgba(255,255,255,0.08)', marginBottom: 4 }}>
                      <div style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                        {user?.username}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                        {user?.email}
                      </div>
                    </div>

                    {[
                      { label: 'Profile & Settings', to: '/app/settings', icon: '⚙' },
                      { label: 'My Playlists', to: '/app/playlists', icon: '♪' },
                    ].map(item => (
                      <Link
                        key={item.label}
                        to={item.to}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 10,
                          padding: '8px 12px', borderRadius: 6,
                          fontSize: '0.875rem', color: 'var(--text-secondary)',
                          textDecoration: 'none', transition: 'all 0.15s ease',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.07)'; e.currentTarget.style.color = '#fff' }}
                        onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)' }}
                      >
                        <span>{item.icon}</span>
                        {item.label}
                      </Link>
                    ))}

                    <hr style={{ border: 'none', height: 1, background: 'rgba(255,255,255,0.08)', margin: '4px 0' }} />

                    <button
                      onClick={handleLogout}
                      style={{
                        width: '100%', display: 'flex', alignItems: 'center', gap: 10,
                        padding: '8px 12px', borderRadius: 6,
                        fontSize: '0.875rem', color: 'var(--text-muted)',
                        background: 'none', border: 'none', cursor: 'pointer',
                        transition: 'all 0.15s ease', textAlign: 'left',
                      }}
                      onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.07)'; e.currentTarget.style.color = '#fff' }}
                      onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)' }}
                    >
                      ↗ Log out
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Mobile hamburger */}
            <button
              className="mobile-only"
              onClick={() => setMenuOpen(!menuOpen)}
              style={{
                background: 'none', border: '1px solid var(--border)',
                borderRadius: 8, padding: '6px 10px', cursor: 'pointer',
                color: 'var(--text-secondary)', fontSize: '1rem',
              }}
            >
              {menuOpen ? '✕' : '☰'}
            </button>
          </div>
        </div>
      </nav>

      {/* ── Mobile Menu Drawer ── */}
      {menuOpen && (
        <div
          className="mobile-only"
          style={{
            position: 'fixed', top: 'var(--navbar-height)', left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.96)', zIndex: 150,
            display: 'flex', flexDirection: 'column',
            padding: '20px 16px',
            animation: 'fadeIn 0.2s ease',
          }}
        >
          {NAV_LINKS.map(link => (
            <Link
              key={link.path}
              to={link.path}
              className={`nav-link ${isActive(link.path) ? 'active' : ''}`}
              style={{
                padding: '14px 16px', borderRadius: 10,
                fontSize: '1rem', marginBottom: 4,
              }}
            >
              <span style={{ fontSize: '1rem' }}>{link.icon}</span>
              {link.label}
            </Link>
          ))}
          <hr style={{ border: 'none', height: 1, background: 'var(--border)', margin: '16px 0' }} />
          <div style={{ marginBottom: 16 }}>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Accent Color
            </p>
            <ThemePicker />
          </div>
          <button
            onClick={handleLogout}
            className="btn btn-ghost"
            style={{ justifyContent: 'flex-start', gap: 10 }}
          >
            ↗ Log out
          </button>
        </div>
      )}
    </>
  )
}
