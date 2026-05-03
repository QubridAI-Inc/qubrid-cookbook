import hashlib
from PIL import Image
import io

def calculate_image_hash(image: Image.Image) -> str:
    """Calculate SHA-256 hash of a PIL image."""
    img_byte_arr = io.BytesIO()
    # Save as PNG to ensure consistent byte representation
    image.save(img_byte_arr, format='PNG')
    return hashlib.sha256(img_byte_arr.getvalue()).hexdigest()

def image_to_bytes(image: Image.Image) -> bytes:
    """Convert PIL image to bytes."""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def bytes_to_image(image_bytes: bytes) -> Image.Image:
    """Convert bytes to PIL image."""
    return Image.open(io.BytesIO(image_bytes))
