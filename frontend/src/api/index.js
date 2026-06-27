import client from './client'

export const authApi = {
  register: (data) => client.post('/auth/register', data),
  login: (data) => client.post('/auth/login', data),
  logout: () => client.post('/auth/logout'),
  getMe: () => client.get('/auth/me'),
  updateMe: (data) => client.patch('/auth/me', data),
  completeOnboarding: () => client.post('/auth/onboarding/complete'),
}

export const moodApi = {
  submitAssessment: (data) => client.post('/mood/assess', data),
  getCurrent: () => client.get('/mood/current'),
  getHistory: (limit = 30) => client.get(`/mood/assessments?limit=${limit}`),
  getTrends: (days = 30) => client.get(`/mood/trends?days=${days}`),
}

export const activityApi = {
  start: (data) => client.post('/activities/start', data),
  end: (sessionId, data) => client.patch(`/activities/${sessionId}/end`, data),
  getList: (limit = 20) => client.get(`/activities?limit=${limit}`),
  getStats: () => client.get('/activities/stats'),
}

export const recommendationsApi = {
  generate: (data) => client.post('/recommendations/generate', data),
  getHistory: (limit = 20) => client.get(`/recommendations/history?limit=${limit}`),
  trackPlay: (sessionId, recTrackId, data) =>
    client.post(`/recommendations/${sessionId}/play/${recTrackId}`, data),
  trackSkip: (sessionId, recTrackId, data) =>
    client.post(`/recommendations/${sessionId}/skip/${recTrackId}`, data),
}

export const feedbackApi = {
  submitSession: (data) => client.post('/feedback/session', data),
  getEffectiveness: () => client.get('/feedback/effectiveness'),
}

export const analyticsApi = {
  getDashboard: () => client.get('/analytics/dashboard'),
  getMoodCalendar: (weeks = 12) => client.get(`/analytics/mood-calendar?weeks=${weeks}`),
  getWeeklyReport: () => client.get('/analytics/weekly-report'),
}

export const playlistsApi = {
  create: (data) => client.post('/playlists', data),
  getList: () => client.get('/playlists'),
  getById: (id) => client.get(`/playlists/${id}`),
  delete: (id) => client.delete(`/playlists/${id}`),
}
