from flask import Flask, request, jsonify
import logging
import os
import hashlib
import time
from functools import lru_cache
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import gc
from collections import defaultdict
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Authentication and Rate Limiting Setup
from functools import wraps
import jwt
from datetime import datetime, timedelta

# Metrics and Monitoring Setup
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import psutil
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for model and cache
model = None
tokenizer = None
response_cache = {}
cache_stats = {"hits": 0, "misses": 0}

# Configuration
CACHE_SIZE = 1000  # Maximum number of cached responses
CACHE_TTL = 3600   # Cache TTL in seconds (1 hour)
MODEL_CACHE_DIR = "/app/model_cache"  # Persistent model cache directory

# Authentication and Rate Limiting Setup
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
VALID_API_KEYS = {
    "user1": os.environ.get('API_KEY_USER1', 'sk-1234567890abcdef'),
    "user2": os.environ.get('API_KEY_USER2', 'sk-fedcba0987654321')
}

# Rate limiting storage
request_counts = defaultdict(list)

# Prometheus Metrics Setup
# Request metrics
REQUEST_COUNT = Counter('llm_requests_total', 'Total number of requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('llm_request_duration_seconds', 'Request duration in seconds', ['method', 'endpoint'])

# Model metrics
MODEL_LOAD_TIME = Histogram('llm_model_load_duration_seconds', 'Model loading duration in seconds')
GENERATION_DURATION = Histogram('llm_generation_duration_seconds', 'Text generation duration in seconds')
GENERATION_TOKENS = Histogram('llm_generation_tokens', 'Number of tokens generated')

# Cache metrics
CACHE_HITS = Counter('llm_cache_hits_total', 'Total cache hits')
CACHE_MISSES = Counter('llm_cache_misses_total', 'Total cache misses')
CACHE_SIZE_GAUGE = Gauge('llm_cache_size', 'Current cache size')

# System metrics
MEMORY_USAGE = Gauge('llm_memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('llm_cpu_usage_percent', 'CPU usage percentage')
MODEL_MEMORY = Gauge('llm_model_memory_bytes', 'Model memory usage in bytes')

# Authentication metrics
AUTH_FAILURES = Counter('llm_auth_failures_total', 'Total authentication failures')
RATE_LIMIT_EXCEEDED = Counter('llm_rate_limit_exceeded_total', 'Total rate limit violations')

# Application metrics
ACTIVE_REQUESTS = Gauge('llm_active_requests', 'Number of active requests')
ERROR_COUNT = Counter('llm_errors_total', 'Total number of errors', ['type'])

# Metrics collection thread
metrics_thread = None
stop_metrics = False

# Authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key not in VALID_API_KEYS.values():
            AUTH_FAILURES.inc()
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status='401').inc()
            REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint).observe(time.time() - start_time)
            return jsonify({"error": "Invalid or missing API key"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Rate limiting decorator
def rate_limit(max_requests=10, window_seconds=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Get user identifier from API key
            api_key = request.headers.get('X-API-Key')
            user_id = None
            for user, key in VALID_API_KEYS.items():
                if key == api_key:
                    user_id = user
                    break
            
            if not user_id:
                AUTH_FAILURES.inc()
                REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status='401').inc()
                REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint).observe(time.time() - start_time)
                return jsonify({"error": "Invalid API key"}), 401
            
            current_time = time.time()
            
            # Clean old requests outside the window
            request_counts[user_id] = [
                req_time for req_time in request_counts[user_id]
                if current_time - req_time < window_seconds
            ]
            
            # Check if user has exceeded limit
            if len(request_counts[user_id]) >= max_requests:
                RATE_LIMIT_EXCEEDED.inc()
                REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status='429').inc()
                REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint).observe(time.time() - start_time)
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": window_seconds,
                    "limit": max_requests,
                    "window": window_seconds
                }), 429
            
            # Add current request
            request_counts[user_id].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def collect_system_metrics():
    """Collect system metrics periodically"""
    global stop_metrics
    while not stop_metrics:
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.used)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)
            
            # Model memory if available
            if model is not None:
                model_memory = sum(p.numel() * p.element_size() for p in model.parameters())
                MODEL_MEMORY.set(model_memory)
            
            # Cache size
            CACHE_SIZE_GAUGE.set(len(response_cache))
            
            time.sleep(30)  # Collect metrics every 30 seconds
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            time.sleep(30)

