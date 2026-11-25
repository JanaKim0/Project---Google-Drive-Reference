import { Link } from 'react-router-dom'
import { getToken } from '../utils/auth.js'

function HomePage() {
  const isLoggedIn = Boolean(getToken())

  return (
    <div>
      <p>pocetna stranica cheeeeck</p>
      <p>welcome</p>
      {isLoggedIn ? (
        <p style={{ color: 'green' }}>Uspešno ste prijavljeni.</p>
      ) : (
        <>
          <Link to="/register">Registracija</Link> | <Link to="/login">Prijava</Link>
        </>
      )}
    </div>
  )
}

export default HomePage