from __future__ import annotations

from io import BytesIO

import numpy as np
from PIL import Image
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

from src.dicom_processor import DicomProcessingError, load_dicom


def _build_dicom_bytes(pixel_array: np.ndarray, photometric: str = "MONOCHROME2", slope: float = 1.0, intercept: float = 0.0) -> bytes:
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()

    dataset = FileDataset("test.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)
    dataset.SOPClassUID = file_meta.MediaStorageSOPClassUID
    dataset.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    dataset.Rows = pixel_array.shape[-2]
    dataset.Columns = pixel_array.shape[-1]
    dataset.SamplesPerPixel = 1
    dataset.PhotometricInterpretation = photometric
    dataset.BitsAllocated = 16
    dataset.BitsStored = 16
    dataset.HighBit = 15
    dataset.PixelRepresentation = 0
    dataset.RescaleSlope = slope
    dataset.RescaleIntercept = intercept
    dataset.is_little_endian = True
    dataset.is_implicit_VR = False

    if pixel_array.ndim == 3:
        dataset.NumberOfFrames = pixel_array.shape[0]

    dataset.PixelData = pixel_array.astype(np.uint16).tobytes()

    buffer = BytesIO()
    dataset.save_as(buffer)
    return buffer.getvalue()


def test_load_dicom_returns_pillow_image() -> None:
    pixel_array = np.array([[0, 1024], [2048, 4095]], dtype=np.uint16)
    image = load_dicom(_build_dicom_bytes(pixel_array))

    assert isinstance(image, Image.Image)
    assert image.mode == "L"
    assert image.size == (2, 2)
    assert image.getextrema() == (0, 255)


def test_load_dicom_inverts_monochrome1() -> None:
    pixel_array = np.array([[0, 1000]], dtype=np.uint16)
    image = load_dicom(_build_dicom_bytes(pixel_array, photometric="MONOCHROME1"))

    assert image.getpixel((0, 0)) == 255
    assert image.getpixel((1, 0)) == 0


def test_load_dicom_uses_first_frame() -> None:
    pixel_array = np.array(
        [
            [[0, 100], [200, 255]],
            [[255, 200], [100, 0]],
        ],
        dtype=np.uint16,
    )
    image = load_dicom(_build_dicom_bytes(pixel_array))

    assert list(image.getdata()) == [0, 100, 200, 255]


def test_load_dicom_rejects_invalid_bytes() -> None:
    try:
        load_dicom(b"not-a-dicom")
    except DicomProcessingError as exc:
        assert "valid DICOM" in str(exc)
    else:
        raise AssertionError("Expected DicomProcessingError")
