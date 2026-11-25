import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { validateLoginForm, validateOtp } from '../utils/validation.js'
import { saveToken } from '../utils/auth.js'

const API_URL = import.meta.env.VITE_API_URL
const SERVER_UNAVAILABLE_MESSAGE = 'Server trenutno nije dostupan. Pokušajte kasnije.'

async function postJson(path, body) {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await response.json().catch(() => ({}))
  return { ok: response.ok, status: response.status, data }
}

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [step, setStep] = useState('credentials')
  const [form, setForm] = useState({ email: '', password: '' })
  const [otp, setOtp] = useState('')
  const [errors, setErrors] = useState({})
  const [errorMessage, setErrorMessage] = useState('')
  const [infoMessage, setInfoMessage] = useState(location.state?.message || '')
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  function handleOtpChange(e) {
    setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))
  }

  function backToCredentials(message = '') {
    setStep('credentials')
    setOtp('')
    setErrors({})
    setInfoMessage('')
    setErrorMessage(message)
  }

  async function handleLogin(e) {
    e.preventDefault()
    setErrorMessage('')
    setInfoMessage('')

    const validationErrors = validateLoginForm(form)
    setErrors(validationErrors)
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    const email = form.email.trim()
    setLoading(true)
    try {
      const { ok, data } = await postJson('/login', { email, password: form.password })
      if (ok) {
        setForm({ email, password: '' })
        setOtp('')
        setInfoMessage(data.message)
        setStep('otp')
      } else {
        setErrors(data.errors || {})
        setErrorMessage(data.detail || 'Prijava nije uspela.')
      }
    } catch {
      setErrorMessage(SERVER_UNAVAILABLE_MESSAGE)
    } finally {
      setLoading(false)
    }
  }

  async function handleVerify(e) {
    e.preventDefault()
    setErrorMessage('')

    const otpError = validateOtp(otp)
    setErrors(otpError ? { otp: otpError } : {})
    if (otpError) {
      return
    }

    setLoading(true)
    try {
      const { ok, status, data } = await postJson('/login/verify', { email: form.email, otp })
      if (ok) {
        saveToken(data.access_token, data.expires_in)
        navigate('/', { replace: true })
        return
      }
      if (status === 429) {
        backToCredentials(data.detail)
        return
      }
      setOtp('')
      setErrors(data.errors || {})
      setErrorMessage(data.detail || 'Kod nije ispravan.')
    } catch {
      setErrorMessage(SERVER_UNAVAILABLE_MESSAGE)
    } finally {
      setLoading(false)
    }
  }

  if (step === 'otp') {
    return (
      <form onSubmit={handleVerify} noValidate>
        <h2>Prijava – potvrda koda</h2>
        {infoMessage && <p style={{ color: 'green' }}>{infoMessage}</p>}
        <p>Unesite 6-cifreni kod koji je poslat na {form.email}.</p>

        <div>
          <label htmlFor="otp">Kod</label>
          <div>
            <input
              id="otp"
              name="otp"
              value={otp}
              onChange={handleOtpChange}
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              autoFocus
            />
          </div>
          {errors.otp && <p style={{ color: 'red' }}>{errors.otp}</p>}
        </div>

        {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}

        <button type="submit" disabled={loading}>
          {loading ? 'Provera...' : 'Potvrdi'}
        </button>
        <button type="button" onClick={() => backToCredentials()} disabled={loading}>
          Nazad
        </button>
      </form>
    )
  }

  return (
    <form onSubmit={handleLogin} noValidate>
        <h2>Prijava</h2>
        {infoMessage && <p style={{ color: 'green' }}>{infoMessage}</p>}


      <div>
        <label htmlFor="email">Imejl</label>
        <div>
          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            autoComplete="username"
            maxLength={254}
          />
        </div>
        {errors.email && <p style={{ color: 'red' }}>{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="password">Lozinka</label>
        <div>
          <input
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            autoComplete="current-password"
            maxLength={64}
          />
        </div>
        {errors.password && <p style={{ color: 'red' }}>{errors.password}</p>}
      </div>

      {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}

      <button type="submit" disabled={loading}>
        {loading ? 'Slanje...' : 'Prijavi se'}
      </button>

      <p>
        Nemate nalog? <Link to="/register">Registrujte se</Link>
      </p>
    </form>
  )
}

export default LoginPage