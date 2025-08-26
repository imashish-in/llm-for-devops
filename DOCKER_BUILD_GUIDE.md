# Docker Multi-Platform Build Guide

This comprehensive guide covers building the LLM Flask application for all major operating systems and architectures.

## 🖥️ **Supported Platforms**

### **Architectures**
- **ARM64** (Apple Silicon M1/M2, ARM servers, Raspberry Pi)
- **AMD64** (Intel/AMD x86_64, most cloud providers)

### **Operating Systems**
- **macOS** (Apple Silicon and Intel)
- **Windows** (WSL2, Docker Desktop)
- **Linux** (Ubuntu, CentOS, RHEL, etc.)
- **Cloud Platforms** (AWS, GCP, Azure, DigitalOcean)

## 🚀 **Quick Build Commands**

### **Universal Build (Recommended)**
```bash
# Build for your current platform
docker build -t ashishsoldy/llm-flask:latest .

# Build for specific platform
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .
```

### **Multi-Platform Build**
```bash
# Enable buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t ashishsoldy/llm-flask:latest .

# Build and push to registry
docker buildx build --platform linux/amd64,linux/arm64 -t ashishsoldy/llm-flask:latest --push .
```

## 🍎 **macOS Build Instructions**

### **Apple Silicon (M1/M2) Macs**

#### **Prerequisites**
```bash
# Install Docker Desktop for Mac
# Ensure "Use the new Virtualization framework" is enabled
# Enable "Use Rosetta for x86/amd64 emulation on Apple Silicon"
```

#### **Build Commands**
```bash
# Build for ARM64 (native)
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .

# Build for AMD64 (emulated)
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t ashishsoldy/llm-flask:latest .
```

#### **Troubleshooting**
```bash
# Check Docker version
docker version

# Check available platforms
docker buildx ls

# Enable buildx
docker buildx create --use

# If you get platform errors, install QEMU
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

### **Intel Macs**

#### **Build Commands**
```bash
# Build for AMD64 (native)
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# Build for ARM64 (emulated)
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .
```

## 🪟 **Windows Build Instructions**

### **Windows with WSL2 (Recommended)**

#### **Prerequisites**
```bash
# Enable WSL2
wsl --install

# Install Docker Desktop for Windows
# Enable WSL2 integration in Docker Desktop settings
```

#### **Build Commands**
```bash
# Open WSL2 terminal
wsl

# Navigate to project directory
cd /mnt/c/path/to/your/project

# Build for AMD64 (recommended for Windows)
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# Build for ARM64 (if needed)
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .
```

#### **Troubleshooting**
```bash
# Check WSL2 status
wsl --list --verbose

# Update WSL2
wsl --update

# Restart WSL2
wsl --shutdown
wsl
```

### **Windows with Docker Desktop (Legacy)**

#### **Build Commands**
```bash
# Build for AMD64
docker build -t ashishsoldy/llm-flask:latest .

# Build with specific platform
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .
```

## 🐧 **Linux Build Instructions**

### **Ubuntu/Debian**

#### **Prerequisites**
```bash
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

#### **Build Commands**
```bash
# Build for AMD64 (native)
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# Build for ARM64 (if needed)
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t ashishsoldy/llm-flask:latest .
```

### **CentOS/RHEL**

#### **Prerequisites**
```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

#### **Build Commands**
```bash
# Same as Ubuntu/Debian
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .
```

### **ARM64 Linux (Raspberry Pi, ARM Servers)**

#### **Build Commands**
```bash
# Build for ARM64 (native)
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .

# Build for AMD64 (emulated, slow)
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .
```

## ☁️ **Cloud Platform Builds**

### **AWS EC2**

#### **Amazon Linux 2**
```bash
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Build
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .
```

#### **Ubuntu on EC2**
```bash
# Install Docker
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Build
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .
```

### **Google Cloud Platform**

#### **Compute Engine**
```bash
# Install Docker
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Build
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .
```

### **Azure**

#### **Ubuntu VM**
```bash
# Install Docker
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker azureuser

# Build
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .
```

## 🏷️ **Version Tagging and Registry**

### **Local Tagging**
```bash
# Tag with version
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:v1.0.0 .

