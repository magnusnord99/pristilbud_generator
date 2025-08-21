#!/usr/bin/env python3
"""
Test script for the new paper texture and layered background PDF generation
"""

import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Define BASE_DIR for file path checking
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def test_paper_texture_pdf():
    """Test the new paper texture and layered background PDF generation"""
    print("Testing paper texture and layered background PDF generation...")
    
    try:
        from write_to_pdf import generate_project_description_pdf
        
        # Mock data for testing
        mock_content = {
            "goals": "Skape en inspirerende historie gjennom video og foto mens vi leverer et allsidig pakke med videoer og foto som viser Billabongs samling av våtdrakter og klær, designet for bruk på tvers av flere plattformer over en utvidet periode.",
            "concept": "Bli med oss på en ekstraordinær reise til Nord-Norge mens vi viser Billabongs innovative våtdrakt- og klesamling i et av verdens mest imponerende og barske landskap. Dette vil være en av de første innholdsproduksjonene på disse unike stedene.",
            "target_audience": "Surfere og eventyrere som verdsetter kvalitet, ytelse og bærekraft i ekstreme forhold",
            "key_features": "Profesjonell fotografering, drone-opptak, action-shots, landskapsfotografering, produktvisning i naturlige omgivelser",
            "timeline": "Planlegging: 2 måneder, Produksjon: 3 måneder, Post-produksjon: 1 måned, Lansering: 1 måned",
            "success_metrics": "Engasjement på sosiale medier, merkevarebevissthet, salg av våtdrakter, medieomtale, kundetilbakemeldinger"
        }
        
        mock_images = [
            {
                "image_id": "logo1",
                "filename": "customer_logo.png",
                "url": "/uploads/customer_logo.png",
                "placeholder_type": "logo"
            },
            {
                "image_id": "header1",
                "filename": "header_surfer.jpg",
                "url": "/uploads/header_surfer.jpg",
                "placeholder_type": "header"
            },
            {
                "image_id": "content1", 
                "filename": "content_wave.jpg",
                "url": "/uploads/content_wave.jpg",
                "placeholder_type": "content"
            }
        ]
        
        print("📄 Generating layered background PDF...")
        print(f"📊 Content sections: {len(mock_content)}")
        print(f"🖼️ Images: {len(mock_images)}")
        print("🎨 Using paper texture + gradient background layers")
        
        # Check for paper texture files
        paper_texture_paths = [
            os.path.join(BASE_DIR, "assets", "backgrounds", "texture_papir.jpg"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "texture_papir.png"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "texture_papir"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "paper_texture.jpg"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "paper_texture.png"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "papir_tekstur.jpg"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "papir_tekstur.png"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "texture.jpg"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "texture.png")
        ]
        
        print("\n🔍 Checking for paper texture files:")
        for path in paper_texture_paths:
            if os.path.exists(path):
                print(f"   ✅ Found: {path}")
            else:
                print(f"   ❌ Not found: {path}")
        
        # Check for gradient background
        gradient_paths = [
            os.path.join(BASE_DIR, "assets", "backgrounds", "Grainy Gradient Background 10.jpg"),
            os.path.join(BASE_DIR, "assets", "backgrounds", "Grainy Gradient Background 10.png")
        ]
        
        print("\n🔍 Checking for gradient background files:")
        for path in gradient_paths:
            if os.path.exists(path):
                print(f"   ✅ Found: {path}")
            else:
                print(f"   ❌ Not found: {path}")
        
        # Generate PDF
        pdf_buffer = generate_project_description_pdf(
            project_type="advertising",
            project_name="Billabong Nord-Norge Kampanje 2025",
            generated_content=mock_content,
            images=mock_images,
            project_text="Content Production 25",  # Test project text
            language="NO"
        )
        
        print(f"\n✅ Layered background PDF generated successfully!")
        print(f"📏 File size: {len(pdf_buffer.getvalue())} bytes")
        
        # Save test PDF
        output_filename = "test_paper_texture_layered_pdf.pdf"
        with open(output_filename, "wb") as f:
            f.write(pdf_buffer.getvalue())
        print(f"💾 PDF saved as '{output_filename}'")
        
        # Check file size
        file_size = os.path.getsize(output_filename)
        print(f"📁 File size on disk: {file_size} bytes")
        
        if file_size > 1000:
            print("✅ PDF file appears to be properly generated")
            print("🎯 Layout should now have paper texture + gradient background layers")
        else:
            print("⚠️ PDF file seems too small, might have issues")
            
    except Exception as e:
        print(f"❌ Paper texture PDF test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the paper texture PDF test"""
    print("=== Paper Texture & Layered Background PDF Test ===\n")
    
    test_paper_texture_pdf()
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main()
