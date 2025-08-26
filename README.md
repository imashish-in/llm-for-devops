# LLM Flask Application

A Flask-based web application for LLM (Large Language Model) inference using Microsoft's DialoGPT-medium model, designed to run in Kubernetes with Docker containerization.

## 🚀 Features

- **Flask Web Server**: RESTful API endpoints for LLM interactions
- **DialoGPT-medium Model**: Powered by Microsoft's DialoGPT-medium model via Hugging Face Transformers
- **Docker Containerization**: Easy deployment and scaling
- **Kubernetes Ready**: Complete deployment configuration
- **Health Monitoring**: Built-in health checks and readiness probes
- **Error Handling**: Comprehensive error handling and logging

## 📋 Prerequisites

- Docker Desktop
- Kubernetes cluster (Docker Desktop Kubernetes, Minikube, or cloud provider)
- kubectl CLI tool
- Python 3.10+ (for local development)

## 🏗️ Project Structure

```
LLM for DevOps/
├── app.py                          # Main Flask application with DialoGPT-medium
├── Dockerfile                      # Docker container configuration
├── requirements.txt                # Python dependencies (transformers, torch)
├── llm-flask-deployment.yaml      # Kubernetes deployment configuration
└── README.md                       # This file
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

```bash
# Build the Docker image
docker build --platform linux/arm64 -t ashishsoldy/llm-flask:latest .

# Run the container locally
docker run -p 8080:8080 ashishsoldy/llm-flask:latest

# Push to Docker Hub (optional)
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
  "message": "DialoGPT-medium model is loaded and ready"
}
```

### Generate Response
```http
POST /generate
Content-Type: application/json

{
  "prompt": "Your input text here"
}
```

**Response:**
```json
{
  "response": "Generated text from DialoGPT-medium model"
}
```

### Example LLM Interaction
```bash
# Test the LLM endpoint with a sample prompt
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain what is machine learning in simple terms"
  }'
```

**Expected Response:**
```json
{
  "response": "Machine learning is the process of learning a new thing. You will learn what you have learned."
}
```

## 🔧 Configuration

### Model Configuration

The application uses:
- **Model**: `microsoft/DialoGPT-medium` from Hugging Face
- **Library**: Transformers with PyTorch backend
- **Generation Parameters**: 
  - Temperature: 0.8
  - Max new tokens: 256
  - Top-p: 0.9 (nucleus sampling)
  - Top-k: 50
  - Repetition penalty: 1.1

### Kubernetes Configuration

The deployment includes:
- **Resource Management**: 4Gi memory request, 8Gi limit
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

### Platform-Specific Notes

#### Apple Silicon (M1/M2) Macs
- Build images with `--platform linux/arm64` flag
- Use ARM64-compatible base images
- Ensure Kubernetes cluster supports ARM64

#### Intel/AMD64 Systems
- Build images with `--platform linux/amd64` flag
- Use AMD64-compatible base images

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
# Build new image
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
- [ ] Model caching and optimization
- [ ] Authentication and rate limiting
- [ ] Metrics and monitoring
- [ ] Horizontal pod autoscaling
- [ ] Ingress configuration for external access
- [ ] Support for additional models
- [ ] Batch processing capabilities

### Model Options
The application can be easily modified to use other models:
- **DialoGPT-large**: Larger conversational model
- **GPT-2**: OpenAI's GPT-2 model
- **BLOOM**: Multilingual model
- **Custom fine-tuned models**: Domain-specific models

## 📝 Notes

### Current Capabilities
- **Real LLM Responses**: Uses actual DialoGPT-medium model for text generation
- **Docker Compatible**: Fully containerized and Kubernetes-ready
- **Production Ready**: Stable deployment with health checks
- **Memory Efficient**: Medium-sized model suitable for containerized environments
- **Open Access**: No authentication required for model access

### Performance Considerations
- **Model Size**: DialoGPT-medium requires ~1.5GB RAM
- **Response Time**: First response may take 3-5 seconds for model loading
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

## 🎯 Quick Test Commands

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test text generation
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a short poem about technology"}'

# Test with different prompt
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing in one sentence"}'

# Test conversational response
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
```
