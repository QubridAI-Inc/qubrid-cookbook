"""
Image processing utilities for SnapCode AI.
Handles loading, validation, dimensions, and base64 encoding.
"""
import base64
from typing import Tuple
from io import BytesIO
from PIL import Image
from config.settings import MAX_FILE_SIZE_MB, SUPPORTED_FORMATS

def validate_image(uploaded_file) -> Tuple[bool, str]:
    """
    Validates the uploaded file format and size.
    Returns (is_valid, error_message).
    """
    if uploaded_file is None:
        return False, "No file uploaded."
    
    # Check size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds the {MAX_FILE_SIZE_MB}MB limit."
    
    # Check format using file extension from name or mime type
    file_ext = uploaded_file.name.split('.')[-1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        return False, f"Unsupported file format '{file_ext}'. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        
    return True, ""

def load_and_encode(uploaded_file) -> Tuple[str, str]:
    """
    Reads the file, heavily compresses it to prevent payload timeouts at the API gateway,
    and returns base64 string and mime type.
    """
    image = Image.open(uploaded_file)
    
    # 1. Convert any RGBA/Palette images to standard RGB for JPEG compression
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        
    # 2. Resize maintaining aspect ratio if the image is too large (max 1600px)
    max_size = 1600
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
    # 3. Compress heavily into memory buffer
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=80)
    
    # 4. Final Base64 encoding
    base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_string, "image/jpeg"

def get_image_dimensions(uploaded_file) -> Tuple[int, int]:
    """
    Gets the dimensions (width, height) from the uploaded image.
    Uses PIL.
    """
    try:
        image = Image.open(uploaded_file)
        return image.size
    except Exception as e:
        return 0, 0
