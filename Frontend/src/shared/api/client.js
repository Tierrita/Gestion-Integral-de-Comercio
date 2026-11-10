import axios from 'axios'

const SESSION_KEY = 'gestion-integral.session'

export function readToken() {
  return sessionStorage.getItem(SESSION_KEY)
}

export function saveToken(token) {
  sessionStorage.setItem(SESSION_KEY, token)
}

export function clearToken() {
  sessionStorage.removeItem(SESSION_KEY)
}

export const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = readToken()

  if (token && config.url !== '/auth/login') {
    config.headers.set('Authorization', `Bearer ${token}`)
  }

  return config
})