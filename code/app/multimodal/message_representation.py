"""Unified multimodal message representation.

This module combines text, image, and voice outputs into one object that later
stages can consume without depending on the source type.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class MessageRepresentation:
    """A unified structure for multimodal message understanding."""

    def __init__(self) -> None:
        self.text_features: Dict[str, Any] = {}
        self.image_features: Dict[str, Any] = {}
        self.voice_features: Dict[str, Any] = {}
        self.combined_text: str = ""
        self.urgency_signals: list[str] = []
        self.topics: list[str] = []
        self.requests: list[str] = []
        self.suspicious_signals: list[str] = []
        self.event_terms: list[str] = []
        self.warning_signals: list[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation for downstream modules."""
        return {
            "text_features": self.text_features,
            "image_features": self.image_features,
            "voice_features": self.voice_features,
            "combined_text": self.combined_text,
            "urgency_signals": self.urgency_signals,
            "topics": self.topics,
            "requests": self.requests,
            "suspicious_signals": self.suspicious_signals,
            "event_terms": self.event_terms,
            "warning_signals": self.warning_signals,
        }
