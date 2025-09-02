## Pristilbud Generator

Monorepo med backend (FastAPI) og frontend (Vite React + TS) for å generere PDF-pristilbud fra Google Sheets.

### Backend

Krav:
- Python 3.13
- `backend/credentials.json` (Google service account) eller `GOOGLE_APPLICATION_CREDENTIALS` env var

Kjør lokalt:
```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Tester:
```bash
cd backend
PYTHONPATH=. pytest -q
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host
```
Åpne `http://localhost:5173`. Dev-proxy ruter `/generate-pdf` til `http://localhost:8000`.

### Deploy (skisse)
Bruk Google Cloud Run.

#### Backend → Cloud Run
1. Bygg og push image (erstatt `PROJECT_ID`):
```bash
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/pristilbud-backend
```
2. Deploy til Cloud Run:
```bash
gcloud run deploy pristilbud-backend \
  --image gcr.io/PROJECT_ID/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CREDENTIALS_JSON="$(cat credentials.json | tr '\n' ' ')"
```
3. Notér URL-en som returneres (f.eks. `https://pristilbud-backend-xxxx.a.run.app`).

#### Frontend → Cloud Run (statisk)
1. Bygg lokalt (eller med Cloud Build) og server med `serve` image:
```bash
cd frontend
docker build -t gcr.io/PROJECT_ID/pristilbud-frontend .
docker push gcr.io/PROJECT_ID/pristilbud-frontend
```
2. Deploy (angi backend-URL for prod):
```bash
gcloud run deploy pristilbud-frontend \
  --image gcr.io/PROJECT_ID/pristilbud-frontend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --set-env-vars VITE_BACKEND_URL="https://<BACKEND_URL>"
```

Tips:
- Alternativt: Host frontend på Vercel/Netlify og sett `VITE_BACKEND_URL` der.
- Ikke commit `credentials.json`. Bruk `GOOGLE_CREDENTIALS_JSON`.

# Test deployment Tue Sep  2 12:54:48 CEST 2025
# Test base64 credentials Tue Sep  2 13:36:27 CEST 2025
# Test correct base64 credentials Tue Sep  2 13:56:25 CEST 2025
