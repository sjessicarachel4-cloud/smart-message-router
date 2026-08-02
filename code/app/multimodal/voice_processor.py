"""Voice-note transcription and analysis utilities.

This module provides a lightweight placeholder pipeline for converting voice
notes into text and extracting key information. It does not implement routing
logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


class VoiceProcessor:
    """Transcribe and analyze voice-note content."""

    def __init__(self, dataset_dir: Optional[Path] = None) -> None:
        self.dataset_dir = dataset_dir or Path(__file__).resolve().parents[3] / "dataset"
        self.audio_dir = self.dataset_dir / "media" / "audio"

    def _audio_path(self, voice_id: Optional[str]) -> Optional[Path]:
        """Resolve the audio file path from the voice-note ID."""
        if not voice_id:
            return None
        candidate = self.audio_dir / f"{voice_id}.mp3"
        if candidate.exists():
            return candidate
        return None

    def transcribe_voice(self, voice_id: Optional[str]) -> str:
        """Return a placeholder transcription for a voice-note file.

        This is intentionally lightweight; a real implementation can later swap
        in a speech-to-text backend.
        """
        if not voice_id:
            return ""

        audio_path = self._audio_path(voice_id)
        if audio_path is None:
            return ""

        return f"voice_transcript:{audio_path.stem}"

    def analyze_voice(self, voice_id: Optional[str], message_text: str = "") -> Dict[str, object]:
        """Return a structured representation of voice-note content."""
        transcript = self.transcribe_voice(voice_id)
        combined_text = f"{message_text} {transcript}".strip()
        lowered = combined_text.lower()

        urgency_terms = [term for term in ["urgent", "now", "today", "deadline", "emergency"] if term in lowered]
        event_terms = [term for term in ["exam", "interview", "meeting", "venue", "payment", "reminder"] if term in lowered]
        warning_terms = [term for term in ["warning", "alert", "verify", "otp", "blocked"] if term in lowered]

        return {
            "voice_id": voice_id,
            "voice_path": str(self._audio_path(voice_id)) if self._audio_path(voice_id) else None,
            "transcript": transcript,
            "combined_text": combined_text,
            "urgency_terms": urgency_terms,
            "event_terms": event_terms,
            "warning_terms": warning_terms,
            "has_urgency": bool(urgency_terms),
            "has_event_terms": bool(event_terms),
            "has_warning": bool(warning_terms),
        }
