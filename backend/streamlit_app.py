import streamlit as st
import os
import tempfile
from datetime import datetime
from pdf_generators.project_description import generate_project_description_pdf
from models import GeneratedContent, ProjectDescriptionRequest
from typing import List
import json
import base64
from io import BytesIO

# Page config
st.set_page_config(
    page_title="🎬 Prosjektbeskrivelse Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .quick-start {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .template-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .template-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .preview-container {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = None
if 'pdf_preview' not in st.session_state:
    st.session_state.pdf_preview = None

# Predefined templates for quick start
PROJECT_TEMPLATES = {
    "event": {
        "name": "Event Produksjon",
        "icon": "🎉",
        "description": "Perfekt for arrangementer, konferanser og live-events",
        "sample_content": {
            "goals": "Skape et minneverdig arrangement som engasjerer målgruppen og oppnår definerte mål",
            "concept": "Et innovativt event som kombinerer kreativitet med praktisk funksjonalitet",
            "target_audience": "Primært målgruppe som er interessert i innholdet",
            "key_features": "Interaktive elementer, profesjonell produksjon, engasjerende innhold",
            "timeline": "Planlegging: 3 måneder, Produksjon: 1 måned, Lansering: 1 uke",
            "success_metrics": "Deltakerantall, engasjement, feedback, måloppnåelse"
        }
    },
    "advertising": {
        "name": "Reklamekampanje",
        "icon": "📢",
        "description": "Ideelt for markedsføringskampanjer og produktlanseringer",
        "sample_content": {
            "goals": "Øke merkevarebevissthet og drive handlinger fra målgruppen",
            "concept": "En kreativ reklamekampanje som skiller seg ut",
            "target_audience": "Målgruppe som kan dra nytte av produktet/tjenesten",
            "key_features": "Kreativt budskap, strategisk plassering, målbare resultater",
            "timeline": "Strategi: 2 uker, Produksjon: 3 uker, Kjøring: 8 uker",
            "success_metrics": "Reach, engasjement, klikk, konverteringer"
        }
    },
    "product": {
        "name": "Produktlansering",
        "icon": "🚀",
        "description": "Perfekt for nye produkter og tjenester",
        "sample_content": {
            "goals": "Lansere et produkt som løser reelle problemer for målgruppen",
            "concept": "En innovativ løsning som revolusjonerer hvordan produktet fungerer",
            "target_audience": "Brukere som trenger denne typen løsning",
            "key_features": "Brukervennlig design, kraftig funksjonalitet, skalerbar arkitektur",
            "timeline": "Utvikling: 6 måneder, Testing: 2 måneder, Lansering: 1 måned",
            "success_metrics": "Brukeradopsjon, tilbakemeldinger, salg, tilbakevendende kunder"
        }
    },
    "branding": {
        "name": "Merkevarebygging",
        "icon": "🎨",
        "description": "Ideelt for merkevareidentitet og visuell kommunikasjon",
        "sample_content": {
            "goals": "Skape en sterk og gjenkjennelig merkevareidentitet",
            "concept": "En visuell identitet som reflekterer merkevarens essens og verdier",
            "target_audience": "Kunder og potensielle kunder som identifiserer seg med merkevaren",
            "key_features": "Konsistent design, emosjonell tilknytning, fleksibilitet på tvers av medier",
            "timeline": "Research: 2 uker, Design: 4 uker, Implementering: 6 uker",
            "success_metrics": "Merkevaregjenkjenning, kundelojalitet, visuell konsistens"
        }
    }
}

def create_pdf_preview(pdf_buffer):
    """Create a base64 encoded preview of the PDF"""
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    return f"data:application/pdf;base64,{pdf_base64}"

def main():
    st.markdown('<div class="main-header">🎬 Prosjektbeskrivelse Generator</div>', unsafe_allow_html=True)
    
    # Quick Start Section
    st.markdown('<div class="quick-start">', unsafe_allow_html=True)
    st.markdown("### 🚀 Rask Start")
    st.markdown("Velg en mal nedenfor for å komme i gang raskt, eller fyll ut skjemaet manuelt.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Template Selection
    st.markdown('<div class="section-header">📋 Velg Mal</div>', unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, (template_key, template_data) in enumerate(PROJECT_TEMPLATES.items()):
        with cols[i % 2]:
            if st.button(
                f"{template_data['icon']} {template_data['name']}",
                key=f"template_{template_key}",
                help=template_data['description'],
                use_container_width=True
            ):
                st.session_state.selected_template = template_key
                st.session_state.generated_content = GeneratedContent(**template_data['sample_content'])
                st.rerun()
    
    # Sidebar for navigation
    with st.sidebar:
        st.image("logo.png", width=150)
        st.markdown("---")
        
        # Project type selection
        project_types = {
            "event": "Event",
            "advertising": "Reklamekampanje", 
            "product": "Produktlansering",
            "branding": "Merkevarebygging"
        }
        
        selected_type = st.selectbox(
            "Velg prosjekttype:",
            options=list(project_types.keys()),
            format_func=lambda x: project_types[x],
            index=list(project_types.keys()).index(st.session_state.selected_template) if st.session_state.selected_template else 0
        )
        
        st.markdown("---")
        
        # Language selection
        language = st.radio(
            "Språk:",
            options=["NO", "EN"],
            format_func=lambda x: "Norsk" if x == "NO" else "English"
        )
        
        st.markdown("---")
        
        # Project text input
        project_text = st.text_input(
            "Prosjekttekst (under logo):",
            value="Content Production 25",
            help="Tekst som vises under kundelogo"
        )

    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-header">📝 Prosjektinformasjon</div>', unsafe_allow_html=True)
        
        # Project name
        project_name = st.text_input(
            "Prosjektnavn:",
            placeholder="Skriv inn prosjektnavn...",
            help="Navnet på prosjektet som skal genereres"
        )
        
        # Target audience
        target_audience = st.text_area(
            "Målgruppe:",
            placeholder="Beskriv målgruppen for prosjektet...",
            help="Hvem er målgruppen for dette prosjektet?"
        )
        
        st.markdown('<div class="section-header">🖼️ Bilder</div>', unsafe_allow_html=True)
        
        # Image upload section
        uploaded_files = st.file_uploader(
            "Last opp bilder:",
            type=['png', 'jpg', 'jpeg', 'webp'],
            accept_multiple_files=True,
            help="Last opp logo og innholdsbilder. Merk: Første bilde blir brukt som logo."
        )
        
        # Display uploaded images
        if uploaded_files:
            st.session_state.uploaded_images = []
            
            for i, file in enumerate(uploaded_files):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.name}") as tmp_file:
                    tmp_file.write(file.getvalue())
                    tmp_path = tmp_file.name
                
                # Determine placeholder type
                placeholder_type = "logo" if i == 0 else "content"
                
                st.session_state.uploaded_images.append({
                    'filename': file.name,
                    'url': f"/uploads/{file.name}",
                    'placeholder_type': placeholder_type,
                    'temp_path': tmp_path
                })
            
            # Show image previews
            cols = st.columns(min(len(uploaded_files), 3))
            for i, img_data in enumerate(st.session_state.uploaded_images):
                with cols[i % 3]:
                    st.image(uploaded_files[i], caption=f"{img_data['placeholder_type'].title()}: {img_data['filename']}", width=150)
        
        # AI Content Generation (simplified)
        if not st.session_state.generated_content:
            st.markdown('<div class="section-header">🤖 Generer Innhold</div>', unsafe_allow_html=True)
            if st.button("🎯 Generer AI-innhold", type="primary"):
                if not project_name:
                    st.error("Vennligst skriv inn prosjektnavn først!")
                else:
                    with st.spinner("Genererer AI-innhold..."):
                        # Use template content or generate new
                        if st.session_state.selected_template:
                            template_data = PROJECT_TEMPLATES[st.session_state.selected_template]
                            content = GeneratedContent(**template_data['sample_content'])
                        else:
                            # Generate content based on project type
                            if selected_type == "event":
                                content = GeneratedContent(
                                    goals="Skape et minneverdig arrangement som engasjerer målgruppen og oppnår definerte mål",
                                    concept=f"Et innovativt {project_name} som kombinerer kreativitet med praktisk funksjonalitet",
                                    target_audience=target_audience or "Primært målgruppe som er interessert i innholdet",
                                    key_features="Interaktive elementer, profesjonell produksjon, engasjerende innhold",
                                    timeline="Planlegging: 3 måneder, Produksjon: 1 måned, Lansering: 1 uke",
                                    success_metrics="Deltakerantall, engasjement, feedback, måloppnåelse"
                                )
                            elif selected_type == "advertising":
                                content = GeneratedContent(
                                    goals="Øke merkevarebevissthet og drive handlinger fra målgruppen",
                                    concept=f"En kreativ reklamekampanje for {project_name} som skiller seg ut",
                                    target_audience=target_audience or "Målgruppe som kan dra nytte av produktet/tjenesten",
                                    key_features="Kreativt budskap, strategisk plassering, målbare resultater",
                                    timeline="Strategi: 2 uker, Produksjon: 3 uker, Kjøring: 8 uker",
                                    success_metrics="Reach, engasjement, klikk, konverteringer"
                                )
                            elif selected_type == "product":
                                content = GeneratedContent(
                                    goals="Lansere et produkt som løser reelle problemer for målgruppen",
                                    concept=f"En innovativ løsning som revolusjonerer hvordan {project_name} fungerer",
                                    target_audience=target_audience or "Brukere som trenger denne typen løsning",
                                    key_features="Brukervennlig design, kraftig funksjonalitet, skalerbar arkitektur",
                                    timeline="Utvikling: 6 måneder, Testing: 2 måneder, Lansering: 1 måned",
                                    success_metrics="Brukeradopsjon, tilbakemeldinger, salg, tilbakevendende kunder"
                                )
                            else:  # branding
                                content = GeneratedContent(
                                    goals="Skape en sterk og gjenkjennelig merkevareidentitet",
                                    concept=f"En visuell identitet som reflekterer {project_name} sin essens og verdier",
                                    target_audience=target_audience or "Kunder og potensielle kunder som identifiserer seg med merkevaren",
                                    key_features="Konsistent design, emosjonell tilknytning, fleksibilitet på tvers av medier",
                                    timeline="Research: 2 uker, Design: 4 uker, Implementering: 6 uker",
                                    success_metrics="Merkevaregjenkjenning, kundelojalitet, visuell konsistens"
                                )
                        
                        st.session_state.generated_content = content
                        st.success("✅ AI-innhold generert!")
                        st.rerun()
        
        # Display generated content (simplified)
        if st.session_state.generated_content:
            st.markdown('<div class="section-header">📋 Generert Innhold</div>', unsafe_allow_html=True)
            
            content = st.session_state.generated_content
            
            # Show content in a more compact way
            st.write("**🎯 Mål:**", content.goals)
            st.write("**💡 Konsept:**", content.concept)
            st.write("**👥 Målgruppe:**", content.target_audience)
            st.write("**⭐ Nøkkelfunksjoner:**", content.key_features)
            st.write("**📅 Tidslinje:**", content.timeline)
            st.write("**📊 Suksessmetrikker:**", content.success_metrics)
    
    with col2:
        st.markdown('<div class="section-header">📄 PDF Generering & Forhåndsvisning</div>', unsafe_allow_html=True)
        
        # Status check
        can_generate = st.session_state.generated_content and project_name
        
        if not can_generate:
            st.warning("⚠️ Fyll ut prosjektnavn og generer innhold før PDF-generering")
        
        # Generate PDF button
        if st.button("📄 Generer PDF", type="primary", disabled=not can_generate):
            with st.spinner("Genererer PDF..."):
                try:
                    # Create images list for PDF generator
                    images = []
                    for img_data in st.session_state.uploaded_images:
                        # Copy file to uploads directory
                        uploads_dir = "uploads"
                        os.makedirs(uploads_dir, exist_ok=True)
                        
                        final_path = os.path.join(uploads_dir, img_data['filename'])
                        
                        # Copy from temp file to uploads
                        with open(img_data['temp_path'], 'rb') as src:
                            with open(final_path, 'wb') as dst:
                                dst.write(src.read())
                        
                        images.append({
                            'filename': img_data['filename'],
                            'url': img_data['url'],
                            'placeholder_type': img_data['placeholder_type']
                        })
                    
                    # Generate PDF
                    pdf_buffer = generate_project_description_pdf(
                        project_type=selected_type,
                        project_name=project_name,
                        generated_content=st.session_state.generated_content.dict(),
                        images=images,
                        project_text=project_text,
                        language=language
                    )
                    
                    # Save PDF
                    downloads_dir = "downloads"
                    os.makedirs(downloads_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_filename = f"prosjektbeskrivelse_{project_name}_{timestamp}.pdf"
                    pdf_path = os.path.join(downloads_dir, pdf_filename)
                    
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_buffer.getvalue())
                    
                    # Store PDF preview
                    st.session_state.pdf_preview = pdf_buffer
                    
                    st.success("✅ PDF generert!")
                    st.markdown(f'<div class="success-box">📄 PDF lagret som: <code>{pdf_filename}</code></div>', unsafe_allow_html=True)
                    
                    # Provide download link
                    with open(pdf_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Last ned PDF",
                            data=file.read(),
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
                
                except Exception as e:
                    st.error(f"❌ Feil ved PDF-generering: {str(e)}")
                    st.exception(e)
        
        # Live Preview Section
        st.markdown('<div class="section-header">👀 Live Forhåndsvisning</div>', unsafe_allow_html=True)
        
        if st.session_state.generated_content and project_name:
            st.markdown('<div class="preview-container">', unsafe_allow_html=True)
            st.write(f"**📋 Prosjekt:** {project_name}")
            st.write(f"**🏷️ Type:** {project_types[selected_type]}")
            st.write(f"**🌐 Språk:** {'Norsk' if language == 'NO' else 'English'}")
            st.write(f"**🖼️ Bilder:** {len(st.session_state.uploaded_images)}")
            st.write(f"**📝 Prosjekttekst:** {project_text}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Quick preview button
            if st.button("👁️ Forhåndsvis PDF", disabled=not can_generate):
                with st.spinner("Genererer forhåndsvisning..."):
                    try:
                        # Create images list for PDF generator
                        images = []
                        for img_data in st.session_state.uploaded_images:
                            # Copy file to uploads directory
                            uploads_dir = "uploads"
                            os.makedirs(uploads_dir, exist_ok=True)
                            
                            final_path = os.path.join(uploads_dir, img_data['filename'])
                            
                            # Copy from temp file to uploads
                            with open(img_data['temp_path'], 'rb') as src:
                                with open(final_path, 'wb') as dst:
                                    dst.write(src.read())
                            
                            images.append({
                                'filename': img_data['filename'],
                                'url': img_data['url'],
                                'placeholder_type': img_data['placeholder_type']
                            })
                        
                        # Generate PDF for preview
                        pdf_buffer = generate_project_description_pdf(
                            project_type=selected_type,
                            project_name=project_name,
                            generated_content=st.session_state.generated_content.dict(),
                            images=images,
                            project_text=project_text,
                            language=language
                        )
                        
                        # Show PDF preview
                        pdf_base64 = create_pdf_preview(pdf_buffer)
                        st.markdown(f'<iframe src="{pdf_base64}" width="100%" height="600px" type="application/pdf"></iframe>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"❌ Feil ved forhåndsvisning: {str(e)}")
        else:
            st.info("📝 Fyll ut prosjektinformasjon for å se forhåndsvisning")
        
        # Reset button
        if st.button("🔄 Nullstill alt"):
            st.session_state.uploaded_images = []
            st.session_state.generated_content = None
            st.session_state.selected_template = None
            st.session_state.pdf_preview = None
            st.rerun()

if __name__ == "__main__":
    main()
