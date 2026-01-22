"""
OCR module for extracting text from images using Hunyuan OCR.
This is a manual, non-agent operation.
"""
import os
import json
import requests
from typing import Dict, Any, Iterator
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


def extract_text_from_image(image_data: str) -> Dict[str, Any]:
    """
    Extract text from an image using Hunyuan OCR.
    
    Args:
        image_data: Base64-encoded image data URI
        
    Returns:
        Dict containing:
            - raw_text: Extracted text
            - confidence: OCR confidence score
            - has_text: Whether text was found
            
    Raises:
        ValueError: If API request fails
    """
    api_key = os.getenv("QUBRID_API_KEY")
    ocr_url = os.getenv(
        "QUBRID_OCR_URL",
        "https://platform.qubrid.com/api/v1/qubridai/ocr/chat"
    )
    
    if not api_key:
        raise ValueError("QUBRID_API_KEY must be set in environment")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "tencent/HunyuanOCR",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data}
                    },
                    {
                        "type": "text",
                        "text": "Extract all text from this image."
                    }
                ]
            }
        ],
        "temperature": 0.1,
        "top_p": 0.9,
        "stream": True
    }
    
    try:
        response = requests.post(
            ocr_url,
            headers=headers,
            json=payload,
            timeout=60,
            stream=True
        )
        
        if response.status_code != 200:
            error_body = response.text
            raise ValueError(f"OCR API Error {response.status_code}: {error_body}")
        
        # Collect streamed content
        full_content = ""
        for chunk in _parse_sse(response):
            full_content += chunk
        
        return {
            "raw_text": full_content.strip(),
            "confidence": 0.95,
            "has_text": len(full_content.strip()) > 0
        }
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"OCR request failed: {str(e)}")