def start_metrics_collection():
    """Start the metrics collection thread"""
    global metrics_thread, stop_metrics
    stop_metrics = False
    metrics_thread = threading.Thread(target=collect_system_metrics, daemon=True)
    metrics_thread.start()
    logger.info("Metrics collection started")

def stop_metrics_collection():
    """Stop the metrics collection thread"""
    global stop_metrics
    stop_metrics = True
    if metrics_thread:
        metrics_thread.join(timeout=5)

# Request tracking decorator
def track_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        ACTIVE_REQUESTS.inc()
        
        try:
            result = f(*args, **kwargs)
            # Track successful requests
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status='200').inc()
            REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint).observe(time.time() - start_time)
            return result
        except Exception as e:
            # Track errors
            ERROR_COUNT.labels(type='request_error').inc()
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status='500').inc()
            REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint).observe(time.time() - start_time)
            raise
        finally:
            ACTIVE_REQUESTS.dec()
    
    return decorated_function

def setup_model_cache():
    """Setup model cache directory"""
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
    os.environ['TRANSFORMERS_CACHE'] = MODEL_CACHE_DIR
    os.environ['HF_HOME'] = MODEL_CACHE_DIR

def load_model_with_optimizations():
    """Load model with various optimizations"""
    global model, tokenizer
    
    try:
        logger.info("Setting up model cache directory...")
        setup_model_cache()
        
        logger.info("Attempting to load DialoGPT-medium model with optimizations...")
        start_time = time.time()
        
        # Use DialoGPT-medium model (open access, no authentication required)
        model_name = "microsoft/DialoGPT-medium"
        
        # Load tokenizer with caching
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=MODEL_CACHE_DIR,
            local_files_only=False  # Allow downloading if not cached
        )
        
        # Load model with optimizations
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=MODEL_CACHE_DIR,
            local_files_only=False,
            torch_dtype=torch.float16,  # Use half precision for memory efficiency
            low_cpu_mem_usage=True,     # Reduce CPU memory usage
        )
        
        # Add padding token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Move model to GPU if available, otherwise keep on CPU
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        model.eval()  # Set to evaluation mode
        
        # Record model load time
        load_time = time.time() - start_time
        MODEL_LOAD_TIME.observe(load_time)
        
        logger.info(f"DialoGPT-medium model loaded successfully on {device}!")
        logger.info(f"Model cache directory: {MODEL_CACHE_DIR}")
        logger.info(f"Model load time: {load_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Failed to load DialoGPT-medium model: {e}")
        ERROR_COUNT.labels(type='model_load').inc()
        raise e

def generate_cache_key(prompt, temperature=0.8, max_tokens=256):
    """Generate a cache key for the prompt and parameters"""
    cache_string = f"{prompt}_{temperature}_{max_tokens}"
    return hashlib.md5(cache_string.encode()).hexdigest()

def get_cached_response(cache_key):
    """Get cached response if available and not expired"""
    if cache_key in response_cache:
        cached_data = response_cache[cache_key]
        if time.time() - cached_data['timestamp'] < CACHE_TTL:
            cache_stats["hits"] += 1
            CACHE_HITS.inc()
            return cached_data['response']
        else:
            # Remove expired cache entry
            del response_cache[cache_key]
    
    cache_stats["misses"] += 1
    CACHE_MISSES.inc()
    return None

def cache_response(cache_key, response):
    """Cache the response"""
    if len(response_cache) >= CACHE_SIZE:
        # Remove oldest entry (simple LRU)
        oldest_key = next(iter(response_cache))
        del response_cache[oldest_key]
    
    response_cache[cache_key] = {
        'response': response,
        'timestamp': time.time()
    }

