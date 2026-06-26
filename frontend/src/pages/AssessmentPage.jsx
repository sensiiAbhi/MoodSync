import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { moodApi } from '../api'
import toast from 'react-hot-toast'

const QUESTIONS = [
  {
    id: 'feeling', label: 'Feeling & Goal',
    desc: 'How are you feeling right now, and how do you want to feel in 30 minutes?',
    emoji: '🧠',
    type: 'select',
    options: [
      'Anxious ➔ Calm',
      'Tired ➔ Energized',
      'Distracted ➔ Focused',
      'Stressed ➔ Relaxed',
      'Sad ➔ Uplifted',
      'Just want to vibe'
    ]
  },
  {
    id: 'activity', label: 'Activity',
    desc: 'What exactly will you be doing while listening?',
    emoji: '🎯',
    type: 'select',
    options: [
      'Deep Work / Studying',
      'Working Out',
      'Commuting',
      'Relaxing / Doing Nothing',
      'Doing Chores'
    ]
  },
  {
    id: 'attention', label: 'Attention Level',
    desc: 'On a scale from "background hum" to "front-row concert", how much of your attention will the music have?',
    emoji: '👁️',
    type: 'slider',
    lowLabel: 'Background Hum', highLabel: 'Front-Row Concert',
  },
  {
    id: 'cravings', label: 'Cravings / Avoidances',
    desc: 'Are there any specific instruments, eras, or genres you are craving right now (or absolutely want to avoid)?',
    emoji: '🎸',
    type: 'multi',
    options: [
      'Acoustic / Unplugged',
      'Heavy Bass',
      '80s Synth',
      'Lo-Fi Beats',
      'Classical / Orchestral',
      'No Vocals (Instrumental only)',
      'Upbeat Pop'
    ]
  },
  {
    id: 'familiarity', label: 'Familiarity',
    desc: 'Do you want the comfort of familiar favorites, or are you looking to discover something completely new?',
    emoji: '✨',
    type: 'select',
    options: [
      'Comfort of familiar favorites',
      'A mix of old and new',
      'Discover something completely new'
    ]
  },
]

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

  const handleSelectChange = (value) => {
    setAnswers(prev => ({ ...prev, [currentQuestion.id]: value }))
  }

  const handleMultiChange = (value) => {
    setAnswers(prev => {
      const current = prev[currentQuestion.id] || []
      const updated = current.includes(value)
        ? current.filter(item => item !== value)
        : [...current, value]
      return { ...prev, [currentQuestion.id]: updated }
    })
  }

  const handleNext = async () => {
    if (!(currentQuestion.id in answers)) {
      if (currentQuestion.type === 'slider') handleSliderChange(5)
      else if (currentQuestion.type === 'multi') handleMultiChange([])
      else handleSelectChange(currentQuestion.options[0])
    }

    if (currentQ < QUESTIONS.length - 1) {
      setCurrentQ(currentQ + 1)
    } else {
      // Submit directly to recommendations page
      const finalAnswers = { ...answers }
      navigate('/app/recommend', { state: { conversational_answers: finalAnswers } })
    }
  }

  const handleBack = () => {
    if (currentQ > 0) setCurrentQ(currentQ - 1)
  }

  const currentValue = answers[currentQuestion?.id]

  // Removed Result Screen completely, now skips straight to RecommendationPage


  // ── Result Screen ──


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

          {currentQuestion.type === 'slider' && (
            <>
              <div style={{
                fontSize: '4rem', fontWeight: 800,
                fontFamily: 'var(--font-heading)',
                background: 'var(--gradient-primary)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                marginBottom: 24, lineHeight: 1,
              }}>
                {currentValue || 5}
              </div>

              <div style={{ padding: '0 8px', marginBottom: 16 }}>
                <input
                  type="range"
                  min={1} max={10} step={1}
                  value={currentValue || 5}
                  onChange={e => handleSliderChange(e.target.value)}
                  style={{
                    background: `linear-gradient(90deg, var(--primary) ${((currentValue || 5) - 1) / 9 * 100}%, rgba(255,255,255,0.1) ${((currentValue || 5) - 1) / 9 * 100}%)`,
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 40 }}>
                <span>1 · {currentQuestion.lowLabel}</span>
                <span>{currentQuestion.highLabel} · 10</span>
              </div>
            </>
          )}

          {currentQuestion.type === 'select' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 40 }}>
              {currentQuestion.options.map(opt => (
                <button
                  key={opt}
                  onClick={() => handleSelectChange(opt)}
                  style={{
                    padding: '16px', borderRadius: 12,
                    background: currentValue === opt ? 'rgba(124,58,237,0.2)' : 'rgba(255,255,255,0.03)',
                    border: currentValue === opt ? '1px solid var(--primary)' : '1px solid rgba(255,255,255,0.1)',
                    color: currentValue === opt ? 'white' : 'var(--text-secondary)',
                    fontWeight: 600, cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  {opt}
                </button>
              ))}
            </div>
          )}

          {currentQuestion.type === 'multi' && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center', marginBottom: 40 }}>
              {currentQuestion.options.map(opt => {
                const isSelected = (currentValue || []).includes(opt)
                return (
                  <button
                    key={opt}
                    onClick={() => handleMultiChange(opt)}
                    style={{
                      padding: '12px 20px', borderRadius: 99,
                      background: isSelected ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                      border: isSelected ? 'none' : '1px solid rgba(255,255,255,0.1)',
                      color: 'white', fontWeight: 500, cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    {opt}
                  </button>
                )
              })}
            </div>
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
