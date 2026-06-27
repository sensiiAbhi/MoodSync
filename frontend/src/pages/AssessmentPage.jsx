import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { moodApi } from '../api'
import toast from 'react-hot-toast'

const QUESTIONS = [
  {
    id: 'language_preference', label: 'Language Preference',
    desc: 'What language of songs do you want to listen to?',
    emoji: '🌍',
    type: 'select',
    options: ['English', 'Hindi', 'Japanese', 'Any'],
  },
  {
    id: 'energy_level', label: 'Energy Level',
    desc: 'How energetic do you feel right now?',
    emoji: '⚡',
    lowLabel: 'Completely exhausted', highLabel: 'Bursting with energy',
  },
  {
    id: 'stress_level', label: 'Stress Level',
    desc: 'How stressed or overwhelmed are you feeling?',
    emoji: '😰',
    lowLabel: 'Completely calm', highLabel: 'Extremely stressed',
  },
  {
    id: 'focus_level', label: 'Focus Level',
    desc: 'How well are you able to concentrate?',
    emoji: '🎯',
    lowLabel: 'Very scattered', highLabel: 'Laser focused',
  },
  {
    id: 'motivation_level', label: 'Motivation',
    desc: 'How motivated do you feel to get things done?',
    emoji: '🔥',
    lowLabel: 'No motivation', highLabel: 'Highly driven',
  },
  {
    id: 'sleep_quality', label: 'Sleep Quality',
    desc: 'How well did you sleep last night?',
    emoji: '😴',
    lowLabel: 'Terrible sleep', highLabel: 'Excellent sleep',
  },
  {
    id: 'mental_fatigue', label: 'Mental Fatigue',
    desc: 'How mentally tired or burned out do you feel?',
    emoji: '🧠',
    lowLabel: 'Completely fresh', highLabel: 'Totally burned out',
  },
  {
    id: 'social_mood', label: 'Social Mood',
    desc: 'How do you feel about connecting with others?',
    emoji: '💬',
    lowLabel: 'Want to be alone', highLabel: 'Very sociable',
  },
]

const MOOD_COLORS = {
  stressed: '#EF4444', anxious: '#F97316', burned_out: '#6B7280',
  sleepy: '#8B5CF6', energetic: '#F59E0B', motivated: '#10B981',
  calm: '#06B6D4', focused: '#3B82F6', relaxed: '#84CC16',
}
const MOOD_EMOJI = {
  stressed: '😰', anxious: '😟', burned_out: '😔', sleepy: '😴',
  energetic: '⚡', motivated: '🔥', calm: '😌', focused: '🎯', relaxed: '😎',
}

