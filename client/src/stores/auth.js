import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://localhost:${import.meta.env.VITE_PORT || 3000}/api`

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async register(userData) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`${API_BASE_URL}/register`, userData)
        this.token = response.data.token
        this.user = response.data.user
        localStorage.setItem('token', this.token)
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.error || 'Registration failed'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async login(credentials) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`${API_BASE_URL}/login`, credentials)
        this.token = response.data.token
        this.user = response.data.user
        localStorage.setItem('token', this.token)
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.error || 'Login failed'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async changePassword(passwordData) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`${API_BASE_URL}/change-password`, passwordData, {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.error || 'Password change failed'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async fetchProfile() {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`${API_BASE_URL}/profile`, {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        this.user = response.data.user
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to fetch profile'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.error = null
      localStorage.removeItem('token')
    }
  }
})
