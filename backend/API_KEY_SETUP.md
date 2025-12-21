# API Key Setup for Server-Side Authentication

## Oversikt

For å bruke API-et fra Next.js eller andre server-side applikasjoner, kan du bruke en API key i stedet for JWT tokens. API keys utløper ikke og er perfekte for server-side integrasjoner.

## Hvordan sette opp API Key

### Metode 1: Bruk eksisterende miljøvariabel

Hvis du allerede har satt `QUOTE_API_TOKEN` i backend-miljøvariablene, vil den automatisk fungere.

### Metode 2: Generer ny API key via admin endpoint

1. **Logg inn som admin** (via frontend eller test endpoint)
2. **Kall admin endpoint** for å generere ny key:

```bash
curl -X POST https://pristilbud-backend-288294266038.europe-north1.run.app/admin/generate-api-key \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response:**
```json
{
  "api_key": "generated-api-key-here",
  "message": "Save this API key securely. It will not be shown again.",
  "usage": "Use this as QUOTE_API_TOKEN in your Next.js .env.local file",
  "header_format": "Authorization: Bearer generated-api-key-here"
}
```

3. **Lagre API key** i backend miljøvariabler:
   - I Cloud Run: Sett `API_KEY` eller `QUOTE_API_TOKEN` environment variable
   - Lokalt: Legg til i `.env` fil

### Metode 3: Sett manuelt

Opprett en sikker API key selv og sett den som miljøvariabel:

```bash
# Generer en sikker key (32 bytes base64-encoded)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Sett den i backend-miljøvariabler som `API_KEY` eller `QUOTE_API_TOKEN`.

## Bruke API Key i Next.js

### 1. Legg til i `.env.local`:

```env
QUOTE_API_URL=https://pristilbud-backend-288294266038.europe-north1.run.app
QUOTE_API_TOKEN=din-api-key-her
```

### 2. Bruk i Next.js API routes:

```typescript
const response = await fetch(`${backendUrl}/api/quotes/data`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.QUOTE_API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ url: googleSheetsUrl })
})
```

## Fordeler med API Key

✅ **Utløper ikke** - Perfekt for server-side bruk
✅ **Enkel** - Ingen refresh token logikk nødvendig
✅ **Sikker** - Kun tilgjengelig server-side (ikke eksponert til browser)
✅ **Ingen rate limiting** - Server-side kall er ikke rate-limited

## Sikkerhet

⚠️ **VIKTIG:**
- Lagre API key **kun** i server-side miljøvariabler
- **Aldri** committ API key til git
- Bruk **aldri** API key i frontend-kode (kun i Next.js API routes/server-side)
- Roter API key regelmessig hvis den blir kompromittert

## Eksempel: Full Next.js integrasjon

```typescript
// app/api/fetch-quote/route.ts
export async function POST(request: Request) {
  const { url } = await request.json()
  
  const backendUrl = process.env.QUOTE_API_URL
  const apiToken = process.env.QUOTE_API_TOKEN
  
  const response = await fetch(`${backendUrl}/api/quotes/data`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url })
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch quote data')
  }
  
  const data = await response.json()
  
  // Transform data til ditt format
  return Response.json({
    // ... transformed data
    _originalData: data  // Behold original for PDF-generering
  })
}
```

## Test API Key

```bash
curl -X POST https://pristilbud-backend-288294266038.europe-north1.run.app/api/quotes/data \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "GOOGLE_SHEETS_URL"}'
```

Hvis det fungerer, får du JSON-data tilbake. Hvis ikke, får du 401 Unauthorized.

