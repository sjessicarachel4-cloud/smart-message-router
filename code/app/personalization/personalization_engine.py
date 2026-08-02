"""Personalization engine for estimating message relevance to a specific user.

This module evaluates how relevant a message is based on the user's profile,
behavior, group relationships, and business history. It does not implement
final routing decisions.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class PersonalizationEngine:
    """Score message relevance for a recipient user."""

    def __init__(self) -> None:
        pass

    def analyze(self, message_representation: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return personalization signals for a message and user context."""
        context = context or {}
        combined_text = (
            message_representation.combined_text
            if hasattr(message_representation, "combined_text")
            else ""
        )
        lowered = combined_text.lower()

        user_profile = context.get("user_profile", {})
        user_interests = user_profile.get("interests", [])
        user_domain = user_profile.get("domain", "")
        user_type = user_profile.get("user_type", "")

        behavior = context.get("user_behavior", {})
        opened = behavior.get("opened_messages", 0)
        replied = behavior.get("replied_messages", 0)
        dismissed = behavior.get("dismissed_messages", 0)
        muted = behavior.get("muted_messages", 0)
        reported = behavior.get("reported_messages", 0)

        group_context = context.get("group_context", {})
        is_important_group = bool(group_context.get("important_group", False))
        is_admin = bool(group_context.get("is_admin", False))
        group_activity = group_context.get("group_activity", 0)
        participation = group_context.get("participation", 0)

        business_context = context.get("business_context", {})
        previous_orders = business_context.get("previous_orders", 0)
        previous_bookings = business_context.get("previous_bookings", 0)
        previous_payments = business_context.get("previous_payments", 0)
        opted_in = business_context.get("opted_in", False)
        opted_out = business_context.get("opted_out", False)

        interest_match = 0.0
        if user_interests:
            matched = sum(1 for interest in user_interests if interest.lower() in lowered)
            interest_match = min(1.0, matched / max(1, len(user_interests)))

        if user_domain and user_domain.lower() in lowered:
            interest_match = max(interest_match, 0.8)

        if user_type:
            if user_type.lower() in lowered:
                interest_match = max(interest_match, 0.7)

        relationship_score = 0.0
        if is_important_group:
            relationship_score += 0.25
        if is_admin:
            relationship_score += 0.2
        relationship_score += min(0.25, group_activity / 1000)
        relationship_score += min(0.2, participation / 100)

        behavior_score = 0.0
        behavior_score += min(0.25, opened / 100)
        behavior_score += min(0.2, replied / 100)
        behavior_score += max(0.0, 0.15 - (dismissed / 500))
        behavior_score += max(0.0, 0.1 - (muted / 500))
        behavior_score += max(0.0, 0.1 - (reported / 500))

        business_score = 0.0
        business_score += min(0.2, previous_orders / 20)
        business_score += min(0.15, previous_bookings / 10)
        business_score += min(0.15, previous_payments / 10)
        if opted_in:
            business_score += 0.15
        if opted_out:
            business_score -= 0.1

        business_score = max(0.0, min(0.5, business_score))

        relevance_score = round(min(1.0, interest_match * 0.45 + relationship_score * 0.3 + behavior_score * 0.15 + business_score * 0.1), 2)

        if relevance_score >= 0.75:
            personalization_reason = "The message strongly matches the user's interests and history."
        elif relevance_score >= 0.45:
            personalization_reason = "The message is moderately relevant based on the user's context and behavior."
        else:
            personalization_reason = "The message appears less relevant to this user's profile and history."

        return {
            "relevance_score": relevance_score,
            "user_interest_match": round(interest_match, 2),
            "relationship_score": round(relationship_score, 2),
            "behavior_score": round(behavior_score, 2),
            "personalization_reason": personalization_reason,
        }
