import requests
import os
import uuid
import random
from config.settings import API_KEY, GENERATION_URL, MODEL_ID, GENERATED_IMAGES_DIR
from backend.state import AgentState
from database.db import add_message

def generate_asset_node(state: AgentState) -> AgentState:
    try:
        print(f"🎨 Generating: {state['user_prompt']}")
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Standard High-Quality Generation Payload
        payload = {
            "model": MODEL_ID,
            "positive_prompt": state['user_prompt'],
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg": 7.5,
            "seed": random.randint(1, 999999),
            "output_format": "png"
        }

        response = requests.post(GENERATION_URL, headers=headers, json=payload)

        if response.status_code == 200:
            filename = f"img_{uuid.uuid4().hex}.png"
            file_path = os.path.join(GENERATED_IMAGES_DIR, filename)
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            # Save interaction
            add_message(state['session_id'], "user", state['user_prompt'])
            add_message(state['session_id'], "assistant", "Generated Asset", file_path)
            
            return {"generated_image_url": file_path, "error": None}
        else:
            return {"generated_image_url": None, "error": f"API Error: {response.text}"}
        
    except Exception as e:
        return {"generated_image_url": None, "error": str(e)}