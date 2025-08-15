# api_gateway/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# First install build dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    gcc \
    g++ \
    git \
    libssl-dev \
    tesseract-ocr \
    ffmpeg \
    libsm6 \
    libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]