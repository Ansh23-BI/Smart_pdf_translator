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

# Page config
st.set_page_config(
    page_title="PDF Language Translator",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("📚 PDF Language Translator")
st.markdown("Translate PDF books from one language to another using AI vision models")

# Sidebar for settings
st.sidebar.header("⚙️ Settings")

# API Key input
api_key = st.sidebar.text_input(
    "OpenRouter API Key",
    value=os.getenv("OPEN_ROUTER_KEY", ""),
    type="password",
    help="Get your API key from https://openrouter.ai/keys"
)

# Model selection
st.sidebar.subheader("🤖 Model Selection")
model_options = {
    "GPT-4o (Recommended)": "openai/gpt-4o",
    "GPT-4 Turbo Vision": "openai/gpt-4-turbo",
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet-20241022",
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "Gemini 2.0 Flash (Free)": "google/gemini-2.0-flash-exp:free",
    "Gemini Flash 1.5": "google/gemini-flash-1.5"
}

selected_model = st.sidebar.selectbox(
    "Choose AI Model",
    options=list(model_options.keys()),
    index=0,
    help="Paid models require credits. Free models may have rate limits."
)

# Language selection
st.sidebar.subheader("🌍 Languages")

source_lang = st.sidebar.selectbox(
    "Source Language (in PDF)",
    ["Gujarati", "Hindi", "English", "Marathi", "Tamil", "Telugu", "Bengali", "Punjabi", "Other"],
    index=0
)

target_lang = st.sidebar.selectbox(
    "Target Language (translation)",
    ["Hindi", "English", "Gujarati", "Marathi", "Tamil", "Telugu", "Bengali", "Punjabi", "Other"],
    index=0
)

# Custom language input if "Other" is selected
if source_lang == "Other":
    source_lang = st.sidebar.text_input("Enter source language:", "")
if target_lang == "Other":
    target_lang = st.sidebar.text_input("Enter target language:", "")

# Wait time settings
st.sidebar.subheader("⏱️ Rate Limiting")
wait_time = st.sidebar.slider(
    "Wait time between pages (seconds)",
    min_value=5,
    max_value=60,
    value=15,
    help="Increase this if you get rate limit errors. Free models need longer waits (15-30s)."
)

# Main content
col1, col2 = st.columns([1, 1])
#dividing in 2 parts, left column for input and page selection.
#Right column for summary and cost info

with col1:
    st.subheader("📤 Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload the book you want to translate"
    )
    
    if uploaded_file:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name
        
        # Get total pages
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        
        st.success(f"✅ Uploaded: {uploaded_file.name} ({total_pages} pages)")
        
        # Page selection
        st.subheader("📄 Page Selection")
        
        page_option = st.radio(
            "Select pages to translate:",
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
        st.info(f"📊 Will translate {pages_to_translate} page(s): {start_page} to {end_page}")

with col2:
    st.subheader("📊 Translation Info")
    
    if uploaded_file:
        st.markdown(f"""
        **File:** {uploaded_file.name}  
        **Total Pages:** {total_pages}  
        **Pages to Translate:** {pages_to_translate}  
        **Source Language:** {source_lang}  
        **Target Language:** {target_lang}  
        **Model:** {selected_model}
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
    
    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are an expert translator. This image contains {source_lang} text from a book.

Please:
1. Read and extract ALL the {source_lang} text from this image
2. Translate it accurately to {target_lang}
3. Maintain the original structure, paragraphs, and formatting
4. Preserve the meaning, tone, and cultural context

Provide ONLY the {target_lang} translation without any preamble or explanations."""
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
                wait = 10 * (attempt + 1)  # 10s, 20s, 30s
                time.sleep(wait)
            
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            # Check for specific errors
            if response.status_code == 404:
                return None, f"Model '{model_id}' not found. Please select a different model."
            elif response.status_code == 429:
                if attempt < retry_count - 1:
                    continue  # Retry
                return None, "Rate limit exceeded. Please increase wait time or add credits."
            
            response.raise_for_status()
            result = response.json()
            translation = result['choices'][0]['message']['content']
            return translation, None
            
        except requests.exceptions.HTTPError as e:
            if attempt < retry_count - 1:
                continue
            return None, f"HTTP Error {e.response.status_code}: {e.response.text[:200]}"
        except Exception as e:
            if attempt < retry_count - 1:
                continue
            return None, str(e)
    
    return None, "All retry attempts failed"

# Start translation button
if uploaded_file and api_key:
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
            
            translation, error = translate_image(
                img['data'],
                page_num,
                model_options[selected_model],
                api_key,
                source_lang,
                target_lang
            )
            
            if translation:
                all_translations.append(f"\n--- Page {page_num} ---\n{translation}")
            else:
                all_translations.append(f"\n--- Page {page_num} ---\n[Translation failed: {error}]")
                failed_pages.append(page_num)
                st.error(f"❌ Page {page_num} failed: {error}")
        
        # Combine translations
        final_translation = "\n".join(all_translations)
        
        # Success
        progress_bar.progress(1.0)
        status_text.text("✅ Translation complete!")
        
        # Display results
        if failed_pages:
            st.warning(f"⚠️ Translated {len(images) - len(failed_pages)}/{len(images)} pages. Failed pages: {', '.join(map(str, failed_pages))}")
        else:
            st.success(f"🎉 Successfully translated all {len(images)} page(s)!")
        
        # Show translation in expandable section
        with st.expander("📖 View Translation", expanded=True):
            st.text_area(
                "Translation Result",
                final_translation,
                height=400,
                label_visibility="collapsed"
            )
        
        # Download buttons
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            st.download_button(
                label="📥 Download as TXT",
                data=final_translation,
                file_name=f"{uploaded_file.name.split('.')[0]}_{target_lang}_translation.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_download2:
            st.download_button(
                label="📥 Download as Markdown",
                data=final_translation,
                file_name=f"{uploaded_file.name.split('.')[0]}_{target_lang}_translation.md",
                mime="text/markdown",
                use_container_width=True
            )

elif not uploaded_file:
    st.info("👆 Please upload a PDF file to get started")
elif not api_key:
    st.warning("⚠️ Please enter your OpenRouter API key in the sidebar")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
    Built with Streamlit | Powered by OpenRouter AI Models<br>
    Get your API key at <a href='https://openrouter.ai/keys' target='_blank'>openrouter.ai/keys</a>
    </small>
</div>
""", unsafe_allow_html=True)