@lru_cache(maxsize=1000)
def encode_prompt(prompt, max_length=1024):
    """Cache encoded prompts to avoid re-encoding"""
    return tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt", max_length=max_length, truncation=True)

def optimize_memory():
    """Optimize memory usage"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# Load model on startup
load_model_with_optimizations()

@app.route("/health", methods=["GET"])
@track_request
def health():
    if model is not None:
        cache_info = {
            "cache_size": len(response_cache),
            "cache_hits": cache_stats["hits"],
            "cache_misses": cache_stats["misses"],
            "hit_rate": cache_stats["hits"] / (cache_stats["hits"] + cache_stats["misses"]) if (cache_stats["hits"] + cache_stats["misses"]) > 0 else 0
        }
        return jsonify({
            "status": "healthy", 
            "message": "DialoGPT-medium model is loaded and ready",
            "cache_info": cache_info,
            "device": str(next(model.parameters()).device)
        })
    else:
        return jsonify({"status": "unhealthy", "error": "No model loaded"}), 500

@app.route("/generate", methods=["POST"])
@track_request
@require_api_key
@rate_limit(max_requests=5, window_seconds=60)  # 5 requests per minute per user
def generate():
    try:
        prompt = request.json.get("prompt", "")
        temperature = request.json.get("temperature", 0.8)
        max_tokens = request.json.get("max_tokens", 256)
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        if model is not None:
            start_time = time.time()
            logger.info(f"Generating response for prompt: {prompt[:50]}...")
            
            # Check cache first
            cache_key = generate_cache_key(prompt, temperature, max_tokens)
            cached_response = get_cached_response(cache_key)
            
            if cached_response:
                logger.info("Response served from cache")
                return jsonify({
                    "response": cached_response,
                    "cached": True,
                    "generation_time": 0.0
                })
            
            # Encode the input (with caching)
            inputs = encode_prompt(prompt, max_length=1024)
            attention_mask = torch.ones_like(inputs)
            
            # Generate response with optimizations
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_new_tokens=max_tokens,
                    num_return_sequences=1,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    use_cache=True  # Enable KV cache for faster generation
                )
            
            # Decode the response
            full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated response (remove the input prompt)
            response = full_response[len(prompt):].strip()
            
            # Clean up any remaining special tokens
            response = response.replace("<|endoftext|>", "").replace("<|eot_id|>", "").strip()
            
            # If response is empty or too short, try a different approach
            if not response or len(response) < 5:
                logger.info("Attempting fallback generation...")
                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        attention_mask=attention_mask,
                        max_new_tokens=128,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id,
                        eos_token_id=tokenizer.eos_token_id
                    )
                
                full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = full_response[len(prompt):].strip()
            
            # Cache the response
            cache_response(cache_key, response)
            
            generation_time = time.time() - start_time
            
            # Record generation metrics
            GENERATION_DURATION.observe(generation_time)
            token_count = len(tokenizer.encode(response))
            GENERATION_TOKENS.observe(token_count)
            
            logger.info(f"Response generated successfully in {generation_time:.2f}s")
            logger.info(f"Generated {token_count} tokens")
            
            # Optimize memory after generation
            optimize_memory()
            
            return jsonify({
                "response": response,
                "cached": False,
                "generation_time": generation_time,
                "tokens_generated": token_count
            })
        else:
            return jsonify({"error": "Model not loaded"}), 500
            
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/cache/stats", methods=["GET"])
def cache_stats_endpoint():
    """Get cache statistics"""
    return jsonify({
        "cache_size": len(response_cache),
        "cache_hits": cache_stats["hits"],
        "cache_misses": cache_stats["misses"],
        "hit_rate": cache_stats["hits"] / (cache_stats["hits"] + cache_stats["misses"]) if (cache_stats["hits"] + cache_stats["misses"]) > 0 else 0,
        "cache_ttl": CACHE_TTL,
        "max_cache_size": CACHE_SIZE
    })

@app.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Clear the response cache"""
    global response_cache, cache_stats
    response_cache.clear()
    cache_stats = {"hits": 0, "misses": 0}
    optimize_memory()
    return jsonify({"message": "Cache cleared successfully"})

