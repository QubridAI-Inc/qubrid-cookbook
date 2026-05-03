"""
Translation pipeline orchestration using Agno agents.
Agents execute via Agno's agent.run() with explicit Qubrid configuration.
"""
from typing import Dict, Any
from backend.agents import create_language_detection_agent, create_translation_agent


class TranslationPipeline:
    """
    Orchestrates the translation workflow using Agno agents.
    
    Pipeline:
    1. Language Detection Agent (Agno) → Qubrid GPT-OSS-20B
    2. Translation Agent (Agno) → Qubrid GPT-OSS-20B
    
    Uses Agno framework for agent lifecycle and execution.
    """
    
    def __init__(self):
        """Initialize the translation pipeline with Agno agents."""
        self.detection_agent = create_language_detection_agent()
        self.translation_agent = create_translation_agent()
    
    def _collect_streaming_response(self, response) -> str:
        """
        Collect content from Agno streaming response.
        
        Args:
            response: Agno RunOutput or generator
            
        Returns:
            Complete response text
        """
        # If response has content attribute (non-streaming), use it directly
        if hasattr(response, 'content'):
            return response.content.strip()
        
        # Otherwise, it's a streaming generator - collect all chunks
        full_content = ""
        try:
            for chunk in response:
                if hasattr(chunk, 'content') and chunk.content:
                    full_content += chunk.content
        except Exception as e:
            # If streaming fails, try to get content from the response object
            if hasattr(response, 'content'):
                return response.content.strip()
            raise e
        
        return full_content.strip()
    
    def translate(self, text: str, target_language: str) -> Dict[str, Any]:
        """
        Execute the translation pipeline using Agno agents.
        
        Args:
            text: Text to translate
            target_language: Target language name or code
            
        Returns:
            Dict containing:
                - success: Whether translation succeeded
                - detected_language: Source language
                - translated_text: Translation result
                - error: Error message if failed
        """
        try:
            # Step 1: Language Detection via Agno Agent
            detection_response = self.detection_agent.run(
                input=f"Detect the language of this text: {text}"
            )
            detected_lang = self._collect_streaming_response(detection_response)
            
            # Step 2: Translation via Agno Agent
            translation_response = self.translation_agent.run(
                input=f"Translate the following text to {target_language}:\n\n{text}"
            )
            translated = self._collect_streaming_response(translation_response)
            
            return {
                "success": True,
                "detected_language": detected_lang,
                "is_multilingual": False,  # Can be enhanced later
                "translated_text": translated,
                "raw_output": translated
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "detected_language": None,
                "translated_text": None
            }



