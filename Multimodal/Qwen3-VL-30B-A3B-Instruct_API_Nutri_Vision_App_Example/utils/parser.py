"""Parse AI responses using Pydantic Schemas"""
import json
import re
from .schemas import NutritionData

def parse_nutrition_data(response_text: str) -> dict:
    """
    Parses AI response into strict Pydantic model and returns dictionary.
    Handles cleanup of markdown formatting if present.
    """
    try:
        # 1. Clean the response (remove ```json ... ``` wrappers if AI adds them)
        clean_text = response_text.strip()
        if "```" in clean_text:
            # Extract content inside code blocks
            match = re.search(r"```(?:json)?(.*?)```", clean_text, re.DOTALL)
            if match:
                clean_text = match.group(1).strip()
        
        # 2. Parse JSON
        # Handle common JSON errors (like trailing commas) loosely if needed
        data_dict = json.loads(clean_text)
        
        # 3. Validate with Pydantic (This fixes types, e.g., "200" string -> 200 int)
        validated_data = NutritionData(**data_dict)
        
        # 4. Return compatible dictionary for your UI
        return validated_data.to_app_dict()

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Parsing Error: {e}")
        # Fallback: Return a "safe" empty structure so the app doesn't crash
        return {
            'dish_name': 'Error Parsing Food',
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'health_score': 0,
            'dietary': {},
            'error': str(e)
        }
