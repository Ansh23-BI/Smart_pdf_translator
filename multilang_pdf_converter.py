def txt_to_pdf_multilang(text_content, target_language='english', font_path=None):
    """
    Convert TXT to PDF with multiple language support
    
    Args:
        text_content: Text to convert to PDF
        target_language: Language of the text ('hindi', 'english', 'tamil', 'bengali', 'gujarati', etc.)
        font_path: Custom font path (optional)
    
    Returns:
        tuple: (pdf_bytes, error_message)
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from io import BytesIO
        import os
        
    except ImportError:
        return None, "Please install reportlab: pip install reportlab"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    
    # Language to font mapping
    LANGUAGE_FONTS = {
        'hindi': {
            'default_font': 'NotoSansDevanagari-Regular.ttf',
            'font_name': 'Devanagari',
            'requires_special_font': True
        },
        'english': {
            'default_font': 'Helvetica',
            'font_name': 'Helvetica',
            'requires_special_font': False
        },
        'tamil': {
            'default_font': 'NotoSansTamil-Regular.ttf',
            'font_name': 'Tamil',
            'requires_special_font': True
        },
        'bengali': {
            'default_font': 'NotoSansBengali-Regular.ttf',
            'font_name': 'Bengali',
            'requires_special_font': True
        },
        'gujarati': {
            'default_font': 'NotoSansGujarati-Regular.ttf',
            'font_name': 'Gujarati',
            'requires_special_font': True
        },
        'telugu': {
            'default_font': 'NotoSansTelugu-Regular.ttf',
            'font_name': 'Telugu',
            'requires_special_font': True
        },
        'kannada': {
            'default_font': 'NotoSansKannada-Regular.ttf',
            'font_name': 'Kannada',
            'requires_special_font': True
        },
        'malayalam': {
            'default_font': 'NotoSansMalayalam-Regular.ttf',
            'font_name': 'Malayalam',
            'requires_special_font': True
        },
        'punjabi': {
            'default_font': 'NotoSansGurmukhi-Regular.ttf',
            'font_name': 'Punjabi',
            'requires_special_font': True
        }
    }
    
    # Common font search locations
    FONT_SEARCH_PATHS = [
        script_dir,  # Current directory
        os.path.join(script_dir, 'fonts'),  # fonts subfolder
        os.path.join(script_dir, '..', 'fonts'),  # parent fonts folder
        '/usr/share/fonts',  # Linux system fonts
        '/System/Library/Fonts',  # macOS system fonts
        'C:\\Windows\\Fonts',  # Windows system fonts
    ]
    
    try:
        # Normalize language input
        target_language = target_language.lower().strip()
        
        # Check if language is supported
        if target_language not in LANGUAGE_FONTS:
            return None, f"Language '{target_language}' not supported. Supported languages: {', '.join(LANGUAGE_FONTS.keys())}"
        
        lang_config = LANGUAGE_FONTS[target_language]
        
        # Register font if required
        if lang_config['requires_special_font']:
            # Find font file
            found_font = None
            
            # If custom font path provided, use it directly
            if font_path:
                if os.path.isabs(font_path) and os.path.exists(font_path):
                    found_font = font_path
                else:
                    # Try relative to script directory
                    test_path = os.path.join(script_dir, font_path)
                    if os.path.exists(test_path):
                        found_font = test_path
            
            # If not found, search for default font
            if not found_font:
                font_filename = lang_config['default_font']
                
                # Search in common locations
                for search_path in FONT_SEARCH_PATHS:
                    if not os.path.exists(search_path):
                        continue
                    
                    # Direct file in search path
                    test_path = os.path.join(search_path, font_filename)
                    if os.path.exists(test_path):
                        found_font = test_path
                        break
                    
                    # Search recursively in fonts folders
                    if 'fonts' in search_path.lower():
                        for root, dirs, files in os.walk(search_path):
                            if font_filename in files:
                                found_font = os.path.join(root, font_filename)
                                break
                        if found_font:
                            break
            
            # Check if font was found
            if not found_font:
                error_msg = (
                    f"Font file '{lang_config['default_font']}' not found.\n\n"
                    f"Please download Noto Sans font for {target_language.title()} from:\n"
                    f"https://fonts.google.com/noto\n\n"
                    f"Place the font file in one of these locations:\n"
                    f"  - {script_dir}\n"
                    f"  - {os.path.join(script_dir, 'fonts')}\n\n"
                    f"Or provide the full path using the font_path parameter."
                )
                return None, error_msg
            
            # Register the font
            try:
                pdfmetrics.registerFont(TTFont(lang_config['font_name'], found_font))
            except Exception as e:
                return None, f"Error registering font '{found_font}': {str(e)}"
        
        # Create PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Font settings
        font_name = lang_config['font_name']
        font_size = 11
        
        # Split content by pages if marked
        if "--- Page" in text_content:
            pages_content = text_content.split("--- Page")
        else:
            pages_content = [text_content]
        
        for page_content in pages_content:
            if not page_content.strip():
                continue
            
            y = height - 50  # Start from top
            
            # Split into lines
            lines = page_content.strip().split('\n')
            
            for line in lines:
                if y < 50:  # New page if at bottom
                    c.showPage()
                    y = height - 50
                
                if line.strip():
                    # Set the font
                    c.setFont(font_name, font_size)
                    
                    # Word wrap
                    max_width = width - 100
                    words = line.split()
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        # Check width
                        if c.stringWidth(test_line, font_name, font_size) > max_width and current_line:
                            c.drawString(50, y, current_line)
                            y -= 16
                            current_line = word
                            if y < 50:
                                c.showPage()
                                y = height - 50
                        else:
                            current_line = test_line
                    
                    if current_line:
                        c.drawString(50, y, current_line)
                        y -= 16
                else:
                    y -= 8  # Blank line
            
            c.showPage()  # New page for next section
        
        c.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes, None
        
    except Exception as e:
        return None, f"Error creating PDF: {str(e)}"


# Example usage:
if __name__ == "__main__":
    # Hindi example
    hindi_text = "नमस्ते! यह एक परीक्षण है।\nयह हिंदी में लिखा गया है।"
    pdf_bytes, error = txt_to_pdf_multilang(hindi_text, target_language='hindi')
    
    if pdf_bytes:
        with open('hindi_output.pdf', 'wb') as f:
            f.write(pdf_bytes)
        print("Hindi PDF created successfully!")
    else:
        print(f"Error: {error}")
    
    # English example
    english_text = "Hello! This is a test.\nThis is written in English."
    pdf_bytes, error = txt_to_pdf_multilang(english_text, target_language='english')
    
    if pdf_bytes:
        with open('english_output.pdf', 'wb') as f:
            f.write(pdf_bytes)
        print("English PDF created successfully!")
    else:
        print(f"Error: {error}")