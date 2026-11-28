import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { clearToken, getToken } from '../utils/auth.js'

const FILES_API_URL = import.meta.env.VITE_FILES_API_URL
const SERVER_UNAVAILABLE_MESSAGE = 'Server trenutno nije dostupan. Pokušajte kasnije.'
const SESSION_EXPIRED_MESSAGE = 'Sesija je istekla. Prijavite se ponovo.'
const FORBIDDEN_NAME_CHARS = /[/\\]/

function validateFolderName(name) {
  const value = name.trim()
  if (!value) return 'Naziv foldera je obavezan.'
  if (value.length > 255) return 'Naziv foldera može imati najviše 255 karaktera.'
  if (FORBIDDEN_NAME_CHARS.test(value)) return 'Naziv foldera ne sme sadržati znakove / i \\.'
  if (/^\.+$/.test(value)) return 'Naziv foldera nije dozvoljen.'
  return ''
}

function DrivePage() {
  const navigate = useNavigate()
  const { folderId = 'root' } = useParams()
  const [token] = useState(() => getToken())
  const [reloadKey, setReloadKey] = useState(0)
  const [result, setResult] = useState({ key: null, items: [], path: [], error: '' })
  const [newName, setNewName] = useState('')
  const [nameError, setNameError] = useState('')
  const [creating, setCreating] = useState(false)

  const requestKey = `${folderId}:${reloadKey}`
  const loading = result.key !== requestKey
  const errorMessage = loading ? '' : result.error

  useEffect(() => {
    if (!token) return

    let active = true
    const key = `${folderId}:${reloadKey}`
    const headers = { Authorization: `Bearer ${token}` }
    const id = encodeURIComponent(folderId)

    Promise.all([
      fetch(`${FILES_API_URL}/folders/${id}/content`, { headers }),
      fetch(`${FILES_API_URL}/folders/${id}/path`, { headers }),
    ])
      .then(async ([contentResponse, pathResponse]) => {
        if (!active) return

        if (contentResponse.status === 401 || pathResponse.status === 401) {
          clearToken()
          navigate('/login', { replace: true, state: { message: SESSION_EXPIRED_MESSAGE } })
          return
        }
        if (!contentResponse.ok || !pathResponse.ok) {
          const data = await contentResponse.json().catch(() => ({}))
          setResult({ key, items: [], path: [], error: data.detail || SERVER_UNAVAILABLE_MESSAGE })
          return
        }

        const items = await contentResponse.json()
        const path = await pathResponse.json()
        if (active) {
          setResult({ key, items, path, error: '' })
        }
      })
      .catch(() => {
        if (active) {
          setResult({ key, items: [], path: [], error: SERVER_UNAVAILABLE_MESSAGE })
        }
      })

    return () => {
      active = false
    }
  }, [token, folderId, reloadKey, navigate])

  if (!token) {
    return <Navigate to="/login" replace />
  }

  async function handleCreateFolder(e) {
    e.preventDefault()

    const validationError = validateFolderName(newName)
    setNameError(validationError)
    if (validationError) return

    setCreating(true)
    try {
      const response = await fetch(`${FILES_API_URL}/folders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newName.trim(),
          parent_id: folderId === 'root' ? null : folderId,
        }),
      })
      const data = await response.json().catch(() => ({}))

      if (response.status === 401) {
        clearToken()
        navigate('/login', { replace: true, state: { message: SESSION_EXPIRED_MESSAGE } })
        return
      }
      if (!response.ok) {
        setNameError(data.errors?.name || data.detail || 'Kreiranje foldera nije uspelo.')
        return
      }

      setNewName('')
      setReloadKey((current) => current + 1)
    } catch {
      setNameError(SERVER_UNAVAILABLE_MESSAGE)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div>
      <h2>Moj disk</h2>

      <nav>
        <Link to="/drive">Moj disk</Link>
        {result.path.map((folder) => (
          <span key={folder.id}>
            {' / '}
            <Link to={`/drive/${folder.id}`}>{folder.name}</Link>
          </span>
        ))}
      </nav>

      <form onSubmit={handleCreateFolder} noValidate>
        <input
          aria-label="Naziv novog foldera"
          placeholder="Naziv novog foldera"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          maxLength={255}
        />
        <button type="submit" disabled={creating || loading || Boolean(errorMessage)}>
          {creating ? 'Kreiranje...' : 'Novi folder'}
        </button>
        {nameError && <p style={{ color: 'red' }}>{nameError}</p>}
      </form>

      {loading && <p>Učitavanje...</p>}
      {errorMessage && (
        <p style={{ color: 'red' }}>
          {errorMessage} <Link to="/drive">Nazad na Moj disk</Link>
        </p>
      )}

      {!loading && !errorMessage && result.items.length === 0 && <p>Folder je prazan.</p>}

      {!loading && !errorMessage && result.items.length > 0 && (
        <ul>
          {result.items.map((item) => (
            <li key={item.id}>
              {item.type === 'folder' ? (
                <Link to={`/drive/${item.id}`}>📁 {item.name}</Link>
              ) : (
                <span>📄 {item.name}</span>
              )}
            </li>
          ))}
        </ul>
      )}

      <p>
        <Link to="/">Nazad na početnu</Link>
      </p>
    </div>
  )
}

export default DrivePage