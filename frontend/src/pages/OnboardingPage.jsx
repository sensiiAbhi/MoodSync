import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

const STEPS = [
  {
    id: 'welcome',
    title: 'Welcome to MoodSync 🎵',
    subtitle: 'Let\'s take 2 minutes to understand how you want to use music in your life.',
  },
  {
    id: 'profile',
    title: 'Tell us about yourself',
    subtitle: 'This helps us tailor recommendations to your lifestyle.',
  },
  {
    id: 'ready',
    title: 'You\'re all set! 🚀',
    subtitle: 'MoodSync is ready to sync with your mood.',
  },
]

const AGE_RANGES = ['Under 18', '18-24', '25-34', '35-44', '45-54', '55+']
const OCCUPATIONS = ['Student', 'Developer/Engineer', 'Creative Professional', 'Office Worker', 'Healthcare Worker', 'Other']

export default function OnboardingPage() {
  const [step, setStep] = useState(0)
  const [profile, setProfile] = useState({ age_range: '', occupation: '' })
  const navigate = useNavigate()
  const { fetchMe } = useAuthStore()

  const handleFinish = async () => {
    try {
      if (profile.age_range || profile.occupation) {
        await authApi.updateMe(profile)
      }
      await authApi.completeOnboarding()
      await fetchMe()
      toast.success('Setup complete! Let\'s find your first playlist 🎵')
      navigate('/app/assess')
    } catch {
      navigate('/app/dashboard')
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      padding: 24,
      background: 'radial-gradient(ellipse at 50% 40%, rgba(124,58,237,0.12) 0%, transparent 60%)',
    }}>
      <div style={{
        width: '100%', maxWidth: 560,
        background: 'rgba(26,26,53,0.85)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 'var(--radius-2xl)',
        padding: 48,
        backdropFilter: 'blur(24px)',
      }}>
        {/* Progress */}
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Step {step + 1} of {STEPS.length}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--primary-light)' }}>
              {Math.round(((step + 1) / STEPS.length) * 100)}%
            </span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${((step + 1) / STEPS.length) * 100}%` }} />
          </div>
        </div>

        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <h2 style={{ marginBottom: 12 }}>{STEPS[step].title}</h2>
          <p style={{ color: 'var(--text-secondary)' }}>{STEPS[step].subtitle}</p>
        </div>

        {/* Step Content */}
        {step === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              { icon: '🧠', text: 'Assess your mood in under 2 minutes with 7 questions' },
              { icon: '🎯', text: 'Select your activity and what outcome you want to achieve' },
              { icon: '✦', text: 'Get 20–30 high-quality music tracks perfectly matched to your psychological state' },
              { icon: '📊', text: 'Track how music affects your mood and productivity over time' },
            ].map(item => (
              <div key={item.text} style={{
                display: 'flex', alignItems: 'center', gap: 16,
                padding: '16px 20px',
                background: 'rgba(124,58,237,0.07)',
                border: '1px solid rgba(124,58,237,0.15)',
                borderRadius: 'var(--radius-lg)',
              }}>
                <span style={{ fontSize: '1.5rem' }}>{item.icon}</span>
                <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{item.text}</span>
              </div>
            ))}
          </div>
        )}

        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div>
              <label className="form-label" style={{ marginBottom: 12, display: 'block' }}>
                What's your age range? (optional)
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {AGE_RANGES.map(age => (
                  <button
                    key={age}
                    className={`btn ${profile.age_range === age ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                    onClick={() => setProfile({ ...profile, age_range: age })}
                  >
                    {age}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="form-label" style={{ marginBottom: 12, display: 'block' }}>
                What's your occupation? (optional)
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {OCCUPATIONS.map(occ => (
                  <button
                    key={occ}
                    className={`btn ${profile.occupation === occ ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                    onClick={() => setProfile({ ...profile, occupation: occ })}
                  >
                    {occ}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              { icon: '◉', label: 'Daily Check-In', desc: 'Assess your mood anytime to get fresh recommendations' },
              { icon: '✦', label: 'Discover Music', desc: 'Select your activity and get perfectly matched playlists' },
              { icon: '📊', label: 'Track Progress', desc: 'Watch how music improves your focus, energy, and mood' },
            ].map(item => (
              <div key={item.label} style={{
                display: 'flex', alignItems: 'flex-start', gap: 16,
                padding: '16px 20px',
                background: 'rgba(16,185,129,0.07)',
                border: '1px solid rgba(16,185,129,0.2)',
                borderRadius: 'var(--radius-lg)',
              }}>
                <span style={{
                  fontSize: '1.2rem', color: '#10B981',
                  background: 'rgba(16,185,129,0.15)',
                  width: 36, height: 36, borderRadius: 8,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}>{item.icon}</span>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{item.label}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Navigation */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 40, gap: 16 }}>
          {step > 0 ? (
            <button className="btn btn-ghost" onClick={() => setStep(step - 1)}>← Back</button>
          ) : <div />}

          {step < STEPS.length - 1 ? (
            <button className="btn btn-primary" onClick={() => setStep(step + 1)}>
              Continue →
            </button>
          ) : (
            <button className="btn btn-primary btn-lg" onClick={handleFinish}>
              🎵 Start My First Check-In
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
