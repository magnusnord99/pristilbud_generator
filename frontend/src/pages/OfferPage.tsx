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
      const res = await fetch('/generate-pdf', {
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
    <div>
      <h1>Pristilbud</h1>
      <p>Lim inn Google Sheets-URL og velg alternativer for å generere PDF.</p>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 16 }}>
        <label>
          <div>Google Sheets URL</div>
          <input
            type="url"
            placeholder="https://docs.google.com/spreadsheets/d/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            style={{ width: '100%', padding: 10 }}
          />
        </label>

        <label>
          <div>Språk</div>
          <select value={language} onChange={(e) => setLanguage(e.target.value as Language)}>
            <option value="NO">Norsk</option>
            <option value="EN">English</option>
          </select>
        </label>

        <label>
          <div>Inkluder reise</div>
          <select value={reise} onChange={(e) => setReise(e.target.value as YesNo)}>
            <option value="y">Ja</option>
            <option value="n">Nei</option>
          </select>
        </label>

        <label>
          <div>Inkluder MVA</div>
          <select value={mva} onChange={(e) => setMva(e.target.value as YesNo)}>
            <option value="y">Ja</option>
            <option value="n">Nei</option>
          </select>
        </label>

        <button type="submit" disabled={loading || !isValid}>
          {loading ? 'Genererer…' : 'Generer PDF'}
        </button>
      </form>

      {error && (
        <p style={{ color: 'crimson' }}>Feil: {error}</p>
      )}
    </div>
  )
}


