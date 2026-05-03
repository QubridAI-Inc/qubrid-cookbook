"""API client for Qubrid Vision Model with streaming support"""
import requests
import json
from typing import List, Dict, Generator
from config import Config

def call_qubrid_api(messages: List[Dict], stream: bool = False) -> str:
    """
    Call Qubrid API without streaming (default)
    
    Args:
        messages: List of message dictionaries
        stream: Enable streaming (not used in default call)
        
    Returns:
        Complete response text
    """
    headers = {
        "Authorization": f"Bearer {Config.API_KEY}",
        "Content-Type": "application/json"
    }
    
    api_messages = _format_messages(messages)
    
    payload = {
        "model": Config.MODEL_NAME,
        "messages": api_messages,
        "max_tokens": Config.MAX_TOKENS,
        "temperature": Config.TEMPERATURE,
        "stream": False,
        "top_p": Config.TOP_P,
        "presence_penalty": Config.PRESENCE_PENALTY
    }
    
    try:
        response = requests.post(
            Config.API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=Config.TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if "content" in result:
                return result["content"]
            elif "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0].get("message", {}).get("content")
        else:
            raise Exception(f"API Error {response.status_code}: {response.text}")
            
    except Exception as e:
        raise Exception(f"API call failed: {str(e)}")

def call_qubrid_api_stream(messages: List[Dict]) -> Generator[str, None, None]:
    """
    Call Qubrid API with streaming enabled
    
    Args:
        messages: List of message dictionaries
        
    Yields:
        Text chunks as they arrive
    """
    headers = {
        "Authorization": f"Bearer {Config.API_KEY}",
        "Content-Type": "application/json"
    }
    
    api_messages = _format_messages(messages)
    
    payload = {
        "model": Config.MODEL_NAME,
        "messages": api_messages,
        "max_tokens": Config.MAX_TOKENS,
        "temperature": Config.TEMPERATURE,
        "stream": True,
        "top_p": Config.TOP_P,
        "presence_penalty": Config.PRESENCE_PENALTY
    }
    
    try:
        response = requests.post(
            Config.API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=Config.TIMEOUT,
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:]
                    if json_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(json_str)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            content = chunk["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
                        
    except Exception as e:
        raise Exception(f"Streaming API call failed: {str(e)}")

def _format_messages(messages: List[Dict]) -> List[Dict]:
    """Format messages for API"""
    api_messages = []
    
    for msg in messages:
        if msg["role"] == "user":
            content = [{"type": "text", "text": msg["content"]}]
            if "image" in msg:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{msg['image']}"}
                })
            api_messages.append({"role": "user", "content": content})
        else:
            api_messages.append({
                "role": "assistant",
                "content": [{"type": "text", "text": msg["content"]}]
            })
    
    return api_messages
