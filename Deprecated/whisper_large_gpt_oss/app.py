import streamlit as st
from PIL import Image
from Deprecated.whisper_large_gpt_oss.config.settings import config

st.set_page_config(
    page_title="Audio Snap AI",
    page_icon=Image.open("qubrid_logo.png"),
    layout="wide",
    initial_sidebar_state="collapsed"
)

config.setup_directories()

from Deprecated.whisper_large_gpt_oss.backend.database import init_db
from Deprecated.whisper_large_gpt_oss.frontend.styles import load_css
from Deprecated.whisper_large_gpt_oss.frontend.views import render_main_view

def main():
    init_db()
    load_css()
    render_main_view()

if __name__ == "__main__":
    main()
