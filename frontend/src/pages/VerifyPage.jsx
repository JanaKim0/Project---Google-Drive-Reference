import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

const API_URL = import.meta.env.VITE_API_URL

function VerifyPage() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('loading')
  const [message, setMessage] = useState('')
  const requestSent = useRef(false)

  useEffect(() => {
    if (requestSent.current) {
      return
    }
    requestSent.current = true

    const token = searchParams.get('token')
    if (!token) {
      setStatus('error')
      setMessage('Link za potvrdu nije ispravan.')
      return
    }

    fetch(`${API_URL}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })
      .then(async (response) => {
        const data = await response.json()
        if (response.ok) {
          setStatus('success')
          setMessage(data.message)
        } else {
          setStatus('error')
          setMessage(data.detail || 'Potvrda naloga nije uspela.')
        }
      })
      .catch(() => {
        setStatus('error')
        setMessage('Server trenutno nije dostupan. Pokušajte kasnije.')
      })
  }, [searchParams])

  return (
    <div>
      <h2>Potvrda naloga</h2>
      {status === 'loading' && <p>Potvrđujemo nalog...</p>}
      {status === 'success' && <p style={{ color: 'green' }}>{message}</p>}
      {status === 'error' && <p style={{ color: 'red' }}>{message}</p>}
      {status !== 'loading' && <Link to="/">Nazad na početnu</Link>}
    </div>
  )
}

export default VerifyPage