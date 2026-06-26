import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { analyticsApi, moodApi } from '../api'
import toast from 'react-hot-toast'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts'

const MOOD_EMOJI = {
  stressed: '😰', anxious: '😟', burned_out: '😔', sleepy: '😴',
  energetic: '⚡', motivated: '🔥', calm: '😌', focused: '🎯', relaxed: '😎',
}
const MOOD_COLOR = {
  stressed: '#EF4444', anxious: '#F97316', burned_out: '#6B7280',
  sleepy: '#8B5CF6', energetic: '#F59E0B', motivated: '#10B981',
  calm: '#06B6D4', focused: '#3B82F6', relaxed: '#84CC16',
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [dashboard, setDashboard] = useState(null)
  const [trendData, setTrendData] = useState([])
  const [currentMood, setCurrentMood] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [dashRes, trendRes] = await Promise.all([
        analyticsApi.getDashboard(),
        moodApi.getTrends(30),
      ])
      setDashboard(dashRes.data)
      setTrendData(trendRes.data.data_points || [])
    } catch (err) {
      console.error('Dashboard load error:', err)
    }

    try {
      const moodRes = await moodApi.getCurrent()
      setCurrentMood(moodRes.data)
    } catch {}

    setLoading(false)
  }

  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  if (loading) {
    return (
      <div className="page-layout" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="spinner spinner-lg" style={{ margin: '0 auto 16px' }} />
          <p>Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  const mood = dashboard?.mood_summary
  const listening = dashboard?.listening_summary
  const effectiveness = dashboard?.recommendation_effectiveness
  const activityDist = dashboard?.activity_distribution || {}

  return (
    <div className="page-layout">
      <div className="main-content">
        {/* ── Header ── */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 40, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 style={{ fontSize: '2rem', marginBottom: 6 }}>
              {greeting()}, {user?.username || 'friend'} 👋
            </h1>
            <p style={{ color: 'var(--text-muted)' }}>
              {currentMood
                ? `Your current mood: ${MOOD_EMOJI[currentMood.primary_mood] || '🎵'} ${currentMood.primary_mood?.charAt(0).toUpperCase() + currentMood.primary_mood?.slice(1)}`
                : 'No mood check-in today yet'}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <Link to="/app/assess" className="btn btn-primary">
              ◉ Check In Now
            </Link>
            <Link to="/app/recommend" className="btn btn-secondary">
              ✦ Get Music
            </Link>
          </div>
        </div>

        {/* ── KPI Cards ── */}
        <div className="grid-4" style={{ marginBottom: 40 }}>
          {[
            {
              icon: '◉', label: 'Check-ins (30d)',
              value: mood?.total_assessments || 0,
              color: '#7C3AED',
            },
            {
              icon: '🎵', label: 'Sessions',
              value: listening?.total_sessions || 0,
              color: '#0EA5E9',
            },
            {
              icon: '⭐', label: 'Avg Rating',
              value: effectiveness?.avg_rating ? effectiveness.avg_rating.toFixed(1) + '/5' : 'N/A',
              color: '#F59E0B',
            },
            {
              icon: '🔥', label: 'Streak',
              value: (dashboard?.streaks?.current_streak || 0) + ' days',
              color: '#EC4899',
            },
          ].map(kpi => (
            <div key={kpi.label} className="kpi-card">
              <div className="kpi-icon" style={{ background: `${kpi.color}20` }}>
                <span style={{ fontSize: '1.25rem' }}>{kpi.icon}</span>
              </div>
              <div className="kpi-value">{kpi.value}</div>
              <div className="kpi-label">{kpi.label}</div>
            </div>
          ))}
        </div>

        {/* ── Main Grid ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24, marginBottom: 32 }}>
          {/* Mood Trend Chart */}
          <div className="card">
            <div className="section-header" style={{ marginBottom: 24 }}>
              <div>
                <div className="section-title">Mood Trend (30 days)</div>
                <div className="section-subtitle">Wellbeing & stress over time</div>
              </div>
            </div>
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={trendData.slice(-14)} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="wellbeingGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#7C3AED" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="stressGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748B' }}
                    tickFormatter={d => d.slice(5)} />
                  <YAxis tick={{ fontSize: 10, fill: '#64748B' }} domain={[0, 10]} />
                  <Tooltip
                    contentStyle={{ background: '#1A1A35', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12 }}
                    labelStyle={{ color: '#F1F5F9', fontSize: 12 }}
                    itemStyle={{ fontSize: 12 }}
                  />
                  <Area type="monotone" dataKey="wellbeing" stroke="#7C3AED" fill="url(#wellbeingGrad)"
                    name="Wellbeing" strokeWidth={2} dot={false} />
                  <Area type="monotone" dataKey="stress" stroke="#EF4444" fill="url(#stressGrad)"
                    name="Stress" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12 }}>
                <span style={{ fontSize: '2.5rem' }}>📊</span>
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', fontSize: '0.9rem' }}>
                  Complete mood check-ins to see your trend chart
                </p>
                <Link to="/app/assess" className="btn btn-primary btn-sm">Take First Check-In</Link>
              </div>
            )}
          </div>

          {/* Mood Distribution */}
          <div className="card">
            <div className="section-title" style={{ marginBottom: 20 }}>Mood Distribution</div>
            {mood?.dominant_mood && mood.dominant_mood !== 'unknown' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {Object.entries(mood.mood_distribution || {})
                  .sort(([,a],[,b]) => b - a)
                  .slice(0, 6)
                  .map(([m, pct]) => (
                    <div key={m}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 6 }}>
                          {MOOD_EMOJI[m]} <span style={{ textTransform: 'capitalize' }}>{m.replace('_', ' ')}</span>
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {(pct * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="progress-bar" style={{ height: 4 }}>
                        <div style={{
                          height: '100%', borderRadius: 99,
                          background: MOOD_COLOR[m] || 'var(--primary)',
                          width: `${pct * 100}%`,
                          transition: 'width 0.8s ease',
                        }} />
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '32px 0' }}>
                <span style={{ fontSize: '2.5rem', display: 'block', marginBottom: 8 }}>🧠</span>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Check in daily to see your mood patterns
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ── Activity Distribution + Quick Actions ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          {/* Activity Distribution */}
          <div className="card">
            <div className="section-title" style={{ marginBottom: 20 }}>Activity Distribution</div>
            {Object.keys(activityDist).length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {Object.entries(activityDist)
                  .sort(([,a],[,b]) => b - a)
                  .slice(0, 5)
                  .map(([act, pct]) => (
                    <div key={act} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{
                        flex: 1, height: 32, borderRadius: 8,
                        background: `linear-gradient(90deg, rgba(14,165,233,0.3) ${pct*100}%, rgba(255,255,255,0.03) ${pct*100}%)`,
                        display: 'flex', alignItems: 'center', padding: '0 12px',
                        fontSize: '0.8rem', textTransform: 'capitalize',
                      }}>
                        {act.replace('_', ' ')}
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', width: 36, textAlign: 'right' }}>
                        {(pct * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '24px 0' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Generate playlists for different activities to see your distribution
                </p>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="card">
            <div className="section-title" style={{ marginBottom: 20 }}>Quick Actions</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                { icon: '◉', label: 'Mood Check-In', desc: 'How are you feeling right now?', to: '/app/assess', color: '#7C3AED' },
                { icon: '✦', label: 'Get Music', desc: 'Find tracks for your current goal', to: '/app/recommend', color: '#0EA5E9' },
                { icon: '📊', label: 'Analytics', desc: 'View your mood & listening trends', to: '/app/analytics', color: '#10B981' },
                { icon: '♪', label: 'My Playlists', desc: 'Saved session playlists', to: '/app/playlists', color: '#F59E0B' },
              ].map(action => (
                <Link
                  key={action.label}
                  to={action.to}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 14,
                    padding: '12px 16px',
                    background: 'rgba(255,255,255,0.03)',
                    border: `1px solid ${action.color}20`,
                    borderRadius: 12, textDecoration: 'none',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = `${action.color}12`; e.currentTarget.style.borderColor = `${action.color}40` }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.03)'; e.currentTarget.style.borderColor = `${action.color}20` }}
                >
                  <div style={{
                    width: 36, height: 36, borderRadius: 8,
                    background: `${action.color}20`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1rem', flexShrink: 0,
                  }}>{action.icon}</div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>{action.label}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{action.desc}</div>
                  </div>
                  <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '1rem' }}>→</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
