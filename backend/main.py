# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from write_to_pdf import generate_pdf

app = FastAPI()

# CORS (adjust origins for your deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PDFRequest(BaseModel):
    url: str = Field(min_length=10)
    language: Literal["NO", "EN"]
    reise: Literal["y", "n"]
    mva: Literal["y", "n"]

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="no">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pristilbud Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .loading { display: none; }
        </style>
    </head>
    <body>
        <h1>🎬 Pristilbud Generator</h1>
        <p>Fyll ut skjemaet nedenfor for å generere ditt pristilbud:</p>
        
        <form id="pdfForm">
            <div class="form-group">
                <label for="url">Google Sheets URL:</label>
                <input type="url" id="url" name="url" required 
                       placeholder="https://docs.google.com/spreadsheets/d/...">
            </div>
            
            <div class="form-group">
                <label for="language">Språk:</label>
                <select id="language" name="language" required>
                    <option value="NO">Norsk</option>
                    <option value="EN">English</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="reise">Inkluder reise:</label>
                <select id="reise" name="reise" required>
                    <option value="y">Ja</option>
                    <option value="n">Nei</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="mva">Inkluder MVA:</label>
                <select id="mva" name="mva" required>
                    <option value="y">Ja</option>
                    <option value="n">Nei</option>
                </select>
            </div>
            
            <button type="submit">Generer PDF</button>
        </form>
        
        <div class="loading" id="loading">
            <p>Genererer PDF... Vennligst vent.</p>
        </div>
        
        <script>
            function getFilenameFromDisposition(header) {
                if (!header) return 'pristilbud.pdf';
                const match = header.match(/filename=\"?([^\";]+)\"?/i);
                return match ? match[1] : 'pristilbud.pdf';
            }

            document.getElementById('pdfForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const loading = document.getElementById('loading');
                const submitBtn = document.querySelector('button[type="submit"]');
                
                loading.style.display = 'block';
                submitBtn.disabled = true;
                
                try {
                    const formData = {
                        url: document.getElementById('url').value,
                        language: document.getElementById('language').value,
                        reise: document.getElementById('reise').value,
                        mva: document.getElementById('mva').value
                    };
                    
                    const response = await fetch('/generate-pdf', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        const cd = response.headers.get('Content-Disposition');
                        a.download = getFilenameFromDisposition(cd);
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                    } else {
                        const text = await response.text();
                        alert('Feil ved generering av PDF: ' + text);
                    }
                } catch (error) {
                    alert('En feil oppstod: ' + error.message);
                } finally {
                    loading.style.display = 'none';
                    submitBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/generate-pdf")
def create_pdf(req: PDFRequest):
    try:
        buffer, filename = generate_pdf(req.url, req.language, req.reise, req.mva)
    except ValueError as ve:
        # e.g., invalid URL format
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as ex:
        # Upstream errors (e.g., Google API, credentials, etc.)
        raise HTTPException(status_code=502, detail="Kunne ikke hente data fra Google Sheets") from ex

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )