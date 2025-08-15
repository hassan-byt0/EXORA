# tests/integration/api_tests/test_multimodal_api.py
import pytest
from fastapi.testclient import TestClient
from api_gateway.app.main import app
from common.config import settings
import os

client = TestClient(app)

@pytest.fixture(scope="module")
def test_image():
    # Create a test image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='blue')
    img_path = "tests/test_image.png"
    img.save(img_path)
    yield img_path
    os.remove(img_path)

def test_health_check():
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_text_processing():
    response = client.post(
        "/api/v1/process",
        data={"text": "Test API input"}
    )
    assert response.status_code == 200
    assert "context_id" in response.json()

def test_image_processing(test_image):
    with open(test_image, "rb") as img_file:
        response = client.post(
            "/api/v1/process",
            files={"image": ("test_image.png", img_file, "image/png")}
        )
    assert response.status_code == 200
    assert "context_id" in response.json()

def test_invalid_input():
    response = client.post("/api/v1/process")
    assert response.status_code == 400
    assert "required" in response.json()["detail"]