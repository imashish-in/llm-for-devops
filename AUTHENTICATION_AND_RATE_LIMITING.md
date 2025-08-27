# 🔐 Authentication and Rate Limiting Guide

## 📋 Overview

This guide explains the authentication and rate limiting features implemented in the LLM Flask application to secure API access and prevent abuse.

## 🔑 Authentication

### What is Authentication?

Authentication verifies the identity of users before allowing access to the API. It acts as a digital ID card system for your application.

### Why Authentication is Important

- **🔒 Security**: Prevents unauthorized access to your API
- **📊 Usage Tracking**: Know who is using your API and how much
- **💰 Billing**: Charge users based on their usage
- **⚖️ Rate Limiting**: Apply different limits per user
- **📝 Audit Trail**: Track who made what requests and when

### Implementation Details

#### API Key Authentication

The application uses API key authentication, which is simple and effective for server-to-server communication.

```python
# Configuration
VALID_API_KEYS = {
    "user1": "sk-1234567890abcdef",
    "user2": "sk-fedcba0987654321"
}

# Environment Variables (Recommended for production)
API_KEY_USER1=sk-1234567890abcdef
API_KEY_USER2=sk-fedcba0987654321
```

#### How to Use API Keys

1. **Include in Request Headers**:
   ```bash
   curl -X POST http://localhost:8080/generate \
     -H "Content-Type: application/json" \
     -H "X-API-Key: sk-1234567890abcdef" \
     -d '{"prompt": "Hello, how are you?"}'
   ```

2. **Response for Invalid/Missing API Key**:
   ```json
   {
     "error": "Invalid or missing API key"
   }
   ```
   **Status Code**: 401 Unauthorized

### Security Best Practices

1. **Use Environment Variables**: Never hardcode API keys in your code
2. **Rotate Keys Regularly**: Change API keys periodically
3. **Use HTTPS**: Always use HTTPS in production
4. **Monitor Usage**: Track API key usage for suspicious activity
5. **Limit Permissions**: Different keys for different access levels

## 🚦 Rate Limiting

### What is Rate Limiting?

Rate limiting controls how many requests a user can make in a given time period. It's like a traffic light for your API.

### Why Rate Limiting is Important

- **🛡️ Resource Protection**: Prevent server overload
- **💰 Cost Control**: Limit expensive LLM API calls
- **⚖️ Fair Usage**: Ensure fair access for all users
- **🔒 Security**: Prevent abuse and DDoS attacks
- **⚡ Performance**: Maintain consistent response times

### Current Implementation

#### Rate Limit Configuration

- **Requests per Window**: 5 requests
- **Window Duration**: 60 seconds (1 minute)
- **Per User**: Each API key has its own limit

#### Rate Limit Headers

The API includes rate limit information in response headers:

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1640995200
```

#### Rate Limit Exceeded Response

When a user exceeds their rate limit:

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "limit": 5,
  "window": 60
}
```
**Status Code**: 429 Too Many Requests

### Rate Limit Status Endpoint

Check your current rate limit status:

```bash
curl -H "X-API-Key: sk-1234567890abcdef" \
  http://localhost:8080/rate-limit/status
```

**Response**:
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

## 🛠️ Implementation Details

### Authentication Decorator

```python
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key not in VALID_API_KEYS.values():
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function
```

### Rate Limiting Decorator

```python
def rate_limit(max_requests=10, window_seconds=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user identifier from API key
            api_key = request.headers.get('X-API-Key')
            user_id = get_user_from_api_key(api_key)
            
            current_time = time.time()
            
            # Clean old requests outside the window
            request_counts[user_id] = [
                req_time for req_time in request_counts[user_id]
                if current_time - req_time < window_seconds
            ]
            
            # Check if user has exceeded limit
            if len(request_counts[user_id]) >= max_requests:
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
```

## 📊 Usage Examples

### 1. Basic API Call with Authentication

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-1234567890abcdef" \
  -d '{"prompt": "Write a short poem about technology"}'
```

### 2. Check Rate Limit Status

```bash
curl -H "X-API-Key: sk-1234567890abcdef" \
  http://localhost:8080/rate-limit/status
```

### 3. Test Rate Limiting

```bash
# Make multiple requests quickly to test rate limiting
for i in {1..10}; do
  curl -X POST http://localhost:8080/generate \
    -H "Content-Type: application/json" \
    -H "X-API-Key: sk-1234567890abcdef" \
    -d '{"prompt": "Test request '$i'"}'
  echo "Request $i completed"
done
```

### 4. Invalid API Key Test

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key" \
  -d '{"prompt": "This should fail"}'
```

## 🔧 Configuration

### Environment Variables

Set these environment variables for production deployment:

```bash
# Authentication
SECRET_KEY=your-super-secret-key-change-this
API_KEY_USER1=sk-1234567890abcdef
API_KEY_USER2=sk-fedcba0987654321

# Rate Limiting (optional - defaults are used if not set)
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=60
```

### Kubernetes Configuration

