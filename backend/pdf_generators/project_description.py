# Project description PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import os
from .common import BASE_DIR, LOGO_PATH


def _draw_fallback_subtitle(c, y_position, project_type, language, page_width):
    """Draw fallback subtitle text when no customer logo is provided"""
    c.setFont("Helvetica", 20)
    subtitle = f"{project_type.upper()} PRODUKSJON 2025"
    if language == "EN":
        subtitle = f"{project_type.upper()} PRODUCTION 2025"
    
    subtitle_width = c.stringWidth(subtitle, "Helvetica", 20)
    subtitle_x = (page_width - subtitle_width) / 2
    c.drawString(subtitle_x, y_position, subtitle)


def _draw_logo_placeholder(c, x, y, width, height):
    """Draw a placeholder for the customer logo"""
    # Draw placeholder box
    c.setStrokeColorRGB(1, 1, 1)  # White border
    c.setLineWidth(2)
    c.rect(x, y, width, height)
    
    # Draw placeholder text
    c.setFillColorRGB(1, 1, 1)  # White text
    c.setFont("Helvetica", 12)
    placeholder_text = "Customer Logo"
    text_width = c.stringWidth(placeholder_text, "Helvetica", 12)
    text_x = x + (width - text_width) / 2
    text_y = y + height / 2
    c.drawString(text_x, text_y, placeholder_text)


def _calculate_image_fit(image_path, target_width, target_height):
    """
    Calculate image dimensions to fit target area while preserving aspect ratio.
    Returns (crop_x, crop_y, crop_width, crop_height, target_width, target_height).
    """
    try:
        from PIL import Image
        print(f"🔍 Opening image: {image_path}")
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            print(f"📏 Image dimensions: {img_width}x{img_height}")
            print(f"🎯 Target dimensions: {target_width}x{target_height}")
            
            img_ratio = img_width / img_height
            target_ratio = target_width / target_height
            print(f"📐 Image ratio: {img_ratio:.2f}, Target ratio: {target_ratio:.2f}")
            
            if img_ratio > target_ratio:
                # Image is wider than target - fit to height and crop width
                # Scale image to fit target height, then crop width
                scale_factor = target_height / img_height
                scaled_width = img_width * scale_factor
                scaled_height = target_height
                
                # Calculate how much to crop from left and right
                crop_amount = (scaled_width - target_width) / 2
                crop_x = crop_amount / scale_factor
                crop_width = target_width / scale_factor
                
                result = (crop_x, 0, crop_width, img_height, target_width, target_height)
                print(f"✂️ Wide image - Crop: x={crop_x:.1f}, y=0, w={crop_width:.1f}, h={img_height}")
                return result
            else:
                # Image is taller than target - fit to width and crop height
                # Scale image to fit target width, then crop height
                scale_factor = target_width / img_width
                scaled_width = target_width
                scaled_height = img_height * scale_factor
                
                # Calculate how much to crop from top and bottom
                crop_amount = (scaled_height - target_height) / 2
                crop_y = crop_amount / scale_factor
                crop_height = target_height / scale_factor
                
                result = (0, crop_y, img_width, crop_height, target_width, target_height)
                print(f"✂️ Tall image - Crop: x=0, y={crop_y:.1f}, w={img_width}, h={crop_height:.1f}")
                return result
    except ImportError as e:
        print(f"⚠️ PIL not available: {e}")
        # PIL not available, fallback to simple centering
        return (0, 0, target_width, target_height, target_width, target_height)
    except Exception as e:
        print(f"❌ Error in _calculate_image_fit: {e}")
        # Any error, fallback to simple centering
        return (0, 0, target_width, target_height, target_width, target_height)


def _draw_project_text(c, project_text, logo_y, page_width):
    """Draw project text under logo with consistent styling"""
    c.setFont("Helvetica", 32)
    c.setFillColorRGB(1, 1, 1)  # White text
    project_text_width = c.stringWidth(project_text, "Helvetica", 32)
    project_text_x = (page_width - project_text_width) / 2
    project_text_y = logo_y - 80  # Plassering kan endres her
    c.drawString(project_text_x, project_text_y, project_text)
    return project_text_y


