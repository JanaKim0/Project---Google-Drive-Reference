import { Link } from 'react-router-dom'

function HomePage() {
  return (
    <div>
      <p>pocetna stranica cheeeeck</p>
      <p>welcome</p>
      <Link to="/register">Registracija</Link>
    </div>
  )
}

export default HomePage