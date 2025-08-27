# LLM Flask Application

A Flask-based web application for LLM (Large Language Model) inference using Microsoft's DialoGPT-medium model, designed to run in Kubernetes with Docker containerization. Features advanced caching and optimization for production-ready performance.

## 🚀 Features

- **Flask Web Server**: RESTful API endpoints for LLM interactions
- **DialoGPT-medium Model**: Powered by Microsoft's DialoGPT-medium model via Hugging Face Transformers
- **Advanced Caching**: Response caching with TTL and LRU eviction
- **Model Optimization**: Half-precision, memory optimization, and performance tuning
- **Authentication**: API key-based authentication for secure access
- **Rate Limiting**: Configurable rate limiting per user (5 requests/minute)
- **Docker Containerization**: Easy deployment and scaling
- **Kubernetes Ready**: Complete deployment configuration with persistent storage
- **Health Monitoring**: Built-in health checks and readiness probes
- **Error Handling**: Comprehensive error handling and logging
- **Multi-Platform Support**: Build for any OS and architecture

## 📋 Prerequisites

- Docker Desktop or Docker Engine
- Kubernetes cluster (Docker Desktop Kubernetes, Minikube, or cloud provider)
- kubectl CLI tool
- Python 3.10+ (for local development)

## 🏗️ Project Structure

```
LLM for DevOps/
├── app.py                          # Main Flask application with DialoGPT-medium
├── Dockerfile                      # Docker container configuration
├── requirements.txt                # Python dependencies (transformers, torch, accelerate)
├── llm-flask-deployment.yaml      # Kubernetes deployment configuration
├── CACHING_AND_OPTIMIZATION.md    # Detailed caching and optimization guide
└── README.md                       # This file
```

## 🐳 Docker Build Instructions

### **Multi-Platform Build Support**

The application supports building for multiple operating systems and architectures:

#### **1. Apple Silicon (M1/M2) Macs**
```bash
# Build for ARM64 (Apple Silicon)
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .

# Run locally
docker run -p 8080:8080 ashishsoldy/llm-flask:latest
```

#### **2. Intel/AMD64 Systems (Windows, Linux, Intel Macs)**
```bash
# Build for AMD64 (Intel/AMD)
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# Run locally
docker run -p 8080:8080 ashishsoldy/llm-flask:latest
```

#### **3. Multi-Platform Build (Recommended)**
```bash
# Build for both ARM64 and AMD64 simultaneously
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t ashishsoldy/llm-flask:latest .

# Push multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 -t ashishsoldy/llm-flask:latest --push .
```

#### **4. Windows-Specific Build**
```bash
# For Windows with WSL2
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# For Windows with Docker Desktop
docker build -t ashishsoldy/llm-flask:latest .
```

#### **5. Linux-Specific Build**
```bash
# For Linux systems
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# For ARM64 Linux (Raspberry Pi, etc.)
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .
```

### **Build Options and Tags**

#### **Version Tagging**
```bash
# Build with version tag
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:v1.0.0 .

# Build with multiple tags
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest -t ashishsoldy/llm-flask:v1.0.0 .
```

#### **Build Arguments (Advanced)**
```bash
# Build with custom arguments
docker build \
  --platform linux/arm64 \
  --build-arg PYTHON_VERSION=3.10 \
  --build-arg MODEL_NAME=microsoft/DialoGPT-medium \
  -t ashishsoldy/llm-flask:latest .
```

## 🚀 Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application locally
python app.py
```

The application will be available at `http://localhost:8080`

### 2. Docker Deployment

#### **Step-by-Step Docker Build**

```bash
# 1. Clone the repository
git clone https://github.com/imashish-in/llm-for-devops.git
cd llm-for-devops

# 2. Build the Docker image (choose your platform)
# For Apple Silicon:
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .

# For Intel/AMD64:
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# 3. Run the container locally
docker run -p 8080:8080 ashishsoldy/llm-flask:latest

# 4. Push to Docker Hub (optional)
docker push ashishsoldy/llm-flask:latest
```

### 3. Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f llm-flask-deployment.yaml

# Check deployment status
kubectl get pods -l app=llm-flask

# Port forward to access the service
kubectl port-forward service/llm-flask-service 8080:8080

