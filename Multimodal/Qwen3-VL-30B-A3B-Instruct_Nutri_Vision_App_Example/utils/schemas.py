"""
Pydantic schemas for strict type enforcement.
This acts as a guardrail against hallucinations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class DietaryCheck(BaseModel):
    vegan: bool = Field(description="Is the dish vegan?")
    vegetarian: bool = Field(description="Is the dish vegetarian?")
    keto_friendly: bool = Field(description="Is the dish keto-friendly?")
    gluten_free: bool = Field(description="Is the dish gluten-free?")
    dairy_free: bool = Field(description="Is the dish dairy-free?")
    high_protein: bool = Field(description="Is the dish considered high-protein?")

class NutritionData(BaseModel):
    dish_name: str = Field(description="The identified name of the dish")
    calories: int = Field(description="Estimated calories per 100g")
    protein: float = Field(description="Protein content in grams per 100g")
    carbs: float = Field(description="Carbohydrate content in grams per 100g")
    fat: float = Field(description="Fat content in grams per 100g")
    fiber: float = Field(description="Fiber content in grams per 100g")
    sugar: float = Field(description="Sugar content in grams per 100g")
    health_score: int = Field(description="Health score from 0-100", ge=0, le=100)
    dietary: DietaryCheck = Field(description="Dietary compatibility flags")
    health_insights: List[str] = Field(description="3 distinct bullet points about health benefits/risks")
    allergens: List[str] = Field(description="List of potential allergens")

    # Helper to convert to the dictionary format your app expects
    def to_app_dict(self):
        data = self.model_dump()
        # Flatten dietary for the existing UI components
        return data
