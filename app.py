from __future__ import annotations

from io import BytesIO

import streamlit as st

from src.image_loader import ImageLoadError, load_uploaded_image
from src.label_manager import LABELS, LabelManager


def initialize_state() -> None:
    state = st.session_state
    state.setdefault("files", [])
    state.setdefault("current_index", 0)
    state.setdefault("labels", {})
    state.setdefault("errors", {})
    state.setdefault("uploader_key", 0)
    state.setdefault("confirm_reset", False)


def reset_session() -> None:
    st.session_state.files = []
    st.session_state.current_index = 0
    st.session_state.labels = {}
    st.session_state.errors = {}
    st.session_state.uploader_key += 1
    st.session_state.confirm_reset = False


def handle_uploads(uploaded_files) -> None:
    manager = LabelManager(st.session_state.labels)
    files = []
    errors = {}

    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.getvalue()

        try:
            image = load_uploaded_image(uploaded_file)
        except ImageLoadError as exc:
            errors[uploaded_file.name] = str(exc)
            continue

        image_id = manager.generate_image_id(
            filename=uploaded_file.name,
            file_size=len(file_bytes),
            file_bytes=file_bytes,
        )
        record = manager.ensure_record(image_id=image_id, filename=uploaded_file.name)
        files.append(
            {
                "image_id": image_id,
                "filename": uploaded_file.name,
                "image": image,
                "bytes": file_bytes,
                "record": record,
            }
        )

    st.session_state.files = files
    st.session_state.errors = errors
    st.session_state.current_index = 0
    st.session_state.labels = manager.records


def set_current_label(label_name: str) -> None:
    files = st.session_state.files
    if not files:
        return
    current = files[st.session_state.current_index]
    manager = LabelManager(st.session_state.labels)
    manager.update_label(current["image_id"], label_name)
    st.session_state.labels = manager.records


def set_current_notes(notes: str) -> None:
    files = st.session_state.files
    if not files:
        return
    current = files[st.session_state.current_index]
    manager = LabelManager(st.session_state.labels)
    manager.update_notes(current["image_id"], notes)
    st.session_state.labels = manager.records


def move_previous() -> None:
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1


def move_next() -> None:
    if st.session_state.current_index < len(st.session_state.files) - 1:
        st.session_state.current_index += 1


def main() -> None:
    st.set_page_config(page_title="MammoScreen", layout="wide")
    initialize_state()

    st.title("MammoScreen")
    st.caption("Browser-based mammography image review and labeling.")

    uploaded_files = st.file_uploader(
        "Upload mammography images",
        type=["dcm", "jpg", "jpeg", "png", "bmp"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if uploaded_files:
        current_names = [item["filename"] for item in st.session_state.files]
        incoming_names = [item.name for item in uploaded_files]
        if current_names != incoming_names:
            handle_uploads(uploaded_files)

    if st.session_state.errors:
        for filename, error in st.session_state.errors.items():
            st.error(f"{filename}: {error}")

    files = st.session_state.files
    if not files:
        st.info("Upload one or more JPG, JPEG, PNG, BMP, or DICOM files to begin.")
        return

    current = files[st.session_state.current_index]
    record = st.session_state.labels[current["image_id"]]
    labelled_count = sum(1 for item in st.session_state.labels.values() if item["label"])

    st.subheader(f"Image {st.session_state.current_index + 1} of {len(files)}")
    st.write(current["filename"])

    left, right = st.columns([3, 2])

    with left:
        preview = current["image"].copy()
        preview.thumbnail((1200, 1200))
        st.image(preview, use_container_width=True)

    with right:
        current_label = record["label"] or "Unlabeled"
        st.metric("Current label", current_label)
        st.progress(labelled_count / len(files), text=f"Progress: {labelled_count} of {len(files)} labelled")

        st.write("Assign label")
        label_columns = st.columns(len(LABELS))
        for column, label_name in zip(label_columns, LABELS.keys()):
            with column:
                st.button(
                    label_name,
                    key=f"label_{current['image_id']}_{label_name}",
                    on_click=set_current_label,
                    args=(label_name,),
                    use_container_width=True,
                )

        notes = st.text_area("Notes", value=record["notes"], placeholder="Optional notes for this image")
        if notes != record["notes"]:
            set_current_notes(notes)

        nav1, nav2 = st.columns(2)
        with nav1:
            st.button("Previous", on_click=move_previous, disabled=st.session_state.current_index == 0, use_container_width=True)
        with nav2:
            st.button(
                "Next",
                on_click=move_next,
                disabled=st.session_state.current_index >= len(files) - 1,
                use_container_width=True,
            )

        csv_bytes = LabelManager(st.session_state.labels).export_csv().encode("utf-8")
        st.download_button(
            "Download labels as CSV",
            data=BytesIO(csv_bytes),
            file_name="mammoscreen_labels.csv",
            mime="text/csv",
            use_container_width=True,
        )

        if st.button("Reset session", use_container_width=True):
            st.session_state.confirm_reset = True

        if st.session_state.confirm_reset:
            st.warning("Confirm reset to clear uploaded files and labels for this session.")
        if st.session_state.confirm_reset and st.button("Confirm reset", use_container_width=True):
            reset_session()
            st.rerun()

    if labelled_count == len(files):
        st.success("All uploaded images have labels. You can still review and edit them before export.")


if __name__ == "__main__":
    main()
