"""
Custom Agno model for Qubrid API compatibility.
Wraps Qubrid API to work with Agno's agent framework.
"""
import os
from typing import Optional, Dict, Any, List
from agno.models.openai import OpenAIChat


class QubridModel(OpenAIChat):
    """
    Custom Agno model for Qubrid API.
    Extends OpenAIChat to ensure proper configuration.
    """
    
    def __init__(
        self,
        id: str = "openai/gpt-oss-20b",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Qubrid model for Agno.
        
        Args:
            id: Model identifier
            api_key: Qubrid API key (defaults to QUBRID_API_KEY env var)
            base_url: Qubrid base URL (defaults to QUBRID_CHAT_URL env var)
            **kwargs: Additional OpenAIChat parameters
        """
        # Get credentials from environment if not provided
        api_key = api_key or os.getenv("QUBRID_API_KEY")
        base_url = base_url or os.getenv("QUBRID_CHAT_URL", "https://platform.qubrid.com/api/v1/qubridai")
        
        # Ensure base_url doesn't have trailing slash
        if base_url.endswith("/"):
            base_url = base_url.rstrip("/")
        
        # Initialize with explicit stream=False to avoid streaming issues
        super().__init__(
            id=id,
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )
