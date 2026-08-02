"""Decision engine for routing messages.

This module combines safety, critical-event, personalization, and context
signals to decide whether a message should be routed as notify, digest, or
mute. It does not generate output.csv.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class DecisionEngine:
    """Produce a routing decision from multimodal and contextual analysis."""

    def __init__(self) -> None:
        pass

    def decide(
        self,
        message_representation: Any,
        safety_result: Optional[Dict[str, Any]] = None,
        critical_event_result: Optional[Dict[str, Any]] = None,
        personalization_result: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return a routing decision object for the message."""
        context = context or {}
        safety_result = safety_result or {}
        critical_event_result = critical_event_result or {}
        personalization_result = personalization_result or {}

        safety_score = safety_result.get("safety_risk_score", 0.0)
        detected_risks = safety_result.get("detected_risks", [])
        suspicious_signals = safety_result.get("suspicious_signals", [])
        recommendation = safety_result.get("recommendation", "safe_to_process")

        critical_event = critical_event_result.get("is_critical_event", False)
        event_type = critical_event_result.get("event_type", "none")
        urgency_level = critical_event_result.get("urgency_level", "low")
        event_explanation = critical_event_result.get("explanation", "")

        relevance_score = personalization_result.get("relevance_score", 0.0)
        personalization_reason = personalization_result.get("personalization_reason", "")

        user_behavior = context.get("user_behavior", {})
        opened = user_behavior.get("opened_messages", 0)
        replied = user_behavior.get("replied_messages", 0)
        dismissed = user_behavior.get("dismissed_messages", 0)
        muted = user_behavior.get("muted_messages", 0)
        reported = user_behavior.get("reported_messages", 0)

        action = "digest"
        message_type = "unknown"
        reason = "The message appears useful but not urgent."
        confidence = 0.6
        evidence_message_ids = "none"

        text = (message_representation.combined_text or "").lower()
        suspicious_text = " ".join(suspicious_signals).lower()

        business_context = context.get("business_context", {})
        business_verified = bool(business_context.get("verified", False))
        business_history = any(
            [
                int(business_context.get("previous_orders", 0) or 0) > 0,
                int(business_context.get("previous_bookings", 0) or 0) > 0,
                int(business_context.get("previous_payments", 0) or 0) > 0,
            ]
        )
        group_context = context.get("group_context", {})
        sender_is_unknown = bool(context.get("sender_is_unknown", False))

        has_confirmed_safety_issue = (
            "scam" in detected_risks
            or "phishing" in detected_risks
            or "suspicious link" in suspicious_text
            or "risky link" in suspicious_text
            or "reported sender" in suspicious_text
            or ("reported" in suspicious_text and "sender" in suspicious_text)
            or any(term in text for term in ["otp", "password", "verification", "verify", "login code", "account blocked", "blocked", "support alert", "fake support", "wallet verification", "keep access active"])
        )

        promotional_terms = ["offer", "promo", "promotion", "discount", "sale", "marketing", "advertisement", "cash prize", "50% off", "unsubscribe"]
        forwarded_terms = ["forward", "fwd", "forwarding", "share", "sharing", "blessings", "good luck", "good vibes", "chain"]
        has_promotional_content = any(term in text for term in promotional_terms)
        has_forwarded_content = any(term in text for term in forwarded_terms)
        is_repeated_unwanted = (dismissed > 40 or muted > 25 or reported > 10) and (has_promotional_content or has_forwarded_content)

        is_emergency = any(term in text for term in ["accident", "hospital", "emergency", "urgent help", "cannot wait", "injured", "critical"]) or (critical_event and event_type.lower() == "emergency")

        critical_event_types = {"schedule_change", "location_change", "important_update", "time_change", "emergency"}
        is_time_sensitive_update = (
            critical_event and event_type.lower() in critical_event_types
        ) or any(
            term in text
            for term in ["exam", "interview", "deadline", "rescheduled", "postponed", "venue", "location", "timing", "today", "leaving early", "before eod", "eod", "submit", "join now", "reply once", "come online"]
        )

        business_terms = ["order", "delivery", "appointment", "booking", "payment", "invoice", "reminder"]
        has_verified_business_update = business_verified and business_history and any(term in text for term in business_terms)

        direct_request_terms = ["call me", "call", "reply", "can you", "need help", "join now", "come online", "please", "pls"]
        important_context_terms = ["admin", "faculty", "announcement", "notice", "school", "work", "office", "class", "assignment", "exam", "deadline", "update"]
        has_important_context = any(term in text for term in important_context_terms) or bool(group_context.get("important_group", False))
        has_direct_request = any(term in text for term in direct_request_terms)
        is_trusted_direct_request = (
            has_direct_request
            and not sender_is_unknown
            and not has_confirmed_safety_issue
            and (has_important_context or any(term in text for term in ["help", "family", "friend", "doctor", "school", "work", "office"]))
        )

        if has_confirmed_safety_issue:
            action = "mute"
            message_type = "scam"
            reason = "The message uses scam, phishing, suspicious verification, or fake-support language and should be suppressed."
            confidence = 0.95
        elif is_emergency:
            action = "notify"
            message_type = "urgent"
            reason = event_explanation or "The message describes an emergency or urgent help request."
            confidence = 0.93
        elif is_time_sensitive_update:
            action = "notify"
            if critical_event and event_type.lower() in {"schedule_change", "location_change", "important_update", "time_change", "emergency"}:
                message_type = "event"
                reason = event_explanation or "The message contains a time-sensitive update or operational change."
            else:
                message_type = "urgent"
                reason = "The message contains an urgent time-sensitive request that should interrupt the user."
            confidence = 0.88
        elif has_verified_business_update:
            action = "notify"
            message_type = "business_update"
            reason = "A verified business is sending a transactional update that matches the user's history."
            confidence = 0.9
        elif is_trusted_direct_request:
            action = "notify"
            message_type = "personal"
            reason = "The sender makes a direct request for action or response that appears important."
            confidence = 0.84
        elif is_repeated_unwanted:
            action = "mute"
            message_type = "promotion"
            reason = "The message looks like repeated unwanted promotional or forwarded content."
            confidence = 0.82
        else:
            action = "digest"
            message_type = "unknown"
            reason = "The message is useful but not urgent, risky, or clearly unwanted."
            confidence = 0.72

        return {
            "action": action,
            "message_type": message_type,
            "reason": reason,
            "confidence": round(confidence, 2),
            "evidence_message_ids": evidence_message_ids,
        }
