import axios from 'axios'

export const TOKEN_KEY = 'auth_token'
export const USER_KEY = 'auth_user'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const reqUrl = error.config?.url || ''
    const isAuthForm =
      reqUrl.includes('/auth/login/') || reqUrl.includes('/auth/register/')
    if (status === 401 && !isAuthForm) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      delete api.defaults.headers.common.Authorization
      if (!window.location.pathname.startsWith('/login') && window.location.pathname !== '/register') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api
