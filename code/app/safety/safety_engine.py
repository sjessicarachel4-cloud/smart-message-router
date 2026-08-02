"""Safety analysis engine for multimodal messages.

This module evaluates a unified message representation for phishing, scam,
suspicious links, and sender-related risk. It does not implement routing
or final notification decisions.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


class SafetyEngine:
    """Analyze a message representation for safety risk."""

    def __init__(self) -> None:
        self.phishing_terms = {
            "verify",
            "verification",
            "otp",
            "password",
            "login",
            "suspended",
            "blocked",
            "account",
            "security",
            "confirm",
            "urgent",
        }
        self.scam_terms = {
            "lottery",
            "prize",
            "money",
            "payment",
            "transfer",
            "cash",
            "reward",
            "winner",
            "claim",
            "gift",
            "impersonat",
            "fake",
        }
        self.risky_link_patterns = [
            r"\.in$",
            r"bit\.ly",
            r"tinyurl",
            r"t\.co",
            r"goo\.gl",
            r"shorturl",
            r"click",
            r"login",
            r"verify",
        ]

    def _has_any(self, text: str, terms: set[str]) -> bool:
        lowered = text.lower()
        return any(term in lowered for term in terms)

    def _extract_links(self, text: str) -> List[str]:
        return re.findall(r"https?://[^\s]+|www\.[^\s]+", text)

    def analyze(self, message_representation: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze a unified message representation for safety risk."""
        context = context or {}
        text = message_representation.combined_text if hasattr(message_representation, "combined_text") else ""
        text_features = message_representation.text_features if hasattr(message_representation, "text_features") else {}
        image_features = message_representation.image_features if hasattr(message_representation, "image_features") else {}
        voice_features = message_representation.voice_features if hasattr(message_representation, "voice_features") else {}

        detected_risks: List[str] = []
        suspicious_signals: List[str] = []

        if self._has_any(text, self.phishing_terms):
            detected_risks.append("phishing")
            suspicious_signals.append("fake verification or account request")

        if self._has_any(text, self.scam_terms):
            detected_risks.append("scam")
            suspicious_signals.append("fraud-like payment or reward language")

        if image_features.get("has_warning") or image_features.get("has_suspicious_content"):
            detected_risks.append("visual_suspicion")
            suspicious_signals.append("image contains warning or suspicious cues")

        if voice_features.get("has_warning"):
            detected_risks.append("voice_warning")
            suspicious_signals.append("voice content includes warning cues")

        links = self._extract_links(text)
        if links:
            for link in links:
                if any(re.search(pattern, link, re.IGNORECASE) for pattern in self.risky_link_patterns):
                    suspicious_signals.append(f"risky link: {link}")
                    break

        sender_context = context or {}
        sender_type = sender_context.get("conversation_type")
        sender_is_unknown = sender_context.get("sender_is_unknown", False)
        business_verified = sender_context.get("business_verified", True)
        business_reported = sender_context.get("business_reported", False)

        if sender_is_unknown:
            detected_risks.append("unknown_sender")
            suspicious_signals.append("sender is unknown")

        if sender_type == "business" and not business_verified:
            detected_risks.append("unverified_business")
            suspicious_signals.append("business sender is unverified")

        if business_reported:
            detected_risks.append("reported_business")
            suspicious_signals.append("business account has prior reports")

        risk_score = 0.0
        if "phishing" in detected_risks:
            risk_score += 0.35
        if "scam" in detected_risks:
            risk_score += 0.30
        if "visual_suspicion" in detected_risks:
            risk_score += 0.15
        if "voice_warning" in detected_risks:
            risk_score += 0.10
        if "unknown_sender" in detected_risks:
            risk_score += 0.15
        if "unverified_business" in detected_risks:
            risk_score += 0.15
        if "reported_business" in detected_risks:
            risk_score += 0.20
        if suspicious_signals:
            risk_score += min(0.15, 0.03 * len(suspicious_signals))

        risk_score = min(1.0, round(risk_score, 2))

        if risk_score >= 0.7:
            recommendation = "high_risk_review"
        elif risk_score >= 0.35:
            recommendation = "moderate_risk_review"
        else:
            recommendation = "safe_to_process"

        return {
            "safety_risk_score": risk_score,
            "detected_risks": detected_risks,
            "suspicious_signals": suspicious_signals,
            "recommendation": recommendation,
        }
