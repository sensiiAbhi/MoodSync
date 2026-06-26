import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// ── Available accent color themes ──
export const THEMES = [
  {
    id: 'green',
    label: 'MoodSync Green',
    accent:      '#1ED760',
    accentHover: '#1FDF64',
    accentDark:  '#17A84A',
    accentMuted: 'rgba(30,215,96,0.15)',
    accentBorder:'rgba(30,215,96,0.30)',
    accentGlow:  'rgba(30,215,96,0.25)',
    accentGlowSm:'rgba(30,215,96,0.15)',
  },
  {
    id: 'sky',
    label: 'Sky Blue',
    accent:      '#38BDF8',
    accentHover: '#7DD3FC',
    accentDark:  '#0284C7',
    accentMuted: 'rgba(56,189,248,0.15)',
    accentBorder:'rgba(56,189,248,0.30)',
    accentGlow:  'rgba(56,189,248,0.25)',
    accentGlowSm:'rgba(56,189,248,0.15)',
  },
  {
    id: 'orange',
    label: 'Fire Orange',
    accent:      '#FF6B35',
    accentHover: '#FF8C5A',
    accentDark:  '#CC4E1A',
    accentMuted: 'rgba(255,107,53,0.15)',
    accentBorder:'rgba(255,107,53,0.30)',
    accentGlow:  'rgba(255,107,53,0.25)',
    accentGlowSm:'rgba(255,107,53,0.15)',
  },
  {
    id: 'yellow',
    label: 'Solar Yellow',
    accent:      '#FFD60A',
    accentHover: '#FFE04D',
    accentDark:  '#CC9C00',
    accentMuted: 'rgba(255,214,10,0.15)',
    accentBorder:'rgba(255,214,10,0.30)',
    accentGlow:  'rgba(255,214,10,0.25)',
    accentGlowSm:'rgba(255,214,10,0.15)',
  },
  {
    id: 'purple',
    label: 'Electric Purple',
    accent:      '#A855F7',
    accentHover: '#C084FC',
    accentDark:  '#7C3AED',
    accentMuted: 'rgba(168,85,247,0.15)',
    accentBorder:'rgba(168,85,247,0.30)',
    accentGlow:  'rgba(168,85,247,0.25)',
    accentGlowSm:'rgba(168,85,247,0.15)',
  },
  {
    id: 'rose',
    label: 'Neon Rose',
    accent:      '#F43F5E',
    accentHover: '#FB7185',
    accentDark:  '#BE123C',
    accentMuted: 'rgba(244,63,94,0.15)',
    accentBorder:'rgba(244,63,94,0.30)',
    accentGlow:  'rgba(244,63,94,0.25)',
    accentGlowSm:'rgba(244,63,94,0.15)',
  },
]

export const useThemeStore = create(
  persist(
    (set, get) => ({
      themeId: 'green',

      setTheme: (id) => {
        const theme = THEMES.find(t => t.id === id)
        if (!theme) return
        set({ themeId: id })
        applyTheme(theme)
      },

      getTheme: () => {
        const { themeId } = get()
        return THEMES.find(t => t.id === themeId) || THEMES[0]
      },

      initTheme: () => {
        const { themeId } = get()
        const theme = THEMES.find(t => t.id === themeId) || THEMES[0]
        applyTheme(theme)
      },
    }),
    {
      name: 'moodsync-theme',
      partialize: (state) => ({ themeId: state.themeId }),
    }
  )
)

// Injects CSS variables into :root
function applyTheme(theme) {
  const root = document.documentElement
  root.style.setProperty('--accent',         theme.accent)
  root.style.setProperty('--accent-hover',   theme.accentHover)
  root.style.setProperty('--accent-dark',    theme.accentDark)
  root.style.setProperty('--accent-muted',   theme.accentMuted)
  root.style.setProperty('--accent-border',  theme.accentBorder)
  root.style.setProperty('--accent-glow',    theme.accentGlow)
  root.style.setProperty('--accent-glow-sm', theme.accentGlowSm)
  // Update the shadow variables that reference accent
  root.style.setProperty('--shadow-accent',    `0 0 24px ${theme.accentGlow}`)
  root.style.setProperty('--shadow-accent-sm', `0 0 12px ${theme.accentGlowSm}`)
}