@app.route("/rate-limit/status")
@require_api_key
def rate_limit_status():
    """Get current rate limit status for the authenticated user"""
    api_key = request.headers.get('X-API-Key')
    user_id = None
    for user, key in VALID_API_KEYS.items():
        if key == api_key:
            user_id = user
            break
    
    if not user_id:
        return jsonify({"error": "Invalid API key"}), 401
    
    current_time = time.time()
    window_seconds = 60
    max_requests = 5
    
    # Clean old requests
    request_counts[user_id] = [
        req_time for req_time in request_counts[user_id]
        if current_time - req_time < window_seconds
    ]
    
    current_requests = len(request_counts[user_id])
    remaining_requests = max(0, max_requests - current_requests)
    
    return jsonify({
        "user_id": user_id,
        "current_requests": current_requests,
        "remaining_requests": remaining_requests,
        "limit": max_requests,
        "window_seconds": window_seconds,
        "reset_time": current_time + window_seconds if current_requests > 0 else None
    })

@app.route("/model/info", methods=["GET"])
def model_info():
    """Get model information"""
    if model is not None:
        device = next(model.parameters()).device
        model_size = sum(p.numel() for p in model.parameters())
        return jsonify({
            "model_name": "microsoft/DialoGPT-medium",
            "device": str(device),
            "parameters": model_size,
            "dtype": str(next(model.parameters()).dtype),
            "cache_directory": MODEL_CACHE_DIR
        })
    else:
        return jsonify({"error": "Model not loaded"}), 500

@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route("/dashboard")
def dashboard():
    """Application dashboard with key metrics"""
    try:
        # System metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent()
        
        # Model metrics
        model_info = {}
        if model is not None:
            device = next(model.parameters()).device
            model_size = sum(p.numel() for p in model.parameters())
            model_memory = sum(p.numel() * p.element_size() for p in model.parameters())
            model_info = {
                "device": str(device),
                "parameters": model_size,
                "memory_mb": round(model_memory / 1024 / 1024, 2),
                "dtype": str(next(model.parameters()).dtype)
            }
        
        # Cache metrics
        cache_info = {
            "size": len(response_cache),
            "hits": cache_stats["hits"],
            "misses": cache_stats["misses"],
            "hit_rate": round(cache_stats["hits"] / (cache_stats["hits"] + cache_stats["misses"]) * 100, 2) if (cache_stats["hits"] + cache_stats["misses"]) > 0 else 0,
            "ttl_seconds": CACHE_TTL,
            "max_size": CACHE_SIZE
        }
        
        # Request metrics (approximate from Prometheus metrics)
        request_info = {
            "active_requests": ACTIVE_REQUESTS._value.get(),
            "total_requests": 0,  # Will be calculated from actual metrics
            "auth_failures": AUTH_FAILURES._value.get(),
            "rate_limit_violations": RATE_LIMIT_EXCEEDED._value.get()
        }
        
        # System info
        system_info = {
            "memory_used_mb": round(memory.used / 1024 / 1024, 2),
            "memory_total_mb": round(memory.total / 1024 / 1024, 2),
            "memory_percent": round(memory.percent, 2),
            "cpu_percent": round(cpu_percent, 2),
            "uptime_seconds": time.time() - app.start_time if hasattr(app, 'start_time') else 0
        }
        
        return jsonify({
            "status": "healthy" if model is not None else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "model": model_info,
            "cache": cache_info,
            "requests": request_info,
            "system": system_info
        })
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.start_time = time.time()
    logger.info("Starting LLM Flask application with metrics and monitoring...")
    start_metrics_collection()
    app.run(host="0.0.0.0", port=8080)
