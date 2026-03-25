"""
ReVive AI — CrewAI tools wrapping image_processor.py functions.
These tools are assigned to the Image Restorer agent.
"""

from __future__ import annotations

import json
from typing import Any, Type

import numpy as np

try:
    from pydantic import BaseModel, Field
    from crewai.tools import BaseTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    CREWAI_TOOLS_AVAILABLE = False

from backend import image_processor as ip


# ── Input schemas ─────────────────────────────────────────────────────────────

if CREWAI_TOOLS_AVAILABLE:
    class ImagePathInput(BaseModel):
        """Input model for tools that take an image path."""
        image_path: str = Field(..., description="Path to the input image file")
        parameters: dict = Field(default_factory=dict, description="Operation parameters")

    class ColorizationInput(BaseModel):
        """Input model for the colorization tool."""
        image_path: str = Field(..., description="Path to the image file")
        plan: dict = Field(..., description="Colorization plan dict from colorizer agent")

    class SaveInput(BaseModel):
        """Input model for the save tool."""
        image_path: str = Field(..., description="Path to the image file to save")
        output_name: str = Field(default="restored.png", description="Output filename")


# ── Helper ────────────────────────────────────────────────────────────────────

def _load_and_save(image_path: str, fn, params: dict) -> str:
    """Load image from path, apply fn, save result, return new path."""
    img, mime = ip.load_image_from_path(image_path)
    result = fn(img, params)
    return ip.save_image(result, "processed.png")


# ── Tool classes ──────────────────────────────────────────────────────────────

if CREWAI_TOOLS_AVAILABLE:
    class DenoiseImageTool(BaseTool):
        """Remove noise and grain from image."""

        name: str = "denoise_image"
        description: str = (
            "Remove noise and grain from a photograph. "
            "Input: image_path (str), parameters (dict with optional 'h' key for strength)."
        )
        args_schema: Type[BaseModel] = ImagePathInput

        def _run(self, image_path: str, parameters: dict = {}) -> str:
            return _load_and_save(image_path, ip._denoise, parameters)

    class ContrastEnhanceTool(BaseTool):
        """Apply CLAHE contrast enhancement."""

        name: str = "enhance_contrast"
        description: str = (
            "Apply CLAHE contrast enhancement to improve tonal range. "
            "Input: image_path (str), parameters (dict with clipLimit, tileGridSize)."
        )
        args_schema: Type[BaseModel] = ImagePathInput

        def _run(self, image_path: str, parameters: dict = {}) -> str:
            return _load_and_save(image_path, ip._contrast_clahe, parameters)

    class SharpenImageTool(BaseTool):
        """Sharpen image details and edges."""

        name: str = "sharpen_image"
        description: str = (
            "Sharpen image edges and fine details. "
            "Input: image_path (str), parameters (dict with optional 'amount' key)."
        )
        args_schema: Type[BaseModel] = ImagePathInput

        def _run(self, image_path: str, parameters: dict = {}) -> str:
            return _load_and_save(image_path, ip._sharpen, parameters)

    class InpaintRegionTool(BaseTool):
        """Fill in tears, missing regions, and scratches."""

        name: str = "inpaint_region"
        description: str = (
            "Fill in damaged regions, tears, and scratches using inpainting. "
            "Input: image_path (str), parameters (dict with optional 'inpaintRadius')."
        )
        args_schema: Type[BaseModel] = ImagePathInput

        def _run(self, image_path: str, parameters: dict = {}) -> str:
            return _load_and_save(image_path, ip._inpaint, parameters)

    class ColorCorrectTool(BaseTool):
        """Fix color balance, remove yellowing, restore tones."""

        name: str = "color_correct"
        description: str = (
            "Fix color balance, remove yellowing, and restore natural tones. "
            "Input: image_path (str), parameters (dict with color, contrast, brightness)."
        )
        args_schema: Type[BaseModel] = ImagePathInput

        def _run(self, image_path: str, parameters: dict = {}) -> str:
            return _load_and_save(image_path, ip._color_correct, parameters)

    class ApplyColorizationTool(BaseTool):
        """Apply colorization plan to B&W image."""

        name: str = "apply_colorization"
        description: str = (
            "Apply a colorization plan to convert a B&W image to color. "
            "Input: image_path (str), plan (colorization plan dict)."
        )
        args_schema: Type[BaseModel] = ColorizationInput

        def _run(self, image_path: str, plan: dict) -> str:
            img, mime = ip.load_image_from_path(image_path)
            colorized = ip.apply_colorization(img, plan)
            return ip.save_image(colorized, "colorized.png")

    class SaveRestoredImageTool(BaseTool):
        """Save the processed image to outputs directory."""

        name: str = "save_image"
        description: str = (
            "Save the processed image to the outputs directory. "
            "Input: image_path (str), output_name (str)."
        )
        args_schema: Type[BaseModel] = SaveInput

        def _run(self, image_path: str, output_name: str = "restored.png") -> str:
            img, mime = ip.load_image_from_path(image_path)
            return ip.save_image(img, output_name)

else:
    # Stub classes when crewai.tools unavailable
    class _StubTool:
        def __init__(self) -> None:
            pass

    DenoiseImageTool = _StubTool
    ContrastEnhanceTool = _StubTool
    SharpenImageTool = _StubTool
    InpaintRegionTool = _StubTool
    ColorCorrectTool = _StubTool
    ApplyColorizationTool = _StubTool
    SaveRestoredImageTool = _StubTool
