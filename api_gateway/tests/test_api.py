import pytest
from fastapi.testclient import TestClient
from app.main import app
from common.config import settings

client = TestClient(app)

# Test data
TEST_AUDIO_PATH = "api_gateway/tests/harvard.wav"
TEST_IMAGE_PATH = "api_gateway/tests/harward.jpg"
TEST_TEXT = "This is a test input"

def test_health_check():
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "aahb-api-gateway"

def test_no_input():
    response = client.post("/api/v1/process")
    assert response.status_code == 400
    assert "at least one input" in response.json()["detail"].lower()

def test_text_only():
    response = client.post(
        "/api/v1/process",
        data={"text": TEST_TEXT},
        headers={"Content-Type": "multipart/form-data"}
    )
    assert response.status_code == 200
    assert "context_id" in response.json()
    assert response.json()["status"] == "success"

@pytest.mark.skipif(not settings.TEST_AUDIO_ENABLED, reason="Audio tests disabled")
def test_audio_only():
    with open(TEST_AUDIO_PATH, "rb") as audio_file:
        response = client.post(
            "/api/v1/process",
            files={"audio": ("test_audio.wav", audio_file, "audio/wav")}
        )
    assert response.status_code == 200
    assert "context_id" in response.json()
    assert "audio" in response.json()["message"]

@pytest.mark.skipif(not settings.TEST_IMAGE_ENABLED, reason="Image tests disabled")
def test_image_only():
    with open(TEST_IMAGE_PATH, "rb") as image_file:
        response = client.post(
            "/api/v1/process",
            files={"image": ("test_image.jpg", image_file, "image/jpeg")}
        )
    assert response.status_code == 200
    assert "context_id" in response.json()
    assert "image" in response.json()["message"]

def test_large_text():
    large_text = "a" * 15000
    response = client.post(
        "/api/v1/process",
        data={"text": large_text},
        headers={"Content-Type": "multipart/form-data"}
    )
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"]