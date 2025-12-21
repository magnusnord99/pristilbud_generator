# API Refactoring - Strukturert Datahenting og PDF-generering

## Oversikt

Systemet er refaktorert for å separere datahenting fra PDF-generering. Dette gir mer fleksibilitet og lar deg:
- Hente data som JSON for interaktiv visning
- Bruke samme data til å generere PDF
- Unngå duplisert datahenting

## Ny Struktur

### Services Layer
- `services/quote_service.py` - Håndterer datahenting og forberedelse
  - `fetch_quote_data(url)` - Henter data fra Google Sheets
  - `prepare_quote_data_for_pdf(data)` - Forbereder data for PDF-generering

### PDF Generators
- `pdf_generators/price_quote.py` - PDF-generering
  - `generate_pdf_from_data(data, ...)` - Genererer PDF fra data (ny)
  - `generate_pdf(url, ...)` - Genererer PDF fra URL (beholdt for bakoverkompatibilitet)

## Nye API Endpoints

### 1. Hent Quote Data som JSON

**Endpoint:** `POST /api/quotes/data`

**Request:**
```json
{
  "url": "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit"
}
```

**Response:**
```json
{
  "grouped_sums": [
    ["Kategori 1", 1000.0],
    ["Kategori 2", 2000.0]
  ],
  "total_days": 5,
  "post_prod_days": 3,
  "pre_prod_days": 2,
  "details": {
    "Kunde": "Kundenavn",
    "Prosjekt": "Prosjektnavn",
    "Versjon": "v1.0",
    ...
  },
  "company_info": {
    "Adresse": "Gateadresse",
    ...
  },
  "total_excl_mva": 10000.0,
  "total_incl_mva": 12500.0,
  "sheet_id": "SPREADSHEET_ID"
}
```

**Autentisering:** Krever autentisering

**Bruk:**
```python
import requests

response = requests.post(
    "https://your-api-url/api/quotes/data",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"url": "GOOGLE_SHEETS_URL"}
)
data = response.json()
```

### 2. Generer PDF fra Data

**Endpoint:** `POST /api/quotes/pdf`

**Request:**
```json
{
  "data": {
    "grouped_sums": [...],
    "total_days": 5,
    ...
  },
  "language": "NO",
  "reise": "y",
  "mva": "y",
  "discount_percent": 10
}
```

**Response:** PDF-fil som binary stream

**Autentisering:** Krever autentisering

**Bruk:**
```python
# Først hent data
data_response = requests.post(
    "https://your-api-url/api/quotes/data",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"url": "GOOGLE_SHEETS_URL"}
)
data = data_response.json()

# Deretter generer PDF fra samme data
pdf_response = requests.post(
    "https://your-api-url/api/quotes/pdf",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "data": data,
        "language": "NO",
        "reise": "y",
        "mva": "y",
        "discount_percent": 10
    }
)

# Lagre PDF
with open("quote.pdf", "wb") as f:
    f.write(pdf_response.content)
```

## Eksisterende Endpoints (Uendret)

### `/generate-pdf` 
Fungerer fortsatt som før - henter data og genererer PDF i ett steg.

**Request:**
```json
{
  "url": "GOOGLE_SHEETS_URL",
  "language": "NO",
  "reise": "y",
  "mva": "y",
  "discount_percent": 10
}
```

## Anbefalt Flyt

### For interaktiv visning:
1. Kall `/api/quotes/data` for å hente data
2. Vis data interaktivt i ditt system
3. Kall `/api/quotes/pdf` hvis brukeren vil ha PDF (samme data)

### For kun PDF-generering:
- Bruk `/generate-pdf` (raskere, enklere)

## Fordeler med ny struktur

✅ **Separasjon av bekymringer**: Datahenting og PDF-generering er separert
✅ **Gjenbruk**: Hent data én gang, bruk flere ganger
✅ **Fleksibilitet**: Bruk data for interaktiv visning eller PDF
✅ **Bakoverkompatibilitet**: Gamle endpoints fungerer fortsatt
✅ **Bedre struktur**: Koden er mer organisert og vedlikeholdbar

## Migrering

Du trenger **ikke** å endre eksisterende kode. Den gamle `/generate-pdf` endpointen fungerer fortsatt som før.

For nye implementasjoner, bruk den nye strukturen:
1. `/api/quotes/data` - hent data
2. `/api/quotes/pdf` - generer PDF fra data

