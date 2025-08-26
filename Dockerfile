FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install flask transformers torch gpt4all

# Copy app source code
COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]
