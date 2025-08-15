import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { config } from '../config'

export default function LoginPage() {
  const [invitationCode, setInvitationCode] = useState('')
  const [googleToken, setGoogleToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setLoading(true)

    try {
      // Get backend URL from config
      const backendUrl = config.backendUrl;
      console.log('Using backend URL:', backendUrl);
      
      // First verify invitation
      try {
        const inviteResponse = await fetch(`${backendUrl}/invitations/use`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ invitation_code: invitationCode })
        })
        
        if (!inviteResponse.ok) {
          const error = await inviteResponse.text()
          setError('Ugyldig invitasjonskode: ' + error)
          return
        }
        
        // Then authenticate with Google
        const authResponse = await fetch(`${backendUrl}/auth/google`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ google_token: googleToken })
        })
        
        if (authResponse.ok) {
          const authData = await authResponse.json()
          localStorage.setItem('access_token', authData.access_token)
          localStorage.setItem('refresh_token', authData.refresh_token)
          setSuccess('Innlogging vellykket! Du kan nå bruke API-et.')
        } else {
          const error = await authResponse.text()
          setError('Innlogging feilet: ' + error)
        }
      } catch (error) {
        setError('En feil oppstod: ' + (error instanceof Error ? error.message : String(error)))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'En feil oppstod')
    } finally {
      setLoading(false)
    }
  }

  const handleTestMode = async () => {
    setError(null)
    setSuccess(null)
    setLoading(true)

    try {
      // Get backend URL from config
      const backendUrl = config.backendUrl
      
      // Use test endpoint that bypasses Google OAuth
      const response = await fetch(`${backendUrl}/test/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (response.ok) {
        const authData = await response.json()
        
        // Store tokens in localStorage
        localStorage.setItem('access_token', authData.access_token)
        localStorage.setItem('refresh_token', authData.refresh_token)
        localStorage.setItem('user', JSON.stringify(authData.user))
        
        setSuccess('Test innlogging vellykket! Omdirigerer...')
        
        // Redirect to main page after successful login
        setTimeout(() => {
          navigate('/')
        }, 1500)
      } else {
        const errorText = await response.text()
        throw new Error(`Test innlogging feilet: ${errorText}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'En feil oppstod')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      maxWidth: '500px',
      margin: '0 auto',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        border: '1px solid #e1e5e9',
        position: 'relative'
      }}>
        {/* Leafilms Logo */}
        <div style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          display: 'flex',
          alignItems: 'center'
        }}>
          <span style={{
            color: '#000000',
            fontWeight: '700',
            fontSize: '1.2rem',
            letterSpacing: '0.5px'
          }}>
            Leafilms
          </span>
        </div>

        <h1 style={{
          margin: '0 0 24px 0',
          color: '#2c3e50',
          fontSize: '2rem',
          fontWeight: '600',
          textAlign: 'center',
          marginTop: '20px'
        }}>
          Logg inn
        </h1>
        
        <p style={{
          margin: '0 0 24px 0',
          color: '#5a6c7d',
          fontSize: '1.1rem',
          lineHeight: '1.6',
          textAlign: 'center'
        }}>
          Du må ha en invitasjonskode for å bruke tjenesten.
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
              Invitasjonskode
            </label>
            <input
              type="text"
              value={invitationCode}
              onChange={(e) => setInvitationCode(e.target.value)}
              required
              placeholder="Skriv inn invitasjonskode"
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

          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '500',
              color: '#2c3e50',
              fontSize: '1rem'
            }}>
              Google Token (for testing)
            </label>
            <input
              type="text"
              value={googleToken}
              onChange={(e) => setGoogleToken(e.target.value)}
              required
              placeholder="Google OAuth token for testing"
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
            <small style={{
              color: '#6b7280',
              fontSize: '0.875rem',
              marginTop: '4px',
              display: 'block'
            }}>
              Dette er for testing. Senere erstatter vi med Google Sign-In knapp.
            </small>
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
            {loading ? 'Logger inn...' : 'Logg inn'}
          </button>
        </form>

        {/* Test Mode Button */}
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <div style={{
            borderTop: '1px solid #e5e7eb',
            paddingTop: '24px'
          }}>
            <p style={{
              color: '#6b7280',
              fontSize: '0.9rem',
              marginBottom: '16px'
            }}>
              🧪 Test Mode (bypass OAuth)
            </p>
            <button
              onClick={handleTestMode}
              disabled={loading}
              style={{
                padding: '12px 24px',
                backgroundColor: loading ? '#9ca3af' : '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '0.9rem',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s'
              }}
            >
              {loading ? 'Tester...' : 'Test Innlogging (Admin)'}
            </button>
          </div>
        </div>

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

        {success && (
          <div style={{
            marginTop: '20px',
            padding: '16px',
            backgroundColor: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '8px',
            color: '#16a34a',
            fontSize: '0.95rem'
          }}>
            ✅ {success}
          </div>
        )}
      </div>
    </div>
  )
}
