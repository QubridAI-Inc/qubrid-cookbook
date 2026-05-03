import streamlit as st  # Main library for building the web interface

def render_uploader():
    """
    Renders the File Upload Widget in the sidebar or main area.
    
    Returns:
        UploadedFile: A file-like object if the user uploads something, 
                      otherwise returns None.
    """
    # st.file_uploader creates the drag-and-drop box.
    # - label: The title above the box.
    # - type: Restricts files to only images (no PDFs or Word docs).
    # - help: Shows a small tooltip (?) with extra advice when hovered.
    return st.file_uploader(
        "Upload Industrial Component Image", 
        type=["jpg", "png", "jpeg"],
        help="Supports PCB, Metal tools, and Machinery parts."
    )