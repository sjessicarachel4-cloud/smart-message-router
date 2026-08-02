"""Text-only message analysis utilities.

This module performs lightweight cleaning and feature extraction for message
text. It does not implement routing logic.
"""

from __future__ import annotations

import re
from typing import Dict, List


URGENT_KEYWORDS = {
    "urgent",
    "deadline",
    "today",
    "now",
    "immediately",
    "urgent request",
    "asap",
    "alarm",
    "emergency",
    "payment",
    "otp",
    "verify",
    "confirm",
    "blocked",
    "expire",
    "last minute",
    "eod",
}

TOPIC_KEYWORDS = {
    "exam",
    "interview",
    "meeting",
    "venue",
    "payment",
    "delivery",
    "offer",
    "discount",
    "school",
    "society",
    "doctor",
    "appointment",
    "hospital",
    "reminder",
    "account",
    "login",
    "otp",
    "security",
    "support",
    "pickup",
    "schedule",
}

REQUEST_KEYWORDS = {
    "please",
    "pls",
    "call",
    "reply",
    "check",
    "confirm",
    "join",
    "come",
    "send",
    "share",
    "review",
    "verify",
    "update",
}


class TextProcessor:
    """Clean and extract lightweight features from plain text messages."""

    def __init__(self) -> None:
        self._stopwords = {
            "the",
            "and",
            "for",
            "with",
            "this",
            "that",
            "your",
            "you",
            "are",
            "is",
            "to",
            "of",
            "in",
            "on",
            "a",
            "an",
            "be",
            "it",
            "or",
            "if",
            "from",
            "will",
            "can",
            "as",
            "at",
            "by",
            "have",
            "has",
            "was",
            "were",
            "not",
            "no",
            "do",
            "did",
            "our",
            "my",
            "me",
            "we",
            "all",
            "just",
            "now",
            "please",
        }

    def clean_text(self, text: str) -> str:
        """Normalize message text for analysis."""
        if not text:
            return ""
        cleaned = text.replace("\n", " ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def extract_keywords(self, text: str) -> List[str]:
        """Extract simple keyword candidates from text."""
        cleaned = self.clean_text(text).lower()
        if not cleaned:
            return []

        tokens = re.findall(r"[a-zA-Z0-9]+", cleaned)
        tokens = [token for token in tokens if token.lower() not in self._stopwords]
        return tokens

    def analyze_text(self, text: str) -> Dict[str, object]:
        """Return a lightweight structured representation for a text message."""
        cleaned = self.clean_text(text)
        lowered = cleaned.lower()
        keywords = self.extract_keywords(cleaned)

        urgency_signals = [word for word in URGENT_KEYWORDS if word in lowered]
        topic_hits = [word for word in TOPIC_KEYWORDS if word in lowered]
        request_hits = [word for word in REQUEST_KEYWORDS if word in lowered]

        return {
            "text": cleaned,
            "cleaned_text": cleaned,
            "keywords": keywords,
            "urgency_signals": urgency_signals,
            "topics": topic_hits,
            "requests": request_hits,
            "has_request": bool(request_hits),
            "has_urgency": bool(urgency_signals),
        }
