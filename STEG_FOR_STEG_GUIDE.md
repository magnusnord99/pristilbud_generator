# Steg-for-steg Guide: Slik får du API Key til å fungere

## 🎯 Oversikt
1. Generer en API key
2. Sett den i Python API (Cloud Run)
3. Sett den i Next.js (.env.local)
4. Test at det fungerer

---

## STEG 1: Generer API Key

### Alternativ A: Via Python (enklest)
Åpne terminal og kjør:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Kopier den lange strengen som vises** - dette er din API key!
(Eksempel: `xK9mP2qL8vR4nT7wY1zA5bC6dE9fG0hI3jK5lM8nO0pQ2rS4tU6vW8xY0zA`)

### Alternativ B: Via Admin Endpoint
Hvis du vil bruke admin endpoint (krever at du først er innlogget som admin):

```bash
# 1. Først, få admin token
curl -X POST https://pristilbud-backend-288294266038.europe-north1.run.app/test/auth

# 2. Kopier access_token fra responsen
# 3. Generer API key:
curl -X POST https://pristilbud-backend-288294266038.europe-north1.run.app/admin/generate-api-key \
  -H "Authorization: Bearer DIN_ACCESS_TOKEN_HER"
```

**Anbefaling:** Bruk Alternativ A (Python kommando) - enklere og raskere!

---

## STEG 2: Sett API Key i Python API (Cloud Run)

### Metode 1: Via Google Cloud Console (anbefalt)

1. **Gå til Google Cloud Console:**
   - https://console.cloud.google.com/
   - Velg ditt prosjekt

2. **Finn Cloud Run tjenesten:**
   - Gå til "Cloud Run" i venstre meny
   - Finn `pristilbud-backend` (eller hva tjenesten din heter)

3. **Rediger miljøvariabler:**
   - Klikk på tjenesten
   - Klikk "EDIT & DEPLOY NEW REVISION"
   - Scroll ned til "Variables & Secrets"
   - Klikk "ADD VARIABLE"

4. **Legg til API key:**
   - **Name:** `API_KEY`
   - **Value:** (lim inn API key-en du genererte i Steg 1)
   - Klikk "SAVE"

5. **Deploy:**
   - Scroll ned og klikk "DEPLOY"
   - Vent til deploy er ferdig (~1-2 minutter)

### Metode 2: Via gcloud CLI

```bash
# Sett API key (erstatt YOUR_API_KEY med den faktiske key-en)
gcloud run services update pristilbud-backend \
  --region=europe-north1 \
  --update-env-vars="API_KEY=YOUR_API_KEY_HER"
```

---

## STEG 3: Sett API Key i Next.js

1. **Finn `.env.local` filen** i Next.js prosjektet ditt
   - Hvis den ikke finnes, opprett den i roten av Next.js-prosjektet

2. **Legg til disse linjene:**

```env
QUOTE_API_URL=https://pristilbud-backend-288294266038.europe-north1.run.app
QUOTE_API_TOKEN=DIN_API_KEY_HER
```

**Viktig:** Erstatt `DIN_API_KEY_HER` med samme API key som du satte i Steg 2!

3. **Restart Next.js serveren:**
   - Stopp serveren (Ctrl+C)
   - Start den igjen (`npm run dev` eller `yarn dev`)

---

## STEG 4: Test at det fungerer

### Test 1: Test direkte mot Python API

```bash
curl -X POST https://pristilbud-backend-288294266038.europe-north1.run.app/api/quotes/data \
  -H "Authorization: Bearer DIN_API_KEY_HER" \
  -H "Content-Type: application/json" \
  -d '{"url": "EN_GOOGLE_SHEETS_URL_HER"}'
```

**Hvis det fungerer:**
- Du får JSON-data tilbake med quote informasjon
- ✅ Suksess!

**Hvis det ikke fungerer:**
- Du får `401 Unauthorized` eller lignende
- ❌ Sjekk at API key er riktig satt i Cloud Run

### Test 2: Test fra Next.js

1. **Åpne Next.js appen**
2. **Gå til et prosjekt i edit mode**
3. **Legg til "Pristilbud"-seksjon**
4. **Fyll inn Google Sheets URL**
5. **Klikk "Hent tilbud"**

**Hvis det fungerer:**
- Data vises interaktivt
- ✅ Alt fungerer!

**Hvis det ikke fungerer:**
- Sjekk Next.js server logs for feilmeldinger
- Sjekk at `.env.local` er riktig satt
- Sjekk at Next.js server er restartet

---

## ✅ Checkliste

Før du tester, sjekk at:

- [ ] API key er generert
- [ ] API key er satt i Cloud Run (`API_KEY` miljøvariabel)
- [ ] Cloud Run tjeneste er re-deployed
- [ ] API key er satt i Next.js `.env.local` (`QUOTE_API_TOKEN`)
- [ ] Next.js server er restartet
- [ ] Du bruker samme API key i begge steder

---

## 🐛 Feilsøking

### Problem: "401 Unauthorized"

**Mulige årsaker:**
1. API key er ikke satt i Cloud Run
   - **Løsning:** Sjekk Cloud Run miljøvariabler, sett `API_KEY`

2. API key er feil i Next.js
   - **Løsning:** Sjekk `.env.local`, sjekk at det er samme key som i Cloud Run

3. Cloud Run er ikke re-deployed etter endring
   - **Løsning:** Deploy Cloud Run tjenesten på nytt

### Problem: Next.js får ikke data

**Mulige årsaker:**
1. Next.js server er ikke restartet
   - **Løsning:** Restart Next.js server (Ctrl+C, så `npm run dev`)

2. `.env.local` filen er ikke lastet
   - **Løsning:** Sjekk at filen ligger i roten av Next.js-prosjektet

3. Feil miljøvariabel navn
   - **Løsning:** Sjekk at det heter `QUOTE_API_TOKEN` (ikke `API_KEY`)

### Problem: "Could not validate credentials"

**Mulige årsaker:**
- API key matcher ikke
- **Løsning:** Sjekk at du bruker eksakt samme streng i begge steder (ingen mellomrom, nye linjer, etc.)

---

## 📝 Eksempel på korrekt setup

**Cloud Run miljøvariabel:**
```
API_KEY=xK9mP2qL8vR4nT7wY1zA5bC6dE9fG0hI3jK5lM8nO0pQ2rS4tU6vW8xY0zA
```

**Next.js `.env.local`:**
```env
QUOTE_API_URL=https://pristilbud-backend-288294266038.europe-north1.run.app
QUOTE_API_TOKEN=xK9mP2qL8vR4nT7wY1zA5bC6dE9fG0hI3jK5lM8nO0pQ2rS4tU6vW8xY0zA
```

**Viktig:** Begge må være identiske!

---

## 🎉 Når det fungerer

Du skal nå kunne:
- ✅ Hente quote data fra Next.js
- ✅ Vise data interaktivt
- ✅ Generere PDF fra samme data

Alt skal fungere automatisk! 🚀

