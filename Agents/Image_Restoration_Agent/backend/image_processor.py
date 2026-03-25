"""
ReVive AI — All PIL/OpenCV image operations.
No image manipulation should happen outside this module.
"""

import base64
import os
import uuid
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageEnhance

from config.settings import OUTPUTS_DIR, MAX_FILE_SIZE_MB, SUPPORTED_FORMATS


# ── Loading & encoding ────────────────────────────────────────────────────────

def load_image(uploaded_file: Any) -> tuple[np.ndarray, str]:
    """
    Load a Streamlit uploaded file into a cv2 BGR image.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        (cv2_bgr_image, mime_type) tuple.

    Raises:
        ValueError: For unsupported format or oversized file.
    """
    filename: str = uploaded_file.name.lower()
    ext = filename.rsplit(".", 1)[-1]
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: .{ext}. Use {SUPPORTED_FORMATS}")

    data = uploaded_file.read()
    size_mb = len(data) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File too large ({size_mb:.1f} MB). Max {MAX_FILE_SIZE_MB} MB.")

    # Determine MIME
    mime_map = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "webp": "image/webp", "bmp": "image/bmp", "tiff": "image/tiff",
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. File may be corrupted.")

    return img, mime_type


def load_image_from_path(path: str) -> tuple[np.ndarray, str]:
    """Load an image from a file path into cv2 BGR format."""
    ext = path.rsplit(".", 1)[-1].lower()
    mime_map = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "webp": "image/webp", "bmp": "image/bmp", "tiff": "image/tiff",
    }
    mime_type = mime_map.get(ext, "image/jpeg")
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not load image from path: {path}")
    return img, mime_type


def image_to_base64(image: np.ndarray, mime: str = "image/jpeg") -> str:
    """
    Convert a cv2 BGR image to a base64-encoded string.

    Args:
        image: cv2 BGR numpy array.
        mime:  MIME type hint for encoding format selection.

    Returns:
        Base64 string (no data-URI prefix).
    """
    fmt = ".jpg" if "jpeg" in mime else ".png"
    success, buffer = cv2.imencode(fmt, image)
    if not success:
        raise ValueError("Failed to encode image to base64.")
    return base64.b64encode(buffer).decode("utf-8")


def save_image(image: np.ndarray, filename: str) -> str:
    """
    Save a cv2 image to OUTPUTS_DIR with a unique name.

    Args:
        image:    cv2 BGR numpy array.
        filename: Desired filename (will be prefixed with uuid).

    Returns:
        Absolute path to the saved file.
    """
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    uid = uuid.uuid4().hex[:8]
    safe_name = filename.replace(" ", "_")
    out_path = os.path.join(OUTPUTS_DIR, f"{uid}_{safe_name}")
    cv2.imwrite(out_path, image)
    return out_path


# ── Safe parameter limits ─────────────────────────────────────────────────────
# These hard caps prevent AI-suggested params from creating destructive effects.
# fastNlMeansDenoising h≥7 produces the "oil-painting" smear on modern photos.
_PARAM_LIMITS: dict[str, dict[str, tuple[float, float]]] = {
    "denoise":           {"h": (1, 4)},          # >4 = painterly smear on clean photos
    "denoise_bw":        {"h": (1, 7)},
    "contrast_clahe":    {"clipLimit": (0.5, 1.5), "tileGridSize": (4, 16)},
    "sharpen":           {"amount": (0.1, 0.6)},  # unsharp-mask; >0.6 creates halos
    "color_correct":     {"color": (0.9, 1.3), "contrast": (0.9, 1.2), "brightness": (0.9, 1.15)},
    "gamma_correct":     {"gamma": (0.8, 1.4)},
    "fade_restore":      {"blend": (0.1, 0.4)},
    "inpaint":           {"inpaintRadius": (1, 5)},
    "scratch_remove":    {"inpaintRadius": (1, 5)},
    "enhance":           {"strength": (0.2, 0.75), "sigma_s": (5, 15), "sigma_r": (0.05, 0.15)},
    "clarity":           {"amount": (0.05, 0.45)},
    "shadows_highlights":{"shadows": (0.0, 0.35), "highlights": (0.0, 0.25)},
}


def _clamp_params(op: str, params: dict) -> dict:
    """Return params with every value clamped to the op's safe range."""
    limits = _PARAM_LIMITS.get(op, {})
    out = dict(params)
    for key, (lo, hi) in limits.items():
        if key in out:
            try:
                out[key] = max(lo, min(hi, type(lo)(out[key])))
            except (TypeError, ValueError):
                out[key] = lo
    return out


