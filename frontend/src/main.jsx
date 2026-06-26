import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './styles/index.css'
import { useThemeStore } from './store/themeStore.js'

// Apply saved accent theme before first render (avoids flash)
useThemeStore.getState().initTheme()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1A1A1A',
            color: '#FFFFFF',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px',
            fontFamily: 'Inter, sans-serif',
            fontSize: '14px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
          },
          success: {
            iconTheme: { primary: 'var(--accent)', secondary: '#000' },
          },
          error: {
            iconTheme: { primary: '#E5534B', secondary: '#1A1A1A' },
          },
          duration: 3500,
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
)
