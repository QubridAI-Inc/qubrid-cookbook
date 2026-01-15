import streamlit as st  # Main library for the UI

def render_header():
    """
    Renders the main DiagnostiQ branding header.
    
    Why separate this?
    It allows you to change the Logo or Title in one place, 
    and it updates the look across your entire application.
    """
    # 1. Spacer to push content down slightly
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Main Title (The new Brand Name)
    # The CSS for 'h1' is defined in frontend/styles.py
    st.markdown("<h1>DiagnostiQ</h1>", unsafe_allow_html=True)
    
    # 3. Subtitle (The Function)
    # The CSS for 'h3' gives it that technical, monospaced engineering look
    st.markdown("<h3>INDUSTRIAL COMPONENT DIAGNOSTICS</h3>", unsafe_allow_html=True)
    
    # 4. Bottom Spacer
    st.markdown("<br>", unsafe_allow_html=True)