# Deploy Backend til Cloud Run

## 🚀 Rask Deploy Guide

### Forutsetninger:
- Du må ha `gcloud` CLI installert
- Du må være autentisert: `gcloud auth login`
- Du må ha riktig prosjekt valgt: `gcloud config set project PRISTILBUDBUDKONV` (eller ditt prosjekt-navn)

---

## Steg 1: Sjekk prosjekt og region

```bash
# Sjekk hvilket prosjekt du er i
gcloud config get-value project

# Sjekk hvilket prosjekt Cloud Run tjenesten kjører i
# (Sjekk i Google Cloud Console hvis du er usikker)
```

---

## Steg 2: Bygg og push Docker image

```bash
cd backend

# Bygg og push image til Google Container Registry
# Erstatt PRISTILBUDBUDKONV med ditt prosjekt-ID
gcloud builds submit --tag gcr.io/PRISTILBUDBUDKONV/pristilbud-backend
```

**Dette tar 2-5 minutter.** Vent til det er ferdig.

---

## Steg 3: Deploy til Cloud Run

```bash
# Deploy med eksisterende miljøvariabler
gcloud run deploy pristilbud-backend \
  --image gcr.io/PRISTILBUDBUDKONV/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated
```

**Viktig:** Hvis du har miljøvariabler (som `GOOGLE_CREDENTIALS_JSON` eller `API_KEY`), må du legge dem til:

```bash
gcloud run deploy pristilbud-backend \
  --image gcr.io/PRISTILBUDBUDKONV/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --update-env-vars GOOGLE_CREDENTIALS_JSON="$(cat credentials.json | tr '\n' ' ')",API_KEY="DIN_API_KEY_HER"
```

---

## Steg 4: Verifiser deploy

Etter deploy, test at de nye endpointene fungerer:

```bash
# Test health endpoint
curl https://pristilbud-backend-288294266038.europe-north1.run.app/health

# Test nye endpoint (hvis du har API key)
curl -X POST https://pristilbud-backend-288294266038.europe-north1.run.app/api/quotes/data \
  -H "Authorization: Bearer DIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "GOOGLE_SHEETS_URL"}'
```

---

## Alternativ: Deploy via Cloud Console

Hvis du foretrekker GUI:

1. Gå til: https://console.cloud.google.com/cloud-build/builds
2. Klikk "TRIGGER BUILD" eller "CREATE BUILD"
3. Velg "Cloud Build configuration file" eller "Dockerfile"
4. Velg `backend/Dockerfile`
5. Angi image: `gcr.io/PRISTILBUDBUDKONV/pristilbud-backend`
6. Klikk "RUN"

Etter build:
1. Gå til: https://console.cloud.google.com/run
2. Finn `pristilbud-backend`
3. Klikk "EDIT & DEPLOY NEW REVISION"
4. Under "Container image URL", lim inn: `gcr.io/PRISTILBUDBUDKONV/pristilbud-backend`
5. Klikk "DEPLOY"

---

## 🐛 Feilsøking

### Feil: "Permission denied"
```bash
# Sjekk at du er autentisert
gcloud auth login

# Sjekk at du har riktig prosjekt
gcloud config set project PRISTILBUDBUDKONV
```

### Feil: "Image not found"
- Sjekk at build var vellykket
- Sjekk at du bruker riktig prosjekt-ID

### Feil: "Service not found"
- Tjenesten kan ha et annet navn
- Sjekk i Cloud Console hva tjenesten heter

---

## 📝 Full kommando (alle steg)

```bash
# 1. Naviger til backend
cd backend

# 2. Bygg og push
gcloud builds submit --tag gcr.io/PRISTILBUDBUDKONV/pristilbud-backend

# 3. Deploy
gcloud run deploy pristilbud-backend \
  --image gcr.io/PRISTILBUDBUDKONV/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated
```

---

## ⚡ Rask deploy (hvis du allerede har bygget)

Hvis du bare har gjort kodeendringer (ikke dependency-endringer):

```bash
cd backend
gcloud builds submit --tag gcr.io/PRISTILBUDBUDKONV/pristilbud-backend && \
gcloud run deploy pristilbud-backend \
  --image gcr.io/PRISTILBUDBUDKONV/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated
```