# ── Restoration operations ────────────────────────────────────────────────────

def _denoise(img: np.ndarray, params: dict) -> np.ndarray:
    h = int(params.get("h", 3))          # safe default: 3 (was 10 → oil-paint)
    template_size = int(params.get("template_window_size", 7))
    search_size = int(params.get("search_window_size", 21))
    if len(img.shape) == 3:
        return cv2.fastNlMeansDenoisingColored(img, None, h, h, template_size, search_size)
    return cv2.fastNlMeansDenoising(img, None, h, template_size, search_size)


def _denoise_bw(img: np.ndarray, params: dict) -> np.ndarray:
    h = int(params.get("h", 5))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    denoised = cv2.fastNlMeansDenoising(gray, None, h, 7, 21)
    if len(img.shape) == 3:
        return cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
    return denoised


def _contrast_clahe(img: np.ndarray, params: dict) -> np.ndarray:
    clip = float(params.get("clipLimit", 1.2))  # safe default: 1.2 (was 2.0)
    tile = int(params.get("tileGridSize", 8))
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
    if len(img.shape) == 3:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_orig = lab[:, :, 0].copy()
        l_enhanced = clahe.apply(l_orig)
        # Blend 50/50 to avoid over-enhancement
        lab[:, :, 0] = cv2.addWeighted(l_orig, 0.5, l_enhanced, 0.5, 0)
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return clahe.apply(img)


def _sharpen(img: np.ndarray, params: dict) -> np.ndarray:
    """Unsharp mask — far gentler than the edge-enhance kernel; no halos."""
    amount = float(params.get("amount", 0.4))   # safe default: 0.4 (was 1.5)
    sigma = float(params.get("sigma", 1.0))
    blurred = cv2.GaussianBlur(img, (0, 0), sigma)
    sharpened = cv2.addWeighted(img, 1.0 + amount, blurred, -amount, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def _inpaint(img: np.ndarray, params: dict) -> np.ndarray:
    radius = int(params.get("inpaintRadius", 3))
    # Build mask from extreme artifact regions only (not normal image content)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    _, mask_dark = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)   # very dark
    _, mask_bright = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)     # blown-out
    mask = cv2.bitwise_or(mask_dark, mask_bright)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.dilate(mask, kernel, iterations=1)
    return cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)


def _color_correct(img: np.ndarray, params: dict) -> np.ndarray:
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    color_factor     = float(params.get("color",      1.05))  # safe defaults
    contrast_factor  = float(params.get("contrast",   1.05))
    brightness_factor= float(params.get("brightness", 1.0))
    pil = ImageEnhance.Color(pil).enhance(color_factor)
    pil = ImageEnhance.Contrast(pil).enhance(contrast_factor)
    pil = ImageEnhance.Brightness(pil).enhance(brightness_factor)
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def _gamma_correct(img: np.ndarray, params: dict) -> np.ndarray:
    gamma = float(params.get("gamma", 1.1))   # safe default: 1.1 (was 1.2)
    inv_gamma = 1.0 / gamma
    table = (np.arange(256) / 255.0) ** inv_gamma * 255
    table = table.astype(np.uint8)
    return cv2.LUT(img, table)


def _scratch_remove(img: np.ndarray, params: dict) -> np.ndarray:
    radius = int(params.get("inpaintRadius", 3))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    _, mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    mask = cv2.dilate(mask, kernel2, iterations=1)
    return cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)


def _fade_restore(img: np.ndarray, params: dict) -> np.ndarray:
    """
    Restore faded images by boosting luminance only.

    Equalises the L channel in LAB space — never the R/G/B channels
    independently, which would create severe colour casts and grain.
    """
    alpha = float(params.get("blend", 0.5))
    if len(img.shape) == 3:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_orig = lab[:, :, 0]
        l_eq = cv2.equalizeHist(l_orig)
        # Gentle blend: don't blow out highlights
        lab[:, :, 0] = cv2.addWeighted(l_orig, 1.0 - alpha, l_eq, alpha, 0)
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    # Grayscale path
    return cv2.equalizeHist(img)


