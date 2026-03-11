# Fix: Container feiler ved oppstart

## Problem
Containeren starter ikke. Dette kan være fordi:
1. Appen feiler ved startup (startup_event)
2. Manglende miljøvariabler
3. Import-feil i ny kode

## Løsning 1: Sjekk at services mappen er inkludert i Docker

Sjekk at `services/` mappen blir kopiert til Docker image. I Dockerfile:
```dockerfile
COPY . .  # Denne skal kopiere alt, inkludert services/
```

## Løsning 2: Deploy med miljøvariabler

Containeren kan feile hvis `GOOGLE_CREDENTIALS_JSON` mangler ved oppstart:

```bash
cd backend
gcloud run deploy pristilbud-backend \
  --image gcr.io/smoringauto/pristilbud-backend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --port 8080 \
  --env-vars-file .cloudrun.env.yaml \
  --timeout 300 \
  --memory 512Mi
```

## Løsning 3: Sjekk logs

Gå til Cloud Run logs og se hva som faktisk feiler:
https://console.cloud.google.com/logs/query?project=smoringauto

Filtrer på:
- Resource: Cloud Run Revision
- Service: pristilbud-backend
- Siste 10 minutter

Se etter:
- Import errors
- Startup errors
- Missing credentials errors

## Løsning 4: Test lokalt først

Test at koden fungerer lokalt før deploy:

```bash
cd backend
python3 -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
python3 -c "from services.quote_service import fetch_quote_data; print('OK')"
```

## Løsning 5: Midlertidig fix - Gjør startup mer robust

Hvis startup feiler, kan vi gjøre det mer robust ved å ikke feile ved manglende credentials:

I `main.py`, endre startup_event til å ikke feile:

```python
@app.on_event("startup")
async def startup_event():
    """Initialize database and create required directories"""
    try:
        # ... existing code ...
    except Exception as e:
        print(f"⚠️ Warning during startup: {e}")
        # Don't raise - let app continue
```

