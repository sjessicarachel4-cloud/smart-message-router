"""Critical event detection for multimodal messages.

This module analyzes a unified message representation for urgent, high-priority
situations such as time changes, location changes, deadlines, and emergencies.
It does not implement final routing decisions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class CriticalEventDetector:
    """Detect important events that may require immediate attention."""

    def __init__(self) -> None:
        self.time_change_terms = {
            "rescheduled",
            "changed",
            "time changed",
            "schedule",
            "moved",
            "shifted",
            "updated",
        }
        self.location_change_terms = {
            "venue",
            "room",
            "location",
            "place",
            "hall",
            "building",
        }
        self.important_update_terms = {
            "postponed",
            "interview",
            "deadline",
            "payment deadline",
            "payment",
            "reminder",
            "important",
        }
        self.emergency_terms = {
            "accident",
            "hospital",
            "urgent help",
            "emergency",
            "help",
            "injured",
            "critical",
        }

    def analyze(self, message_representation: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze a unified message representation for critical events."""
        context = context or {}
        combined_text = (
            message_representation.combined_text
            if hasattr(message_representation, "combined_text")
            else ""
        )
        lowered = combined_text.lower()

        detected_terms: List[str] = []

        if any(term in lowered for term in ["meeting", "exam", "event"]):
            if any(term in lowered for term in ["rescheduled", "changed", "moved", "shifted", "updated"]):
                detected_terms.extend([term for term in ["meeting", "exam", "event"] if term in lowered])
                detected_terms.append("time_change")

        if any(term in lowered for term in self.location_change_terms):
            if any(term in lowered for term in ["changed", "updated", "moved", "shifted"]):
                detected_terms.append("location_change")

        if any(term in lowered for term in self.important_update_terms):
            if any(term in lowered for term in ["interview", "deadline", "payment", "postponed", "reminder"]):
                detected_terms.append("important_update")

        if any(term in lowered for term in self.emergency_terms):
            detected_terms.append("emergency")

        is_critical_event = bool(detected_terms)

        if "emergency" in detected_terms:
            event_type = "emergency"
            urgency_level = "high"
            explanation = "The message describes an emergency or urgent help request."
        elif "location_change" in detected_terms and "time_change" in detected_terms:
            event_type = "schedule_change"
            urgency_level = "high"
            explanation = "The message reports a schedule or location change that may affect attendance."
        elif "location_change" in detected_terms:
            event_type = "location_change"
            urgency_level = "medium"
            explanation = "The message reports a location change that may require attention."
        elif "important_update" in detected_terms:
            event_type = "important_update"
            urgency_level = "high"
            explanation = "The message contains an important update or deadline-related information."
        elif "time_change" in detected_terms:
            event_type = "time_change"
            urgency_level = "medium"
            explanation = "The message indicates a time change for an event or meeting."
        else:
            event_type = "none"
            urgency_level = "low"
            explanation = "No critical event pattern detected."

        # Critical events should remain high priority even when the sender is unknown.
        if is_critical_event and urgency_level == "low":
            urgency_level = "medium"

        return {
            "is_critical_event": is_critical_event,
            "event_type": event_type,
            "urgency_level": urgency_level,
            "detected_terms": detected_terms,
            "explanation": explanation,
        }
