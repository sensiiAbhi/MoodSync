import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const FEATURES = [
  { icon: '🧠', title: 'Mood Classification', desc: 'Deep psychological profiling across 7 dimensions mapped to Russell\'s Circumplex Model.' },
  { icon: '🎯', title: 'Context-Aware AI', desc: 'ISO Principle-based recommendation engine that matches your mood, then guides you to your goal.' },
  { icon: '📊', title: 'Behavioral Analytics', desc: 'Track mood trends, listening patterns, and recommendation effectiveness over time.' },
  { icon: '🎵', title: 'Audio Feature Analysis', desc: 'Every recommendation backed by Spotify audio features — BPM, energy, valence, instrumentalness.' },
  { icon: '🔄', title: 'Adaptive Learning', desc: 'Rate sessions and the system personalizes algorithm weights to your preferences.' },
  { icon: '🔒', title: 'Privacy First', desc: 'GDPR-compliant, your psychological data stays yours. Export or delete anytime.' },
]

const MOODS = [
  { mood: 'Stressed', color: '#EF4444', activity: 'Studying', recommendation: 'Classical · Lo-Fi · 70 BPM · Instrumental' },
  { mood: 'Energetic', color: '#F59E0B', activity: 'Gym Workout', recommendation: 'Hip-Hop · Electronic · 135 BPM · High Energy' },
  { mood: 'Burned Out', color: '#6B7280', activity: 'Relaxing', recommendation: 'Jazz · Acoustic · 72 BPM · Soothing' },
  { mood: 'Focused', color: '#3B82F6', activity: 'Coding', recommendation: 'Neo-Classical · Post-Rock · 85 BPM · Instrumental' },
  { mood: 'Anxious', color: '#F97316', activity: 'Meditation', recommendation: 'Ambient · Drone · 58 BPM · Nature Sounds' },
  { mood: 'Motivated', color: '#10B981', activity: 'Running', recommendation: 'Power-Pop · Electronic · 128 BPM · Upbeat' },
]

