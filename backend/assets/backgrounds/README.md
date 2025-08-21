# Gradient Background for PDFs

## 🎨 Hvordan legge til bakgrunnsbildet:

### **1. Plasser bakgrunnsbildet her:**
- **Filnavn**: `gradient_background.jpg` (eller `.png`)
- **Sti**: `backend/assets/backgrounds/gradient_background.jpg`
- **Format**: JPG, PNG eller andre bildeformater som støttes av ReportLab

### **2. Bildekrav:**
- **Oppløsning**: Minimum 1200x800 piksler (for A4 landscape)
- **Format**: JPG eller PNG anbefales
- **Størrelse**: Under 5MB for rask generering
- **Orientering**: Landscape (bredere enn høy)

### **3. Hva som skjer:**
- **Med bakgrunnsbilde**: PDF-en bruker ditt gradient-bilde som bakgrunn
- **Uten bakgrunnsbilde**: PDF-en bruker fallback oransje-til-blå gradient

### **4. Test:**
```bash
cd backend
source venv/bin/activate
python test_landscape_pdf.py
```

## 🔧 Teknisk informasjon:

### **Fallback gradient (hvis bilde mangler):**
- **Venstre side**: Oransje (`#FF9933`)
- **Høyre side**: Blå (`#3366CC`)

### **Bildeplassering:**
- Bakgrunnen dekker hele siden
- Tekst og innhold plasseres over bakgrunnen
- Hvit tekst for god kontrast

### **Filstruktur:**
```
backend/
├── assets/
│   └── backgrounds/
│       ├── README.md
│       └── gradient_background.jpg  ← Legg bildet her
└── write_to_pdf.py
```

## 💡 Tips:

1. **Bruk høy oppløsning** for best kvalitet
2. **Test med forskjellige bilder** for å finne beste effekten
3. **Sørg for god kontrast** mellom bakgrunn og tekst
4. **Backup originalbildet** før du redigerer

---

**Utviklet av LEA FILMS** 🎬
