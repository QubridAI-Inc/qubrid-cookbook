"""
LangChain-based vision chain for image conversations.
Uses LangChain memory for conversation history management.
"""
from typing import Iterator, Dict, Any
from PIL import Image
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from backend.qubrid_client import QubridVisionLLM
from backend.prompt import get_system_prompt
from backend.utils import prepare_image_for_api


class VisionChain:
    """
    Vision chain that handles image + text conversations using LangChain.
    
    Responsibilities:
    - Initialize and manage LangChain memory
    - Convert PIL images to base64
    - Format messages for Qubrid API
    - Stream responses from Qubrid
    - Automatically update memory with messages
    """
    
    def __init__(self, memory: InMemoryChatMessageHistory):
        """
        Initialize the vision chain.
        
        Args:
            memory: LangChain InMemoryChatMessageHistory instance
        """
        self.qubrid_client = QubridVisionLLM()
        self.memory = memory
        self.system_prompt = get_system_prompt()
    
    def _format_message_for_api(self, message) -> Dict[str, Any]:
        """
        Convert LangChain message to Qubrid API format.
        
        Args:
            message: LangChain message (SystemMessage, HumanMessage, AIMessage)
            
        Returns:
            Message dict in Qubrid API format
        """
        if isinstance(message, SystemMessage):
            role = "system"
        elif isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        else:
            role = "user"
        
        # Format content as array for Qubrid API
        return {
            "role": role,
            "content": [
                {
                    "type": "text",
                    "text": message.content
                }
            ]
        }
    
    def _build_messages(self, image: Image.Image, user_query: str) -> list:
        """
        Build complete message array for API request.
        
        Args:
            image: PIL Image object
            user_query: Current user question
            
        Returns:
            List of messages in Qubrid API format
        """
        messages = []
        
        # 1. Add system prompt
        messages.append({
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": self.system_prompt
                }
            ]
        })
        
        # 2. Add conversation history from LangChain memory
        chat_history = self.memory.messages
        for msg in chat_history:
            messages.append(self._format_message_for_api(msg))
        
        # 3. Add current user query with image
        image_data = prepare_image_for_api(image)
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_data}
                },
                {
                    "type": "text",
                    "text": user_query
                }
            ]
        })
        
        return messages
    
    def stream(
        self,
        image: Image.Image,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.9,
        top_k: int = 40,
        presence_penalty: float = 0.0
    ) -> Iterator[str]:
        """
        Stream response from vision model and update memory.
        
        Args:
            image: PIL Image object
            user_query: User's question about the image
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling limit
            presence_penalty: Penalty for token presence
            
        Yields:
            Response tokens as they arrive
        """
        # Build messages with history
        messages = self._build_messages(image, user_query)
        
        # Add user message to memory
        self.memory.add_user_message(user_query)
        
        # Stream response
        full_response = ""
        for chunk in self.qubrid_client.stream(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            presence_penalty=presence_penalty
        ):
            full_response += chunk
            yield chunk
        
        # Add assistant response to memory
        self.memory.add_ai_message(full_response)
    
    def clear_memory(self):
        """Clear conversation history."""
        self.memory.clear()