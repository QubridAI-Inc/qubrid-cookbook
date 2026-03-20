"""
API client for Qubrid AI platform - Kimi K2 Thinking model integration.
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

# Ensure the environment variables are loaded
load_dotenv()

def solve_problem(question: str, category: str) -> dict:
    """
    Makes a POST request to Qubrid API using the Kimi K2 Thinking model.
    temperature = 1.0 (mandatory for thinking mode)
    
    Returns a dict with:
      - reasoning: str
      - answer: str
      - tokens_used: int
      - thinking_tokens: int
      - latency_ms: float
      
    On failure: returns {"error": str}
    """
    api_key = os.getenv("QUBRID_API_KEY")
    if not api_key:
        return {"error": "API Key not found. Please set QUBRID_API_KEY in .env file."}

    # Normalize url to prevent double slashes before api path
    url = f"{QUBRID_BASE_URL.rstrip('/')}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # As per prompt, only include the basic system prompt and the user question
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }

    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        latency_ms = (time.time() - start_time) * 1000

        choices = data.get("choices", [])
        if not choices:
            return {"error": "Received empty choices array from Qubrid API."}

        message = choices[0].get("message", {})
        usage = data.get("usage", {})

        return {
            "reasoning": message.get("reasoning_content", ""),
            "answer": message.get("content", ""),
            "tokens_used": usage.get("total_tokens", 0),
            "thinking_tokens": usage.get("reasoning_tokens", 0),
            "latency_ms": latency_ms
        }

    except requests.exceptions.HTTPError as e:
        # Provide more specific API error context if available
        status = e.response.status_code
        err_msg = e.response.text
        return {"error": f"HTTP {status} Error: {err_msg}"}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network Error: {str(e)}"}
        
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
