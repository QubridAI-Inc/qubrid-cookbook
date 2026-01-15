from backend.chain import VisionChain
from db.prescriptions import save_prescription
from services.utils import calculate_image_hash, image_to_bytes

def perform_extraction(image, vision_chain: VisionChain):
    """
    Perform full 4-step extraction and save to DB.
    Assume validation has already passed.
    """
    analysis = vision_chain.analyze_prescription(image)
    
    # Calculate hash and bytes for storage
    img_hash = calculate_image_hash(image)
    img_bytes = image_to_bytes(image)
    
    # Inject ambiguity_state into audit for storage
    audit_data = analysis["audit"]
    audit_data["ambiguity_state"] = analysis.get("ambiguity_state", "CLEAR")
    
    # Save to database
    prescription_id = save_prescription(
        image_hash=img_hash,
        image_data=img_bytes,
        extraction_dict=analysis["extraction"],
        audit_dict=audit_data
    )
    
    return prescription_id, analysis
