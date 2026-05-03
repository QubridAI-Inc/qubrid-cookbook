"""
Image utility functions for encoding and processing.
"""
import base64
from io import BytesIO
from PIL import Image


def encode_image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string for API transmission.
    
    Args:
        image: PIL Image object
        
    Returns:
        Base64 encoded string of the image
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')


def prepare_image_for_api(image: Image.Image) -> str:
    """
    Prepare image for Qubrid API by encoding to base64.
    
    Args:
        image: PIL Image object
        
    Returns:
        Data URI string with base64 encoded image
    """
    base64_image = encode_image_to_base64(image)
    return f"data:image/png;base64,{base64_image}"