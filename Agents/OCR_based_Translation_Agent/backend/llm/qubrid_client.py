"""
Qubrid API client for language detection and translation.
Pure function-based infrastructure layer - no CrewAI imports.
"""
import os
import json
import requests
from typing import Dict, Iterator
from dotenv import load_dotenv

load_dotenv()


def _parse_sse(response: requests.Response) -> Iterator[str]:
    """Parse Server-Sent Events from streaming response."""
    for line in response.iter_lines():
        if not line:
            continue
            
        decoded_line = line.decode("utf-8")
        
        if not decoded_line.startswith("data: "):
            continue
        
        json_str = decoded_line[6:]  # Remove "data: " prefix
        
        if json_str.strip() == "[DONE]":
            break
        
        try:
            chunk = json.loads(json_str)
            if "choices" in chunk and len(chunk["choices"]) > 0:
                choice = chunk["choices"][0]
                if "delta" in choice and "content" in choice["delta"]:
                    content = choice["delta"]["content"]
                    if content:
                        yield content
                elif "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]
                    if content:
                        yield content
        except (json.JSONDecodeError, KeyError, IndexError):
            continue


def _call_qubrid_api(prompt: str, temperature: float = 0.1) -> str:
    """
    Internal function to call Qubrid GPT-OSS-20B API.
    
    Args:
        prompt: The prompt to send to the model
        temperature: Sampling temperature
        
    Returns:
        Complete response text
        
    Raises:
        ValueError: If API request fails
    """
    api_key = os.getenv("QUBRID_API_KEY")
    chat_url = os.getenv(
        "QUBRID_CHAT_URL",
        "https://platform.qubrid.com/api/v1/qubridai/chat/completions"
    )
    
    if not api_key:
        raise ValueError("QUBRID_API_KEY must be set in environment")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 1024,
        "top_p": 0.9,
        "stream": True
    }
    
    try:
        response = requests.post(
            chat_url,
            headers=headers,
            json=payload,
            timeout=60,
            stream=True
        )
        
        if response.status_code != 200:
            error_body = response.text
            raise ValueError(f"Qubrid API Error {response.status_code}: {error_body}")
        
        # Collect streamed content
        full_content = ""
        for chunk in _parse_sse(response):
            full_content += chunk
        
        return full_content.strip()
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"API request failed: {str(e)}")


