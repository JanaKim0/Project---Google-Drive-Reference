import { useState } from 'react'
import { validateRegisterForm } from '../utils/validation.js'

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
        <input id="firstName" name="firstName" value={form.firstName} onChange={handleChange} maxLength={50} />
        {errors.firstName && <p style={{ color: 'red' }}>{errors.firstName}</p>}
      </div>

      <div>
        <label htmlFor="lastName">Prezime</label>
        <input id="lastName" name="lastName" value={form.lastName} onChange={handleChange} maxLength={50} />
        {errors.lastName && <p style={{ color: 'red' }}>{errors.lastName}</p>}
      </div>

      <div>
        <label htmlFor="email">Imejl</label>
        <input id="email" name="email" type="email" value={form.email} onChange={handleChange} maxLength={254} />
        {errors.email && <p style={{ color: 'red' }}>{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="password">Lozinka</label>
        <input id="password" name="password" type="password" value={form.password} onChange={handleChange} maxLength={64} />
        {errors.password && <p style={{ color: 'red' }}>{errors.password}</p>}
      </div>

      <div>
        <label htmlFor="confirmPassword">Ponovljena lozinka</label>
        <input id="confirmPassword" name="confirmPassword" type="password" value={form.confirmPassword} onChange={handleChange} maxLength={64} />
        {errors.confirmPassword && <p style={{ color: 'red' }}>{errors.confirmPassword}</p>}
      </div>

      <button type="submit">Registruj se</button>
    </form>
  )
}

export default RegisterPage