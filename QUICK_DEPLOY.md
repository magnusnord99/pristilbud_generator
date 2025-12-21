# 🚀 Rask Deploy Guide

## Du må deploye de nye endringene!

Endringene vi har gjort (nye endpoints `/api/quotes/data` og `/api/quotes/pdf`) er kun lokalt. De må push til Cloud Run.

---

## Alternativ 1: Deploy via GitHub (Automatisk) ⭐ Anbefalt

Hvis koden din er på GitHub:

1. **Commit endringene:**
```bash
cd /Users/magnusnordmo/Desktop/pristilbud_generator_api
git add .
git commit -m "Add API key support and new quote endpoints"
git push origin main
```

2. **GitHub Actions deployer automatisk!**
   - Gå til: https://github.com/DIN_BRUKERNAVN/pristilbud_generator_api/actions
   - Vent til deploy er ferdig (~5-10 minutter)

3. **Ferdig!** Nye endpointene er nå live.

---

## Alternativ 2: Deploy manuelt via gcloud CLI

Hvis du vil deploye manuelt (eller hvis GitHub Actions ikke fungerer):

### Steg 1: Naviger til backend-mappen

```bash
cd /Users/magnusnordmo/Desktop/pristilbud_generator_api/backend
```

### Steg 2: Bygg og push Docker image

```bash
gcloud builds submit --tag gcr.io/smoringauto/pristilbud-backend
```

**Dette tar 2-5 minutter.** Vent til det er ferdig.

### Steg 3: Deploy til Cloud Run

Hvis du har eksisterende miljøvariabler (GOOGLE_CREDENTIALS_JSON), deploy slik:

```bash
gcloud run deploy pristilbud-backend \
  --image gcr.io/smoringauto/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --update-env-vars GOOGLE_CREDENTIALS_JSON="$(cat .cloudrun.env.yaml | grep GOOGLE_CREDENTIALS_JSON | cut -d"'" -f2)"
```

Eller hvis du ikke har credentials-fil:

```bash
gcloud run deploy pristilbud-backend \
  --image gcr.io/smoringauto/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated
```

**Viktig:** Hvis du har lagt til `API_KEY` miljøvariabel i Cloud Console, legg den til her også:

```bash
gcloud run deploy pristilbud-backend \
  --image gcr.io/smoringauto/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --update-env-vars API_KEY="DIN_API_KEY_HER"
```

### Steg 4: Test at det fungerer

```bash
# Test at nye endpoint eksisterer
curl https://pristilbud-backend-288294266038.europe-north1.run.app/api/quotes/data

# Du skal få en 405 Method Not Allowed eller lignende (ikke 404 Not Found)
# 404 = endpoint finnes ikke (deploy feilet)
# 405 = endpoint finnes, men du må bruke POST (deploy fungerte!)
```

---

## Alternativ 3: Via Cloud Console (GUI)

1. **Gå til Cloud Build:**
   https://console.cloud.google.com/cloud-build/builds

2. **Klikk "TRIGGER BUILD" eller "CREATE BUILD"**

3. **Velg "Dockerfile"**

4. **Konfigurer:**
   - Source: Upload fra din maskin (velg `backend/` mappen)
   - Dockerfile: `backend/Dockerfile`
   - Image name: `gcr.io/smoringauto/pristilbud-backend`

5. **Klikk "RUN"**

6. **Etter build, deploy til Cloud Run:**
   - Gå til: https://console.cloud.google.com/run
   - Finn `pristilbud-backend`
   - Klikk "EDIT & DEPLOY NEW REVISION"
   - Container image URL: `gcr.io/smoringauto/pristilbud-backend`
   - Klikk "DEPLOY"

---

## ✅ Verifiser at deploy fungerte

Etter deploy, test at de nye endpointene eksisterer:

```bash
# Test health endpoint (skal fungere)
curl https://pristilbud-backend-288294266038.europe-north1.run.app/health

# Test nye endpoint (skal gi 422 eller 401, IKKE 404)
curl -X POST https://pristilbud-backend-288294266038.europe-north1.run.app/api/quotes/data \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Hvis du får 404 Not Found:**
- Deploy feilet eller bruker gammel kode
- Prøv deploy på nytt

**Hvis du får 401 Unauthorized eller 422 Unprocessable Entity:**
- ✅ Deploy fungerte! Endpointet eksisterer
- Du trenger bare å legge til autentisering (API key)

---

## 🎯 Hva skal skje etter deploy?

1. ✅ `/api/quotes/data` endpoint eksisterer
2. ✅ `/api/quotes/pdf` endpoint eksisterer  
3. ✅ API key autentisering fungerer
4. ✅ Next.js kan nå kalle API-et

---

## 💡 Tips

**Hvis GitHub Actions ikke kjører automatisk:**
- Sjekk at workflow-filen er på `main` branch
- Sjekk at GitHub Actions er aktivert i repo-innstillinger
- Sjekk "Actions" tab for feilmeldinger

**Hvis manuell deploy feiler:**
- Sjekk at du er logget inn: `gcloud auth login`
- Sjekk at prosjekt er riktig: `gcloud config set project smoringauto`
- Sjekk at du har riktige tilganger i Cloud Console

