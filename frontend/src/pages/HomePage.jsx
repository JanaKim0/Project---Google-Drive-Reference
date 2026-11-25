import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getToken, logout } from '../utils/auth.js'

function HomePage() {
  const navigate = useNavigate()
  const [loggingOut, setLoggingOut] = useState(false)
  const isLoggedIn = Boolean(getToken())

  async function handleLogout() {
    setLoggingOut(true)
    await logout()
    navigate('/login', { replace: true, state: { message: 'Uspešno ste se odjavili.' } })
  }

  return (
    <div>
      <p>pocetna stranica cheeeeck</p>
      <p>welcome</p>
      {isLoggedIn ? (
        <>
          <p style={{ color: 'green' }}>Prijavljeni ste.</p>
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