from __future__ import annotations

import csv
import hashlib
from io import StringIO

LABELS = {
    "Positive": "Y",
    "Negative": "N",
    "Uncertain": "U",
    "Skip": "",
}


class LabelManager:
    def __init__(self, records: dict[str, dict] | None = None) -> None:
        self.records = records or {}

    def generate_image_id(self, filename: str, file_size: int, file_bytes: bytes) -> str:
        digest = hashlib.sha256(file_bytes).hexdigest()[:16]
        return f"{filename}:{file_size}:{digest}"

    def ensure_record(self, image_id: str, filename: str) -> dict:
        if image_id not in self.records:
            self.records[image_id] = {
                "image_id": image_id,
                "filename": filename,
                "label": "",
                "notes": "",
            }
        return self.records[image_id]

    def update_label(self, image_id: str, label: str) -> None:
        if label not in LABELS:
            raise ValueError(f"Unsupported label: {label}")
        self.records[image_id]["label"] = label

    def update_notes(self, image_id: str, notes: str) -> None:
        self.records[image_id]["notes"] = notes

    def export_csv(self) -> str:
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["image_id", "filename", "label", "label_code", "notes"],
        )
        writer.writeheader()
        for record in self.records.values():
            writer.writerow(
                {
                    "image_id": record["image_id"],
                    "filename": record["filename"],
                    "label": record["label"],
                    "label_code": LABELS.get(record["label"], ""),
                    "notes": record["notes"],
                }
            )
        return output.getvalue()
