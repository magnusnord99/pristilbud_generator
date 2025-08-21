#!/usr/bin/env python3
"""
Test script for project description functionality
"""

import requests
import json
import os

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_TOKEN = "test_token_123"  # This should be a valid token from your auth system

def test_project_types():
    """Test getting project types"""
    print("Testing project types endpoint...")
    
    response = requests.get(f"{BACKEND_URL}/project-types")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        types = response.json()
        print(f"Found {len(types)} project types:")
        for t in types:
            print(f"  - {t['name']}: {t['description']}")
    else:
        print(f"Error: {response.text}")
    
    print()

def test_content_generation():
    """Test AI content generation"""
    print("Testing content generation endpoint...")
    
    # First get a test token (you'll need to implement this)
    # For now, we'll skip this test
    print("Skipping content generation test (requires authentication)")
    print()

def test_image_upload():
    """Test image upload functionality"""
    print("Testing image upload endpoint...")
    
    # Create a test image
    test_image_path = "test_image.png"
    
    # Create a simple test image using PIL if available
    try:
        from PIL import Image, ImageDraw
        
        # Create a 100x100 test image
        img = Image.new('RGB', (100, 100), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), "TEST", fill='white')
        img.save(test_image_path)
        print(f"Created test image: {test_image_path}")
        
    except ImportError:
        print("PIL not available, skipping image upload test")
        return
    
    # Test upload (requires authentication)
    print("Skipping upload test (requires authentication)")
    
    # Cleanup
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"Removed test image: {test_image_path}")
    
    print()

def test_pdf_generation():
    """Test PDF generation functionality"""
    print("Testing PDF generation...")
    
    # Test the PDF generation function directly
    try:
        from write_to_pdf import generate_project_description_pdf
        
        # Mock data
        mock_content = {
            "goals": "Test goal",
            "concept": "Test concept", 
            "target_audience": "Test audience",
            "key_features": "Test features",
            "timeline": "Test timeline",
            "success_metrics": "Test metrics"
        }
        
        mock_images = [
            {
                "image_id": "test1",
                "filename": "test1.png",
                "url": "/uploads/test1.png",
                "placeholder_type": "header"
            }
        ]
        
        # Generate PDF
        pdf_buffer = generate_project_description_pdf(
            project_type="event",
            project_name="Test Project",
            generated_content=mock_content,
            images=mock_images,
            language="NO"
        )
        
        print(f"PDF generated successfully! Size: {len(pdf_buffer.getvalue())} bytes")
        
        # Save test PDF
        with open("test_project_description.pdf", "wb") as f:
            f.write(pdf_buffer.getvalue())
        print("Test PDF saved as 'test_project_description.pdf'")
        
    except Exception as e:
        print(f"Error testing PDF generation: {e}")
    
    print()

def main():
    """Run all tests"""
    print("=== Project Description API Tests ===\n")
    
    test_project_types()
    test_content_generation()
    test_image_upload()
    test_pdf_generation()
    
    print("=== Tests completed ===")

if __name__ == "__main__":
    main()
