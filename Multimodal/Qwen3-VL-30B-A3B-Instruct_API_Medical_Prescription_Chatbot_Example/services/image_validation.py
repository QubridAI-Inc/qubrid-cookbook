from backend.chain import VisionChain
from langchain_core.chat_history import InMemoryChatMessageHistory

def validate_prescription(image):
    """
    Validate if the image is a medical prescription.
    Uses VisionChain's Step 0 classification.
    """
    # Temporary chain for one-off validation
    temp_memory = InMemoryChatMessageHistory()
    vision_chain = VisionChain(temp_memory)
    
    # We call analyze_prescription which now includes Step 0
    # and returns early if it fails.
    result = vision_chain.analyze_prescription(image)
    
    val = result.get("validation", {})
    is_valid = val.get("is_prescription", False) and val.get("confidence", 0) >= 0.7
    
    return is_valid, val
