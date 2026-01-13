import streamlit as st
import fitz  # PyMuPDF
import base64
import requests
import os
from dotenv import load_dotenv
import time
import tempfile

# Load environment variables
load_dotenv()

# Initialize session state
if 'translation_complete' not in st.session_state:
    st.session_state.translation_complete = False
if 'final_translation' not in st.session_state:
    st.session_state.final_translation = ""
if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = ""
if 'target_lang' not in st.session_state:
    st.session_state.target_lang = ""

# Page config
st.set_page_config(
    page_title="Smart PDF Translator",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header"><h1>📚 Smart PDF Translator</h1><p>Translate PDFs with AI Vision Models</p></div>', unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "🔑 OpenRouter API Key",
        value=os.getenv("OPEN_ROUTER_KEY", ""),
        type="password",
        help="Get your API key from https://openrouter.ai/keys"
    )
    
    st.divider()
    
    # Model selection
    st.subheader("🤖 Model Selection")
    model_options = {
        "GPT-4o (Recommended)": "openai/gpt-4o",
        "GPT-4o Mini (Fast & Cheap)": "openai/gpt-4o-mini",
        "Claude 3.5 Sonnet (Excellent)": "anthropic/claude-3.5-sonnet-20241022",
        "Claude 3.5 Haiku (Fast)": "anthropic/claude-3.5-haiku",
        "GPT-4 Turbo": "openai/gpt-4-turbo",
        "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet-20241022",
        "Claude 3 Opus": "anthropic/claude-3-opus",
        "Gemini 2.0 Flash (Free)": "google/gemini-2.0-flash-exp:free",
    }
    
    selected_model = st.selectbox(
        "Choose AI Model",
        options=list(model_options.keys()),
        index=0
    )
    
    st.divider()
    
    # Language selection
    st.subheader("🌍 Languages")
    
    # Auto-detect option
    auto_detect = st.checkbox("Auto-detect source language", value=True)
    
    if not auto_detect:
        source_lang = st.selectbox(
            "Source Language",
            ["Gujarati", "Hindi", "English", "Marathi", "Tamil", "Telugu", "Bengali", "Punjabi"],
            index=0
        )
    else:
        source_lang = "Auto-detect"
        st.info("Source language will be detected automatically")
    
    target_lang = st.selectbox(
        "Target Language (translation)",
        ["English", "Hindi", "Gujarati", "Marathi", "Tamil", "Telugu", "Bengali", "Punjabi"],
        index=0
    )
    
    st.divider()
    
    # Rate limiting
    st.subheader("⏱️ Rate Limiting")
    wait_time = st.slider(
        "Wait time between pages (seconds)",
        min_value=5,
        max_value=60,
        value=15,
        help="Increase for free models to avoid rate limits"
    )

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Upload PDF Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload the book or document you want to translate"
    )

with col2:
    if uploaded_file:
        st.metric("📄 File Name", uploaded_file.name)
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.metric("💾 File Size", f"{file_size_mb:.2f} MB")

# Page selection
if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.read())
        pdf_path = tmp_file.name
    
    # Get total pages
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    st.success(f"✅ PDF loaded successfully: {total_pages} pages")
    
    # Page selection UI
    st.subheader("📄 Select Pages to Translate")
    
    page_option = st.radio(
        "Translation scope:",
        ["Single Page", "Page Range", "All Pages"],
        horizontal=True
    )
    
    if page_option == "Single Page":
        page_num = st.number_input(
            "Page Number",
            min_value=1,
            max_value=total_pages,
            value=1
        )
        start_page = page_num
        end_page = page_num
    elif page_option == "Page Range":
        col_start, col_end = st.columns(2)
        with col_start:
            start_page = st.number_input(
                "Start Page",
                min_value=1,
                max_value=total_pages,
                value=1
            )
        with col_end:
            end_page = st.number_input(
                "End Page",
                min_value=start_page,
                max_value=total_pages,
                value=min(start_page + 9, total_pages)
            )
    else:  # All Pages
        start_page = 1
        end_page = total_pages
    
    pages_to_translate = end_page - start_page + 1
    
    # Translation info box
    st.info(f"📊 Will translate **{pages_to_translate} page(s)**: Page {start_page} to {end_page}")
    
    # Detailed info in sidebar or expander
    with st.expander("📊 Translation Details", expanded=False):
        st.markdown(f"""
        **File:** {uploaded_file.name}  
        **Total Pages:** {total_pages}  
        **Pages to Translate:** {pages_to_translate}  
        **Source Language:** {source_lang}  
        **Target Language:** {target_lang}  
        **Model:** {selected_model.split(' (')[0]}
        """)
        
        # Cost estimate
        if "Free" in selected_model:
            st.info("💰 Using free model (rate limits may apply)")
        else:
            estimated_cost = pages_to_translate * 0.01  # Rough estimate
            st.info(f"💰 Estimated cost: ${estimated_cost:.2f} - ${estimated_cost * 2:.2f}")

