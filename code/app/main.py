"""Entry point for the routing pipeline.

This module orchestrates the data-loading, analysis, decision-making, and
output-generation workflow for the message notification router.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, List

from code.app.data.loader import load_all_data
from code.app.decision.decision_engine import DecisionEngine
from code.app.events.critical_event_detector import CriticalEventDetector
from code.app.evaluation.evaluator import PipelineEvaluator
from code.app.multimodal.image_processor import ImageProcessor
from code.app.multimodal.message_representation import MessageRepresentation
from code.app.multimodal.text_processor import TextProcessor
from code.app.multimodal.voice_processor import VoiceProcessor
from code.app.personalization.personalization_engine import PersonalizationEngine
from code.app.safety.safety_engine import SafetyEngine


REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "dataset"
OUTPUT_PATH = DATASET_DIR / "output.csv"


def build_message_representation(message: Dict[str, str], data: Dict[str, object]) -> MessageRepresentation:
    """Create a unified multimodal representation for a single message."""
    text_processor = TextProcessor()
    image_processor = ImageProcessor(DATASET_DIR)
    voice_processor = VoiceProcessor(DATASET_DIR)

    message_representation = MessageRepresentation()

    message_text = message.get("message_text", "")
    media_type = message.get("media_type", "")
    media_id = message.get("media_id", "")

    message_representation.text_features = text_processor.analyze_text(message_text)

    if media_type == "image":
        message_representation.image_features = image_processor.analyze_image(media_id, message_text)
    elif media_type == "voice":
        message_representation.voice_features = voice_processor.analyze_voice(media_id, message_text)

    combined_parts = [
        message_representation.text_features.get("text", ""),
        message_representation.image_features.get("combined_text", ""),
        message_representation.voice_features.get("combined_text", ""),
    ]
    message_representation.combined_text = " ".join(part for part in combined_parts if part).strip()

    urgency_signals = list(
        dict.fromkeys(
            message_representation.text_features.get("urgency_signals", [])
            + message_representation.voice_features.get("urgency_terms", [])
        )
    )
    topics = list(
        dict.fromkeys(
            message_representation.text_features.get("topics", [])
            + message_representation.image_features.get("event_terms", [])
            + message_representation.voice_features.get("event_terms", [])
        )
    )
    requests = message_representation.text_features.get("requests", [])
    suspicious_signals = message_representation.image_features.get("suspicious_content", [])
    event_terms = message_representation.voice_features.get("event_terms", [])
    warning_signals = message_representation.voice_features.get("warning_terms", [])

    message_representation.urgency_signals = urgency_signals
    message_representation.topics = topics
    message_representation.requests = requests
    message_representation.suspicious_signals = suspicious_signals
    message_representation.event_terms = event_terms
    message_representation.warning_signals = warning_signals

    return message_representation


def build_context(message: Dict[str, str], data: Dict[str, object]) -> Dict[str, object]:
    """Build contextual information for a message from the loaded datasets."""
    users_by_id = {row.get("user_id"): row for row in data.get("users", [])}
    groups_by_id = {row.get("group_id"): row for row in data.get("groups", [])}
    business_accounts = data.get("business_accounts", [])

    user_id = message.get("user_id")
    user_profile = users_by_id.get(user_id, {})

    group_id = message.get("group_id")
    group_context = {}
    if group_id:
        group_row = groups_by_id.get(group_id, {})
        group_context = {
            "important_group": group_row.get("group_type") in {"family", "school_group", "society", "coworker"},
            "is_admin": False,
            "group_activity": int(group_row.get("messages_30d", 0) or 0),
            "participation": 0,
        }

    business_id = message.get("business_id")
    business_context = {}
    if business_id:
        business_row = next((row for row in business_accounts if row.get("business_id") == business_id), {})
        business_context = {
            "previous_orders": 0,
            "previous_bookings": 0,
            "previous_payments": 0,
            "opted_in": False,
            "opted_out": False,
        }
        if business_row:
            business_context["verified"] = business_row.get("verified") == "1"
            business_context["reported"] = int(business_row.get("user_reports_30d", 0) or 0) > 0

    history_context = {
        "user_behavior": {
            "opened_messages": int(user_profile.get("messages_opened_30d", 0) or 0),
            "replied_messages": int(user_profile.get("messages_replied_30d", 0) or 0),
            "dismissed_messages": int(user_profile.get("notifications_dismissed_30d", 0) or 0),
            "muted_messages": 0,
            "reported_messages": int(user_profile.get("messages_reported_30d", 0) or 0),
        },
        "user_profile": {
            "interests": [],
            "domain": "",
            "user_type": "",
        },
        "group_context": group_context,
        "business_context": business_context,
        "sender_is_unknown": bool(message.get("sender_user_id") is None and message.get("business_id") is None),
        "conversation_type": message.get("conversation_type", ""),
    }

    return history_context


def retrieve_evidence(message: Dict[str, str], data: Dict[str, object]) -> str:
    """Retrieve up to three historical message IDs relevant to the current message."""
    history_rows = data.get("message_history", [])
    if not history_rows:
        return "none"

    user_id = message.get("user_id", "")
    group_id = message.get("group_id", "")
    business_id = message.get("business_id", "")
    sender_user_id = message.get("sender_user_id", "")
    message_text = (message.get("message_text") or "").lower()

    def text_score(row_text: str) -> int:
        if not row_text:
            return 0
        row_text = row_text.lower()
        shared_terms = set(re.findall(r"[a-z0-9]+", message_text)) & set(re.findall(r"[a-z0-9]+", row_text))
        return len(shared_terms)

    candidates = []
    for row in history_rows:
        row_user = row.get("user_id", "")
        row_group = row.get("group_id", "")
        row_business = row.get("business_id", "")
        row_sender = row.get("sender_user_id", "")
        row_text = row.get("message_text", "")

        same_user = row_user == user_id
        same_group = bool(group_id) and row_group == group_id
        same_business = bool(business_id) and row_business == business_id
        same_sender = bool(sender_user_id) and row_sender == sender_user_id

        if not (same_user or same_group or same_business or same_sender):
            continue

        score = 0
        if same_user:
            score += 3
        if same_group:
            score += 2
        if same_business:
            score += 2
        if same_sender:
            score += 2
        score += text_score(row_text)

        if score > 0:
            candidates.append((score, row))

    if not candidates:
        return "none"

    candidates.sort(key=lambda item: (-item[0], item[1].get("message_id", "")))
    selected_ids = [row.get("message_id") for _, row in candidates[:3] if row.get("message_id")]
    return ";".join(selected_ids) if selected_ids else "none"


def run_pipeline() -> List[Dict[str, str]]:
    """Run the full routing pipeline and return output rows."""
    data = load_all_data()
    messages = data.get("messages", [])

    text_processor = TextProcessor()
    image_processor = ImageProcessor(DATASET_DIR)
    voice_processor = VoiceProcessor(DATASET_DIR)
    safety_engine = SafetyEngine()
    critical_event_detector = CriticalEventDetector()
    personalization_engine = PersonalizationEngine()
    decision_engine = DecisionEngine()

    rows: List[Dict[str, str]] = []
    for message in messages:
        representation = build_message_representation(message, data)
        context = build_context(message, data)

        safety_result = safety_engine.analyze(
            representation,
            {
                "conversation_type": message.get("conversation_type", ""),
                "sender_is_unknown": context.get("sender_is_unknown", False),
                "business_verified": context.get("business_context", {}).get("verified", True),
                "business_reported": context.get("business_context", {}).get("reported", False),
            },
        )
        critical_event_result = critical_event_detector.analyze(representation)
        personalization_result = personalization_engine.analyze(representation, context)
        decision_result = decision_engine.decide(
            representation,
            safety_result=safety_result,
            critical_event_result=critical_event_result,
            personalization_result=personalization_result,
            context=context,
        )

        evidence_message_ids = retrieve_evidence(message, data)
        row = {
            "message_id": message.get("message_id", ""),
            "action": decision_result["action"],
            "message_type": decision_result["message_type"],
            "reason": decision_result["reason"],
            "confidence": str(decision_result["confidence"]),
            "evidence_message_ids": evidence_message_ids,
        }
        rows.append(row)

    evaluator = PipelineEvaluator(OUTPUT_PATH)
    evaluator.write_output(rows)
    return rows


def main() -> None:
    """Execute the pipeline and write output.csv."""
    run_pipeline()


if __name__ == "__main__":
    main()
