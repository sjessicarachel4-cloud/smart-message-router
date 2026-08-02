"""Data loading helpers for the message routing challenge.

This module reads the provided CSV files from the repository dataset folder and
exposes simple functions for accessing the data without implementing routing
logic.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[3]
DATASET_DIR = REPO_ROOT / "dataset"


def get_dataset_dir() -> Path:
    """Return the absolute path to the dataset directory."""
    return DATASET_DIR


def _read_csv(filename: str) -> List[Dict[str, str]]:
    """Read a CSV file from the dataset directory."""
    file_path = DATASET_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_messages() -> List[Dict[str, str]]:
    """Load incoming messages from messages.csv."""
    return _read_csv("messages.csv")


def load_users() -> List[Dict[str, str]]:
    """Load user profile data from users.csv."""
    return _read_csv("users.csv")


def load_groups() -> List[Dict[str, str]]:
    """Load group metadata from groups.csv."""
    return _read_csv("groups.csv")


def load_group_members() -> List[Dict[str, str]]:
    """Load user-group relationship data from group_members.csv."""
    return _read_csv("group_members.csv")


def load_business_accounts() -> List[Dict[str, str]]:
    """Load business account metadata from business_accounts.csv."""
    return _read_csv("business_accounts.csv")


def load_message_history() -> List[Dict[str, str]]:
    """Load historical messages from message_history.csv."""
    return _read_csv("message_history.csv")


def load_message_events() -> List[Dict[str, str]]:
    """Load historical interaction events from message_events.csv."""
    return _read_csv("message_events.csv")


def load_images() -> List[Dict[str, str]]:
    """Load image metadata from images.csv."""
    return _read_csv("images.csv")


def load_voice_notes() -> List[Dict[str, str]]:
    """Load voice-note metadata from voice_notes.csv."""
    return _read_csv("voice_notes.csv")


def load_media_metadata() -> Dict[str, List[Dict[str, str]]]:
    """Load all media metadata files as a single dictionary."""
    return {
        "images": load_images(),
        "voice_notes": load_voice_notes(),
    }


def load_all_data() -> Dict[str, object]:
    """Load all available datasets used by the routing pipeline."""
    return {
        "messages": load_messages(),
        "users": load_users(),
        "groups": load_groups(),
        "group_members": load_group_members(),
        "business_accounts": load_business_accounts(),
        "message_history": load_message_history(),
        "message_events": load_message_events(),
        "media_metadata": load_media_metadata(),
    }
