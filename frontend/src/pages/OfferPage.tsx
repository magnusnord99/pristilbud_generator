import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

export default function OfferPage() {
  const [url, setUrl] = useState('')
  const [language, setLanguage] = useState<'NO' | 'EN'>('NO')
  const [reise, setReise] = useState<'y' | 'n'>('y')
  const [mva, setMva] = useState<'y' | 'n'>('y')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { user, isAuthenticated } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Get access token from localStorage
      const accessToken = localStorage.getItem('access_token')
      if (!accessToken) {
        throw new Error('Ingen tilgangstoken funnet. Vennligst logg inn på nytt.')
      }

      const response = await fetch('http://127.0.0.1:8000/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}` // Add auth header
        },
        body: JSON.stringify({
          url,
          language,
          reise,
          mva
        })
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Sesjon utløpt. Vennligst logg inn på nytt.')
        }
        const errorData = await response.json()
        throw new Error(errorData.detail || 'En feil oppstod')
      }

      // Handle PDF download
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `pristilbud_${language}_${Date.now()}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(downloadUrl)
      document.body.removeChild(a)

      // Reset form
      setUrl('')
      setLanguage('NO')
      setReise('y')
      setMva('y')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'En feil oppstod')
    } finally {
      setLoading(false)
    }
  }

  // Show loading or error state
  if (!isAuthenticated) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        border: '1px solid #e1e5e9',
        minHeight: '400px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2>🔐 Innlogging kreves</h2>
          <p>Du må logge inn for å bruke denne funksjonen.</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '16px',
      padding: '32px',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
      border: '1px solid #e1e5e9',
      minHeight: '400px'
    }}>
      <h1 style={{
        margin: '0 0 24px 0',
        color: '#2c3e50',
        fontSize: '2rem',
        fontWeight: '600'
      }}>
        🎬 Generer Pristilbud
      </h1>
      
      <p style={{
        margin: '0 0 24px 0',
        color: '#5a6c7d',
        fontSize: '1.1rem',
        lineHeight: '1.6'
      }}>
        Logget inn som: <strong>{user?.name}</strong> ({user?.email})
      </p>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '20px' }}>
        <div>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: '500',
            color: '#2c3e50',
            fontSize: '1rem'
          }}>
            Google Sheets URL
          </label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            placeholder="https://docs.google.com/spreadsheets/d/..."
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #d1d5db',
              fontSize: '1rem',
              outline: 'none',
              transition: 'border-color 0.2s'
            }}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '500',
              color: '#2c3e50',
              fontSize: '1rem'
            }}>
              Språk
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as 'NO' | 'EN')}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                fontSize: '1rem',
                outline: 'none'
              }}
            >
              <option value="NO">Norsk</option>
              <option value="EN">English</option>
            </select>
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '500',
              color: '#2c3e50',
              fontSize: '1rem'
            }}>
              Reise
            </label>
            <select
              value={reise}
              onChange={(e) => setReise(e.target.value as 'y' | 'n')}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                fontSize: '1rem',
                outline: 'none'
              }}
            >
              <option value="y">Ja</option>
              <option value="n">Nei</option>
            </select>
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '500',
              color: '#2c3e50',
              fontSize: '1rem'
            }}>
              MVA
            </label>
            <select
              value={mva}
              onChange={(e) => setMva(e.target.value as 'y' | 'n')}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                fontSize: '1rem',
                outline: 'none'
              }}
            >
              <option value="y">Ja</option>
              <option value="n">Nei</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '14px 24px',
            backgroundColor: loading ? '#9ca3af' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '1rem',
            fontWeight: '500',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.2s',
            marginTop: '8px'
          }}
        >
          {loading ? 'Genererer PDF...' : 'Generer PDF'}
        </button>
      </form>

      {error && (
        <div style={{
          marginTop: '20px',
          padding: '16px',
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          color: '#dc2626',
          fontSize: '0.95rem'
        }}>
          ❌ {error}
        </div>
      )}
    </div>
  )
}


