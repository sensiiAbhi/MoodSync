import { create } from 'zustand'
import { authApi } from '../api'

export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isLoading: false,
  isAuthenticated: !!localStorage.getItem('access_token'),

  login: async (credentials) => {
    set({ isLoading: true })
    try {
      const res = await authApi.login(credentials)
      const { access_token, user } = res.data
      localStorage.setItem('access_token', access_token)
      set({ token: access_token, user, isAuthenticated: true, isLoading: false })
      return { success: true, user }
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  register: async (data) => {
    set({ isLoading: true })
    try {
      const res = await authApi.register(data)
      set({ isLoading: false })
      return { success: true, data: res.data }
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  logout: async () => {
    try { await authApi.logout() } catch {}
    localStorage.removeItem('access_token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  fetchMe: async () => {
    try {
      const res = await authApi.getMe()
      set({ user: res.data, isAuthenticated: true })
    } catch {
      localStorage.removeItem('access_token')
      set({ user: null, token: null, isAuthenticated: false })
    }
  },

  updateUser: (updates) => set(state => ({ user: { ...state.user, ...updates } })),
}))
