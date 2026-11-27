import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { clearToken, getToken, logout } from '../utils/auth.js'

const API_URL = import.meta.env.VITE_API_URL

function formatDateTime(value) {
  return new Date(value).toLocaleString('sr-Latn-RS', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function HomePage() {
  const navigate = useNavigate()
  const [token, setToken] = useState(() => getToken())
  const [user, setUser] = useState(null)
  const [loggingOut, setLoggingOut] = useState(false)

  useEffect(() => {
    if (!token) {
      return
    }

    let active = true
    fetch(`${API_URL}/users/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (response) => {
        if (!active) {
          return
        }
        if (response.status === 401) {
          clearToken()
          setToken(null)
          return
        }
        if (response.ok) {
          setUser(await response.json())
        }
      })
      .catch(() => null)

    return () => {
      active = false
    }
  }, [token])

  async function handleLogout() {
    setLoggingOut(true)
    await logout()
    navigate('/login', { replace: true, state: { message: 'Uspešno ste se odjavili.' } })
  }

  return (
    <div>
      <p>pocetna stranica cheeeeck</p>
      <p>welcome</p>
      {token ? (
        <>
          <p style={{ color: 'green' }}>
            {user ? `Zdravo, ${user.first_name}!` : 'Prijavljeni ste.'}
          </p>
          {user?.password_expiry_warning && user.password_expires_at && (
            <p style={{ color: 'darkorange' }}>
              ⚠ Vaša lozinka ističe {formatDateTime(user.password_expires_at)}.{' '}
              <Link to="/change-password">Promenite lozinku</Link>
            </p>
          )}
          <p>
            <Link to="/change-password">Promena lozinke</Link>
          </p>
          <button type="button" onClick={handleLogout} disabled={loggingOut}>
            {loggingOut ? 'Odjava...' : 'Odjavi se'}
          </button>
        </>
      ) : (
        <>
          <Link to="/register">Registracija</Link> | <Link to="/login">Prijava</Link>
        </>
      )}
    </div>
  )
}

export default HomePage