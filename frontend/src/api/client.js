import axios from 'axios'

// In production (Firebase): use the Render backend URL set in .env
// In development: Vite proxy routes /api → localhost:8000
const PROD_API = import.meta.env.VITE_API_URL
const API_BASE = PROD_API ? `${PROD_API}/api/v1` : '/api/v1'


const client = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach access token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor: handle 401 → refresh token
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const res = await axios.post(`${API_BASE}/auth/refresh`, {}, { withCredentials: true })
        const { access_token } = res.data
        localStorage.setItem('access_token', access_token)
        original.headers.Authorization = `Bearer ${access_token}`
        return client(original)
      } catch {
        localStorage.removeItem('access_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default client
