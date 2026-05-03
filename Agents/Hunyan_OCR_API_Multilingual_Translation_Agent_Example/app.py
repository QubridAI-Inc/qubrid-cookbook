"""
Streamlit UI for Translate AI.
Simplified workflow: Upload → Select Language → Translate → Display
"""
import streamlit as st
import base64
from backend.ocr import extract_text_from_image
from backend.pipeline import TranslationPipeline
from frontend.ui_components import (
    render_header,
    render_upload_section,
    render_translation_settings,
    render_translation_results
)



# Page configuration
st.set_page_config(
    page_title="Translate AI",
    page_icon="frontend/assets/qubrid_logo.png",
    layout="wide"
)


def encode_image(uploaded_file) -> str:
    """Convert uploaded file to base64 data URI."""
    bytes_data = uploaded_file.read()
    base64_image = base64.b64encode(bytes_data).decode("utf-8")
    mime_type = uploaded_file.type
    return f"data:{mime_type};base64,{base64_image}"


def main():
    """Main application logic."""
    # Render header
    render_header()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = render_upload_section()
    
    with col2:
        target_lang, translate_button = render_translation_settings()
    
    # Translation workflow
    if uploaded_file and translate_button:
        with st.spinner("Processing..."):
            try:
                # Step 1: Encode image
                image_b64 = encode_image(uploaded_file)
                
                # Step 2: OCR Extraction
                st.info("🔍 Extracting text from image...")
                ocr_result = extract_text_from_image(image_b64)
                
                if not ocr_result["has_text"]:
                    st.error("❌ No text detected in the image. Please upload a different image.")
                    return
                
                extracted_text = ocr_result["raw_text"]
                
                # Step 3: Translation via Pipeline
                st.info(f"🌍 Translating to {target_lang}...")
                pipeline = TranslationPipeline()
                translation_result = pipeline.translate(extracted_text, target_lang)
                
                if not translation_result["success"]:
                    st.error(f"❌ Translation failed: {translation_result.get('error', 'Unknown error')}")
                    return
                
                # Step 4: Display Results
                render_translation_results(
                    extracted_text=extracted_text,
                    detected_language=translation_result.get("detected_language", "Processing..."),
                    translated_text=translation_result["translated_text"],
                    target_lang=target_lang
                )
                

                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.exception(e)


if __name__ == "__main__":
    main()
