import { useState } from 'react'
import { validateRegisterForm } from '../utils/validation.js'

const HINTS = {
  firstName: '2–50 characters. Letters, spaces, apostrophes and hyphens only.',
  lastName: '2–50 characters. Letters, spaces, apostrophes and hyphens only.',
  email: 'Up to 254 characters, e.g. name@example.com.',
  password:
    '8–64 characters. Must contain an uppercase letter, a lowercase letter, a digit and a special character.',
  confirmPassword: 'Must match the password (8–64 characters).',
}

function FieldHint({ text }) {
  return (
    <span className="field-hint" tabIndex={0} aria-label={text}>
      ?
      <span className="field-hint-text" role="tooltip">
        {text}
      </span>
    </span>
  )
}

function RegisterPage() {
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [errors, setErrors] = useState({})

  function handleChange(e) {
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  function handleSubmit(e) {
    e.preventDefault()

    const validationErrors = validateRegisterForm(form)
    setErrors(validationErrors)

    if (Object.keys(validationErrors).length > 0) {
      return
    }

    console.log('Forma je ispravna:', form.email)
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h2>Registracija</h2>

      <div>
        <label htmlFor="firstName">Ime</label>
        <div className="field-row">
          <input id="firstName" name="firstName" value={form.firstName} onChange={handleChange} maxLength={50} />
          <FieldHint text={HINTS.firstName} />
        </div>
        {errors.firstName && <p style={{ color: 'red' }}>{errors.firstName}</p>}
      </div>

      <div>
        <label htmlFor="lastName">Prezime</label>
        <div className="field-row">
          <input id="lastName" name="lastName" value={form.lastName} onChange={handleChange} maxLength={50} />
          <FieldHint text={HINTS.lastName} />
        </div>
        {errors.lastName && <p style={{ color: 'red' }}>{errors.lastName}</p>}
      </div>

      <div>
        <label htmlFor="email">Imejl</label>
        <div className="field-row">
          <input id="email" name="email" type="email" value={form.email} onChange={handleChange} maxLength={254} />
          <FieldHint text={HINTS.email} />
        </div>
        {errors.email && <p style={{ color: 'red' }}>{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="password">Lozinka</label>
        <div className="field-row">
          <input id="password" name="password" type="password" value={form.password} onChange={handleChange} maxLength={64} />
          <FieldHint text={HINTS.password} />
        </div>
        {errors.password && <p style={{ color: 'red' }}>{errors.password}</p>}
      </div>

      <div>
        <label htmlFor="confirmPassword">Ponovljena lozinka</label>
        <div className="field-row">
          <input id="confirmPassword" name="confirmPassword" type="password" value={form.confirmPassword} onChange={handleChange} maxLength={64} />
          <FieldHint text={HINTS.confirmPassword} />
        </div>
        {errors.confirmPassword && <p style={{ color: 'red' }}>{errors.confirmPassword}</p>}
      </div>

      <button type="submit">Registruj se</button>
    </form>
  )
}

export default RegisterPage