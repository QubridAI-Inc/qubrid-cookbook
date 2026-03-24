"""Attachment parsing helpers for chat input uploads."""

from __future__ import annotations

import base64
import json
from io import BytesIO
from pathlib import Path
from typing import Any, Sequence
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from config.prompts import IMAGE_CONTEXT

_IMAGE_MIME: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".csv", ".json", ".py", ".html", ".htm"}
DOC_SUFFIXES = {".docx"}
PDF_SUFFIXES = {".pdf"}


def _decode_text(data: bytes) -> str:
    """Decode bytes into text using common encodings."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _extract_pdf_text(data: bytes) -> tuple[str, str]:
    """Extract PDF text when pypdf is available."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return "", "PDF uploaded, but its text could not be read in the current setup."

    reader = PdfReader(BytesIO(data))
    page_texts = []
    for page in reader.pages:
        page_texts.append(page.extract_text() or "")

    text = "\n\n".join(section.strip() for section in page_texts if section.strip())
    if not text:
        return "", f"PDF uploaded ({len(reader.pages)} pages), but no readable text was extracted."
    return text, f"PDF document ({len(reader.pages)} pages, text extracted)"


def _extract_docx_text(data: bytes) -> tuple[str, str]:
    """Extract text from a DOCX archive using the standard library."""
    try:
        with ZipFile(BytesIO(data)) as archive:
            document_xml = archive.read("word/document.xml")
    except (BadZipFile, KeyError):
        return "", "DOCX uploaded, but its text could not be extracted."

    root = ET.fromstring(document_xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        runs = [
            node.text.strip()
            for node in paragraph.findall(".//w:t", namespace)
            if node.text and node.text.strip()
        ]
        if runs:
            paragraphs.append("".join(runs))

    text = "\n\n".join(paragraphs).strip()
    if not text:
        return "", "DOCX uploaded, but it did not contain extractable text."
    return text, f"DOCX document ({len(paragraphs)} paragraphs, text extracted)"


def _extract_text_file(data: bytes) -> tuple[str, str]:
    """Extract plain text from text-like files."""
    text = _decode_text(data).strip()
    if not text:
        return "", "Text document uploaded, but it was empty."
    return text, "Text document (text extracted)"


def _compress_image(data: bytes, mime: str, max_side: int = 1024) -> tuple[bytes, str]:
    """Resize and compress an image to keep the base64 payload small.

    Falls back to the original bytes if Pillow is not installed.
    """
    try:
        from PIL import Image
    except ImportError:
        return data, mime

    try:
        img = Image.open(BytesIO(data))
        img.thumbnail((max_side, max_side), Image.LANCZOS)
        buf = BytesIO()
        fmt = "JPEG" if mime == "image/jpeg" else "PNG"
        out_mime = "image/jpeg" if fmt == "JPEG" else "image/png"
        img.convert("RGB").save(buf, format=fmt, quality=85, optimize=True)
        return buf.getvalue(), out_mime
    except Exception:
        return data, mime


def _summarize_file(name: str, detail: str) -> str:
    """Return a markdown-safe attachment summary line."""
    return f"`{name}` - {detail}"


def _build_api_attachment_block(name: str, extracted_text: str, note: str) -> str:
    """Build the model-facing attachment block."""
    if extracted_text:
        return f"[Begin extracted content from {name}]\n{extracted_text}\n[End extracted content from {name}]"
    return f"[Attachment: {name}]\n{note}"


def prepare_submission(user_text: str, uploaded_files: Sequence[Any]) -> dict[str, str]:
    """Prepare visible chat content and model-facing content for a submission."""
    clean_text = user_text.strip()
    files = list(uploaded_files)
    if not clean_text and not files:
        return {"display_content": "", "api_content": "", "title_seed": ""}

    visible_lines: list[str] = []
    api_lines: list[str] = []
    attachment_summaries: list[str] = []
    attachment_blocks: list[str] = []
    # Each entry: {"url": "data:<mime>;base64,..."}
    image_parts: list[dict[str, Any]] = []

    for uploaded_file in files:
        name = str(getattr(uploaded_file, "name", "uploaded-file"))
        suffix = Path(name).suffix.lower()
        data = uploaded_file.getvalue()

        if suffix in PDF_SUFFIXES:
            extracted_text, detail = _extract_pdf_text(data)
            attachment_summaries.append(_summarize_file(name, detail))
            attachment_blocks.append(_build_api_attachment_block(name, extracted_text, detail))
        elif suffix in DOC_SUFFIXES:
            extracted_text, detail = _extract_docx_text(data)
            attachment_summaries.append(_summarize_file(name, detail))
            attachment_blocks.append(_build_api_attachment_block(name, extracted_text, detail))
        elif suffix in TEXT_SUFFIXES:
            extracted_text, detail = _extract_text_file(data)
            attachment_summaries.append(_summarize_file(name, detail))
            attachment_blocks.append(_build_api_attachment_block(name, extracted_text, detail))
        elif suffix in IMAGE_SUFFIXES:
            mime = _IMAGE_MIME.get(suffix, "image/jpeg")
            processed_data, mime = _compress_image(data, mime)
            b64 = base64.b64encode(processed_data).decode("utf-8")
            detail = "Image attachment"
            attachment_summaries.append(_summarize_file(name, detail))
            image_parts.append({"url": f"data:{mime};base64,{b64}"})
            # Fallback text block so text-only models still know an image was shared
            attachment_blocks.append(IMAGE_CONTEXT.format(name=name))
        else:
            detail = "Uploaded file"
            attachment_summaries.append(_summarize_file(name, detail))
            attachment_blocks.append(
                _build_api_attachment_block(
                    name,
                    "",
                    "A file was attached, but this file type is not text-extracted in the current build.",
                )
            )

    if clean_text:
        visible_lines.append(clean_text)
        api_lines.append(clean_text)
    elif attachment_summaries:
        visible_lines.append("Uploaded files for analysis.")
        api_lines.append("Please analyze the attached files.")

    if attachment_summaries:
        attachments_markdown = "**Attachments**\n" + "\n".join(
            f"- {summary}" for summary in attachment_summaries
        )
        visible_lines.append(attachments_markdown)
        api_lines.append("Attached files:\n" + "\n".join(f"- {summary}" for summary in attachment_summaries))

    if attachment_blocks:
        api_lines.append("\n\n".join(attachment_blocks))

    text_api_content = "\n\n".join(api_lines).strip()

    # Build multimodal content list when images are present
    if image_parts:
        content_list: list[dict[str, Any]] = []
        if text_api_content:
            content_list.append({"type": "text", "text": text_api_content})
        for img in image_parts:
            content_list.append({"type": "image_url", "image_url": img})
        api_content = json.dumps(content_list)
    else:
        api_content = text_api_content

    title_seed = clean_text or (str(getattr(files[0], "name", "Uploaded file")) if files else "")
    return {
        "display_content": "\n\n".join(visible_lines).strip(),
        "api_content": api_content,
        "title_seed": title_seed[:60],
    }
