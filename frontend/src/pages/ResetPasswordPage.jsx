import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { validateResetPasswordForm } from '../utils/validation.js'

const API_URL = import.meta.env.VITE_API_URL
const SERVER_UNAVAILABLE_MESSAGE = 'Server trenutno nije dostupan. Pokušajte kasnije.'

function ResetPasswordPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [token] = useState(() => searchParams.get('token') || '')
  const [form, setForm] = useState({ newPassword: '', confirmNewPassword: '' })
  const [errors, setErrors] = useState({})
  const [errorMessage, setErrorMessage] = useState('')
  const [showNewLinkHint, setShowNewLinkHint] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (searchParams.has('token')) {
      navigate('/reset-password', { replace: true })
    }
  }, [searchParams, navigate])

  if (!token) {
    return (
      <div>
        <h2>Resetovanje lozinke</h2>
        <p style={{ color: 'red' }}>Link za resetovanje lozinke nije ispravan.</p>
        <Link to="/forgot-password">Zatražite novi link</Link>
      </div>
    )
  }

  function handleChange(e) {
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErrorMessage('')
    setShowNewLinkHint(false)

    const validationErrors = validateResetPasswordForm(form)
    setErrors(validationErrors)
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/password-reset/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          new_password: form.newPassword,
          confirm_new_password: form.confirmNewPassword,
        }),
      })
      const data = await response.json().catch(() => ({}))

      if (response.ok) {
        navigate('/login', { replace: true, state: { message: data.message } })
        return
      }

      const serverErrors = data.errors || {}
      setErrors({
        ...(serverErrors.new_password && { newPassword: serverErrors.new_password }),
        ...(serverErrors.confirm_new_password && { confirmNewPassword: serverErrors.confirm_new_password }),
      })
      setErrorMessage(data.detail || 'Resetovanje lozinke nije uspelo.')
      setShowNewLinkHint(response.status === 400 || Boolean(serverErrors.token))
      setLoading(false)
    } catch {
      setErrorMessage(SERVER_UNAVAILABLE_MESSAGE)
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h2>Resetovanje lozinke</h2>

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
      {showNewLinkHint && (
        <p>
          <Link to="/forgot-password">Zatražite novi link</Link>
        </p>
      )}

      <button type="submit" disabled={loading}>
        {loading ? 'Čuvanje...' : 'Postavi novu lozinku'}
      </button>

      <p>
        <Link to="/login">Nazad na prijavu</Link>
      </p>
    </form>
  )
}

export default ResetPasswordPage