def _enhance(img: np.ndarray, params: dict) -> np.ndarray:
    """
    Lightroom-style sharpening: bilateral denoise → unsharp mask → mild saturation.

    bilateralFilter is the gold-standard for edge-preserving noise reduction —
    it smooths flat areas without blurring edges, so the subsequent unsharp
    mask sharpens real detail, not noise.  Saturation boost is capped at +12
    HSV points to prevent colour-cast blobs on old/warm-toned images.
    """
    strength = float(params.get("strength", 0.60))
    sigma_s  = float(params.get("sigma_s",  10))    # bilateral spatial sigma
    sigma_r  = float(params.get("sigma_r",  0.10))  # colour sensitivity (0-1 scale)

    # 1. Edge-preserving denoise via bilateral filter
    color_sigma = sigma_r * 255          # convert to 0-255 scale for OpenCV
    d = max(5, int(sigma_s * 0.5) | 1)  # kernel diameter (must be odd, ≥5)
    smooth = cv2.bilateralFilter(img, d, color_sigma, sigma_s * 2.5)

    # 2. Unsharp mask on the smoothed image (avoids sharpening noise)
    blur = cv2.GaussianBlur(smooth, (0, 0), 1.2)
    sharp = cv2.addWeighted(smooth, 1.0 + strength * 0.45,
                            blur,   -strength * 0.45, 0)

    # 3. Mild saturation boost — hard cap at +12 HSV to prevent colour blobs
    hsv = cv2.cvtColor(sharp, cv2.COLOR_BGR2HSV).astype(np.float32)
    sat = hsv[:, :, 1]
    boost = np.clip((1.0 - sat / 255.0) * 12.0 * strength, 0, 12)
    hsv[:, :, 1] = np.clip(sat + boost, 0, 255)
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    return np.clip(result, 0, 255).astype(np.uint8)


def _clarity(img: np.ndarray, params: dict) -> np.ndarray:
    """
    Lightroom-style Clarity: wide-Gaussian local contrast boost.

    Formula: result = img + amount × (img − wide_blur(img))
    The wide Gaussian (σ=15) captures broad tonal regions; subtracting it
    from the original isolates mid-frequency texture.  Adding that texture
    back gives depth and punch without edge halos or noise amplification.
    """
    amount = float(params.get("amount", 0.28))

    # Wide blur captures macro luminance → residual is texture only
    low_freq = cv2.GaussianBlur(img, (0, 0), 15.0)
    residual = img.astype(np.float32) - low_freq.astype(np.float32)

    result = img.astype(np.float32) + residual * amount
    return np.clip(result, 0, 255).astype(np.uint8)


def _shadows_highlights(img: np.ndarray, params: dict) -> np.ndarray:
    """
    Lift crushed shadows; gently pull back blown highlights.

    Uses a luminance-based mask so only dark pixels are lifted and only
    bright pixels are recovered — midtones stay untouched.
    """
    shadows    = float(params.get("shadows",    0.15))
    highlights = float(params.get("highlights", 0.10))

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L   = lab[:, :, 0]   # 0–255 range in cv2's LAB

    # Shadow mask: 1.0 at L=0, 0.0 at L=128+
    shadow_mask = np.clip(1.0 - L / 128.0, 0, 1) ** 2
    # Highlight mask: 0.0 at L=128, 1.0 at L=255
    highlight_mask = np.clip((L - 128.0) / 127.0, 0, 1) ** 2

    L = L + shadow_mask    * shadows    * 60   # lift shadows up to +60 pts
    L = L - highlight_mask * highlights * 40   # pull highlights down up to -40 pts
    lab[:, :, 0] = np.clip(L, 0, 255)

    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


_OP_MAP = {
    "denoise":           _denoise,
    "denoise_bw":        _denoise_bw,
    "contrast_clahe":    _contrast_clahe,
    "sharpen":           _sharpen,
    "inpaint":           _inpaint,
    "color_correct":     _color_correct,
    "gamma_correct":     _gamma_correct,
    "scratch_remove":    _scratch_remove,
    "fade_restore":      _fade_restore,
    "enhance":           _enhance,
    "clarity":           _clarity,
    "shadows_highlights":_shadows_highlights,
}


def apply_restoration(
    image: np.ndarray,
    steps: list[dict],
) -> np.ndarray:
    """
    Execute each restoration step from the strategist brief in order.

    Args:
        image: Input cv2 BGR image.
        steps: List of step dicts with keys: operation, parameters.

    Returns:
        Restored cv2 BGR image.
    """
    result = image.copy()
    for step in steps:
        op = step.get("operation", "")
        params = step.get("parameters", {})
        if isinstance(params, str):
            params = {}
        fn = _OP_MAP.get(op)
        if fn:
            try:
                safe_params = _clamp_params(op, params)   # enforce hard safety limits
                result = fn(result, safe_params)
            except Exception:
                # Skip failed step; never crash the pipeline
                pass
    return result