export default function AssessmentPage() {
  const navigate = useNavigate()
  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const currentQuestion = QUESTIONS[currentQ]
  const progress = ((currentQ) / QUESTIONS.length) * 100

  const handleSliderChange = (value) => {
    setAnswers(prev => ({ ...prev, [currentQuestion.id]: parseInt(value) }))
  }

  const handleNext = async () => {
    if (!(currentQuestion.id in answers)) {
      setAnswers(prev => ({ ...prev, [currentQuestion.id]: currentQuestion.type === 'select' ? currentQuestion.options[0] : 5 }))
    }

    if (currentQ < QUESTIONS.length - 1) {
      setCurrentQ(currentQ + 1)
    } else {
      // Submit assessment
      const finalAnswers = { ...answers }
      if (!(currentQuestion.id in finalAnswers)) {
        finalAnswers[currentQuestion.id] = currentQuestion.type === 'select' ? currentQuestion.options[0] : 5
      }
      await submitAssessment(finalAnswers)
    }
  }

  const handleBack = () => {
    if (currentQ > 0) setCurrentQ(currentQ - 1)
  }

  const submitAssessment = async (data) => {
    setLoading(true)
    try {
      const payload = {
        language_preference: data.language_preference || 'English',
        energy_level: data.energy_level || 5,
        stress_level: data.stress_level || 5,
        focus_level: data.focus_level || 5,
        motivation_level: data.motivation_level || 5,
        sleep_quality: data.sleep_quality || 5,
        mental_fatigue: data.mental_fatigue || 5,
        social_mood: data.social_mood || 5,
        assessment_type: 'full',
      }
      const res = await moodApi.submitAssessment(payload)
      setResult(res.data)
      toast.success('Assessment complete! 🧠')
    } catch (err) {
      toast.error('Failed to save assessment')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const currentValue = answers[currentQuestion?.id] ?? (currentQuestion?.type === 'select' ? currentQuestion.options[0] : 5)

  // ── Result Screen ──
  if (result) {
    const moodColor = MOOD_COLORS[result.primary_mood] || 'var(--primary)'
    const moodEmoji = MOOD_EMOJI[result.primary_mood] || '🎵'

    return (
      <div className="page-layout">
        <div className="main-content" style={{ maxWidth: 680, margin: '0 auto' }}>
          <div className="card animate-fade-in" style={{
            textAlign: 'center', padding: 48,
            border: `1px solid ${moodColor}30`,
          }}>
            {/* Mood Badge */}
            <div style={{
              width: 96, height: 96, borderRadius: '50%',
              background: `${moodColor}20`, border: `2px solid ${moodColor}40`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '3rem', margin: '0 auto 24px',
              boxShadow: `0 0 30px ${moodColor}30`,
            }}>
              {moodEmoji}
            </div>

            <div style={{
              display: 'inline-block', background: `${moodColor}20`,
              border: `1px solid ${moodColor}40`, color: moodColor,
              padding: '6px 20px', borderRadius: 99, fontWeight: 700,
              fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em',
              marginBottom: 20,
            }}>
              {result.primary_mood?.replace('_', ' ')}
            </div>

            <h2 style={{ marginBottom: 12 }}>Assessment Complete</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 32, lineHeight: 1.7 }}>
              {result.mood_description}
            </p>

            {/* Stats Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
              {[
                { label: 'Valence', value: ((result.mood_valence + 1) / 2 * 100).toFixed(0) + '%', desc: 'Positivity' },
                { label: 'Arousal', value: (result.mood_arousal * 100).toFixed(0) + '%', desc: 'Energy State' },
                { label: 'Wellbeing', value: result.wellbeing_score?.toFixed(0) + '/100', desc: 'Score' },
              ].map(stat => (
                <div key={stat.label} style={{
                  background: 'rgba(255,255,255,0.04)', borderRadius: 12,
                  padding: '16px 12px', border: '1px solid rgba(255,255,255,0.06)',
                }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: moodColor }}>{stat.value}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>{stat.desc}</div>
                </div>
              ))}
            </div>

            <p style={{
              fontSize: '0.9rem', color: 'var(--text-secondary)',
              background: 'rgba(255,255,255,0.03)', borderRadius: 12,
              padding: '14px 20px', marginBottom: 32,
              border: '1px solid rgba(255,255,255,0.06)',
            }}>
              💡 {result.recommended_next_step}
            </p>

            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                className="btn btn-primary btn-lg"
                onClick={() => navigate('/app/recommend', { state: { assessmentId: result.assessment_id, mood: result.primary_mood, language: answers.language_preference || 'English' } })}
              >
                ✦ Get Music for My Mood
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => navigate('/app/dashboard')}
              >
                Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // ── Assessment Questions ──
  return (
    <div className="page-layout">
      <div className="main-content" style={{ maxWidth: 680, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <h1 style={{ marginBottom: 8 }}>Mood Check-In</h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Question {currentQ + 1} of {QUESTIONS.length} · Takes about 2 minutes
          </p>
        </div>

        {/* Progress Bar */}
        <div className="progress-bar" style={{ marginBottom: 40, height: 8 }}>
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>

        {/* Question Card */}
        <div className="card" style={{ padding: 48, textAlign: 'center' }}>
          <div style={{ fontSize: '3.5rem', marginBottom: 20 }}>
            {currentQuestion.emoji}
          </div>

          <h3 style={{ marginBottom: 8 }}>{currentQuestion.label}</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 40, fontSize: '0.95rem' }}>
            {currentQuestion.desc}
          </p>

          {currentQuestion.type === 'select' ? (
            <div style={{ padding: '0 24px', marginBottom: 40 }}>
              <select
                value={currentValue}
                onChange={(e) => setAnswers(prev => ({ ...prev, [currentQuestion.id]: e.target.value }))}
                style={{
                  width: '100%', padding: '16px', borderRadius: '12px',
                  background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
                  color: 'white', fontSize: '1.2rem', outline: 'none',
                }}
              >
                {currentQuestion.options.map(opt => (
                  <option key={opt} value={opt} style={{ background: '#1e1e24', color: 'white' }}>{opt}</option>
                ))}
              </select>
            </div>
          ) : (
            <>
              {/* Score Display */}
              <div style={{
                fontSize: '4rem', fontWeight: 800,
                fontFamily: 'var(--font-heading)',
                background: 'var(--gradient-primary)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                marginBottom: 24, lineHeight: 1,
              }}>
                {currentValue}
              </div>

              {/* Slider */}
              <div style={{ padding: '0 8px', marginBottom: 16 }}>
                <input
                  type="range"
                  min={1} max={10} step={1}
                  value={currentValue}
                  onChange={e => handleSliderChange(e.target.value)}
                  style={{
                    background: `linear-gradient(90deg, var(--primary) ${(currentValue - 1) / 9 * 100}%, rgba(255,255,255,0.1) ${(currentValue - 1) / 9 * 100}%)`,
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 40 }}>
                <span>1 · {currentQuestion.lowLabel}</span>
                <span>{currentQuestion.highLabel} · 10</span>
              </div>

              {/* Scale Reference */}
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 4, marginBottom: 40 }}>
                {[1,2,3,4,5,6,7,8,9,10].map(n => (
                  <button
                    key={n}
                    onClick={() => handleSliderChange(n)}
                    style={{
                      width: 32, height: 32, borderRadius: '50%',
                      background: n === currentValue ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                      border: n === currentValue ? 'none' : '1px solid rgba(255,255,255,0.08)',
                      color: n === currentValue ? 'white' : 'var(--text-muted)',
                      fontSize: '0.75rem', fontWeight: 600,
                      cursor: 'pointer', transition: 'all 0.15s ease',
                      boxShadow: n === currentValue ? '0 0 12px rgba(124,58,237,0.5)' : 'none',
                    }}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Navigation */}
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
            {currentQ > 0 && (
              <button className="btn btn-ghost" onClick={handleBack}>← Back</button>
            )}
            <button
              className="btn btn-primary btn-lg"
              onClick={handleNext}
              disabled={loading}
              style={{ minWidth: 180 }}
            >
              {loading ? (
                <><div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Processing...</>
              ) : currentQ === QUESTIONS.length - 1 ? '🧠 Analyze My Mood' : 'Next →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
