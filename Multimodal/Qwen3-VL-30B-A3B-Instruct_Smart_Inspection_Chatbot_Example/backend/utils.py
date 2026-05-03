import base64  # Standard library to convert binary image data into text strings
from fpdf import FPDF  # Lightweight library for generating PDF files programmatically

def encode_image_to_base64(image_file) -> str:
    """
    Helper to convert a Streamlit UploadedFile or BytesIO object into a Base64 string.
    
    Why this is needed:
    The AI API cannot accept raw binary files (like .jpg). It requires the image 
    to be converted into a long text string (Base64 format) to be sent inside a JSON payload.
    """
    # .getvalue() gets the raw bytes from the file in memory
    # .b64encode() converts bytes to base64 bytes
    # .decode('utf-8') converts those bytes into a standard string
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def clean_text(text: str) -> str:
    """
    Sanitizes text to remove emojis and unsupported characters.
    
    Why this is needed:
    The FPDF library uses the 'Latin-1' encoding by default. It crashes if it encounters
    modern emojis (😊) or complex Unicode characters. This function filters them out.
    """
    if not text:
        return ""
    
    # 1. Encode to Latin-1: Tries to convert text to basic Western European characters.
    # 2. 'replace': If a character (like an emoji) doesn't exist in Latin-1, replace it with a '?'
    # 3. Decode back: Convert bytes back to a Python string safe for PDF generation.
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(chat_history):
    """
    Generates a professional PDF report from the chat history list.
    Returns the raw PDF bytes to be downloaded by the user.
    """
    # Initialize the PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- HEADER SECTION ---
    pdf.set_font("Arial", "B", 16)  # Bold Arial, size 16
    # Title centered ("C"). 'ln=True' moves cursor to the next line.
    # TODO: Update "Apex Industrial AI" to "DiagnostiQ" below to match your new branding.
    pdf.cell(0, 10, "Apex Industrial AI - Inspection Report", ln=True, align="C")
    pdf.ln(10)  # Add 10 units of vertical spacing (a blank line)
    
    # --- CONTENT SECTION ---
    pdf.set_font("Arial", size=11)  # Standard reading font
    
    # Loop through every message in the conversation history
    for msg in chat_history:
        role = msg["role"].upper()
        
        # CRITICAL: Clean the text before writing to prevent PDF crashes
        content = clean_text(msg["content"])
        
        if role == "USER":
            # Style User messages in Dark Grey to distinguish them
            pdf.set_text_color(100, 100, 100) 
            pdf.cell(0, 10, f"OPERATOR: {content}", ln=True)
        else:
            # Style AI messages in Standard Black
            pdf.set_text_color(0, 0, 0)
            
            # 'multi_cell' automatically wraps long text to the next line
            pdf.multi_cell(0, 10, f"ANALYSIS: {content}")
            pdf.ln(5)  # Add small spacing after the AI response
            
            # --- METRICS SECTION (Token Usage) ---
            # Checks if this message has performance data attached
            if "usage" in msg and msg["usage"] is not None:
                u = msg["usage"]
                
                # Robust Logic: Handle metrics whether they are a Dict (from Database)
                # or a Pydantic Object (fresh from API).
                if isinstance(u, dict):
                    tokens = u.get('total_tokens', 0)
                else:
                    tokens = getattr(u, 'total_tokens', 0)

                # Switch to a monospace font (Courier) for technical data
                pdf.set_font("Courier", size=8)
                pdf.cell(0, 5, f"[METRICS: {tokens} Tokens used]", ln=True)
                pdf.set_font("Arial", size=11) # Reset font back to normal for next loop
        
        pdf.ln(2)  # Small gap between messages

    # Return the PDF file content as a binary string (latin-1 encoded)
    # dest='S' returns the document as a string.
    return pdf.output(dest='S').encode('latin-1')