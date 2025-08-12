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
- Bruk Docker for konsistent kjøring og CI/CD.
- Håndter secrets via env vars, ikke committed filer.

