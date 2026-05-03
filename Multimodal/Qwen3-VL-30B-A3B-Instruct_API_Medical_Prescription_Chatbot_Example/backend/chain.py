"""
LangChain-based vision chain for image conversations.
Uses LangChain memory for conversation history management.
"""
import json
from typing import Iterator, Dict, Any, List
from PIL import Image
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from backend.qubrid_client import QubridVisionLLM
from backend.prompt import get_step_prompt, get_mode_prompt, GLOBAL_DISCLAIMER
from backend.utils import prepare_image_for_api
from db.chat import save_chat_message


class VisionChain:
    """
    Evolved Vision chain for structured medical prescription analysis.
    
    Responsibilities:
    - Multi-step reasoning (OCR -> Normalize -> Audit)
    - Mode-based chat streaming
    - Structured JSON extraction
    """
    
    def __init__(self, memory: InMemoryChatMessageHistory, prescription_id: str = None):
        """
        Initialize the vision chain.
        """
        self.qubrid_client = QubridVisionLLM()
        self.memory = memory
        self.prescription_id = prescription_id
    
    def analyze_prescription(self, image: Image.Image) -> Dict[str, Any]:
        """
        Execute the 4-step medical reasoning pipeline.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict containing extraction results, ambiguities, and confidence.
        """
        image_data = prepare_image_for_api(image)
        
        # STEP 0: CLASSIFICATION
        validation_json_str = self._call_non_streaming(
            prompt=get_step_prompt("validation"),
            image_url=image_data,
            user_query="Is this image a doctor's medical prescription?"
        )
        
        try:
            validation = json.loads(self._clean_json_response(validation_json_str))
        except:
            validation = {"is_prescription": False, "confidence": 0, "reason": "Classification failed"}

        # GATE: Block if not a prescription or low confidence
        if not validation.get("is_prescription") or validation.get("confidence", 0) < 0.7:
            return {
                "validation": validation,
                "extraction": {"medicines": [], "overall_confidence": 0},
                "audit": {"ambiguities": [], "safety_flags": ["Image rejected by safety gate."], "is_safe_to_display": False},
                "raw_ocr": ""
            }

        # STEP 1: RAW OCR
        raw_ocr = self._call_non_streaming(
            prompt=get_step_prompt("ocr"),
            image_url=image_data,
            user_query="Please extract all text from this prescription."
        )
        
        # STEP 2: NORMALIZATION
        normalization_json_str = self._call_non_streaming(
            prompt=get_step_prompt("normalize"),
            user_query=f"Convert this OCR text into the medical JSON schema:\n\n{raw_ocr}"
        )
        
        try:
            extraction = json.loads(self._clean_json_response(normalization_json_str))
        except:
            extraction = {"medicines": [], "overall_confidence": 0}

        # STEP 3 & 4: AUDIT (Ambiguity & Safety)
        audit_json_str = self._call_non_streaming(
            prompt=get_step_prompt("audit"),
            user_query=f"Original OCR Text:\n{raw_ocr}\n\nExtracted JSON:\n{json.dumps(extraction)}\n\nAudit for safety and ambiguity."
        )
        
        try:
            audit = json.loads(self._clean_json_response(audit_json_str))
        except:
            audit = {"ambiguities": [], "safety_flags": [], "is_safe_to_display": False}
        
        audit["validation"] = validation
        
        # DETERMINE AMBIGUITY STATE
        confidence = extraction.get("overall_confidence", 1.0)
        ambiguities = audit.get("ambiguities", [])
        
        if confidence >= 0.7:
            ambiguity_state = "CLEAR"
        elif len(ambiguities) > 0 and any(len(a.get("options", [])) > 0 for a in ambiguities):
            ambiguity_state = "CLARIFIABLE"
        else:
            ambiguity_state = "UNRESOLVABLE"
            # Add safety flags for unresolvable state
            if "safety_flags" not in audit:
                audit["safety_flags"] = []
            if "Handwriting too unclear for safe AI interpretation" not in audit["safety_flags"]:
                audit["safety_flags"].append("Handwriting too unclear for safe AI interpretation")
            if "No medically safe correction candidates available" not in audit["safety_flags"]:
                audit["safety_flags"].append("No medically safe correction candidates available")

        return {
            "validation": validation,
            "extraction": extraction,
            "audit": audit,
            "raw_ocr": raw_ocr,
            "ambiguity_state": ambiguity_state
        }

    def generate_final_schedule(self, merged_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a final JSON schedule from merged AI + Human context.
        """
        response_str = self._call_non_streaming(
            prompt=get_step_prompt("schedule_final"),
            user_query=f"Verified Context:\n{json.dumps(merged_context)}\n\nGenerate schedule JSON."
        )
        
        try:
            return json.loads(self._clean_json_response(response_str))
        except:
            return {"schedule": []}

    def stream_with_mode(
        self,
        image: Image.Image,
        user_query: str,
        mode: str,
        extraction_context: Dict[str, Any],
        ambiguity_state: str = "CLEAR",
        **model_params
    ) -> Iterator[str]:
        """
        Stream response based on specific chat mode and extraction context.
        """
        system_prompt = get_mode_prompt(mode)
        
        # Inject Safety Safeguard for Unresolvable Ambiguity
        if ambiguity_state == "UNRESOLVABLE":
            system_prompt += "\n\nSAFETY RULE: The current prescription handwriting is UNRESOLVABLE. Do NOT infer or suggest medicine names unless the user explicitly provides them in this chat. Avoid all guesses."

        context_msg = f"Context: The following verified data was extracted from the prescription: {json.dumps(extraction_context)}"
        
        # Merge system prompt and context into one system message
        combined_system = f"{system_prompt}\n\n{context_msg}"
        
        messages = [
            {"role": "system", "content": [{"type": "text", "text": combined_system}]}
        ]
        
        # Add history
        for msg in self.memory.messages:
            messages.append(self._format_message_for_api(msg))
            
        # Add current query with image
        image_data = prepare_image_for_api(image)
        messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_data}},
                {"type": "text", "text": user_query}
            ]
        })
        
        # Update memory and DB
        self.memory.add_user_message(user_query)
        if self.prescription_id:
            save_chat_message(self.prescription_id, "user", user_query)
        
        full_response = ""
        for chunk in self.qubrid_client.stream(messages=messages, **model_params):
            full_response += chunk
            yield chunk
            
        # Append disclaimer
        response_with_disclaimer = full_response + GLOBAL_DISCLAIMER
        yield GLOBAL_DISCLAIMER
        
        self.memory.add_ai_message(response_with_disclaimer)
        if self.prescription_id:
            save_chat_message(self.prescription_id, "assistant", response_with_disclaimer)

    def _call_non_streaming(self, prompt: str, user_query: str, image_url: str = None) -> str:
        """Helper for internal reasoning steps."""
        contents = [{"type": "text", "text": prompt}]
        
        user_content = []
        if image_url:
            user_content = [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": user_query}
            ]
        else:
            user_content = user_query
            
        messages = [
            {"role": "system", "content": [{"type": "text", "text": prompt}]},
            {"role": "user", "content": user_content}
        ]
        
        response = ""
        for chunk in self.qubrid_client.stream(messages=messages, temperature=0.1):
            response += chunk
        return response

    def _clean_json_response(self, text: str) -> str:
        """Remove markdown artifacts from JSON responses."""
        return text.strip().replace("```json", "").replace("```", "")

    def _format_message_for_api(self, message) -> Dict[str, Any]:
        role = "system" if isinstance(message, SystemMessage) else \
               "user" if isinstance(message, HumanMessage) else "assistant"
        return {
            "role": role,
            "content": [{"type": "text", "text": message.content}]
        }

    def clear_memory(self):
        self.memory.clear()