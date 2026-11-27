import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { validateChangePasswordForm } from '../utils/validation.js'
import { clearToken, getToken } from '../utils/auth.js'

const API_URL = import.meta.env.VITE_API_URL
const SERVER_UNAVAILABLE_MESSAGE = 'Server trenutno nije dostupan. Pokušajte kasnije.'

const SERVER_FIELD_NAMES = {
  current_password: 'currentPassword',
  new_password: 'newPassword',
  confirm_new_password: 'confirmNewPassword',
}

function mapServerErrors(serverErrors = {}) {
  const errors = {}
  for (const [field, message] of Object.entries(serverErrors)) {
    if (SERVER_FIELD_NAMES[field]) {
      errors[SERVER_FIELD_NAMES[field]] = message
    }
  }
  return errors
}

function ChangePasswordPage() {
  const navigate = useNavigate()
  const [token] = useState(() => getToken())
  const [form, setForm] = useState({ currentPassword: '', newPassword: '', confirmNewPassword: '' })
  const [errors, setErrors] = useState({})
  const [errorMessage, setErrorMessage] = useState('')
  const [loading, setLoading] = useState(false)

  if (!token) {
    return <Navigate to="/login" replace />
  }

  function handleChange(e) {
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  function goToLogin(message) {
    clearToken()
    navigate('/login', { replace: true, state: { message } })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErrorMessage('')

    const validationErrors = validateChangePasswordForm(form)
    setErrors(validationErrors)
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/users/me/password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: form.currentPassword,
          new_password: form.newPassword,
          confirm_new_password: form.confirmNewPassword,
        }),
      })
      const data = await response.json().catch(() => ({}))

      if (response.ok) {
        goToLogin(data.message)
        return
      }
      if (response.status === 401) {
        goToLogin('Sesija je istekla. Prijavite se ponovo.')
        return
      }
      setErrors(mapServerErrors(data.errors))
      setErrorMessage(data.detail || 'Promena lozinke nije uspela.')
      setLoading(false)
    } catch {
      setErrorMessage(SERVER_UNAVAILABLE_MESSAGE)
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h2>Promena lozinke</h2>

      <div>
        <label htmlFor="currentPassword">Trenutna lozinka</label>
        <div>
          <input
            id="currentPassword"
            name="currentPassword"
            type="password"
            value={form.currentPassword}
            onChange={handleChange}
            autoComplete="current-password"
            maxLength={64}
          />
        </div>
        {errors.currentPassword && <p style={{ color: 'red' }}>{errors.currentPassword}</p>}
      </div>

      <div>
        <label htmlFor="newPassword">Nova lozinka</label>
        <div>
          <input
            id="newPassword"
            name="newPassword"
            type="password"
            value={form.newPassword}
            onChange={handleChange}
            autoComplete="new-password"
            maxLength={64}
          />
        </div>
        {errors.newPassword && <p style={{ color: 'red' }}>{errors.newPassword}</p>}
      </div>

      <div>
        <label htmlFor="confirmNewPassword">Ponovljena nova lozinka</label>
        <div>
          <input
            id="confirmNewPassword"
            name="confirmNewPassword"
            type="password"
            value={form.confirmNewPassword}
            onChange={handleChange}
            autoComplete="new-password"
            maxLength={64}
          />
        </div>
        {errors.confirmNewPassword && <p style={{ color: 'red' }}>{errors.confirmNewPassword}</p>}
      </div>

      {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}

      <button type="submit" disabled={loading}>
        {loading ? 'Čuvanje...' : 'Promeni lozinku'}
      </button>

      <p>
        <Link to="/">Nazad na početnu</Link>
      </p>
    </form>
  )
}

export default ChangePasswordPage