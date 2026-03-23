from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from src.services.image_service import validate_image


@pytest.mark.asyncio
async def test_validate_image_success():
    file = UploadFile(
        filename="face.png",
        file=BytesIO(b"fake-image-bytes"),
        headers={"content-type": "image/png"},
    )

    metadata = await validate_image(file)

    assert metadata["filename"] == "face.png"
    assert metadata["content_type"] == "image/png"
    assert metadata["size"] > 0


@pytest.mark.asyncio
async def test_validate_image_invalid_type():
    file = UploadFile(
        filename="notes.txt",
        file=BytesIO(b"hello"),
        headers={"content-type": "text/plain"},
    )

    with pytest.raises(HTTPException) as exc_info:
        await validate_image(file)

    assert exc_info.value.status_code == 400
    assert "Invalid image type" in exc_info.value.detail