# ── Colorization ──────────────────────────────────────────────────────────────

def _hex_to_bgr(hex_color: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' to BGR tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (128, 128, 128)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)


def apply_colorization(
    image: np.ndarray,
    plan: dict,
) -> np.ndarray:
    """
    Apply a colorization plan to a grayscale or sepia image.

    Converts to LAB, applies color hints per region using color transfer,
    blends with original, and applies global adjustments.

    Args:
        image: Input cv2 BGR image (likely grayscale-in-BGR).
        plan:  Colorization plan dict from the colorizer agent.

    Returns:
        Colorized cv2 BGR image.
    """
    # Ensure grayscale-in-BGR → true grayscale first
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Create a warm-toned base using LAB
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)

    regions = plan.get("colorization_regions", [])
    global_adj = plan.get("global_adjustments", {})

    # Build an overall color tint from the first region's base color
    dominant_bgr: tuple[int, int, int] = (120, 90, 60)  # default warm brown
    if regions:
        first_color = regions[0].get("base_color", "#7a5c3c")
        dominant_bgr = _hex_to_bgr(first_color)

    # Create tinted version
    warmth = float(global_adj.get("warmth", 10))
    saturation = float(global_adj.get("saturation", 60)) / 100.0

    # Convert grayscale to pseudo-color via tinting
    gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR).astype(np.float32)

    # Build per-pixel color by lerping with dominant color
    color_layer = np.full_like(gray_3ch, dominant_bgr, dtype=np.float32)
    blended = cv2.addWeighted(gray_3ch, 1.0 - saturation, color_layer, saturation, 0)

    # Apply warmth shift (add to red/subtract from blue)
    warmth_shift = warmth * 0.5
    blended[:, :, 2] = np.clip(blended[:, :, 2] + warmth_shift, 0, 255)  # R
    blended[:, :, 0] = np.clip(blended[:, :, 0] - warmth_shift * 0.3, 0, 255)  # B

    result = blended.astype(np.uint8)

    # Preserve luminance from original L channel
    result_lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB).astype(np.float32)
    result_lab[:, :, 0] = lab[:, :, 0]  # restore original L
    result = cv2.cvtColor(result_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

    # Blend strength from first region
    blend_strength = float(regions[0].get("blend_strength", 0.7)) if regions else 0.7
    final = cv2.addWeighted(image, 1.0 - blend_strength, result, blend_strength, 0)

    return final


# ── Display helpers ───────────────────────────────────────────────────────────

def create_comparison(
    original: np.ndarray,
    restored: np.ndarray,
) -> np.ndarray:
    """
    Create a side-by-side comparison image with a gold divider line.

    Args:
        original: Original damaged image.
        restored: Restored/colorized image.

    Returns:
        Combined comparison image.
    """
    h = max(original.shape[0], restored.shape[0])
    # Resize both to same height
    def _resize_h(img: np.ndarray, target_h: int) -> np.ndarray:
        ratio = target_h / img.shape[0]
        w = int(img.shape[1] * ratio)
        return cv2.resize(img, (w, target_h))

    orig_r = _resize_h(original, h)
    rest_r = _resize_h(restored, h)

    # Add BEFORE/AFTER labels
    def _add_label(img: np.ndarray, label: str) -> np.ndarray:
        out = img.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = max(0.7, img.shape[1] / 600)
        thickness = max(1, int(scale * 2))
        # Shadow
        cv2.putText(out, label, (22, 42), font, scale, (0, 0, 0), thickness + 2)
        # Text
        cv2.putText(out, label, (20, 40), font, scale, (245, 230, 200), thickness)
        return out

    orig_r = _add_label(orig_r, "BEFORE")
    rest_r = _add_label(rest_r, "AFTER")

    # Gold divider
    divider = np.full((h, 4, 3), [67, 168, 212], dtype=np.uint8)  # BGR gold

    return np.hstack([orig_r, divider, rest_r])


def resize_for_display(
    image: np.ndarray,
    max_width: int = 800,
) -> np.ndarray:
    """
    Resize image preserving aspect ratio for display.

    Args:
        image:     cv2 BGR image.
        max_width: Maximum width in pixels.

    Returns:
        Resized image.
    """
    h, w = image.shape[:2]
    if w <= max_width:
        return image
    ratio = max_width / w
    new_h = int(h * ratio)
    return cv2.resize(image, (max_width, new_h), interpolation=cv2.INTER_AREA)


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """Convert PIL Image to cv2 BGR array."""
    rgb = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    """Convert cv2 BGR array to PIL Image."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)