# Test the deployed application
curl http://localhost:8080/health
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is artificial intelligence?"}'
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "DialoGPT-medium model is loaded and ready",
  "cache_info": {
    "cache_size": 45,
    "cache_hits": 123,
    "cache_misses": 67,
    "hit_rate": 0.647
  },
  "device": "cpu"
}
```

### Generate Response
```http
POST /generate
Content-Type: application/json
X-API-Key: sk-1234567890abcdef

{
  "prompt": "Your input text here",
  "temperature": 0.8,
  "max_tokens": 256
}
```

**Response:**
```json
{
  "response": "Generated text from DialoGPT-medium model",
  "cached": false,
  "generation_time": 2.34
}
```

**Authentication Required**: ✅ Yes (API Key)

### Rate Limit Status
```http
GET /rate-limit/status
X-API-Key: sk-1234567890abcdef
```

**Response:**
```json
{
  "user_id": "user1",
  "current_requests": 2,
  "remaining_requests": 3,
  "limit": 5,
  "window_seconds": 60,
  "reset_time": 1640995260
}
```

**Authentication Required**: ✅ Yes (API Key)

### Cache Management
```http
GET /cache/stats
POST /cache/clear
GET /model/info
```

**Authentication Required**: ❌ No (Public endpoints)

### Example LLM Interaction
```bash
# Test the LLM endpoint with a sample prompt
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-1234567890abcdef" \
  -d '{
    "prompt": "Explain what is machine learning in simple terms"
  }'
```

**Expected Response:**
```json
{
  "response": "Machine learning is the process of learning a new thing. You will learn what you have learned.",
  "cached": false,
  "generation_time": 1.23
}
```

## 🔧 Configuration

### Model Configuration

The application uses:
- **Model**: `microsoft/DialoGPT-medium` from Hugging Face
- **Library**: Transformers with PyTorch backend
- **Optimizations**: 
  - Half precision (float16) for memory efficiency
  - Model caching with persistent storage
  - Response caching with TTL
- **Generation Parameters**: 
  - Temperature: 0.8 (configurable)
  - Max new tokens: 256 (configurable)
  - Top-p: 0.9 (nucleus sampling)
  - Top-k: 50
  - Repetition penalty: 1.1

### Kubernetes Configuration

The deployment includes:
- **Resource Management**: 4Gi memory request, 8Gi limit
- **Persistent Storage**: 10Gi PVC for model cache
- **Health Checks**: Liveness and readiness probes
- **Service Discovery**: ClusterIP service for internal communication
- **Scaling**: Horizontal pod autoscaling ready

## 🐛 Troubleshooting

### Common Issues

#### 1. Pod CrashLoopBackOff
```bash
# Check pod logs
kubectl logs -l app=llm-flask

# Check pod status
kubectl describe pod -l app=llm-flask
```

#### 2. Memory Issues
```bash
# Check node memory
kubectl describe nodes

# Reduce memory requests if needed
kubectl edit deployment llm-flask
```

#### 3. Model Loading Issues
```bash
# Check if model is downloading
kubectl logs -f deployment/llm-flask

# Verify internet connectivity in pod
kubectl exec -it <pod-name> -- curl -I https://huggingface.co
```

#### 4. Platform-Specific Issues

**Apple Silicon (M1/M2) Macs:**
```bash
# Ensure you're building for ARM64
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .

# Check if Docker Desktop supports ARM64
docker version
```

**Intel/AMD64 Systems:**
```bash
# Build for AMD64
docker build --platform linux/amd64 -t ashishsoldy/llm-flask:latest .

# For Windows, ensure WSL2 is enabled
wsl --list --verbose
```

### Platform-Specific Notes

#### Apple Silicon (M1/M2) Macs
- Build images with `--platform linux/arm64` flag
- Use ARM64-compatible base images
- Ensure Kubernetes cluster supports ARM64
- Docker Desktop should be configured for ARM64

#### Intel/AMD64 Systems
- Build images with `--platform linux/amd64` flag
- Use AMD64-compatible base images
- Compatible with most cloud providers

#### Windows Systems
- Use WSL2 for best performance
- Docker Desktop should be configured for WSL2
- Build with `--platform linux/amd64` for compatibility

## 🔄 Development Workflow

### 1. Make Changes
Edit `app.py` or other source files

### 2. Test Locally
```bash
# Start the application
python app.py