# Translation functions
def pdf_to_images(pdf_path, start_page, end_page):
    """Convert PDF pages to images"""
    images = []
    doc = fitz.open(pdf_path)
    
    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("png")
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        images.append({
            'page_num': page_num + 1,
            'data': img_base64
        })
    
    doc.close()
    return images

def translate_image(image_base64, page_num, model_id, api_key, source_lang, target_lang, retry_count=3):
    """Translate text in image with retry logic"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Adjust prompt based on auto-detect
    if source_lang == "Auto-detect":
        lang_instruction = f"""First, detect the language in this image.
Then translate the text to {target_lang}.

Format your response EXACTLY like this:
[DETECTED: language_name]
translated text here"""
    else:
        lang_instruction = f"This image contains {source_lang} text. Translate it to {target_lang}."
    
    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are an expert translator. {lang_instruction}

Please:
1. Read and extract ALL the text from this image
2. Translate it accurately to {target_lang}
3. Maintain the original structure, paragraphs, and formatting
4. Preserve the meaning, tone, and cultural context

Provide ONLY the {target_lang} translation without any additional explanations."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    for attempt in range(retry_count):
        try:
            if attempt > 0:
                wait = 10 * (attempt + 1)
                time.sleep(wait)
            
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 404:
                return None, None, f"Model '{model_id}' not found. Please select a different model."
            elif response.status_code == 429:
                if attempt < retry_count - 1:
                    continue
                return None, None, "Rate limit exceeded. Please increase wait time or add credits."
            
            response.raise_for_status()
            result = response.json()
            translation = result['choices'][0]['message']['content']
            
            # Extract detected language if present
            detected_lang = None
            if "[DETECTED:" in translation:
                try:
                    detected_part = translation.split("[DETECTED:")[1].split("]")[0].strip()
                    detected_lang = detected_part
                    # Remove the detection marker from translation
                    translation = translation.split("]", 1)[1].strip()
                except:
                    pass
            
            return translation, detected_lang, None
            
        except requests.exceptions.HTTPError as e:
            if attempt < retry_count - 1:
                continue
            return None, None, f"HTTP Error {e.response.status_code}"
        except Exception as e:
            if attempt < retry_count - 1:
                continue
            return None, None, str(e)
    
    return None, None, "All retry attempts failed"

def txt_to_pdf_with_hindi(text_content, font_path=None):
    """Convert TXT to PDF with Hindi support"""
    try:
        # Check for Hindi font
        if not font_path or not os.path.exists(font_path):
            font_path = "NotoSansDevanagari-Regular.ttf"
            if not os.path.exists(font_path):
                return None, "Hindi font (NotoSansDevanagari-Regular.ttf) not found in project folder"
        
        # Try using reportlab for better Hindi support
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from io import BytesIO
            
            # Register the font
            pdfmetrics.registerFont(TTFont('Devanagari', font_path))
            
            # Create PDF
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
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
                        # Use the Hindi font
                        c.setFont('Devanagari', 11)
                        
                        # Word wrap
                        max_width = width - 100
                        words = line.split()
                        current_line = ""
                        
                        for word in words:
                            test_line = current_line + " " + word if current_line else word
                            # Simple width estimation
                            if c.stringWidth(test_line, 'Devanagari', 11) > max_width and current_line:
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
            
        except ImportError:
            # Fallback message if reportlab not available
            return None, "Please install reportlab: pip install reportlab"
        
    except Exception as e:
        return None, f"Error creating PDF: {str(e)}"

# Start translation button
if uploaded_file and api_key:
    st.divider()
    
    # Only show start button if translation is not complete
    if not st.session_state.translation_complete:
        if st.button("🚀 Start Translation", type="primary", use_container_width=True):
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Convert pages to images
            status_text.text("📸 Converting PDF pages to images...")
            images = pdf_to_images(pdf_path, start_page, end_page)
            
            # Translate each page
            all_translations = []
            failed_pages = []
            detected_languages = []
            
            for i, img in enumerate(images):
                page_num = img['page_num']
                progress = (i + 1) / len(images)
                
                status_text.text(f"🔄 Translating page {page_num}/{end_page}...")
                progress_bar.progress(progress)
                
                # Add wait time between pages (except first page)
                if i > 0:
                    status_text.text(f"⏳ Waiting {wait_time} seconds to avoid rate limits...")
                    time.sleep(wait_time)
                    status_text.text(f"🔄 Translating page {page_num}/{end_page}...")
                
                translation, detected_lang, error = translate_image(
                    img['data'],
                    page_num,
                    model_options[selected_model],
                    api_key,
                    source_lang,
                    target_lang
                )
                
                if translation:
                    all_translations.append(f"\n--- Page {page_num} ---\n{translation}")
                    if detected_lang:
                        detected_languages.append(detected_lang)
                else:
                    all_translations.append(f"\n--- Page {page_num} ---\n[Translation failed: {error}]")
                    failed_pages.append(page_num)
                    st.error(f"❌ Page {page_num} failed: {error}")
            
            # Combine translations and store in session state
            st.session_state.final_translation = "\n".join(all_translations)
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.target_lang = target_lang
            st.session_state.translation_complete = True
            st.session_state.failed_pages = failed_pages
            st.session_state.total_pages = len(images)
            
            # Store detected language
            if detected_languages:
                # Get most common detected language
                most_common = max(set(detected_languages), key=detected_languages.count)
                st.session_state.detected_language = most_common
            else:
                st.session_state.detected_language = None
            
            # Success
            progress_bar.progress(1.0)
            status_text.text("✅ Translation complete!")
            
            st.rerun()

# Display translation results if available
if st.session_state.translation_complete:
    st.divider()
    
    # Show detected language if auto-detect was used
    if st.session_state.get('detected_language'):
        st.info(f"🔍 **Detected Language:** {st.session_state.detected_language}")
    
    # Display results
    if st.session_state.get('failed_pages'):
        failed_count = len(st.session_state.failed_pages)
        success_count = st.session_state.total_pages - failed_count
        st.warning(f"⚠️ Translated {success_count}/{st.session_state.total_pages} pages. Failed pages: {', '.join(map(str, st.session_state.failed_pages))}")
    else:
        st.success(f"🎉 Successfully translated all {st.session_state.total_pages} page(s)!")
    
    # Show translation in expandable section
    with st.expander("📖 View Translation", expanded=True):
        st.text_area(
            "Translation Result",
            st.session_state.final_translation,
            height=400,
            label_visibility="collapsed"
        )
    
    # Download buttons
    st.subheader("💾 Download Options")
    col_download1, col_download2 = st.columns(2)
    
    with col_download1:
        st.download_button(
            label="📥 Download as TXT",
            data=st.session_state.final_translation,
            file_name=f"{st.session_state.uploaded_filename.split('.')[0]}_{st.session_state.target_lang}_translation.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_download2:
        st.download_button(
            label="📥 Download as Markdown",
            data=st.session_state.final_translation,
            file_name=f"{st.session_state.uploaded_filename.split('.')[0]}_{st.session_state.target_lang}_translation.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # PDF Conversion Section
    st.divider()
    st.subheader("📄 Convert to PDF")
    st.info("💡 Convert your translation to PDF with proper Hindi font support")
    
    col_pdf_btn, col_pdf_info = st.columns([1, 2])
    
    with col_pdf_btn:
        convert_to_pdf = st.button("🔄 Convert to PDF", use_container_width=True, type="primary")
    
    with col_pdf_info:
        st.caption("⚠️ Requires NotoSansDevanagari-Regular.ttf in project folder")
    
    if convert_to_pdf:
        with st.spinner("📝 Creating PDF with Hindi font..."):
            pdf_bytes, error = txt_to_pdf_with_hindi(st.session_state.final_translation)
            
            if error:
                st.error(f"❌ {error}")
                with st.expander("💡 How to fix this"):
                    st.markdown("""
                    **Steps to add Hindi font:**
                    1. Download [Noto Sans Devanagari](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari)
                    2. Extract the zip file
                    3. Find `NotoSansDevanagari-Regular.ttf` 
                    4. Copy it to your project folder (same location as app.py)
                    5. Try converting again
                    """)
            else:
                st.success("✅ PDF created successfully with Hindi font!")
                
                # Make download button prominent
                st.markdown("### 📥 Your PDF is Ready!")
                
                st.download_button(
                    label="📥 Download Translated PDF",
                    data=pdf_bytes,
                    file_name=f"{st.session_state.uploaded_filename.split('.')[0]}_{st.session_state.target_lang}_translation.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
                
                st.balloons()
                st.success("👆 Click the button above to download your PDF!")
    
    # Add a button to start new translation
    st.divider()
    if st.button("🔄 Start New Translation", use_container_width=True):
        st.session_state.translation_complete = False
        st.session_state.final_translation = ""
        st.rerun()

elif not uploaded_file:
    st.info("👆 Please upload a PDF file to get started")
elif not api_key:
    st.warning("⚠️ Please enter your OpenRouter API key in the sidebar")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem 0;'>
    <p><strong>Smart PDF Translator</strong> | Built with Streamlit & OpenRouter AI</p>
    <p><small>Get your API key at <a href='https://openrouter.ai/keys' target='_blank'>openrouter.ai/keys</a></small></p>
</div>
""", unsafe_allow_html=True)
