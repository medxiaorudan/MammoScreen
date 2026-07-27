from __future__ import annotations

from src.label_manager import LabelManager


def test_generate_image_id_is_stable() -> None:
    manager = LabelManager()
    image_id_1 = manager.generate_image_id("sample.dcm", 5, b"12345")
    image_id_2 = manager.generate_image_id("sample.dcm", 5, b"12345")

    assert image_id_1 == image_id_2


def test_export_csv_contains_label_mapping_and_notes() -> None:
    manager = LabelManager()
    image_id = manager.generate_image_id("sample.png", 4, b"data")
    manager.ensure_record(image_id, "sample.png")
    manager.update_label(image_id, "Positive")
    manager.update_notes(image_id, "reviewed")

    csv_output = manager.export_csv()

    assert "sample.png" in csv_output
    assert "Positive" in csv_output
    assert ",Y," in csv_output
    assert "reviewed" in csv_output