# Test health endpoint
curl http://localhost:8080/health

# Test LLM endpoint
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
```

### 3. Build and Deploy
```bash
# Build new image (choose your platform)
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .

# Push to registry
docker push ashishsoldy/llm-flask:latest

# Update Kubernetes deployment
kubectl rollout restart deployment/llm-flask
```

### 4. Verify Deployment
```bash
kubectl get pods -l app=llm-flask
kubectl logs -f deployment/llm-flask
```

## 🔮 Future Enhancements

### Planned Features
- [ ] Model caching and optimization ✅ (Implemented)
- [ ] Authentication and rate limiting ✅ (Implemented)
- [ ] Metrics and monitoring
- [ ] Horizontal pod autoscaling
- [ ] Ingress configuration for external access
- [ ] Support for additional models
- [ ] Batch processing capabilities
- [ ] Redis integration for distributed caching

### Model Options
The application can be easily modified to use other models:
- **DialoGPT-large**: Larger conversational model
- **GPT-2**: OpenAI's GPT-2 model
- **BLOOM**: Multilingual model
- **Custom fine-tuned models**: Domain-specific models

## 📝 Notes

### Current Capabilities
- **Real LLM Responses**: Uses actual DialoGPT-medium model for text generation
- **Advanced Caching**: Response caching with TTL and LRU eviction
- **Model Optimization**: Half-precision and memory optimization
- **Docker Compatible**: Fully containerized and Kubernetes-ready
- **Production Ready**: Stable deployment with health checks
- **Memory Efficient**: Medium-sized model suitable for containerized environments
- **Open Access**: No authentication required for model access
- **Multi-Platform**: Supports all major operating systems and architectures

### Performance Considerations
- **Model Size**: DialoGPT-medium requires ~1.5GB RAM
- **Response Time**: First response may take 3-5 seconds for model loading
- **Cached Responses**: < 100ms for repeated queries
- **Concurrent Requests**: Limited by available memory and CPU
- **Scaling**: Horizontal scaling supported via Kubernetes

### Security Considerations
- Add authentication for production use
- Implement rate limiting
- Use secrets for sensitive configuration
- Enable TLS/SSL for external access
- Regular security updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs: `kubectl logs -l app=llm-flask`
3. Open an issue in the repository
4. Check the deployment status: `kubectl describe deployment llm-flask`

## 🔐 Authentication and Rate Limiting

### API Key Authentication

The application requires API key authentication for secure access. Include your API key in the `X-API-Key` header:

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-1234567890abcdef" \
  -d '{"prompt": "Hello, how are you?"}'
```

### Rate Limiting

- **Limit**: 5 requests per minute per user
- **Window**: 60 seconds
- **Status**: Check your rate limit status with `/rate-limit/status`

### Default API Keys

For testing purposes, the following API keys are available:

- **User 1**: `sk-1234567890abcdef`
- **User 2**: `sk-fedcba0987654321`

**⚠️ Security Note**: Change these keys in production using environment variables.

## 🎯 Quick Test Commands

```bash
# Test health endpoint (no authentication required)
curl http://localhost:8080/health

# Test text generation with authentication
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-1234567890abcdef" \
  -d '{"prompt": "Write a short poem about technology"}'

# Test rate limit status
curl -H "X-API-Key: sk-1234567890abcdef" \
  http://localhost:8080/rate-limit/status

# Test cache statistics (no authentication required)
curl http://localhost:8080/cache/stats

# Test model information (no authentication required)
curl http://localhost:8080/model/info
```

## 📚 Additional Documentation

- **[Caching and Optimization Guide](CACHING_AND_OPTIMIZATION.md)**: Detailed guide on caching features and performance optimization
- **[Authentication and Rate Limiting Guide](AUTHENTICATION_AND_RATE_LIMITING.md)**: Comprehensive guide on security features and API access control
- **[Docker Multi-Platform Build Guide](DOCKER_BUILD_GUIDE.md)**: Comprehensive guide for building on different platforms
