# Prosjektbeskrivelse Generator

Dette er en ny funksjonalitet som lar brukere generere profesjonelle prosjektbeskrivelser med AI-generert innhold og egne bilder.

## Funksjoner

### 1. Prosjekttype-valg
- **Event**: Festivaler, konferanser, lanseringer og andre arrangementer
- **Reklamekampanje**: Digital markedsføring, sosiale medier og tradisjonell reklame
- **Produktlansering**: Nye produkter, tjenester eller løsninger
- **Merkevarebygging**: Visuell identitet, logoer og merkevarestrategi

### 2. AI-generert innhold
Systemet genererer automatisk:
- **Mål**: Prosjektets hovedmål og ambisjoner
- **Konsept**: Hovedideen og tilnærmingen
- **Målgruppe**: Definisjon av målgruppen
- **Nøkkelfunksjoner**: Hovedfunksjoner og egenskaper
- **Tidsplan**: Foreslått tidsramme
- **Suksesskriterier**: Hvordan suksess måles

### 3. Bildeopplasting
- Last opp egne bilder for header, innhold og footer
- Automatisk bildebehandling og optimalisering
- Støtte for alle vanlige bildeformater (PNG, JPG, etc.)

### 4. PDF-generering
- Profesjonell layout med LEA FILMS branding
- Automatisk sidebryting
- Bildeplassering og tekstformatering
- Støtte for norsk og engelsk

## Teknisk implementering

### Backend (FastAPI)

#### Nye endepunkter:
- `GET /project-types` - Hent tilgjengelige prosjekttyper
- `POST /generate-content` - Generer AI-innhold
- `POST /upload-image` - Last opp bilder
- `POST /generate-project-description` - Generer PDF
- `GET /uploads/{filename}` - Server opplastede bilder
- `GET /downloads/{filename}` - Server genererte PDF-er

#### Nye modeller:
```python
class ProjectType(BaseModel):
    id: str
    name: str
    description: str
    template_prompts: List[str]

class GeneratedContent(BaseModel):
    goals: str
    concept: str
    target_audience: str
    key_features: str
    timeline: str
    success_metrics: str

class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    url: str
    placeholder_type: str
```

#### PDF-generering:
- Bruker ReportLab for PDF-generering
- Automatisk sidebryting basert på innhold
- Bildeplassering med feilhåndtering
- Responsivt layout-system

### Frontend (React/TypeScript)

#### Komponenter:
- **Stegbasert grensesnitt** med 3 hovedsteg
- **Prosjekttype-valg** med dropdown
- **Innholdsgenerering** med AI
- **Bildeopplasting** med drag & drop
- **PDF-generering** og nedlasting

#### State management:
- React hooks for lokal state
- API-integrasjon med backend
- Feilhåndtering og loading states
- Responsivt design

## Installasjon og oppsett

### Backend-avhengigheter
```bash
cd backend
pip install -r requirements.txt
```

**Nye avhengigheter:**
- `Pillow` - Bildebehandling
- `python-multipart` - Filopplasting (allerede inkludert)

### Mappestruktur
```
backend/
├── uploads/          # Opplastede bilder
├── downloads/        # Genererte PDF-er
└── write_to_pdf.py  # PDF-generering
```

### Frontend-oppsett
```bash
cd frontend
npm install
npm run dev
```

## Bruk

### 1. Velg prosjekttype
- Velg fra dropdown-menyen
- Fyll ut prosjektnavn og beskrivelse
- Legg til valgfrie detaljer (målgruppe, stil)

### 2. Generer innhold
- Klikk "Generer innhold med AI"
- Gjennomgå generert innhold
- Gå videre til bildeopplasting

### 3. Legg til bilder
- Last opp bilder for header, innhold og footer
- Se forhåndsvisning av opplastede bilder
- Velg språk for PDF

### 4. Generer PDF
- Klikk "Generer PDF"
- Last ned den ferdige prosjektbeskrivelsen

## AI-integrasjon

**Nåværende implementering:**
- Template-basert innhold basert på prosjekttype
- Strukturerte svar for konsistens

**Fremtidige forbedringer:**
- OpenAI API-integrasjon
- Claude API-integrasjon
- Lokale AI-modeller
- Tilpasset prompt-engineering

## Sikkerhet

- **Autentisering**: Alle endepunkter krever gyldig token
- **Filvalidering**: Kun bildefiler tillatt
- **Filstørrelse**: Automatisk komprimering av store bilder
- **Mappestruktur**: Isolerte mapper for opplastinger

## Testing

Kjør test-scriptet:
```bash
cd backend
python test_project_description.py
```

Dette vil teste:
- PDF-generering
- Bildebehandling
- API-endepunkter (krever autentisering)

## Feilhåndtering

### Vanlige feil:
- **Bildeopplasting feilet**: Sjekk filformat og størrelse
- **PDF-generering feilet**: Sjekk at alle felter er fylt ut
- **Autentisering feilet**: Logg inn på nytt

### Logging:
- Backend logger alle operasjoner
- Feilmeldinger returneres til frontend
- PDF-generering med fallback til placeholders

## Fremtidige forbedringer

1. **Avansert AI-integrasjon**
   - OpenAI/Claude API
   - Tilpasset prompt-engineering
   - Flerspråklig støtte

2. **Bildebehandling**
   - AI-bildetags
   - Automatisk beskjæring
   - Filter og effekter

3. **PDF-templates**
   - Flere design-alternativer
   - Tilpassbare layouts
   - Merkevare-templates

4. **Collaboration**
   - Deling av prosjekter
   - Kommentarer og feedback
   - Versjonskontroll

## Support

For spørsmål eller problemer:
1. Sjekk loggene i backend
2. Test med test-scriptet
3. Verifiser autentisering
4. Sjekk filrettigheter for uploads/downloads mapper

---

**Utviklet av LEA FILMS** 🎬