Add environment variables to your Kubernetes deployment:

```yaml
env:
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: llm-secrets
      key: secret-key
- name: API_KEY_USER1
  valueFrom:
    secretKeyRef:
      name: llm-secrets
      key: api-key-user1
- name: API_KEY_USER2
  valueFrom:
    secretKeyRef:
      name: llm-secrets
      key: api-key-user2
```

## 🚀 Advanced Features

### JWT Token Support (Future Enhancement)

For more advanced authentication, JWT tokens can be implemented:

```python
def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### Redis-Based Rate Limiting (Production)

For production environments, use Redis for distributed rate limiting:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def redis_rate_limit(max_requests=10, window_seconds=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_user_id(request)
            key = f"rate_limit:{user_id}"
            
            pipe = redis_client.pipeline()
            current_time = time.time()
            
            # Add current request timestamp
            pipe.zadd(key, {str(current_time): current_time})
            
            # Remove requests older than window
            pipe.zremrangebyscore(key, 0, current_time - window_seconds)
            
            # Count requests in window
            pipe.zcard(key)
            
            # Set expiry on key
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            request_count = results[2]
            
            if request_count > max_requests:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": window_seconds
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## 📈 Monitoring and Analytics

### Rate Limit Metrics

Track rate limit usage:

```python
# Add to your application
rate_limit_metrics = {
    "total_requests": 0,
    "rate_limited_requests": 0,
    "unique_users": set()
}

def log_rate_limit_metrics(user_id, was_limited):
    rate_limit_metrics["total_requests"] += 1
    rate_limit_metrics["unique_users"].add(user_id)
    if was_limited:
        rate_limit_metrics["rate_limited_requests"] += 1
```

### API Usage Dashboard

Create an endpoint to view usage statistics:

```python
@app.route("/admin/usage")
@require_admin_key
def usage_stats():
    return jsonify({
        "total_requests": rate_limit_metrics["total_requests"],
        "rate_limited_requests": rate_limit_metrics["rate_limited_requests"],
        "unique_users": len(rate_limit_metrics["unique_users"]),
        "rate_limit_percentage": (
            rate_limit_metrics["rate_limited_requests"] / 
            rate_limit_metrics["total_requests"] * 100
        ) if rate_limit_metrics["total_requests"] > 0 else 0
    })
```

## 🔒 Security Considerations

### Best Practices

1. **Use Strong API Keys**: Generate cryptographically secure keys
2. **Rotate Keys Regularly**: Change keys every 30-90 days
3. **Monitor for Abuse**: Track unusual usage patterns
4. **Use HTTPS**: Always encrypt API communication
5. **Rate Limit by IP**: Additional protection against abuse
6. **Log Security Events**: Monitor failed authentication attempts

### Common Security Threats

1. **API Key Exposure**: Keys in logs, client-side code, or public repositories
2. **Brute Force Attacks**: Multiple attempts to guess API keys
3. **Rate Limit Bypass**: Using multiple keys or IP addresses
4. **Token Replay**: Reusing expired or stolen tokens

### Mitigation Strategies

1. **Key Rotation**: Regular key updates
2. **IP Whitelisting**: Restrict access to known IP addresses
3. **Request Signing**: Sign requests with timestamps
4. **Monitoring**: Real-time security monitoring
5. **Alerting**: Immediate notifications for suspicious activity

## 🧪 Testing

### Unit Tests

```python
def test_authentication():
    # Test valid API key
    response = client.post('/generate', 
        headers={'X-API-Key': 'sk-1234567890abcdef'},
        json={'prompt': 'test'})
    assert response.status_code == 200
    
    # Test invalid API key
    response = client.post('/generate', 
        headers={'X-API-Key': 'invalid-key'},
        json={'prompt': 'test'})
    assert response.status_code == 401

def test_rate_limiting():
    # Make requests up to the limit
    for i in range(5):
        response = client.post('/generate',
            headers={'X-API-Key': 'sk-1234567890abcdef'},
            json={'prompt': f'test {i}'})
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.post('/generate',
        headers={'X-API-Key': 'sk-1234567890abcdef'},
        json={'prompt': 'should fail'})
    assert response.status_code == 429
```

### Load Testing

```bash
# Test rate limiting with Apache Bench
ab -n 100 -c 10 -H "X-API-Key: sk-1234567890abcdef" \
  -p test_data.json -T application/json \
  http://localhost:8080/generate
```

## 📚 Additional Resources

- [Flask Security Documentation](https://flask-security.readthedocs.io/)
- [JWT.io](https://jwt.io/) - JWT token debugging
- [Redis Rate Limiting](https://redis.io/topics/patterns/distributed-locks)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)

## 🤝 Support

For questions about authentication and rate limiting:

1. Check this documentation
2. Review the implementation in `app.py`
3. Test with the provided examples
4. Open an issue in the repository

---

**Note**: This implementation provides basic authentication and rate limiting. For production use, consider implementing additional security measures like request signing, IP whitelisting, and comprehensive monitoring.
