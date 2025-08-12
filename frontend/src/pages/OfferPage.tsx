import { useMemo, useState } from 'react'

type Language = 'NO' | 'EN'
type YesNo = 'y' | 'n'

export default function OfferPage() {
  const [url, setUrl] = useState('')
  const [language, setLanguage] = useState<Language>('NO')
  const [reise, setReise] = useState<YesNo>('y')
  const [mva, setMva] = useState<YesNo>('y')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const isValid = useMemo(() => url.includes('/spreadsheets/d/'), [url])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!isValid) {
      setError('Ugyldig Google Sheets URL')
      return
    }
    setLoading(true)
    try {
      const base = import.meta.env.VITE_BACKEND_URL || ''
      const res = await fetch(base + '/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, language, reise, mva }),
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `Feil ${res.status}`)
      }
      const blob = await res.blob()
      const cd = res.headers.get('Content-Disposition') || 'attachment; filename="pristilbud.pdf"'
      const match = cd.match(/filename="?([^";]+)"?/i)
      const filename = match ? match[1] : 'pristilbud.pdf'
      const urlObj = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = urlObj
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(urlObj)
      a.remove()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ukjent feil')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      minHeight: '600px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        border: '1px solid #e1e5e9',
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{ flex: '1' }}>
          <h1 style={{
            margin: '0 0 20px 0',
            color: '#2c3e50',
            fontSize: '2rem',
            fontWeight: '600'
          }}>Pristilbud</h1>
          <p style={{
            margin: '0 0 24px 0',
            color: '#5a6c7d',
            fontSize: '1.1rem',
            lineHeight: '1.6'
          }}>Lim inn Google Sheets-URL og velg alternativer for å generere PDF.</p>

          <form onSubmit={handleSubmit} style={{ 
            display: 'grid', 
            gap: '20px',
            marginBottom: '20px'
          }}>
            <label style={{ display: 'grid', gap: '8px' }}>
              <div style={{ 
                fontWeight: '500', 
                color: '#2c3e50',
                fontSize: '1rem'
              }}>Google Sheets URL</div>
              <input
                type="url"
                placeholder="https://docs.google.com/spreadsheets/d/..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
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
            </label>

            <label style={{ display: 'grid', gap: '8px' }}>
              <div style={{ 
                fontWeight: '500', 
                color: '#2c3e50',
                fontSize: '1rem'
              }}>Språk</div>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value as Language)}
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  fontSize: '1rem',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
              >
                <option value="NO">Norsk</option>
                <option value="EN">English</option>
              </select>
            </label>

            <label style={{ display: 'grid', gap: '8px' }}>
              <div style={{ 
                fontWeight: '500', 
                color: '#2c3e50',
                fontSize: '1rem'
              }}>Inkluder reise</div>
              <select 
                value={reise} 
                onChange={(e) => setReise(e.target.value as YesNo)}
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  fontSize: '1rem',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
              >
                <option value="y">Ja</option>
                <option value="n">Nei</option>
              </select>
            </label>

            <label style={{ display: 'grid', gap: '8px' }}>
              <div style={{ 
                fontWeight: '500', 
                color: '#2c3e50',
                fontSize: '1rem'
              }}>Inkluder MVA</div>
              <select 
                value={mva} 
                onChange={(e) => setMva(e.target.value as YesNo)}
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  fontSize: '1rem',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
              >
                <option value="y">Ja</option>
                <option value="n">Nei</option>
              </select>
            </label>

            <button 
              type="submit" 
              disabled={loading || !isValid}
              style={{
                padding: '14px 24px',
                backgroundColor: loading || !isValid ? '#9ca3af' : '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '500',
                cursor: loading || !isValid ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s',
                marginTop: '8px'
              }}
            >
              {loading ? 'Genererer…' : 'Generer PDF'}
            </button>
          </form>

          {error && (
            <div style={{
              padding: '16px',
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              color: '#dc2626',
              fontSize: '0.95rem'
            }}>
              Feil: {error}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


