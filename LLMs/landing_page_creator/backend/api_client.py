"""
API client for making requests to the Qubrid AI platform using Kimi K2.5.
"""
import os
import time
import requests
from dotenv import load_dotenv
from config.settings import (
    QUBRID_BASE_URL,
    MODEL_NAME,
    MAX_TOKENS,
    TEMPERATURE,
    SYSTEM_PROMPT
)

# Load environment variables
load_dotenv()

def generate_code_from_image(image_base64: str, mime_type: str, user_note: str = "") -> dict:
    """
    Builds and sends an OpenAI-compatible multimodal request to Qubrid API.
    Returns dict with code, tokens, latency, or error.
    """
    # Force reload of environment variables on every request
    # This ensures Streamlit picks up changes to .env without resetting the server
    load_dotenv(override=True)
    
    api_key = os.getenv("QUBRID_API_KEY")
    if not api_key:
        return {"error": "API key not found. Please set QUBRID_API_KEY in the .env file."}
        
    url = f"{QUBRID_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Build text prompt based on rules
    full_prompt = f"{SYSTEM_PROMPT}\n\nTask: Analyze this UI screenshot and generate complete HTML + Tailwind CSS code that recreates this interface exactly."
    if user_note:
        full_prompt += f"\nUser Note: {user_note}"
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}
                    }
                ]
            }
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }
    
    start_time = time.time()
    try:
        # Increased timeout to 5 minutes (300s) because vision-to-code generation is highly intensive
        response = requests.post(url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        
        data = response.json()
        latency = round((time.time() - start_time) * 1000, 2)
        
        content = data['choices'][0]['message']['content']
        tokens_used = data.get('usage', {}).get('total_tokens', 0)
        
        return {
            "code": content,
            "tokens_used": tokens_used,
            "latency_ms": latency
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"API Request Failed: {str(e)}"
        if getattr(e, 'response', None) is not None:
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    error_msg = f"API Error: {error_data['error'].get('message', str(error_data['error']))}"
            except Exception:
                pass
        return {"error": error_msg}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"} 
