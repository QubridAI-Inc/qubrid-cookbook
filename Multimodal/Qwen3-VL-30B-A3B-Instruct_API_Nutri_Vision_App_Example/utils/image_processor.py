"""Image processing utilities"""
import base64
from io import BytesIO
from PIL import Image

def encode_image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string for API transmission
    
    Args:
        image: PIL Image object
        
    Returns:
        Base64 encoded string
    """
    buffered = BytesIO()
    
    # Convert to RGB if needed
    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')
    
    # Save as JPEG with high quality
    image.save(buffered, format="JPEG", quality=95)
    
    # Encode to base64
    return base64.b64encode(buffered.getvalue()).decode()
