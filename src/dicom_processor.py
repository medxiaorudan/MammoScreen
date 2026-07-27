from __future__ import annotations

from io import BytesIO

import numpy as np
from PIL import Image
from pydicom import dcmread
from pydicom.errors import InvalidDicomError


class DicomProcessingError(ValueError):
    """Raised when DICOM content cannot be converted into a display image."""


def _normalize_to_uint8(image_array: np.ndarray) -> np.ndarray:
    pixel_min = image_array.min()
    pixel_max = image_array.max()
    pixel_range = pixel_max - pixel_min

    if pixel_range == 0:
        return np.zeros_like(image_array, dtype=np.uint8)

    normalized = 255 * (image_array - pixel_min) / pixel_range
    return normalized.astype(np.uint8)


def load_dicom(file_bytes: bytes) -> Image.Image:
    """Read DICOM bytes and return a displayable Pillow image."""
    try:
        dataset = dcmread(BytesIO(file_bytes))
    except InvalidDicomError as exc:
        raise DicomProcessingError("The uploaded file is not a valid DICOM file.") from exc
    except Exception as exc:
        raise DicomProcessingError(f"Unable to read the DICOM file: {exc}") from exc

    try:
        pixel_array = dataset.pixel_array
    except Exception as exc:
        raise DicomProcessingError(f"The DICOM file does not contain readable pixel data: {exc}") from exc

    if pixel_array.ndim == 4:
        pixel_array = pixel_array[0]
    elif pixel_array.ndim == 3 and getattr(dataset, "SamplesPerPixel", 1) == 1:
        pixel_array = pixel_array[0]

    image_array = pixel_array.astype(np.float32)

    slope = float(getattr(dataset, "RescaleSlope", 1.0))
    intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
    image_array = image_array * slope + intercept

    photometric = getattr(dataset, "PhotometricInterpretation", "MONOCHROME2").upper()

    if image_array.ndim == 2:
        normalized = _normalize_to_uint8(image_array)
        if photometric == "MONOCHROME1":
            normalized = 255 - normalized
        elif photometric != "MONOCHROME2":
            raise DicomProcessingError(
                f"Unsupported grayscale photometric interpretation: {photometric}"
            )
        return Image.fromarray(normalized, mode="L")

    if image_array.ndim == 3 and image_array.shape[-1] in (3, 4):
        normalized = _normalize_to_uint8(image_array)
        if image_array.shape[-1] == 3:
            return Image.fromarray(normalized, mode="RGB")
        return Image.fromarray(normalized[:, :, :3], mode="RGB")

    raise DicomProcessingError(
        f"Unsupported DICOM pixel data shape: {tuple(pixel_array.shape)}"
    )