export default function LandingPage() {
  return (
    <div style={{ minHeight: '100vh', overflowX: 'hidden' }}>
      {/* ── Hero ── */}
      <section style={{
        minHeight: '100vh',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        padding: '80px 24px',
        position: 'relative',
        textAlign: 'center',
      }}>
        {/* Background glow */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at 50% 30%, rgba(124,58,237,0.2) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        {/* Floating orbs */}
        <div style={{
          position: 'absolute', top: '15%', left: '8%',
          width: 300, height: 300,
          background: 'radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%)',
          borderRadius: '50%', animation: 'float 6s ease-in-out infinite',
        }} />
        <div style={{
          position: 'absolute', bottom: '20%', right: '8%',
          width: 200, height: 200,
          background: 'radial-gradient(circle, rgba(14,165,233,0.12) 0%, transparent 70%)',
          borderRadius: '50%', animation: 'float 8s ease-in-out infinite reverse',
        }} />

        <div style={{ position: 'relative', maxWidth: 800 }}>
          <div className="badge badge-primary" style={{ marginBottom: 24, fontSize: '0.75rem' }}>
            🎓 Final Year CS Project · Production-Grade Platform
          </div>

          <h1 style={{
            fontFamily: 'var(--font-heading)', fontWeight: 800,
            fontSize: 'clamp(2.5rem, 6vw, 4.5rem)',
            lineHeight: 1.1, marginBottom: 24,
            background: 'linear-gradient(135deg, #F1F5F9 0%, #A78BFA 50%, #38BDF8 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            Music That Understands<br />Your Psychology
          </h1>

          <p style={{
            fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
            color: 'var(--text-secondary)',
            marginBottom: 40, lineHeight: 1.7, maxWidth: 640, margin: '0 auto 40px',
          }}>
            MoodSync doesn't just track what you listen to — it understands <em>how you feel</em> and recommends music to help you achieve your goals. Powered by psychology, not just history.
          </p>

          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/register" className="btn btn-primary btn-lg">
              ✦ Start Your Journey Free
            </Link>
            <Link to="/login" className="btn btn-ghost btn-lg">
              Sign In
            </Link>
          </div>

          {/* Stats */}
          <div style={{
            display: 'flex', justifyContent: 'center', gap: 48,
            marginTop: 64, flexWrap: 'wrap',
          }}>
            {[
              { n: '9', label: 'Mood States' },
              { n: '12', label: 'Activities' },
              { n: '3-Score', label: 'Ranking Engine' },
              { n: 'ISO', label: 'Principle' },
            ].map(s => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{
                  fontFamily: 'var(--font-heading)', fontWeight: 800,
                  fontSize: '2rem', color: 'var(--primary-light)',
                }}>{s.n}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section style={{ padding: '80px 24px', maxWidth: 1280, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <h2 style={{ marginBottom: 16 }}>How MoodSync Works</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: 560, margin: '0 auto' }}>
            A 3-step psychological process that replaces "what did you listen to" with "how do you feel and what do you need."
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 32 }}>
          {[
            {
              step: '01', icon: '🧠',
              title: 'Psychological Assessment',
              desc: 'Answer 7 questions about your energy, stress, focus, motivation, sleep, fatigue, and social mood. Takes under 2 minutes.',
              color: '#7C3AED',
            },
            {
              step: '02', icon: '🎯',
              title: 'Context Fusion',
              desc: 'Select your activity (studying, gym, sleep...) and desired outcome. Our ISO Principle engine builds your personalized music profile.',
              color: '#0EA5E9',
            },
            {
              step: '03', icon: '✦',
              title: 'Smart Recommendations',
              desc: 'Spotify tracks ranked by Mood Alignment Score, Historical Effectiveness, and Personal Preference. With explanations for each track.',
              color: '#EC4899',
            },
          ].map(step => (
            <div key={step.step} className="card" style={{ position: 'relative', paddingTop: 32 }}>
              <div style={{
                position: 'absolute', top: -20, left: 24,
                background: step.color,
                borderRadius: 10, width: 44, height: 44,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.25rem', boxShadow: `0 4px 16px ${step.color}40`,
              }}>
                {step.icon}
              </div>
              <div style={{ color: step.color, fontWeight: 800, fontSize: '0.7rem', letterSpacing: '0.1em', marginBottom: 8 }}>
                STEP {step.step}
              </div>
              <h4 style={{ marginBottom: 12 }}>{step.title}</h4>
              <p style={{ fontSize: '0.9rem', lineHeight: 1.6 }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Mood × Activity Matrix ── */}
      <section style={{
        padding: '80px 24px', maxWidth: 1280, margin: '0 auto',
        background: 'rgba(255,255,255,0.02)',
        borderRadius: 'var(--radius-2xl)', marginBottom: 32,
      }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <h2 style={{ marginBottom: 16 }}>Mood × Activity Intelligence</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: 520, margin: '0 auto' }}>
            Every combination generates a unique music profile. Here's how the engine thinks:
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
          {MOODS.map(m => (
            <div key={m.mood} style={{
              background: 'var(--bg-card)',
              border: `1px solid ${m.color}30`,
              borderRadius: 'var(--radius-lg)',
              padding: '20px 24px',
              display: 'flex', flexDirection: 'column', gap: 12,
              transition: 'all 0.25s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = `${m.color}60`; e.currentTarget.style.transform = 'translateY(-4px)' }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = `${m.color}30`; e.currentTarget.style.transform = 'translateY(0)' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{
                  background: `${m.color}20`, color: m.color,
                  border: `1px solid ${m.color}40`,
                  padding: '4px 12px', borderRadius: 99,
                  fontSize: '0.8rem', fontWeight: 700,
                }}>{m.mood}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>+ {m.activity}</span>
              </div>
              <div style={{
                fontSize: '0.85rem', color: 'var(--text-secondary)',
                background: 'rgba(255,255,255,0.03)',
                padding: '8px 12px', borderRadius: 8,
                fontFamily: 'monospace', letterSpacing: '0.02em',
              }}>
                → {m.recommendation}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section style={{ padding: '80px 24px', maxWidth: 1280, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <h2 style={{ marginBottom: 16 }}>Built for Production</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: 520, margin: '0 auto' }}>
            FastAPI · PostgreSQL · Scikit-Learn · React · Docker — engineered to professional standards.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 24 }}>
          {FEATURES.map(f => (
            <div key={f.title} className="card">
              <div style={{ fontSize: '2rem', marginBottom: 16 }}>{f.icon}</div>
              <h4 style={{ marginBottom: 8 }}>{f.title}</h4>
              <p style={{ fontSize: '0.9rem', lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{
        padding: '80px 24px', textAlign: 'center',
        background: 'linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(14,165,233,0.1) 100%)',
        margin: '0 24px 40px', borderRadius: 'var(--radius-2xl)',
        border: '1px solid rgba(124,58,237,0.2)',
      }}>
        <h2 style={{ marginBottom: 16, maxWidth: 600, margin: '0 auto 16px' }}>
          Ready to discover music that actually matches how you feel?
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 40 }}>
          Join MoodSync and let psychology guide your playlist.
        </p>
        <Link to="/register" className="btn btn-primary btn-lg">
          ✦ Get Started — It's Free
        </Link>
      </section>

      {/* ── Footer ── */}
      <footer style={{
        textAlign: 'center', padding: '32px 24px',
        color: 'var(--text-muted)', fontSize: '0.8rem',
        borderTop: '1px solid var(--border)',
      }}>
        <p>MoodSync © 2026 · Context-Aware Psychological Music Recommendation Platform</p>
        <p style={{ marginTop: 8 }}>
          Built with FastAPI · PostgreSQL · Scikit-Learn · React · Spotify API
        </p>
      </footer>
    </div>
  )
}
