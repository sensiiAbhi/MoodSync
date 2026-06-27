import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { moodApi } from '../api'
import toast from 'react-hot-toast'

const QUESTIONS = [
  {
    id: 'feeling', label: 'The Emotional Landscape',
    desc: 'How is your heart feeling right now, and where would you like the music to take you?',
    emoji: '🌅',
    type: 'select',
    options: [
      'Ground me. I\'m overwhelmed and need peace.',
      'Uplift me. I\'m feeling heavy and need some light.',
      'Energize me. I\'m drained and need momentum.',
      'Focus me. I\'m scattered and need clarity.',
      'Float with me. I just want to vibe with the current.'
    ]
  },
  {
    id: 'activity', label: 'The Setting',
    desc: 'What is the canvas of your current moment?',
    emoji: '🗺️',
    type: 'select',
    options: [
      'Deep Dive: Immersed in focused work or study',
      'Movement: Pushing limits and breaking a sweat',
      'Journey: Commuting or traveling through the world',
      'Sanctuary: Unwinding, resting, and doing absolutely nothing',
      'Daily Rhythm: Chores and everyday routines'
    ]
  },
  {
    id: 'attention', label: 'The Immersion',
    desc: 'How deeply do you want to fall into the music?',
    emoji: '🌊',
    type: 'slider',
    lowLabel: 'A gentle breeze in the background', highLabel: 'Let it consume my entire soul',
  },
  {
    id: 'cravings', label: 'The Sonic Palette',
    desc: 'What colors or textures are you craving in your soundscape right now?',
    emoji: '🎨',
    type: 'multi',
    options: [
      'Warm & Organic (Acoustic, Earthy)',
      'Deep & Resonant (Heavy Bass, Powerful)',
      'Ethereal & Dreamy (Ambient, Atmospheric)',
      'Raw & Driving (Electric, Upbeat)',
      'Pure & Wordless (Instrumentals only)',
      'Nostalgic & Familiar (Throwbacks, Retro)'
    ]
  },
  {
    id: 'familiarity', label: 'The Journey',
    desc: 'Are we walking familiar paths, or exploring the unknown?',
    emoji: '🧭',
    type: 'select',
    options: [
      'Comforting Embrace: Only songs I already know and love',
      'Wandering: A perfect balance of old favorites and new discoveries',
      'Uncharted Territory: I want to discover completely new horizons'
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
      // Final Question -> Analyze via Gemini ML Extraction
      setLoading(true)
      try {
        const finalAnswers = { ...answers }
        const res = await moodApi.submitConversationalAssessment({
          conversational_answers: finalAnswers
        })
        setResult(res.data)
      } catch (err) {
        toast.error('Failed to analyze mood. Please try again.')
      } finally {
        setLoading(false)
      }
    }
  }

  const handleBack = () => {
    if (currentQ > 0) setCurrentQ(currentQ - 1)
  }

  const handleGetMusic = () => {
    navigate('/app/recommend', {
      state: { 
        assessmentId: result.assessment_id,
        conversational_answers: answers,
        mood: result.primary_mood
      }
    })
  }

  const currentValue = answers[currentQuestion?.id]

  // ── Result Screen ──
  if (result) {
    const isPositive = result.mood_valence >= 0
    const isHighEnergy = result.mood_arousal >= 0.5
    
    return (
      <div className="page-layout">
        <div className="main-content" style={{ maxWidth: 680, margin: '0 auto', textAlign: 'center' }}>
          
          <div style={{ marginBottom: 40 }}>
            <h1 style={{ marginBottom: 8 }}>Mood Profile Generated</h1>
            <p style={{ color: 'var(--text-secondary)' }}>Based on your answers, here is your current state</p>
          </div>

          <div className="card" style={{ padding: 48, marginBottom: 32 }}>
            <div style={{ 
              display: 'inline-block',
              padding: '16px 32px',
              borderRadius: 99,
              background: 'var(--surface)',
              border: `1px solid ${isPositive ? (isHighEnergy ? 'var(--warning)' : 'var(--success)') : 'var(--primary)'}`,
              marginBottom: 32
            }}>
              <span style={{ fontSize: '2.5rem', display: 'block', marginBottom: 8 }}>
                {isPositive ? (isHighEnergy ? '🔥' : '🌱') : (isHighEnergy ? '🌪️' : '🌧️')}
              </span>
              <h2 style={{ textTransform: 'capitalize', margin: 0, color: 'var(--text)' }}>
                {result.primary_mood.replace('_', ' ')}
              </h2>
            </div>

            <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 40 }}>
              {result.mood_description}
            </p>

            {/* Radar / Dimensions Visualization */}
            <div style={{ 
              display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24,
              textAlign: 'left', background: 'rgba(0,0,0,0.2)', padding: 24, borderRadius: 16
            }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.85rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Positivity (Valence)</span>
                  <span style={{ fontWeight: 600 }}>{Math.round((result.mood_valence + 1) * 50)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${(result.mood_valence + 1) * 50}%`, background: 'var(--success)' }} />
                </div>
              </div>
              
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.85rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Energy (Arousal)</span>
                  <span style={{ fontWeight: 600 }}>{Math.round(result.mood_arousal * 100)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${result.mood_arousal * 100}%`, background: 'var(--warning)' }} />
                </div>
              </div>

              <div style={{ gridColumn: '1 / -1', marginTop: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.85rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Overall Wellbeing Score</span>
                  <span style={{ fontWeight: 600, color: 'var(--primary)' }}>{result.wellbeing_score}/100</span>
                </div>
                <div className="progress-bar" style={{ height: 12 }}>
                  <div className="progress-fill" style={{ width: `${result.wellbeing_score}%` }} />
                </div>
              </div>
            </div>
          </div>

          <button 
            className="btn btn-primary btn-lg" 
            style={{ width: '100%', maxWidth: 400 }}
            onClick={handleGetMusic}
          >
            🎵 Get Music for My Mood
          </button>
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
