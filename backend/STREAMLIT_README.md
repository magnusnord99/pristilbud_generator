# 🎬 Prosjektbeskrivelse Generator - Streamlit App v2.0

En **rask og brukervennlig** Streamlit-app for å generere profesjonelle prosjektbeskrivelser som PDF. Perfekt for POC og prototyping!

## ✨ Nye Forbedringer (v2.0)

### 🚀 Rask Start med Maler
- **Forhåndsdefinerte maler** for alle prosjekttyper
- **Ett klikk** for å komme i gang raskt
- **Intelligent innholdsgenerering** basert på valgt mal

### 👀 Live Forhåndsvisning
- **Direkte PDF-forhåndsvisning** i nettleseren
- **Sanntids oppdatering** av prosjektinformasjon
- **Ingen behov for nedlasting** for å se resultatet

### 🎨 Forbedret Brukeropplevelse
- **Moderne design** med gradient-bakgrunner
- **Intuitiv navigasjon** med klar informasjonsflyt
- **Responsivt layout** som fungerer på alle enheter
- **Status-indikatorer** som viser fremgang

## 🏃‍♂️ Rask Start (3 trinn)

### 1. Installer og start
```bash
pip install -r requirements.txt
python run_streamlit.py
```

### 2. Velg Mal
Klikk på en av de forhåndsdefinerte malene:
- 🎉 **Event Produksjon** - Perfekt for arrangementer og konferanser
- 📢 **Reklamekampanje** - Ideelt for markedsføringskampanjer
- 🚀 **Produktlansering** - Perfekt for nye produkter
- 🎨 **Merkevarebygging** - Ideelt for merkevareidentitet

### 3. Generer PDF
- Fyll ut **prosjektnavn**
- Last opp **bilder** (valgfritt)
- Klikk **"Generer PDF"** eller **"Forhåndsvis PDF"**

**🎯 Åpne: http://localhost:8501**

## ✨ Funksjoner

### 📝 Prosjektinformasjon
- **Prosjektnavn**: Navn på prosjektet
- **Målgruppe**: Beskrivelse av målgruppen
- **Prosjekttype**: Event, Reklamekampanje, Produktlansering, eller Merkevarebygging
- **Språk**: Norsk eller Engelsk

### 🖼️ Bildehåndtering
- **Drag & Drop**: Last opp bilder direkte
- **Automatisk logo**: Første bilde blir logo
- **Forhåndsvisning**: Se bildene før PDF-generering
- **Støttede formater**: PNG, JPG, JPEG, WEBP

### 🤖 AI Innholdsgenerering
- **Automatisk generering**: Basert på prosjekttype
- **Strukturert innhold**: Mål, konsept, målgruppe, nøkkelfunksjoner, tidslinje, suksessmetrikker
- **Redigerbart**: Se og godta generert innhold

### 📄 PDF Generering
- **Profesjonell layout**: 1920x1080 landscape format
- **Bakgrunn**: Papirtekstur + gradient overlay
- **Logo-plassering**: Kundelogo øverst, Leaf Films logo øverst til høyre
- **Bildehåndtering**: Smart cropping for perfekt passform
- **Direkte nedlasting**: Last ned PDF med ett klikk

## 🎯 Bruksscenarioer

### For POC/Prototyping (2 minutter)
1. **Velg mal** → **Fyll ut navn** → **Generer PDF**
2. Perfekt for å vise konseptet til kunder raskt

### For Produksjon (5-10 minutter)
1. **Last opp bilder** → **Tilpass innhold** → **Forhåndsvis** → **Generer**
2. Full kontroll over alle elementer

## 🔄 Bruksflyt

1. **Velg prosjekttype** i sidebaren
2. **Fyll ut prosjektinformasjon** (navn, målgruppe)
3. **Last opp bilder** (logo + innholdsbilder)
4. **Generer AI-innhold** med ett klikk
5. **Se forhåndsvisning** av generert innhold
6. **Generer og last ned PDF**

## 🔧 Tekniske detaljer

### Integrasjon med eksisterende kode
- Bruker `pdf_generators/project_description.py` direkte
- Ingen API-kall - alt lokalt
- Samme PDF-generering som FastAPI-versjonen

### Filhåndtering
- Midlertidige filer for opplastede bilder
- Automatisk kopiering til `uploads/` mappe
- PDF lagres i `downloads/` mappe

### Session State
- Husker opplastede bilder
- Husker generert innhold
- Smooth brukeropplevelse

## 🆚 Fordeler vs FastAPI

| FastAPI | Streamlit |
|---------|-----------|
| ❌ Krever frontend | ✅ Ingen frontend |
| ❌ Kompleks setup | ✅ Enkelt å starte |
| ❌ Ikke brukervennlig | ✅ Drag & drop UI |
| ❌ Mange steg | ✅ Lineær flyt |
| ❌ Teknisk | ✅ Intuitivt |

## 🐛 Feilsøking

### Appen starter ikke
```bash
# Sjekk at alle avhengigheter er installert
pip install -r requirements.txt

# Start med verbose output
streamlit run streamlit_app.py --logger.level debug
```

### PDF-generering feiler
- Sjekk at `uploads/` og `downloads/` mapper eksisterer
- Sjekk at bilder er i støttede formater
- Se terminal for feilmeldinger

### Bildehåndtering
- Første bilde blir alltid logo
- Resten blir innholdsbilder
- Støtter maks 3 bilder i forhåndsvisning

## 📁 Filstruktur

```
backend/
├── streamlit_app.py          # Hovedapp
├── run_streamlit.py          # Startup script
├── pdf_generators/           # PDF-generering
├── models.py                 # Data modeller
├── uploads/                  # Opplastede bilder
├── downloads/                # Genererte PDFer
└── assets/                   # Bakgrunn og logoer
```

## 🎨 Tilpasning

### Endre farger og styling
Rediger CSS i `streamlit_app.py`:
```python
st.markdown("""
<style>
    .main-header {
        color: #your-color;
    }
</style>
""", unsafe_allow_html=True)
```

### Legge til nye prosjekttyper
Rediger `project_types` dictionary i `streamlit_app.py`

### Endre AI-innhold
Rediger innholdsgenerering i `streamlit_app.py` (AI-generering seksjon)

---

**🎉 Nyt Streamlit-appen! Den gjør prosjektbeskrivelse-generering mye enklere og mer brukervennlig.**
