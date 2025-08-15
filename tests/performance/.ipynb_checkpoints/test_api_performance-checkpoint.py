# tests/performance/test_api_performance.py
import pytest
import requests
from locust import HttpUser, task, between
from common.config import settings

class APIUser(HttpUser):
    wait_time = between(1, 3)
    host = f"http://localhost:{settings.API_PORT}"
    
    @task
    def health_check(self):
        self.client.get("/health/")
    
    @task(3)
    def process_text(self):
        self.client.post(
            "/api/v1/process",
            data={"text": "Performance test input"}
        )
    
    @task(1)
    def process_image(self):
        # For actual load testing, use a real image file
        files = {"image": ("test.jpg", b"fake_image_data", "image/jpeg")}
        self.client.post("/api/v1/process", files=files)

# To run: locust -f tests/performance/test_api_performance.py

@pytest.mark.performance
def test_api_load():
    """This test is designed to be run with Locust for load testing"""
    pass