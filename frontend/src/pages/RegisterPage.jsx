import { useState } from 'react'

function RegisterPage() {
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  function handleChange(e) {
    const { name, value } = e.target
    setForm({ ...form, [name]: value })
  }

  function handleSubmit(e) {
    e.preventDefault()
    console.log('Forma poslata:', form.email)
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Registracija</h2>

      <div>
        <label htmlFor="firstName">Ime</label>
        <input id="firstName" name="firstName" value={form.firstName} onChange={handleChange} />
      </div>

      <div>
        <label htmlFor="lastName">Prezime</label>
        <input id="lastName" name="lastName" value={form.lastName} onChange={handleChange} />
      </div>

      <div>
        <label htmlFor="email">Imejl</label>
        <input id="email" name="email" type="email" value={form.email} onChange={handleChange} />
      </div>

      <div>
        <label htmlFor="password">Lozinka</label>
        <input id="password" name="password" type="password" value={form.password} onChange={handleChange} />
      </div>

      <div>
        <label htmlFor="confirmPassword">Ponovljena lozinka</label>
        <input id="confirmPassword" name="confirmPassword" type="password" value={form.confirmPassword} onChange={handleChange} />
      </div>

      <button type="submit">Registruj se</button>
    </form>
  )
}

export default RegisterPage