const API_URL = import.meta.env.VITE_API_URL
const TOKEN_KEY = 'access_token'
const EXPIRES_AT_KEY = 'access_token_expires_at'

export function saveToken(token, expiresIn) {
  sessionStorage.setItem(TOKEN_KEY, token)
  sessionStorage.setItem(EXPIRES_AT_KEY, String(Date.now() + expiresIn * 1000))
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(EXPIRES_AT_KEY)
}

export function getToken() {
  const token = sessionStorage.getItem(TOKEN_KEY)
  const expiresAt = Number(sessionStorage.getItem(EXPIRES_AT_KEY))

  if (!token || !expiresAt || Date.now() >= expiresAt) {
    clearToken()
    return null
  }

  return token
}

export async function logout() {
  const token = getToken()
  clearToken()

  if (!token) {
    return
  }

  await fetch(`${API_URL}/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => null)
}