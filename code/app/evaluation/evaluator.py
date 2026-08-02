"""Evaluation helpers for the routing pipeline.

This module validates the generated predictions before writing them out.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Sequence


REQUIRED_COLUMNS = [
    "message_id",
    "action",
    "message_type",
    "reason",
    "confidence",
    "evidence_message_ids",
]

ALLOWED_ACTIONS = {"notify", "digest", "mute"}


class PipelineEvaluator:
    """Validate prediction rows for the final submission output."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def validate(self, rows: Sequence[Dict[str, str]]) -> None:
        """Validate the prediction rows before writing them out."""
        if not rows:
            raise ValueError("No prediction rows were generated.")

        for row in rows:
            for column in REQUIRED_COLUMNS:
                if column not in row:
                    raise ValueError(f"Missing required column in prediction row: {column}")
                if row[column] is None or row[column] == "":
                    raise ValueError(f"Missing required value for column: {column}")

            if row["action"] not in ALLOWED_ACTIONS:
                raise ValueError(f"Invalid action value: {row['action']}")

            try:
                confidence = float(row["confidence"])
            except ValueError as exc:
                raise ValueError(f"Invalid confidence value: {row['confidence']}") from exc

            if not 0 <= confidence <= 1:
                raise ValueError(f"Confidence out of range: {confidence}")

    def write_output(self, rows: Sequence[Dict[str, str]]) -> Path:
        """Write predictions to output.csv in the required format."""
        self.validate(rows)
        with self.output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            for row in rows:
                writer.writerow({column: row.get(column, "") for column in REQUIRED_COLUMNS})
        return self.output_path
