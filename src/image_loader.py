from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from src.dicom_processor import DicomProcessingError, load_dicom

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".dcm"}
MAX_IMAGE_PIXELS = 40_000_000


class ImageLoadError(ValueError):
    """Raised when an uploaded file cannot be loaded as an image."""


def _read_uploaded_file(uploaded_file) -> tuple[str, bytes]:
    filename = getattr(uploaded_file, "name", "uploaded_file")
    if hasattr(uploaded_file, "getvalue"):
        file_bytes = uploaded_file.getvalue()
    elif isinstance(uploaded_file, bytes):
        file_bytes = uploaded_file
    else:
        file_bytes = uploaded_file.read()
    return filename, file_bytes


def load_uploaded_image(uploaded_file) -> Image.Image:
    """Load a browser-uploaded standard image or DICOM file."""
    filename, file_bytes = _read_uploaded_file(uploaded_file)
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ImageLoadError(f"Unsupported file type: {extension or 'missing extension'}")

    if extension == ".dcm":
        try:
            return load_dicom(file_bytes)
        except DicomProcessingError as exc:
            raise ImageLoadError(str(exc)) from exc

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            image.load()
            image = ImageOps.exif_transpose(image)
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ImageLoadError(
                    f"Image is too large to process safely ({image.width}x{image.height})."
                )
            if image.mode not in {"L", "RGB"}:
                image = image.convert("RGB")
            return image.copy()
    except UnidentifiedImageError as exc:
        raise ImageLoadError("The uploaded file is not a readable image.") from exc
    except OSError as exc:
        raise ImageLoadError(f"Unable to decode the uploaded image: {exc}") from exc
