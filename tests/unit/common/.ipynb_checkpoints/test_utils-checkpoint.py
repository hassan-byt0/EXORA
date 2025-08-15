# tests/unit/common/test_utils.py
import pytest
from common.utils import generate_uuid, validate_environment
from common.config import settings
from common.logger import get_logger

logger = get_logger("test_utils")

def test_generate_uuid():
    uuid = generate_uuid()
    assert len(uuid) == 36  # UUID string length
    assert isinstance(uuid, str)

def test_validate_environment(monkeypatch):
    # Test with valid environment
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    validate_environment()
    
    # Test with missing environment variable
    monkeypatch.delenv("NEO4J_URI", raising=False)
    with pytest.raises(EnvironmentError):
        validate_environment()