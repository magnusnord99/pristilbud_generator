# Enkel Forklaring - Hva er problemet og løsningen?

## 🔴 PROBLEMET

### Din situasjon:
1. **Python API** (Pristilbud Generator) - kjører på Cloud Run
2. **Next.js system** (ditt andre prosjekt) - skal hente data fra Python API

### Problemet:
```
Next.js (server-side)
    ↓
Prøver å kalle Python API
    ↓
Python API sier: "Du må autentisere deg!"
    ↓
Next.js: "Hvordan?! Jeg er en server, ikke en browser!"
```

**Før:** Python API kunne bare autentisere brukere som logget inn via browser (JWT tokens).
- JWT tokens utløper etter 30 minutter
- JWT tokens lagres i browser (localStorage)
- Server-side applikasjoner kan ikke bruke browser-tokens

---

## ✅ LØSNINGEN

Lagt til **API Key** støtte i Python API-et.

**API Key** = En hemmelig nøkkel som:
- ✅ Utløper IKKE (varer evig)
- ✅ Fungerer server-side (perfekt for Next.js)
- ✅ Enkel å bruke (bare legg i miljøvariabel)

---

## 🎯 HVORFOR DU TRENGER DETTE

Når Next.js skal kalle Python API fra server-side:

```typescript
// Next.js server-side kode
const response = await fetch('https://python-api.com/api/quotes/data', {
  headers: {
    'Authorization': 'Bearer ???'  // <-- Hva skal her stå?!
  }
})
```

**Før:** Ingen god løsning (JWT tokens fungerte ikke server-side)  
**Nå:** Bruk API Key! 

```typescript
const apiToken = process.env.QUOTE_API_TOKEN  // ← API key fra miljøvariabel
const response = await fetch('...', {
  headers: {
    'Authorization': `Bearer ${apiToken}`  // ← Fungerer perfekt!
  }
})
```

---

## 📋 HVORDAN DET FUNGERER NÅ

### 1. **Python API** aksepterer to typer autentisering:

**Type A: JWT Token** (for browser/frontend)
- Brukere logger inn via Google OAuth
- Får JWT token som varer 30 minutter
- Lagres i browser

**Type B: API Key** (for server-side/Next.js) ✨ NYTT!
- En lang hemmelig streng
- Lagres i miljøvariabel
- Utløper aldri

### 2. **Automatisk deteksjon:**
Når Python API mottar en request:
```
Hvis token ser ut som API key → behandl som API key
Hvis ikke → behandle som JWT token
```

---

## 🔧 HVA DU MÅ GJØRE

### Steg 1: Sett opp API Key i Python API

**I Google Cloud Run** (der Python API kjører):
- Legg til miljøvariabel: `API_KEY` eller `QUOTE_API_TOKEN`
- Verdi: En hemmelig streng (f.eks. generert med: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)

### Steg 2: Sett API Key i Next.js

**I Next.js `.env.local`:**
```env
QUOTE_API_URL=https://pristilbud-backend-288294266038.europe-north1.run.app
QUOTE_API_TOKEN=din-api-key-her
```

### Steg 3: Bruk i Next.js kode

Din Next.js kode bruker allerede `QUOTE_API_TOKEN`, så det skal fungere automatisk! 🎉

---

## 📊 FLOW DIAGRAM

### FØR (ikke fungerte):
```
Next.js Server
    ↓
Kaller Python API
    ↓
Python API: "Trenger JWT token!"
    ↓
Next.js: "Jeg har ikke noen bruker som er logget inn 😢"
    ↓
❌ FAIL
```

### NÅ (fungerer):
```
Next.js Server
    ↓
Leser QUOTE_API_TOKEN fra .env.local
    ↓
Kaller Python API med: Authorization: Bearer <API_KEY>
    ↓
Python API: "Det er en API key! La meg sjekke..."
    ↓
Python API: "API key er gyldig! ✅"
    ↓
Returnerer data
    ↓
✅ SUCCESS
```

---

## 🔐 SIKKERHET

**Viktig:** 
- API Key er som en nøkkel til huset ditt
- Lagre den **kun** i server-side miljøvariabler
- **Aldri** i frontend-kode eller git
- Hvis den lekker ut, generer en ny

---

## 💡 SAMMENDRAG

**Problem:** Next.js (server-side) kunne ikke autentisere mot Python API  
**Løsning:** Lagt til API Key støtte  
**Resultat:** Next.js kan nå autentisere med API key fra miljøvariabel  

**Du trenger bare:**
1. Sett `API_KEY` i Python API (Cloud Run miljøvariabel)
2. Sett `QUOTE_API_TOKEN` i Next.js (`.env.local`)
3. Koden din fungerer! 🎉

---

## ❓ FORTSATT FORVIRRET?

**Spørsmål:** "Hvorfor kan jeg ikke bare bruke JWT token i Next.js?"  
**Svar:** JWT tokens utløper og må refreshes. De er lagret i browser. Next.js kjører på serveren, ikke i browser.

**Spørsmål:** "Hvorfor trenger jeg autentisering i det hele tatt?"  
**Svar:** For å beskytte API-et mot uautorisert tilgang. Uten autentisering kan hvem som helst kalle API-et.

**Spørsmål:** "Er API key trygg?"  
**Svar:** Ja, hvis du lagrer den sikkert (kun server-side, ikke i git). Den fungerer som et passord for serveren din.

