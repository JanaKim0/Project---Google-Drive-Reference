import { useState } from 'react'
import { Link } from 'react-router-dom'
import { validateForgotPasswordForm } from '../utils/validation.js'

const API_URL = import.meta.env.VITE_API_URL
const SERVER_UNAVAILABLE_MESSAGE = 'Server trenutno nije dostupan. Pokušajte kasnije.'

function ForgotPasswordPage() {
  const [form, setForm] = useState({ email: '' })
  const [errors, setErrors] = useState({})
  const [errorMessage, setErrorMessage] = useState('')
  const [infoMessage, setInfoMessage] = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErrorMessage('')
    setInfoMessage('')

    const validationErrors = validateForgotPasswordForm(form)
    setErrors(validationErrors)
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/password-reset/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: form.email.trim() }),
      })
      const data = await response.json().catch(() => ({}))

      if (response.ok) {
        setInfoMessage(data.message)
      } else {
        setErrors(data.errors?.email ? { email: data.errors.email } : {})
        setErrorMessage(data.detail || 'Slanje zahteva nije uspelo.')
      }
    } catch {
      setErrorMessage(SERVER_UNAVAILABLE_MESSAGE)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h2>Zaboravljena lozinka</h2>
      <p>Unesite imejl adresu naloga i poslaćemo vam link za resetovanje lozinke.</p>

      <div>
        <label htmlFor="email">Imejl</label>
        <div>
          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            autoComplete="email"
            maxLength={254}
          />
        </div>
        {errors.email && <p style={{ color: 'red' }}>{errors.email}</p>}
      </div>

      {infoMessage && <p style={{ color: 'green' }}>{infoMessage}</p>}
      {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}

      <button type="submit" disabled={loading}>
        {loading ? 'Slanje...' : 'Pošalji link'}
      </button>

      <p>
        <Link to="/login">Nazad na prijavu</Link>
      </p>
    </form>
  )
}

export default ForgotPasswordPage