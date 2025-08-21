#!/usr/bin/env python3
"""
Test script for PDF design - generates PDFs directly using existing images
This makes it much faster to test and iterate on the PDF design.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_generators.project_description import generate_project_description_pdf

def get_existing_images():
    """Get list of existing images in uploads folder"""
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("❌ Uploads directory not found")
        return []
    
    image_files = []
    for file_path in uploads_dir.glob("*"):
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            image_files.append(file_path)
    
    return image_files

def create_mock_image_data(image_files):
    """Create mock image data for testing"""
    if not image_files:
        print("❌ No image files found in uploads directory")
        return []
    
    # Create different placeholder types for testing
    placeholder_types = ["logo", "content", "footer"]
    images = []
    
    for i, image_file in enumerate(image_files[:3]):  # Use max 3 images
        placeholder_type = placeholder_types[i] if i < len(placeholder_types) else "content"
        
        # Create mock image data structure
        mock_image = type('MockImage', (), {
            'image_id': f'test_{i}',
            'filename': image_file.name,
            'url': f'/uploads/{image_file.name}',
            'placeholder_type': placeholder_type
        })()
        
        images.append(mock_image)
        print(f"📸 Added {image_file.name} as {placeholder_type}")
    
    return images

def test_image_scaling_no_stretch():
    """Test the new image scaling without stretching functionality"""
    print("\n🔍 Testing image scaling without stretching...")
    
    image_files = get_existing_images()
    if len(image_files) < 2:
        print("❌ Need at least 2 images to test scaling")
        return
    
    # Test with different image combinations to see scaling behavior
    test_configs = [
        ("scaling_test_1", image_files[:2]),  # Logo + 1 content
        ("scaling_test_2", image_files[:3]),  # Logo + 2 content
    ]
    
    for test_name, test_images in test_configs:
        print(f"\n📋 Testing: {test_name}")
        
        # Create mock images with specific types
        images = []
        for i, image_file in enumerate(test_images):
            if i == 0:
                placeholder_type = "logo"
            else:
                placeholder_type = "content"
            
            mock_image = type('MockImage', (), {
                'image_id': f'test_{i}',
                'filename': image_file.name,
                'url': f'/uploads/{image_file.name}',
                'placeholder_type': placeholder_type
            })()
            images.append(mock_image)
            print(f"  📸 {image_file.name} → {placeholder_type}")
        
        # Generate test PDF
        mock_content = {
            "goals": f"Test {test_name} - Testing image scaling without stretching",
            "concept": f"Test {test_name} - Images should fill frames completely without distortion",
            "target_audience": "Test målgruppe",
            "key_features": "Test funksjoner",
            "timeline": "Test tidsplan",
            "success_metrics": "Test suksesskriterier"
        }
        
        try:
            pdf_buffer = generate_project_description_pdf(
                project_type="test",
                project_name=f"Test {test_name}",
                generated_content=mock_content,
                images=images,
                language="NO"
            )
            
            output_filename = f"test_{test_name}.pdf"
            with open(output_filename, "wb") as f:
                f.write(pdf_buffer.getvalue())
            
            print(f"  ✅ Generated: {output_filename}")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")

def test_simple_scaling():
    """Test the simplified image scaling approach"""
    print("\n🎯 Testing simplified image scaling...")
    
    image_files = get_existing_images()
    if len(image_files) < 1:
        print("❌ Need at least 1 image to test scaling")
        return
    
    # Test with just one image to see the scaling behavior clearly
    print(f"\n📋 Testing simple scaling with: {image_files[0].name}")
    
    # Create mock image as logo
    mock_image = type('MockImage', (), {
        'image_id': 'test_simple',
        'filename': image_files[0].name,
        'url': f'/uploads/{image_files[0].name}',
        'placeholder_type': 'logo'
    })()
    
    mock_content = {
        "goals": "Test simple scaling - Image should fill frame without stretching",
        "concept": "Test simple scaling - Using simplified PIL-based approach",
        "target_audience": "Test målgruppe",
        "key_features": "Test funksjoner",
        "timeline": "Test tidsplan",
        "success_metrics": "Test suksesskriterier"
    }
    
    try:
        # Generate PDF
        pdf_buffer = generate_project_description_pdf(
            project_type="test",
            project_name="Test Simple Scaling",
            generated_content=mock_content,
            images=[mock_image],
            language="NO"
        )
        
        if pdf_buffer is None:
            print(f"  ⚠️ PDF generation returned None (only logo image)")
            return
            
        output_filename = "test_simple_scaling.pdf"
        with open(output_filename, "wb") as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"  ✅ Generated: {output_filename}")
        print(f"  🔍 Check this PDF to see if the image fills the frame without stretching")
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        import traceback
        traceback.print_exc()

def test_pdf_generation():
    """Test PDF generation with existing images"""
    print("🚀 Testing PDF generation with existing images...")
    
    # Get existing images
    image_files = get_existing_images()
    if not image_files:
        print("❌ No images found. Please add some images to the uploads folder first.")
        return
    
    print(f"✅ Found {len(image_files)} images: {[f.name for f in image_files]}")
    
    # Create mock image data
    images = create_mock_image_data(image_files)
    if not images:
        return
    
    # Create mock content
    mock_content = {
        "goals": "Test mål: Skape en profesjonell presentasjon som imponerer kunden",
        "concept": "Test konsept: Moderne design med fokus på brukeropplevelse og visuell appell",
        "target_audience": "Test målgruppe: Kreative profesjonelle som verdsetter kvalitet og design",
        "key_features": "Test funksjoner: Responsivt design, profesjonell layout, høy kvalitet",
        "timeline": "Test tidsplan: 2 uker planlegging, 1 uke produksjon, 1 uke testing",
        "success_metrics": "Test suksesskriterier: Kundetilfredshet, visuell kvalitet, leveringstid"
    }
    
    try:
        print("\n🎨 Generating PDF...")
        
        # Generate PDF
        pdf_buffer = generate_project_description_pdf(
            project_type="test",
            project_name="Test Prosjekt - PDF Design",
            generated_content=mock_content,
            images=images,
            language="NO"
        )
        
        # Save test PDF
        output_filename = "test_pdf_design.pdf"
        with open(output_filename, "wb") as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = os.path.getsize(output_filename)
        print(f"✅ PDF generated successfully!")
        print(f"📁 Saved as: {output_filename}")
        print(f"📏 File size: {file_size:,} bytes")
        print(f"🔍 Open the PDF to see how it looks")
        
        # Show image usage summary
        print(f"\n📊 Image usage summary:")
        for img in images:
            print(f"  • {img.filename} → {img.placeholder_type}")
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()

def test_different_configurations():
    """Test different image configurations"""
    print("\n🧪 Testing different configurations...")
    
    image_files = get_existing_images()
    if len(image_files) < 2:
        print("❌ Need at least 2 images for configuration testing")
        return
    
    # Test 1: Only logo
    print("\n📋 Test 1: Only logo image")
    logo_only = create_mock_image_data(image_files[:1])
    test_single_config("logo_only", logo_only)
    
    # Test 2: Logo + 1 content
    if len(image_files) >= 2:
        print("\n📋 Test 2: Logo + 1 content image")
        logo_content = create_mock_image_data(image_files[:2])
        test_single_config("logo_content", logo_content)
    
    # Test 3: Logo + 2 content
    if len(image_files) >= 3:
        print("\n📋 Test 3: Logo + 2 content images")
        logo_two_content = create_mock_image_data(image_files[:3])
        test_single_config("logo_two_content", logo_two_content)

def test_single_config(name, images):
    """Test a single configuration"""
    try:
        mock_content = {
            "goals": f"Test {name} - Mål for denne konfigurasjonen",
            "concept": f"Test {name} - Konsept for denne konfigurasjonen",
            "target_audience": "Test målgruppe",
            "key_features": "Test funksjoner",
            "timeline": "Test tidsplan",
            "success_metrics": "Test suksesskriterier"
        }
        
        pdf_buffer = generate_project_description_pdf(
            project_type="test",
            project_name=f"Test {name}",
            generated_content=mock_content,
            images=images,
            language="NO"
        )
        
        output_filename = f"test_{name}.pdf"
        with open(output_filename, "wb") as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"  ✅ Generated: {output_filename}")
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")

if __name__ == "__main__":
    print("🎬 PDF Design Test Script")
    print("=" * 50)
    
    # Test basic PDF generation
    test_pdf_generation()
    
    # Test different configurations
    test_different_configurations()
    
    # Test the new image scaling functionality
    test_image_scaling_no_stretch()
    
    # Test the simplified image scaling functionality
    test_simple_scaling()
    
    print("\n🎉 Testing complete!")
    print("📁 Check the generated PDF files to see the results")
    print("💡 Modify the script to test different configurations")
    print("🔍 Look for 'scaling_test_*.pdf' files to test the new no-stretch functionality")
