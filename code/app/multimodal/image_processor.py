"""Image-based message analysis utilities.

This module uses image metadata and image files to extract visible text and
high-level signals such as offers, warnings, and suspicious content. It does
not implement routing decisions.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional


class ImageProcessor:
    """Analyze images using metadata and optional OCR-style text extraction."""

    def __init__(self, dataset_dir: Optional[Path] = None) -> None:
        self.dataset_dir = dataset_dir or Path(__file__).resolve().parents[3] / "dataset"
        self.images_dir = self.dataset_dir / "media" / "images"

    def _image_path(self, image_id: Optional[str]) -> Optional[Path]:
        """Resolve the image file path from the image ID."""
        if not image_id:
            return None
        candidate = self.images_dir / f"{image_id}.jpg"
        if candidate.exists():
            return candidate
        return None

    def extract_text_from_image(self, image_id: Optional[str]) -> str:
        """Return OCR-like text when an image file exists.

        This is a lightweight placeholder that uses file metadata and filename
        hints rather than a real OCR engine. It still provides a structured
        output shape for later integration with OCR libraries.
        """
        if not image_id:
            return ""

        image_path = self._image_path(image_id)
        if image_path is None:
            return ""

        # Placeholder OCR path: use filename and file metadata as hints.
        stem = image_path.stem.lower()
        return f"image:{stem}"

    def analyze_image(self, image_id: Optional[str], message_text: str = "") -> Dict[str, object]:
        """Return a structured representation of image-based content."""
        extracted_text = self.extract_text_from_image(image_id)
        combined_text = f"{message_text} {extracted_text}".strip()
        lowered = combined_text.lower()

        offers = [token for token in ["offer", "discount", "sale", "cashback", "promo"] if token in lowered]
        warnings = [token for token in ["warning", "alert", "security", "verify", "otp", "blocked"] if token in lowered]
        suspicious = [token for token in ["suspicious", "scam", "phish", "fake", "verify", "otp"] if token in lowered]

        event_terms = [token for token in ["exam", "interview", "meeting", "venue", "deadline", "payment", "reminder"] if token in lowered]

        return {
            "image_id": image_id,
            "image_path": str(self._image_path(image_id)) if self._image_path(image_id) else None,
            "extracted_text": extracted_text,
            "combined_text": combined_text,
            "offers": offers,
            "warnings": warnings,
            "suspicious_content": suspicious,
            "event_terms": event_terms,
            "has_visual_offer": bool(offers),
            "has_warning": bool(warnings),
            "has_suspicious_content": bool(suspicious),
            "has_event_terms": bool(event_terms),
        }
