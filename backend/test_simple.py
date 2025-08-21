#!/usr/bin/env python3
"""
Simple test script for project description functionality
"""

import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Test database functionality"""
    print("Testing database...")
    try:
        import database
        database.init_database()
        print("✅ Database initialized")
        
        # Test user creation
        user_id = database.create_test_user("test@example.com", "Test User", "admin")
        print(f"✅ Test user created with ID: {user_id}")
        
        # Test user retrieval
        user = database.get_user_by_email("test@example.com")
        if user:
            print(f"✅ User retrieved: {user['email']} (ID: {user['id']})")
        else:
            print("❌ Failed to retrieve user")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

def test_pdf_generation():
    """Test PDF generation"""
    print("\nTesting PDF generation...")
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
        
        print(f"✅ PDF generated successfully! Size: {len(pdf_buffer.getvalue())} bytes")
        
        # Save test PDF
        with open("test_project_description.pdf", "wb") as f:
            f.write(pdf_buffer.getvalue())
        print("✅ Test PDF saved as 'test_project_description.pdf'")
        
    except Exception as e:
        print(f"❌ PDF generation test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("=== Simple Project Description Tests ===\n")
    
    test_database()
    test_pdf_generation()
    
    print("\n=== Tests completed ===")

if __name__ == "__main__":
    main()
