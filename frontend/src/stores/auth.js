import { defineStore } from 'pinia'

import api, { TOKEN_KEY, USER_KEY } from '../services/api'

function readUserFromStorage() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY),
    user: readUserFromStorage(),
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    setSession(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
      api.defaults.headers.common.Authorization = `Token ${token}`
    },
    clearSession() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      delete api.defaults.headers.common.Authorization
    },
    async login({ username, password }) {
      const { data } = await api.post('/auth/login/', { username, password })
      const user = { id: data.user_id, username }
      this.setSession(data.token, user)
    },
    async register({ username, password, email }) {
      const { data } = await api.post('/auth/register/', {
        username,
        password,
        email: email || '',
      })
      const user = { id: data.user_id, username, email: email || '' }
      this.setSession(data.token, user)
    },
    logout() {
      this.clearSession()
    },
  },
})