# Tag with multiple versions
docker build --platform linux/amd64 \
  -t ashishsoldy/llm-flask:latest \
  -t ashishsoldy/llm-flask:v1.0.0 \
  -t ashishsoldy/llm-flask:stable .
```

### **Push to Registry**
```bash
# Login to Docker Hub
docker login

# Push to Docker Hub
docker push ashishsoldy/llm-flask:latest
docker push ashishsoldy/llm-flask:v1.0.0

# Push multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ashishsoldy/llm-flask:latest \
  --push .
```

### **Other Registries**
```bash
# AWS ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
docker tag ashishsoldy/llm-flask:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/llm-flask:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/llm-flask:latest

# Google Container Registry
gcloud auth configure-docker
docker tag ashishsoldy/llm-flask:latest gcr.io/PROJECT-ID/llm-flask:latest
docker push gcr.io/PROJECT-ID/llm-flask:latest

# Azure Container Registry
az acr login --name myregistry
docker tag ashishsoldy/llm-flask:latest myregistry.azurecr.io/llm-flask:latest
docker push myregistry.azurecr.io/llm-flask:latest
```

## 🔧 **Advanced Build Options**

### **Build Arguments**
```bash
# Build with custom arguments
docker build \
  --platform linux/amd64 \
  --build-arg PYTHON_VERSION=3.10 \
  --build-arg MODEL_NAME=microsoft/DialoGPT-medium \
  --build-arg CACHE_SIZE=1000 \
  -t ashishsoldy/llm-flask:latest .
```

### **Multi-Stage Builds**
```dockerfile
# Example multi-stage Dockerfile
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app.py .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

### **Build with Cache**
```bash
# Build with cache
docker build --platform linux/amd64 \
  --cache-from ashishsoldy/llm-flask:latest \
  -t ashishsoldy/llm-flask:latest .

# Build without cache
docker build --platform linux/amd64 \
  --no-cache \
  -t ashishsoldy/llm-flask:latest .
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Platform Not Supported**
```bash
# Error: "no matching manifest for linux/arm64"
# Solution: Use buildx for multi-platform builds
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t ashishsoldy/llm-flask:latest .
```

#### **Build Fails on ARM64**
```bash
# Error: "exec format error"
# Solution: Ensure you're building for the correct platform
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .
```

#### **Memory Issues During Build**
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or use buildx with higher memory limit
docker buildx build --platform linux/amd64 \
  --memory=4g \
  -t ashishsoldy/llm-flask:latest .
```

#### **Network Issues**
```bash
# Use buildx with network options
docker buildx build --platform linux/amd64 \
  --network=host \
  -t ashishsoldy/llm-flask:latest .
```

### **Performance Optimization**

#### **Build Time Optimization**
```bash
# Use build cache
docker build --platform linux/amd64 \
  --cache-from ashishsoldy/llm-flask:latest \
  -t ashishsoldy/llm-flask:latest .

# Parallel builds
docker buildx build --platform linux/amd64,linux/arm64 \
  --parallel \
  -t ashishsoldy/llm-flask:latest .
```

#### **Image Size Optimization**
```bash
# Use multi-stage builds
# Remove unnecessary files
# Use .dockerignore to exclude files
```

## 📊 **Build Verification**

### **Test Built Images**
```bash
# Test the built image
docker run --rm -p 8080:8080 ashishsoldy/llm-flask:latest

# Test health endpoint
curl http://localhost:8080/health

# Test generate endpoint
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
```

### **Check Image Details**
```bash
# Inspect image
docker inspect ashishsoldy/llm-flask:latest

# Check image size
docker images ashishsoldy/llm-flask

# Check platform
docker image inspect ashishsoldy/llm-flask:latest --format='{{.Architecture}}'
```

## 📚 **Additional Resources**

- [Docker Multi-Platform Build Documentation](https://docs.docker.com/build/building/multi-platform/)
- [Docker Buildx Documentation](https://docs.docker.com/build/buildx/)
- [QEMU for Cross-Platform Emulation](https://www.qemu.org/)
- [Docker Hub Registry](https://hub.docker.com/)

This guide covers all major platforms and should help you build the LLM Flask application successfully on any system!