def generate_project_description_pdf(
    project_type: str,
    project_name: str,
    generated_content: dict,
    images: list,
    project_text: str = "Content Production 25",  # New parameter for project text under logo
    language: str = "NO"
) -> BytesIO:
    # Check if PIL is available
    try:
        from PIL import Image
        print("✅ PIL is available for image processing")
    except ImportError as e:
        print(f"⚠️ PIL not available: {e}")
        print("⚠️ Images will use fallback scaling")
    """
    Generate a project description PDF with AI content and images
    Matches the professional InDesign presentation style with gradient background
    
    Args:
        project_type: Type of project (event, advertising, product, branding)
        project_name: Name of the project
        generated_content: AI-generated content dictionary
        images: List of image objects with url and placeholder_type
        language: Language for the PDF (NO or EN)
    
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    
    # Use 1920x1080 format (16:9 ratio)
    page_width = 1920
    page_height = 1080
    
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    # Page dimensions for landscape
    left_margin = 60
    right_margin = page_width - 60
    top_margin = page_height - 60
    content_width = right_margin - left_margin
    
    # Add paper texture as base layer (under gradient background)
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
    
    paper_texture_path = None
    for path in paper_texture_paths:
        if os.path.exists(path):
            paper_texture_path = path
            break
    
    # Draw paper texture first (base layer) - covers entire page
    if paper_texture_path:
        c.drawImage(paper_texture_path, 0, 0, width=page_width, height=page_height)
        print(f"✅ Paper texture applied: {paper_texture_path}")
    else:
        print("⚠️ Paper texture not found, using solid color base")
        # Fallback: solid paper-like color
        c.setFillColorRGB(0.95, 0.95, 0.93)  # Light paper color
        c.rect(0, 0, page_width, page_height, fill=1)
    
    # Add gradient background image on top (with transparency effect)
    background_paths = [
        os.path.join(BASE_DIR, "assets", "backgrounds", "Grainy Gradient Background 10.jpg"),
        os.path.join(BASE_DIR, "assets", "backgrounds", "Grainy Gradient Background 10.png"),
        os.path.join(BASE_DIR, "assets", "backgrounds", "gradient_background.jpg"),
        os.path.join(BASE_DIR, "assets", "backgrounds", "gradient_background.png")
    ]
    
    # Check if PSD file exists and warn user
    psd_path = os.path.join(BASE_DIR, "assets", "backgrounds", "Grainy Gradient Background 10.psd")
    if os.path.exists(psd_path):
        print("⚠️ PSD file found but not supported. Please convert to JPG or PNG:")
        print(f"   Found: {psd_path}")
        print("   Convert to: assets/backgrounds/Grainy Gradient Background 10.jpg")
        print("   Or use: assets/backgrounds/Grainy Gradient Background 10.png")
    
    background_path = None
    for path in background_paths:
        if os.path.exists(path):
            background_path = path
            break
    
    if background_path:
        # Draw gradient background with semi-transparency effect
        # Create a semi-transparent overlay effect
        c.saveState()
        c.setFillColorRGB(1, 1, 1, 0.7)  # White with 70% opacity
        c.rect(0, 0, page_width, page_height, fill=1)
        c.restoreState()
        
        # Draw gradient background with 15pt margin
        margin = 20
        c.drawImage(background_path, margin, margin, width=page_width-2*margin, height=page_height-2*margin)
        print(f"✅ Gradient background applied: {background_path}")
    else:
        # Fallback: create gradient-like background with rectangles
        print("⚠️ No supported background image found, using fallback gradient")
        print("💡 Supported formats: JPG, PNG, GIF, TIFF")
        print("💡 PSD files must be converted to JPG or PNG")
        
        # Semi-transparent gradient overlay
        c.saveState()
        c.setFillColorRGB(1, 0.6, 0.2, 0.6)  # Orange with 60% opacity
        c.rect(0, 0, page_width/2, page_height, fill=1)
        c.setFillColorRGB(0.2, 0.4, 0.8, 0.6)  # Blue with 60% opacity
        c.rect(page_width/2, 0, page_width/2, page_height, fill=1)
        c.restoreState()
    
    # Header section - BILLABONG style
    y_position = top_margin - 40
    
    # Customer logo placeholder (replaces main title and subtitle)
    y_position -= 20
    
    # Look for logo in images list
    logo_image = None
    print(f"🔍 Looking for logo among {len(images)} images:")
    for i, img in enumerate(images):
        print(f"  📸 Image {i+1}: {img.filename} ({img.placeholder_type})")
        if img.placeholder_type == "logo":
            logo_image = img
            print(f"✅ Found logo: {img.filename}")
            break
    
    if logo_image:
        print(f"🎯 Using logo: {logo_image.filename}")
    else:
        print("⚠️ No logo found, will use fallback text")
    
    if logo_image:
        # Draw customer logo (centered, reasonable size)
        logo_width = 200
        logo_height = 80
        logo_x = (page_width - logo_width) / 2
        logo_y = y_position - logo_height
        
        try:
            logo_path = os.path.join(BASE_DIR, "uploads", logo_image.filename)
            print(f"🔍 Looking for logo at: {logo_path}")
            print(f"📁 File exists: {os.path.exists(logo_path)}")
            if os.path.exists(logo_path):
                print(f"📏 File size: {os.path.getsize(logo_path)} bytes")
                # Calculate image fit to fill the logo area completely
                print(f"🎨 Processing logo image: {logo_path}")
                crop_result = _calculate_image_fit(logo_path, logo_width, logo_height)
                print(f"📊 Crop result: {crop_result}")
                
                # Use PIL to calculate proper scaling without stretching
                try:
                    from PIL import Image
                    with Image.open(logo_path) as img:
                        img_width, img_height = img.size
                        img_ratio = img_width / img_height
                        target_ratio = logo_width / logo_height
                        
                        if img_ratio > target_ratio:
                            # Image is wider - scale to fit height, then crop width
                            scale_factor = logo_height / img_height
                            scaled_width = img_width * scale_factor
                            scaled_height = logo_height
                            
                            # Ensure the image stays within the frame bounds
                            # Calculate how much extends beyond the frame
                            overflow = scaled_width - logo_width
                            if overflow > 0:
                                # Crop from both sides equally
                                offset_x = logo_x - overflow / 2
                                # Ensure we don't go negative
                                if offset_x < logo_x:
                                    offset_x = logo_x
                            else:
                                offset_x = logo_x
                            
                            c.drawImage(logo_path, offset_x, logo_y, width=scaled_width, height=scaled_height)
                            print(f"✂️ Logo - Wide image scaled to fill: {scaled_width:.1f}x{scaled_height}, offset_x: {offset_x:.1f}")
                        else:
                            # Image is taller - scale to fit width, then crop height
                            scale_factor = logo_width / img_width
                            scaled_width = logo_width
                            scaled_height = img_height * scale_factor
                            
                            # Ensure the image stays within the frame bounds
                            # Calculate how much extends beyond the frame
                            overflow = scaled_height - logo_height
                            if overflow > 0:
                                # Crop from top and bottom equally
                                offset_y = logo_y - overflow / 2
                                # Ensure we don't go negative
                                if offset_y < logo_y:
                                    offset_y = logo_y
                            else:
                                offset_y = logo_y
                            
                            c.drawImage(logo_path, logo_x, offset_y, width=scaled_width, height=scaled_height)
                            print(f"✂️ Logo - Tall image scaled to fill: {scaled_width:.1f}x{scaled_height}, offset_y: {offset_y:.1f}")
                except Exception as e:
                    print(f"⚠️ Logo scaling failed: {e}, using simple scaling")
                    c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, 
                               preserveAspectRatio=True, mask='auto')
                print(f"✅ Customer logo applied: {logo_path}")
                
                # Draw project text under the logo
                project_text_y = _draw_project_text(c, project_text, logo_y, page_width)
                y_position = project_text_y - 40  # Mer plass til neste element
            else:
                # Logo file not found, show placeholder
                _draw_logo_placeholder(c, logo_x, logo_y, logo_width, logo_height)
                
                # Draw project text under the logo placeholder
                project_text_y = _draw_project_text(c, project_text, logo_y, page_width)
                y_position = project_text_y - 40  # Mer plass til neste element
        except Exception as e:
            print(f"Error loading logo: {e}")
            _draw_logo_placeholder(c, logo_x, logo_y, logo_width, logo_height)
            
            # Draw project text under the logo placeholder
            project_text_y = _draw_project_text(c, project_text, logo_y, page_width)
            y_position = project_text_y - 40  # Mer plass til neste element
    else:
        # No logo in images, show fallback text
        _draw_fallback_subtitle(c, y_position, project_type, language, page_width)
    
    y_position -= 620  # Reduced space after logo
    
    # LEA FILMS logo (top right)
    if os.path.exists(LOGO_PATH):
        logo_width = 100
        logo_height = 50
        c.drawImage(LOGO_PATH, page_width - logo_width - 60, top_margin - logo_height, 
                   width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
    
    # Main content area - Two large images side by side (like BILLABONG slide)
    content_start_y = y_position
    
    if images and len(images) >= 2:
        # Calculate image dimensions with same height but different ratios
        # Base height for both images (same height)
        base_height = 650
        
        # Find content images (frontend uses "content" for main images)
        content_images = [img for img in images if img.placeholder_type == "content"]
        print(f"🔍 Found {len(content_images)} content images")
        for i, img in enumerate(content_images):
            print(f"  📸 Content image {i+1}: {img.filename} ({img.placeholder_type})")
        
        # Debug: Show all images and their types
        print(f"🔍 ALL IMAGES RECEIVED:")
        for i, img in enumerate(images):
            print(f"  📸 Image {i+1}: {img.filename} (type: {img.placeholder_type})")
        
        if len(content_images) >= 2:
            left_image = content_images[0]
            right_image = content_images[1]
            print(f"✅ Using content images: {left_image.filename} and {right_image.filename}")
        else:
            # Fallback to first two non-logo images if no content images found
            non_logo_images = [img for img in images if img.placeholder_type != "logo"]
            print(f"🔍 Found {len(non_logo_images)} non-logo images for fallback")
            
            if len(non_logo_images) >= 2:
                left_image = non_logo_images[0]
                right_image = non_logo_images[1]
                print(f"⚠️ Fallback to non-logo images: {left_image.filename} and {right_image.filename}")
            elif len(non_logo_images) == 1:
                left_image = non_logo_images[0]
                right_image = non_logo_images[0]  # Use same image for both
                print(f"⚠️ Only one non-logo image available, using for both: {left_image.filename}")
            else:
                # No suitable images found, create placeholders
                left_image = None
                right_image = None
                print(f"⚠️ No suitable images found, will show placeholders")
        
        if left_image and right_image:
            print(f"🎯 Final selection - Left: {left_image.filename} ({left_image.placeholder_type}), Right: {right_image.filename} ({right_image.placeholder_type})")
            
            # Left image: 4:5 ratio (høyere enn bredt)
            left_image_height = base_height
            left_image_width = (left_image_height * 4) / 5  # 4:5 ratio
            
            # Right image: 5:4 ratio (bredere enn høyt) - same height as left
            right_image_height = base_height  # Same height as left image
            right_image_width = (right_image_height * 5) / 4  # 5:4 ratio
        else:
            print("⚠️ No suitable images for main content, skipping image drawing")
            y_position = content_start_y - 100
            return
        
        # Calculate total width of both images plus spacing (10px margin)
        total_images_width = left_image_width + 10 + right_image_width
        print(f"📏 Image dimensions - Left: {left_image_width:.1f}x{left_image_height}, Right: {right_image_width:.1f}x{right_image_height}")
        print(f"📐 Total width with spacing: {total_images_width:.1f}")
        
        # Center both images on the page
        start_x = (page_width - total_images_width) / 2
        print(f"🎯 Page width: {page_width}, Start X: {start_x:.1f}")
        
        # Left image position
        left_image_x = start_x
        print(f"📍 Left image position: {left_image_x:.1f}")
        
        # Right image position
        right_image_x = start_x + left_image_width + 10
        print(f"📍 Right image position: {right_image_x:.1f}")
        
        # Debug: Show frame boundaries
        print(f"🎯 FRAME BOUNDARIES:")
        print(f"  📐 Left frame: x={left_image_x:.1f}, width={left_image_width:.1f}, right edge={left_image_x + left_image_width:.1f}")
        print(f"  📐 Right frame: x={right_image_x:.1f}, width={right_image_width:.1f}, right edge={right_image_x + right_image_width:.1f}")
        print(f"  📐 Page width: {page_width}, Total content width: {total_images_width:.1f}")
        
        # Draw images with white borders
        c.setStrokeColorRGB(1, 1, 1)
        c.setLineWidth(3)
        
        # Left image
        try:
            image_path = os.path.join(BASE_DIR, "uploads", left_image.filename)
            if os.path.exists(image_path):
                # White border removed - no more c.rect call
                
                # Use PIL to calculate proper scaling without stretching
                try:
                    from PIL import Image
                    with Image.open(image_path) as img:
                        img_width, img_height = img.size
                        img_ratio = img_width / img_height
                        target_ratio = left_image_width / left_image_height
                        
                        if img_ratio > target_ratio:
                            # Image is wider - scale to fit height, then crop width
                            scale_factor = left_image_height / img_height
                            scaled_width = img_width * scale_factor
                            scaled_height = left_image_height
                            
                            # Place image to fill the frame from left to right
                            offset_x = left_image_x
                            
                            c.drawImage(image_path, offset_x, content_start_y, width=scaled_width, height=scaled_height)
                            print(f"✂️ Left image - Wide image scaled to fill frame: {scaled_width:.1f}x{scaled_height}, offset_x: {offset_x:.1f}")
                        else:
                            # Image is taller - scale to fit width, then crop height
                            scale_factor = left_image_width / img_width
                            scaled_width = left_image_width
                            scaled_height = img_height * scale_factor
                            
                            # Ensure the image stays within the frame bounds
                            # Calculate how much extends beyond the frame
                            overflow = scaled_height - left_image_height
                            if overflow > 0:
                                # Crop from top and bottom equally
                                offset_y = content_start_y - overflow / 2
                                # Ensure we don't go negative
                                if offset_y < content_start_y:
                                    offset_y = content_start_y
                            else:
                                offset_y = content_start_y
                            
                            c.drawImage(image_path, left_image_x, offset_y, width=scaled_width, height=scaled_height)
                            print(f"✂️ Left image - Tall image scaled to fill frame: {scaled_width:.1f}x{scaled_height}, offset_y: {offset_y:.1f}")
                except Exception as e:
                    print(f"⚠️ Left image scaling failed: {e}, using simple scaling")
                    c.drawImage(image_path, left_image_x, content_start_y, width=left_image_width, height=left_image_height, 
                               preserveAspectRatio=True, mask='auto')
            else:
                # Placeholder
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(left_image_x, content_start_y, left_image_width, left_image_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.drawString(left_image_x + 10, content_start_y + left_image_height/2, f"Image: {left_image.placeholder_type}")
        except Exception as e:
            print(f"Error loading left image: {e}")
            c.setFillColorRGB(0.9, 0.9, 0.9)
            c.rect(left_image_x, content_start_y, left_image_width, left_image_height, fill=1)
        
        # Right image
        try:
            image_path = os.path.join(BASE_DIR, "uploads", right_image.filename)
            if os.path.exists(image_path):
                # White border removed - no more c.rect call
                
                # Use PIL to calculate proper scaling without stretching
                try:
                    from PIL import Image
                    with Image.open(image_path) as img:
                        img_width, img_height = img.size
                        img_ratio = img_width / img_height
                        target_ratio = right_image_width / right_image_height
                        
                        if img_ratio > target_ratio:
                            # Image is wider - scale to fit height, then crop width
                            scale_factor = right_image_height / img_height
                            scaled_width = img_width * scale_factor
                            scaled_height = right_image_height
                            
                            # Place image to fill the frame from left to right
                            offset_x = right_image_x
                            print(f"🔍 Right image - Wide image fills frame:")
                            print(f"  📏 scaled_width: {scaled_width:.1f}, frame_width: {right_image_width:.1f}")
                            print(f"  📍 right_image_x: {right_image_x:.1f}, offset_x: {offset_x:.1f}")
                            print(f"  ✂️ Image will be cropped on the right side")
                            
                            c.drawImage(image_path, offset_x, content_start_y, width=scaled_width, height=scaled_height)
                            print(f"✂️ Right image - Wide image scaled to fill frame: {scaled_width:.1f}x{scaled_height}, offset_x: {offset_x:.1f}")
                        else:
                            # Image is taller - scale to fit width, then crop height
                            scale_factor = right_image_width / img_width
                            scaled_width = right_image_width
                            scaled_height = img_height * scale_factor
                            
                            # Ensure the image stays within the frame bounds
                            # Calculate how much extends beyond the frame
                            overflow = scaled_height - right_image_height
                            if overflow > 0:
                                # Crop from top and bottom equally
                                offset_y = content_start_y - overflow / 2
                                # Ensure we don't go negative
                                if offset_y < content_start_y:
                                    offset_y = content_start_y
                            else:
                                offset_y = content_start_y
                            
                            c.drawImage(image_path, right_image_x, offset_y, width=scaled_width, height=scaled_height)
                            print(f"✂️ Right image - Tall image scaled to fill frame: {scaled_width:.1f}x{scaled_height}, offset_y: {offset_y:.1f}")
                except Exception as e:
                    print(f"⚠️ Right image scaling failed: {e}, using simple scaling")
                    c.drawImage(image_path, right_image_x, content_start_y, width=right_image_width, height=right_image_height, 
                               preserveAspectRatio=True, mask='auto')
            else:
                # Placeholder
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(right_image_x, content_start_y, right_image_width, right_image_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.drawString(right_image_x + 10, content_start_y + right_image_height/2, f"Image: {right_image.placeholder_type}")
        except Exception as e:
            print(f"Error loading right image: {e}")
            c.setFillColorRGB(0.9, 0.9, 0.9)
            c.rect(right_image_x, content_start_y, right_image_width, right_image_height, fill=1)
        
        y_position = content_start_y - right_image_height - 60
    elif images and len(images) == 1:
        # Single image - center it (but not logo)
        non_logo_images = [img for img in images if img.placeholder_type != "logo"]
        if non_logo_images:
            single_image = non_logo_images[0]
        else:
            # Only logo image available, skip single image display
            print("⚠️ Only logo image available, skipping single image display")
            y_position = content_start_y - 100
            return
        image_height = 500
        image_width = (image_height * 4) / 5  # 4:5 ratio
        
        image_x = (page_width - image_width) / 2
        image_y = content_start_y
        
        # Draw image with white border
        c.setStrokeColorRGB(1, 1, 1)
        c.setLineWidth(3)
        
        try:
            image_path = os.path.join(BASE_DIR, "uploads", single_image.filename)
            if os.path.exists(image_path):
                # White border removed - no more c.rect call
                
                # Use PIL to calculate proper scaling without stretching
                try:
                    from PIL import Image
                    with Image.open(image_path) as img:
                        img_width, img_height = img.size
                        img_ratio = img_width / img_height
                        target_ratio = image_width / image_height
                        
                        if img_ratio > target_ratio:
                            # Image is wider - scale to fit height, then crop width
                            scale_factor = image_height / img_height
                            scaled_width = img_width * scale_factor
                            scaled_height = image_height
                            
                            # Place image to fill the frame from left to right
                            offset_x = image_x
                            
                            c.drawImage(image_path, offset_x, image_y, width=scaled_width, height=scaled_height)
                            print(f"✂️ Single image - Wide image scaled to fill: {scaled_width:.1f}x{scaled_height}, offset_x: {offset_x:.1f}")
                        else:
                            # Image is taller - scale to fit width, then crop height
                            scale_factor = image_width / img_width
                            scaled_width = image_width
                            scaled_height = img_height * scale_factor
                            
                            # Ensure the image stays within the frame bounds
                            # Calculate how much extends beyond the frame
                            overflow = scaled_height - image_height
                            if overflow > 0:
                                # Crop from top and bottom equally
                                offset_y = image_y - overflow / 2
                            else:
                                offset_y = image_y
                            
                            c.drawImage(image_path, image_x, offset_y, width=scaled_width, height=scaled_height)
                            print(f"✂️ Single image - Tall image scaled to fill: {scaled_width:.1f}x{scaled_height}, offset_y: {offset_y:.1f}")
                except Exception as e:
                    print(f"⚠️ Single image scaling failed: {e}, using simple scaling")
                    c.drawImage(image_path, image_x, image_y, width=image_width, height=image_height, 
                               preserveAspectRatio=True, mask='auto')
            else:
                # Placeholder
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(image_x, image_y, image_width, image_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.drawString(image_x + 10, image_y + image_height/2, f"Image: {single_image.placeholder_type}")
        except Exception as e:
            print(f"Error loading single image: {e}")
            c.setFillColorRGB(0.9, 0.9, 0.9)
            c.rect(image_x, image_y, image_width, image_height, fill=1)
        
        y_position = content_start_y - image_height - 60
    else:
        # No images, add content sections
        y_position = content_start_y - 100
    
    # Content sections below images (if space allows)
    if y_position > 200:
        # Add some key content points
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(1, 1, 1)  # White text
        
        content_sections = [
            ("Mål", generated_content.get("goals", "")),
            ("Konsept", generated_content.get("concept", ""))
        ]
        
        for section_title, content in content_sections:
            if y_position < 150:
                break
                
            # Section title
            c.drawString(left_margin, y_position, section_title)
            y_position -= 25
            
            # Section content (truncated for space)
            c.setFont("Helvetica", 11)
            content_preview = content[:80] + "..." if len(content) > 80 else content
            c.drawString(left_margin, y_position, content_preview)
            y_position -= 40
    
    # Footer with website and page number
    c.setFillColorRGB(0.3, 0.3, 0.3)  # Darker gray color
    website = "www.leafilms.no"
    
    # Set font and get exact width for proper centering
    c.setFont("Helvetica", 20)
    website_width = c.stringWidth(website, "Helvetica", 20)
    website_x = (page_width - website_width) / 2
    c.drawString(website_x, 30, website)

    c.showPage()
    c.setPageSize((1920, 1080))
    
    # Apply background to footer page too
    if paper_texture_path:
        # Draw paper texture as base layer (covers entire page)
        c.drawImage(paper_texture_path, 0, 0, width=page_width, height=page_height)
    
    if background_path:
        # Draw gradient background as overlay on top (covers entire page)
        c.drawImage(background_path, 0, 0, width=page_width, height=page_height)
    else:
        # Semi-transparent gradient
        c.saveState()
        c.setFillColorRGB(1, 0.6, 0.2, 0.6)
        c.rect(0, 0, page_width/2, page_height, fill=1)
        c.setFillColorRGB(0.2, 0.4, 0.8, 0.6)
        c.rect(page_width/2, 0, page_width/2, page_height, fill=1)
        c.restoreState()
    
    # Footer content (white text)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 12)
    
    # Page number (bottom left)
    page_text = "1"
    c.drawString(20, 20, page_text)
    
    c.save()
    buffer.seek(0)
    return buffer
