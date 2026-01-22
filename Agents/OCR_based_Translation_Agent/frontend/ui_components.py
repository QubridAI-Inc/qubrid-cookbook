"""
UI Components for Translate AI.
Reusable UI rendering functions.
"""
import streamlit as st
from typing import Optional


def render_header():
    """Render the application header with title."""
    st.title("Translate AI | Powered by Qubrid AI")
    st.markdown("Upload an image with text, select a target language, and get instant translation!")


def render_upload_section():
    """Render the image upload section."""
    st.subheader("📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image with text",
        type=["png", "jpg", "jpeg"],
        help="Upload an image containing text to translate"
    )
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    return uploaded_file


def render_translation_settings():
    """Render the translation settings section with language selector."""
    st.subheader("🎯 Translation Settings")
    target_lang = st.selectbox(
        "Target Language",
        [
            "Arabic", "Basque", "Bengali", "Bulgarian", "Catalan", 
            "Chinese (Simplified)", "Chinese (Traditional)", "Croatian", 
            "Czech", "Danish", "Dutch", "English", "Estonian", "Filipino", 
            "Finnish", "French", "Galician", "German", "Greek", "Hebrew", 
            "Hindi", "Hungarian", "Icelandic", "Indonesian", "Irish", 
            "Italian", "Japanese", "Korean", "Latvian", "Lithuanian", 
            "Malay", "Norwegian", "Polish", "Portuguese", "Romanian", 
            "Russian", "Serbian", "Slovak", "Slovenian", "Spanish", 
            "Swedish", "Swahili", "Thai", "Turkish", "Ukrainian", 
            "Vietnamese", "Welsh", "Zulu"
        ],
        help="Select the language to translate to"
    )
    
    translate_button = st.button("🚀 Translate", type="primary", use_container_width=True)
    
    return target_lang, translate_button


def render_translation_results(extracted_text: str, detected_language: str, translated_text: str, target_lang: str):
    """
    Render the translation results.
    
    Args:
        extracted_text: The text extracted from the image
        detected_language: The detected source language
        translated_text: The translated text
        target_lang: The target language name
    """
    st.success("✅ Translation Complete!")
    st.markdown("---")
    
    # Display extracted text
    st.markdown("### 📝 Extracted Text")
    st.info(extracted_text)
    
    # Display detected language
    st.markdown("### 🔍 Detected Language")
    st.write(detected_language)
    
    # Display translation
    st.markdown(f"### 🌍 Translation ({target_lang})")
    st.success(translated_text)
