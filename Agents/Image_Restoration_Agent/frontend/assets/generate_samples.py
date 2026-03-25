"""
ReVive AI — Sample image generator.
Creates 3 synthetic aged/damaged photographs for demo purposes.
Run automatically on first startup; results saved to assets/samples/.
"""

from __future__ import annotations

import os
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _add_aging(img: np.ndarray, intensity: float = 0.5) -> np.ndarray:
    """Add yellowing, fading, and grain to simulate aged photo."""
    # Convert to float
    f = img.astype(np.float32) / 255.0

    # Fade (reduce contrast, shift toward mid-grey)
    f = f * (1 - intensity * 0.3) + intensity * 0.15

    # Yellowing: boost red/green, reduce blue
    f[:, :, 2] = np.clip(f[:, :, 2] * (1 + intensity * 0.4), 0, 1)  # R
    f[:, :, 1] = np.clip(f[:, :, 1] * (1 + intensity * 0.2), 0, 1)  # G
    f[:, :, 0] = np.clip(f[:, :, 0] * (1 - intensity * 0.3), 0, 1)  # B

    # Grain
    noise = np.random.normal(0, intensity * 0.06, f.shape).astype(np.float32)
    f = np.clip(f + noise, 0, 1)

    return (f * 255).astype(np.uint8)


def _add_scratches(img: np.ndarray, n: int = 8) -> np.ndarray:
    """Add random white/dark scratch lines."""
    out = img.copy()
    h, w = img.shape[:2]
    for _ in range(n):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        x2 = random.randint(0, w)
        y2 = random.randint(0, h)
        color = random.choice([(255, 255, 255), (30, 20, 10)])
        thickness = random.randint(1, 2)
        cv2.line(out, (x1, y1), (x2, y2), color, thickness)
    return out


def _add_spots(img: np.ndarray, n: int = 15) -> np.ndarray:
    """Add dark stain spots."""
    out = img.copy()
    h, w = img.shape[:2]
    overlay = out.copy()
    for _ in range(n):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        r = random.randint(3, 20)
        color = (random.randint(20, 60), random.randint(15, 45), random.randint(10, 35))
        cv2.circle(overlay, (cx, cy), r, color, -1)
    return cv2.addWeighted(out, 0.75, overlay, 0.25, 0)


def _add_vignette(img: np.ndarray) -> np.ndarray:
    """Add dark vignette border."""
    h, w = img.shape[:2]
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    vignette = 1 - np.clip(dist * 0.7, 0, 0.6)
    out = img.astype(np.float32)
    for c in range(3):
        out[:, :, c] *= vignette
    return out.astype(np.uint8)


def _make_bw_portrait(w: int = 640, h: int = 480) -> np.ndarray:
    """Create a synthetic 1940s-style B&W family portrait."""
    pil = Image.new("RGB", (w, h), (180, 170, 155))
    draw = ImageDraw.Draw(pil)

    # Background gradient (studio backdrop)
    for y in range(h):
        shade = int(140 + (y / h) * 40)
        draw.line([(0, y), (w, y)], fill=(shade, shade - 5, shade - 10))

    # Figures (silhouettes)
    # Adult left
    draw.ellipse([120, 80, 200, 170], fill=(80, 70, 65))  # head
    draw.rectangle([100, 170, 220, 380], fill=(60, 55, 50))  # body

    # Adult right
    draw.ellipse([420, 80, 510, 170], fill=(80, 70, 65))
    draw.rectangle([400, 170, 530, 380], fill=(50, 45, 42))

    # Child center
    draw.ellipse([265, 160, 335, 230], fill=(90, 80, 75))
    draw.rectangle([255, 230, 345, 360], fill=(70, 62, 58))

    # Floor/ground
    draw.rectangle([0, 380, w, h], fill=(100, 90, 82))

    img = np.array(pil)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # grayscale-in-BGR

    # Apply aging
    img = _add_aging(img, 0.6)
    img = _add_scratches(img, 12)
    img = _add_spots(img, 20)
    img = _add_vignette(img)
    img = cv2.GaussianBlur(img, (3, 3), 0.8)
    return img


