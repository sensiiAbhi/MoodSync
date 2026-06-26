import { useState, useEffect } from 'react'
import { analyticsApi, moodApi, feedbackApi } from '../api'
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'

const MOOD_COLOR = {
  stressed: '#EF4444', anxious: '#F97316', burned_out: '#6B7280',
  sleepy: '#8B5CF6', energetic: '#F59E0B', motivated: '#10B981',
  calm: '#06B6D4', focused: '#3B82F6', relaxed: '#84CC16',
}
const PIE_COLORS = Object.values(MOOD_COLOR)

export default function AnalyticsPage() {
  const [dashboard, setDashboard] = useState(null)
  const [trends, setTrends] = useState({ data_points: [] })
  const [effectiveness, setEffectiveness] = useState(null)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState(30)

  useEffect(() => { loadAll() }, [period])

  const loadAll = async () => {
    setLoading(true)
    try {
      const [dashRes, trendRes, effectRes] = await Promise.all([
        analyticsApi.getDashboard(),
        moodApi.getTrends(period),
        feedbackApi.getEffectiveness(),
      ])
      setDashboard(dashRes.data)
      setTrends(trendRes.data)
      setEffectiveness(effectRes.data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  if (loading) {
    return (
      <div className="page-layout" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spinner spinner-lg" />
      </div>
    )
  }

  const mood = dashboard?.mood_summary || {}
  const moodDist = mood.mood_distribution || {}
  const pieData = Object.entries(moodDist).map(([name, value]) => ({
    name: name.replace('_', ' '), value: Math.round(value * 100)
  }))

  const trendPoints = trends.data_points || []
  const avgStress = mood.avg_stress || 0
  const avgEnergy = mood.avg_energy || 0

  return (
    <div className="page-layout">
      <div className="main-content">
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 40, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 style={{ marginBottom: 8 }}>Analytics</h1>
            <p style={{ color: 'var(--text-muted)' }}>Your mood patterns and recommendation effectiveness</p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {[7, 30, 90].map(d => (
              <button
                key={d}
                className={`btn btn-sm ${period === d ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setPeriod(d)}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>

        {/* KPI Row */}
        <div className="grid-4" style={{ marginBottom: 32 }}>
          {[
            { icon: '◉', label: 'Assessments', value: mood.total_assessments || 0, color: '#7C3AED' },
            { icon: '😌', label: 'Dominant Mood', value: (mood.dominant_mood || '—').replace('_', ' '), color: MOOD_COLOR[mood.dominant_mood] || '#7C3AED' },
            { icon: '⭐', label: 'Avg Rating', value: effectiveness?.avg_rating ? effectiveness.avg_rating.toFixed(1) + '/5' : '—', color: '#F59E0B' },
            { icon: '🎯', label: 'Goal Success', value: effectiveness?.goal_achievement_rate ? (effectiveness.goal_achievement_rate * 100).toFixed(0) + '%' : '—', color: '#10B981' },
          ].map(kpi => (
            <div key={kpi.label} className="kpi-card">
              <div className="kpi-icon" style={{ background: `${kpi.color}20` }}>
                <span style={{ fontSize: '1.25rem' }}>{kpi.icon}</span>
              </div>
              <div className="kpi-value" style={{ fontSize: '1.75rem', textTransform: 'capitalize' }}>{kpi.value}</div>
              <div className="kpi-label">{kpi.label}</div>
            </div>
          ))}
        </div>

        {/* Main Charts */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24, marginBottom: 32 }}>
          {/* Wellbeing Timeline */}
          <div className="card">
            <div className="section-title" style={{ marginBottom: 20 }}>Wellbeing & Stress Timeline</div>
            {trendPoints.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={trendPoints} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="wbGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#7C3AED" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="stGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748B' }} tickFormatter={d => d.slice(5)} />
                  <YAxis tick={{ fontSize: 10, fill: '#64748B' }} domain={[0, 10]} />
                  <Tooltip
                    contentStyle={{ background: '#1A1A35', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }}
                    labelStyle={{ color: '#F1F5F9' }}
                  />
                  <Area type="monotone" dataKey="wellbeing" stroke="#7C3AED" fill="url(#wbGrad)" name="Wellbeing" strokeWidth={2} dot={false} />
                  <Area type="monotone" dataKey="stress" stroke="#EF4444" fill="url(#stGrad)" name="Stress" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: 'var(--text-muted)' }}>No data yet — complete some mood check-ins</p>
              </div>
            )}
          </div>

          {/* Mood Pie */}
          <div className="card">
            <div className="section-title" style={{ marginBottom: 16 }}>Mood Distribution</div>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={230}>
                <PieChart>
                  <Pie
                    data={pieData} dataKey="value" nameKey="name"
                    cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                    paddingAngle={3}
                  >
                    {pieData.map((entry, i) => (
                      <Cell key={i} fill={MOOD_COLOR[entry.name.replace(' ', '_')] || PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: '#1A1A35', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }}
                    formatter={v => `${v}%`}
                  />
                  <Legend iconSize={8} iconType="circle" wrapperStyle={{ fontSize: 11, color: '#94A3B8' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 230, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', fontSize: '0.85rem' }}>No mood data yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Energy & Focus Chart */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32 }}>
          <div className="card">
            <div className="section-title" style={{ marginBottom: 20 }}>Energy & Focus Over Time</div>
            {trendPoints.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={trendPoints} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748B' }} tickFormatter={d => d.slice(5)} />
                  <YAxis tick={{ fontSize: 10, fill: '#64748B' }} domain={[1, 10]} />
                  <Tooltip contentStyle={{ background: '#1A1A35', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }} />
                  <Line type="monotone" dataKey="energy" stroke="#F59E0B" name="Energy" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="focus" stroke="#0EA5E9" name="Focus" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No data yet</p>
              </div>
            )}
          </div>

          {/* Effectiveness Summary */}
          <div className="card">
            <div className="section-title" style={{ marginBottom: 20 }}>Recommendation Effectiveness</div>
            {effectiveness && effectiveness.sessions_rated > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {[
                  { label: 'Avg Rating', value: effectiveness.avg_rating?.toFixed(1), max: 5, unit: '/5', color: '#F59E0B' },
                  { label: 'Goal Achievement', value: (effectiveness.goal_achievement_rate * 100).toFixed(0), max: 100, unit: '%', color: '#10B981' },
                  { label: 'Mood Improvement', value: (effectiveness.mood_improvement_rate * 100).toFixed(0), max: 100, unit: '%', color: '#7C3AED' },
                ].map(m => (
                  <div key={m.label}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: '0.85rem' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>{m.label}</span>
                      <span style={{ fontWeight: 700, color: m.color }}>{m.value}{m.unit}</span>
                    </div>
                    <div className="progress-bar">
                      <div style={{
                        height: '100%', borderRadius: 99,
                        background: m.color,
                        width: `${(m.value / m.max) * 100}%`,
                        transition: 'width 0.8s ease',
                      }} />
                    </div>
                  </div>
                ))}
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 8 }}>
                  Based on {effectiveness.sessions_rated} rated sessions
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 180, flexDirection: 'column', gap: 12 }}>
                <span style={{ fontSize: '2rem' }}>⭐</span>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center' }}>
                  Rate your playlists to see effectiveness data
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Avg Metrics Summary */}
        <div className="card">
          <div className="section-title" style={{ marginBottom: 20 }}>Period Averages ({period} days)</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 20 }}>
            {[
              { label: 'Avg Stress', value: avgStress.toFixed(1) + '/10', trend: mood.avg_stress_trend, up: false },
              { label: 'Avg Energy', value: avgEnergy.toFixed(1) + '/10', trend: mood.avg_energy_trend, up: true },
            ].map(m => (
              <div key={m.label} style={{
                padding: '20px', background: 'rgba(255,255,255,0.03)',
                borderRadius: 12, border: '1px solid rgba(255,255,255,0.05)',
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>{m.value}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 6 }}>{m.label}</div>
                {m.trend && (
                  <div style={{
                    marginTop: 8, fontSize: '0.7rem', fontWeight: 600,
                    color: (m.trend === 'decreasing' && !m.up) || (m.trend === 'increasing' && m.up)
                      ? '#10B981' : m.trend === 'stable' ? '#94A3B8' : '#EF4444',
                  }}>
                    {m.trend === 'decreasing' ? '↓' : m.trend === 'increasing' ? '↑' : '→'} {m.trend}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
