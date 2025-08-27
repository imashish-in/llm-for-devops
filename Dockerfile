FROM python:3.10-slim

# Install system dependencies required for transformers and torch
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create model cache directory
RUN mkdir -p /app/model_cache

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install flask transformers torch accelerate PyJWT prometheus-client psutil

# Copy app source code
COPY app.py .

# Set environment variables for model caching
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV HF_HOME=/app/model_cache
ENV TORCH_HOME=/app/model_cache

# Create a volume for persistent model cache
VOLUME ["/app/model_cache"]

EXPOSE 8080

CMD ["python", "app.py"]
