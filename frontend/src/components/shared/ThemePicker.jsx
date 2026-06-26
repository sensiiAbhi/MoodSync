import { useThemeStore, THEMES } from '../../store/themeStore'

export default function ThemePicker() {
  const { themeId, setTheme } = useThemeStore()

  return (
    <div
      className="theme-picker"
      title="Change accent color"
      style={{ display: 'flex', alignItems: 'center', gap: 5 }}
    >
      {THEMES.map(theme => (
        <button
          key={theme.id}
          onClick={() => setTheme(theme.id)}
          title={theme.label}
          aria-label={`Switch to ${theme.label} theme`}
          style={{
            width: 18, height: 18,
            borderRadius: '50%',
            background: theme.accent,
            border: themeId === theme.id
              ? '2px solid white'
              : '2px solid transparent',
            cursor: 'pointer',
            outline: themeId === theme.id
              ? `2px solid ${theme.accent}`
              : 'none',
            outlineOffset: 2,
            transition: 'all 0.15s ease',
            transform: themeId === theme.id ? 'scale(1.2)' : 'scale(1)',
            flexShrink: 0,
          }}
        />
      ))}
    </div>
  )
}
