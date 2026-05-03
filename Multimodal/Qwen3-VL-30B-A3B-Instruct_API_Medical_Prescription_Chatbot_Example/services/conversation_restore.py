from db.prescriptions import get_prescription_by_hash
from db.chat import get_chat_history
from services.utils import bytes_to_image
from langchain_core.messages import HumanMessage, AIMessage

def restore_conversation_by_hash(image_hash):
    """
    Check for existing prescription by hash and restore state.
    Returns (prescription_id, image, analysis, chat_history) or None.
    """
    db_record = get_prescription_by_hash(image_hash)
    if not db_record:
        return None
    
    prescription_id = db_record["id"]
    image = bytes_to_image(db_record["image_data"])
    
    analysis = {
        "extraction": db_record["extraction"],
        "audit": db_record["audit"],
        "validation": db_record["audit"].get("validation", {"is_prescription": True, "confidence": 1.0})
    }
    
    # Fetch chat history from DB
    db_history = get_chat_history(prescription_id)
    
    # Format for LangChain/UI
    chat_history = []
    for msg in db_history:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        else:
            chat_history.append(AIMessage(content=msg["content"]))
            
    return prescription_id, image_hash, image, analysis, chat_history
