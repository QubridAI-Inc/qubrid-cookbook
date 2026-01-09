"""
Qubrid API wrapper for vision model integration.
Handles streaming communication with Qubrid's multimodal API.
"""
import os
import json
import requests
from typing import Dict, List, Any, Iterator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class QubridVisionLLM:
    """
    Minimal wrapper for Qubrid's hosted vision model.
    Responsibility: Stream tokens from Qubrid API, nothing else.
    """
    
    def __init__(self):
        """Initialize with API credentials from environment."""
        self.api_key = os.getenv("QUBRID_API_KEY")
        self.api_base = os.getenv(
            "QUBRID_API_BASE", 
            "https://platform.qubrid.com/api/v1/qubridai/multimodal/chat"
        )
        self.model_name = "Qwen/Qwen3-VL-30B-A3B-Instruct"
        
        if not self.api_key:
            raise ValueError("QUBRID_API_KEY must be set in .env file")
    
    def stream(
        self, 
        messages: List[Dict[str, Any]], 
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.9,
        top_k: int = 40,
        presence_penalty: float = 0.0
    ) -> Iterator[str]:
        """
        Stream tokens from Qubrid API.
        
        Args:
            messages: List of message dicts in OpenAI format
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling limit
            presence_penalty: Penalty for token presence
            
        Yields:
            Content chunks as they arrive from the API
            
        Raises:
            requests.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "stream": True,
        }
        
        response = requests.post(
            self.api_base, 
            headers=headers, 
            json=payload, 
            stream=True,
            timeout=60
        )
        response.raise_for_status()
        
        # Parse Server-Sent Events (SSE)
        for line in response.iter_lines():
            if not line:
                continue
                
            decoded_line = line.decode("utf-8")
            
            # SSE format: "data: {json}"
            if not decoded_line.startswith("data: "):
                continue
            
            json_str = decoded_line[6:]  # Remove "data: " prefix
            
            # Check for stream end signal
            if json_str.strip() == "[DONE]":
                break
            
            # Parse and extract content
            try:
                chunk = json.loads(json_str)
                content = chunk["choices"][0]["delta"].get("content", "")
                if content:
                    yield content
            except (json.JSONDecodeError, KeyError, IndexError):
                # Skip malformed chunks
                continue