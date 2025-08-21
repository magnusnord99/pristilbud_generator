#!/usr/bin/env python3
"""
Test script for the new landscape PDF layout
"""

import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_landscape_pdf():
    """Test the new landscape PDF generation with BILLABONG-style layout"""
    print("Testing landscape PDF generation with gradient background...")
    
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
            },
            {
                "image_id": "footer1",
                "filename": "footer_aurora.jpg", 
                "url": "/uploads/footer_aurora.jpg",
                "placeholder_type": "footer"
            }
        ]
        
        print("📄 Generating BILLABONG-style PDF...")
        print(f"📊 Content sections: {len(mock_content)}")
        print(f"🖼️ Images: {len(mock_images)}")
        print("🎨 Using gradient background (fallback if image not found)")
        
        # Generate PDF
        pdf_buffer = generate_project_description_pdf(
            project_type="advertising",
            project_name="Billabong Nord-Norge Kampanje 2025",
            generated_content=mock_content,
            images=mock_images,
            language="NO"
        )
        
        print(f"✅ BILLABONG-style PDF generated successfully!")
        print(f"📏 File size: {len(pdf_buffer.getvalue())} bytes")
        
        # Save test PDF
        output_filename = "test_billabong_style_project_description.pdf"
        with open(output_filename, "wb") as f:
            f.write(pdf_buffer.getvalue())
        print(f"💾 PDF saved as '{output_filename}'")
        
        # Check file size
        file_size = os.path.getsize(output_filename)
        print(f"📁 File size on disk: {file_size} bytes")
        
        if file_size > 1000:  # Basic size check
            print("✅ PDF file appears to be properly generated")
            print("🎯 Layout should now match BILLABONG presentation style")
        else:
            print("⚠️ PDF file seems too small, might have issues")
            
    except Exception as e:
        print(f"❌ BILLABONG-style PDF test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the landscape PDF test"""
    print("=== Landscape PDF Layout Test ===\n")
    
    test_landscape_pdf()
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main()