def _make_sepia_street(w: int = 640, h: int = 480) -> np.ndarray:
    """Create a synthetic 1920s-style sepia street scene."""
    pil = Image.new("RGB", (w, h), (200, 185, 150))
    draw = ImageDraw.Draw(pil)

    # Sky
    for y in range(h // 3):
        v = int(210 + y * 0.3)
        draw.line([(0, y), (w, y)], fill=(v, v - 10, v - 20))

    # Buildings
    building_data = [(0, 80, 160, h), (150, 50, 320, h), (310, 90, 480, h), (470, 60, 640, h)]
    shades = [(120, 105, 88), (100, 88, 72), (115, 100, 82), (95, 82, 68)]
    for (x1, y1, x2, y2), shade in zip(building_data, shades):
        draw.rectangle([x1, y1, x2, y2], fill=shade)
        # Windows
        for wy in range(y1 + 20, y2 - 20, 35):
            for wx in range(x1 + 15, x2 - 15, 30):
                if random.random() > 0.3:
                    draw.rectangle([wx, wy, wx + 14, wy + 18], fill=(60, 50, 35))

    # Street
    draw.rectangle([0, h - 120, w, h], fill=(130, 118, 95))
    # Cobblestone hint
    for _ in range(40):
        sx = random.randint(0, w)
        sy = random.randint(h - 115, h - 5)
        draw.rectangle([sx, sy, sx + 12, sy + 6], fill=(118, 106, 84))

    # Silhouette people
    for px in [180, 300, 430, 520]:
        py = h - 160
        draw.ellipse([px - 12, py, px + 12, py + 25], fill=(50, 42, 35))
        draw.rectangle([px - 10, py + 24, px + 10, py + 70], fill=(40, 34, 28))

    img = np.array(pil)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = _add_aging(img, 0.7)
    img = _add_scratches(img, 15)
    img = _add_spots(img, 25)
    img = _add_vignette(img)
    img = cv2.GaussianBlur(img, (3, 3), 1.0)
    return img


def _make_faded_wedding(w: int = 640, h: int = 480) -> np.ndarray:
    """Create a synthetic 1950s-style faded wedding photograph."""
    pil = Image.new("RGB", (w, h), (210, 200, 185))
    draw = ImageDraw.Draw(pil)

    # Studio backdrop
    for y in range(h):
        v = int(195 + (y / h) * 25)
        draw.line([(0, y), (w, y)], fill=(v, v - 8, v - 15))

    # Arch decoration
    draw.arc([160, -60, 480, 200], 0, 180, fill=(160, 148, 128), width=8)

    # Bride (white dress)
    draw.ellipse([240, 80, 310, 160], fill=(190, 182, 168))  # head
    draw.polygon([(230, 160), (320, 160), (360, 420), (190, 420)], fill=(210, 205, 195))  # dress

    # Groom (dark suit)
    draw.ellipse([330, 80, 400, 160], fill=(180, 170, 158))
    draw.rectangle([320, 160, 410, 400], fill=(70, 64, 58))

    # Flowers
    for fx, fy in [(180, 300), (430, 310), (250, 400)]:
        draw.ellipse([fx - 15, fy - 15, fx + 15, fy + 15], fill=(190, 175, 155))

    # Floor
    draw.rectangle([0, h - 80, w, h], fill=(155, 142, 120))

    img = np.array(pil)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = _add_aging(img, 0.55)
    img = _add_scratches(img, 10)
    img = _add_spots(img, 18)
    img = _add_vignette(img)
    img = cv2.GaussianBlur(img, (3, 3), 0.7)
    return img


def generate_all(output_dir: str = "assets/samples") -> None:
    """Generate all 3 sample images and save to output_dir."""
    os.makedirs(output_dir, exist_ok=True)

    samples = [
        ("sample_1.jpg", _make_bw_portrait),
        ("sample_2.jpg", _make_sepia_street),
        ("sample_3.jpg", _make_faded_wedding),
    ]

    for filename, generator in samples:
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            img = generator()
            cv2.imwrite(path, img)

    print(f"[ReVive AI] Generated {len(samples)} sample images in {output_dir}/")


if __name__ == "__main__":
    generate_all()
