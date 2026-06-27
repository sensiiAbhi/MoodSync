import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { moodApi } from '../api'
import toast from 'react-hot-toast'

const QUESTIONS = [
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
  {
    id: 'language', label: 'Preferred Language', type: 'choice',
    desc: 'What language of music are you looking for?',
    emoji: '🌍',
    options: ['English', 'Hindi', 'Japanese', 'Korean', 'Spanish', 'Russian', 'Any'],
  },
  {
    id: 'vibe', label: 'Music Vibe / Genre', type: 'choice',
    desc: 'Any specific style you want?',
    emoji: '🎸',
    options: ['Pop', 'Rock', 'Anime', 'Phonk', 'Lofi', 'Classical', 'Hip-Hop', 'Any'],
  },
  {
    id: 'activity', label: 'Current Activity', type: 'choice',
    desc: 'What are you doing right now?',
    emoji: '🎧',
    options: ['studying', 'coding', 'reading', 'deep_work', 'creative_thinking', 'gym_workout', 'running', 'yoga', 'meditation', 'sleeping', 'relaxing', 'driving'],
  },
  {
    id: 'outcome', label: 'Desired Outcome', type: 'choice',
    desc: 'What do you want to achieve?',
    emoji: '🎯',
    options: ['improve_focus', 'reduce_stress', 'boost_energy', 'improve_mood', 'sleep_better', 'stay_motivated', 'feel_calm', 'feel_energized'],
  }
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
    // Set default value for sliders if not touched
    if (!(currentQuestion.id in answers) && !currentQuestion.type) {
      setAnswers(prev => ({ ...prev, [currentQuestion.id]: 5 }))
    }
    // Set default for choice if not touched
    if (!(currentQuestion.id in answers) && currentQuestion.type === 'choice') {
      setAnswers(prev => ({ ...prev, [currentQuestion.id]: currentQuestion.options[0] }))
    }

    if (currentQ < QUESTIONS.length - 1) {
      setCurrentQ(currentQ + 1)
    } else {
      // Submit assessment
      const finalAnswers = { ...answers }
      
      setLoading(true)
      try {
        const payload = {
          energy_level: finalAnswers.energy_level || 5,
          stress_level: finalAnswers.stress_level || 5,
          focus_level: finalAnswers.focus_level || 5,
          motivation_level: finalAnswers.motivation_level || 5,
          sleep_quality: finalAnswers.sleep_quality || 5,
          mental_fatigue: finalAnswers.mental_fatigue || 5,
          social_mood: finalAnswers.social_mood || 5,
          assessment_type: 'full',
        }
        
        const res = await moodApi.submitAssessment(payload)
        toast.success('Assessment complete! 🧠')
        
        // Auto-redirect to recommendations directly with all preferences!
        navigate('/app/recommend', { 
          state: { 
            assessmentId: res.data.assessment_id, 
            mood: res.data.primary_mood,
            language: finalAnswers.language || 'Any',
            vibe: finalAnswers.vibe || 'Any',
            activity: finalAnswers.activity || 'relaxing',
            outcome: finalAnswers.outcome || 'improve_mood'
          } 
        })
      } catch (err) {
        toast.error('Failed to save assessment')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleBack = () => {
    if (currentQ > 0) setCurrentQ(currentQ - 1)
  }

  const currentValue = answers[currentQuestion?.id] ?? 5

  // Intermediate Result Screen removed for seamless flow

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

          {/* Question Input Logic */}
          {currentQuestion.type === 'choice' ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center', marginBottom: 40 }}>
              {currentQuestion.options.map(opt => {
                const isSelected = (answers[currentQuestion.id] || currentQuestion.options[0]) === opt;
                return (
                  <button
                    key={opt}
                    onClick={() => setAnswers(prev => ({ ...prev, [currentQuestion.id]: opt }))}
                    style={{
                      padding: '12px 24px', borderRadius: 99,
                      background: isSelected ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                      border: isSelected ? 'none' : '1px solid rgba(255,255,255,0.1)',
                      color: isSelected ? 'white' : 'var(--text-primary)',
                      fontSize: '1rem', fontWeight: 600, cursor: 'pointer',
                      boxShadow: isSelected ? '0 0 16px rgba(124,58,237,0.4)' : 'none',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {opt}
                  </button>
                )
              })}
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
