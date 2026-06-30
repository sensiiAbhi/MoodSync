import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { playlistsApi } from '../api'
import toast from 'react-hot-toast'

const MOOD_COLOR = {
  stressed: '#EF4444', anxious: '#F97316', burned_out: '#6B7280',
  sleepy: '#8B5CF6', energetic: '#F59E0B', motivated: '#10B981',
  calm: '#06B6D4', focused: '#3B82F6', relaxed: '#84CC16',
}

export default function PlaylistsPage() {
  const [playlists, setPlaylists] = useState([])
  const [selectedPlaylist, setSelectedPlaylist] = useState(null)
  const [tracks, setTracks] = useState([])
  const [loading, setLoading] = useState(true)
  const [trackLoading, setTrackLoading] = useState(false)
  const [deleting, setDeleting] = useState(null)

  useEffect(() => { loadPlaylists() }, [])

  const loadPlaylists = async () => {
    setLoading(true)
    try {
      const res = await playlistsApi.getList()
      setPlaylists(res.data)
    } catch {
      toast.error('Failed to load playlists')
    }
    setLoading(false)
  }

  const handleSelect = async (playlist) => {
    if (selectedPlaylist?.playlist_id === playlist.playlist_id) {
      setSelectedPlaylist(null)
      setTracks([])
      return
    }
    setSelectedPlaylist(playlist)
    setTrackLoading(true)
    try {
      const res = await playlistsApi.getById(playlist.playlist_id)
      setTracks(res.data.tracks || [])
    } catch {
      toast.error('Failed to load tracks')
    }
    setTrackLoading(false)
  }

  const handleDelete = async (playlistId, e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this playlist?')) return
    setDeleting(playlistId)
    try {
      await playlistsApi.delete(playlistId)
      setPlaylists(prev => prev.filter(p => p.playlist_id !== playlistId))
      if (selectedPlaylist?.playlist_id === playlistId) {
        setSelectedPlaylist(null)
        setTracks([])
      }
      toast.success('Playlist deleted')
    } catch {
      toast.error('Failed to delete playlist')
    }
    setDeleting(null)
  }

  const formatDuration = (ms) => {
    const min = Math.floor(ms / 60000)
    const sec = Math.floor((ms % 60000) / 1000)
    return `${min}:${sec.toString().padStart(2, '0')}`
  }

  const formatDate = (iso) => {
    if (!iso) return ''
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  if (loading) {
    return (
      <div className="page-layout" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spinner spinner-lg" />
      </div>
    )
  }

  return (
    <div className="page-layout">
      <div className="main-content">
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 40, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 style={{ marginBottom: 8 }}>My Playlists</h1>
            <p style={{ color: 'var(--text-muted)' }}>
              {playlists.length} saved playlist{playlists.length !== 1 ? 's' : ''} from your recommendation sessions
            </p>
          </div>
          <Link to="/app/recommend" className="btn btn-primary">
            ✦ Create New Playlist
          </Link>
        </div>

        {playlists.length === 0 ? (
          /* Empty State */
          <div style={{
            textAlign: 'center', padding: '80px 24px',
            background: 'var(--bg-card)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-2xl)',
          }}>
            <div style={{ fontSize: '4rem', marginBottom: 24 }}>♪</div>
            <h2 style={{ marginBottom: 12 }}>No Playlists Yet</h2>
            <p style={{ color: 'var(--text-muted)', maxWidth: 420, margin: '0 auto 32px' }}>
              After getting music recommendations, click "Save Playlist" to store it here permanently.
            </p>
            <Link to="/app/assess" className="btn btn-primary btn-lg">
              ◉ Start with a Mood Check-In
            </Link>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: selectedPlaylist ? 'minmax(280px, 340px) minmax(0, 1fr)' : '1fr', gap: 24, transition: 'all 0.3s ease', alignItems: 'start' }}>
            {/* Playlist Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {playlists.map(pl => {
                const moodColor = MOOD_COLOR[pl.mood_context] || 'var(--primary)'
                const isSelected = selectedPlaylist?.playlist_id === pl.playlist_id
                return (
                  <div
                    key={pl.playlist_id}
                    onClick={() => handleSelect(pl)}
                    style={{
                      background: isSelected ? 'rgba(124,58,237,0.12)' : 'var(--bg-card)',
                      border: isSelected ? '1px solid rgba(124,58,237,0.4)' : '1px solid var(--border)',
                      borderRadius: 'var(--radius-lg)',
                      padding: '20px 24px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      display: 'flex', alignItems: 'center', gap: 16,
                    }}
                    onMouseEnter={e => { if (!isSelected) e.currentTarget.style.borderColor = 'rgba(255,255,255,0.16)' }}
                    onMouseLeave={e => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--border)' }}
                  >
                    {/* Playlist icon with mood color */}
                    <div style={{
                      width: 52, height: 52, borderRadius: 12, flexShrink: 0,
                      background: `${moodColor}20`, border: `1px solid ${moodColor}40`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '1.5rem',
                    }}>
                      ♪
                    </div>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        fontWeight: 600, fontSize: '0.95rem',
                        color: 'var(--text-primary)', marginBottom: 4,
                        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      }}>
                        {pl.name}
                      </div>
                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
                        {pl.mood_context && (
                          <span style={{
                            fontSize: '0.7rem', fontWeight: 600,
                            background: `${moodColor}20`, color: moodColor,
                            border: `1px solid ${moodColor}30`,
                            padding: '2px 8px', borderRadius: 99,
                            textTransform: 'capitalize',
                          }}>
                            {pl.mood_context.replace('_', ' ')}
                          </span>
                        )}
                        {pl.activity_context && (
                          <span style={{
                            fontSize: '0.7rem', color: 'var(--text-muted)',
                            background: 'rgba(255,255,255,0.05)',
                            padding: '2px 8px', borderRadius: 99,
                            textTransform: 'capitalize',
                          }}>
                            {pl.activity_context.replace('_', ' ')}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {pl.track_count} tracks · {formatDate(pl.created_at)}
                      </div>
                    </div>

                    <button
                      onClick={(e) => handleDelete(pl.playlist_id, e)}
                      disabled={deleting === pl.playlist_id}
                      style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: 'var(--text-muted)', fontSize: '1rem', padding: 6,
                        borderRadius: 6, flexShrink: 0,
                        transition: 'color 0.15s ease',
                      }}
                      onMouseEnter={e => e.currentTarget.style.color = '#EF4444'}
                      onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
                      title="Delete playlist"
                    >
                      {deleting === pl.playlist_id ? '...' : '✕'}
                    </button>
                  </div>
                )
              })}
            </div>

            {/* Track List Panel */}
            {selectedPlaylist && (
              <div className="card" style={{ maxHeight: '75vh', display: 'flex', flexDirection: 'column' }}>
                <div style={{ marginBottom: 20 }}>
                  <h3 style={{ marginBottom: 4 }}>{selectedPlaylist.name}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    {selectedPlaylist.track_count} tracks
                  </p>
                </div>

                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {trackLoading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
                      <div className="spinner" />
                    </div>
                  ) : tracks.length === 0 ? (
                    <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 40 }}>
                      No tracks found in this playlist
                    </p>
                  ) : (
                    tracks.map((track, idx) => (
                      <div key={idx} className="track-card">
                        <span className="track-rank">{track.position}</span>
                        <img
                          className="track-album-art"
                          src={track.album_art_url || `https://picsum.photos/seed/${idx+20}/56/56`}
                          alt={track.album}
                          onError={e => { e.target.src = `https://picsum.photos/seed/${idx+20}/56/56` }}
                          style={{ width: 48, height: 48 }}
                        />
                        <div className="track-info">
                          <div className="track-title">{track.title}</div>
                          <div className="track-artist">{track.artist}</div>
                          {track.duration_ms && (
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 2 }}>
                              {formatDuration(track.duration_ms)}
                            </div>
                          )}
                        </div>
                        {track.spotify_url && (
                          <a
                            href={track.spotify_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              fontSize: '0.75rem', color: '#1DB954',
                              textDecoration: 'none', fontWeight: 600,
                              padding: '4px 8px', borderRadius: 6,
                              background: 'rgba(29,185,84,0.1)',
                            }}
                          >
                            ▶ Play
                          </a>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
