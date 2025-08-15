# tests/unit/api_gateway/test_validation.py
import pytest
from api_gateway.app.utils.validation import validate_inputs
from fastapi import UploadFile
from io import BytesIO

def test_validate_inputs_no_input():
    with pytest.raises(Exception) as exc_info:
        validate_inputs(None, None, None)
    assert "required" in str(exc_info.value)

def test_validate_large_audio():
    large_file = UploadFile(
        file=BytesIO(b"0" * 11 * 1024 * 1024),  # 11MB
        filename="test.wav"
    )
    with pytest.raises(Exception) as exc_info:
        validate_inputs(large_file, None, None)
    assert "exceeds" in str(exc_info.value)

def test_valid_inputs():
    # Should not raise any exceptions
    text = "Valid input"
    validate_inputs(None, None, text)