# Metrics and Monitoring Guide

This guide covers the comprehensive metrics and monitoring features implemented in the LLM Flask application.

## 📊 Overview

The application provides extensive monitoring capabilities through:
- **Prometheus Metrics**: Standard metrics format for monitoring systems
- **Real-time Dashboard**: JSON dashboard with key performance indicators
- **System Monitoring**: CPU, memory, and model resource usage
- **Performance Tracking**: Request duration, generation time, and token counts
- **Security Monitoring**: Authentication failures and rate limiting violations

## 🔧 Prometheus Metrics

### Request Metrics

#### `llm_requests_total`
Total number of requests by endpoint, method, and status.

**Labels:**
- `method`: HTTP method (GET, POST)
- `endpoint`: API endpoint (health, generate, etc.)
- `status`: HTTP status code (200, 401, 429, 500)

**Example:**
```
llm_requests_total{endpoint="health",method="GET",status="200"} 15.0
llm_requests_total{endpoint="generate",method="POST",status="200"} 8.0
llm_requests_total{endpoint="generate",method="POST",status="401"} 2.0
```

#### `llm_request_duration_seconds`
Request duration histograms for performance monitoring.

**Labels:**
- `method`: HTTP method
- `endpoint`: API endpoint

**Buckets:** 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, +Inf

#### `llm_active_requests`
Number of currently active requests (gauge).

### Model Metrics

#### `llm_model_load_duration_seconds`
Time taken to load the DialoGPT-medium model.

**Buckets:** Same as request duration

#### `llm_generation_duration_seconds`
Time taken to generate text responses.

**Buckets:** Same as request duration

#### `llm_generation_tokens`
Number of tokens generated in responses.

**Buckets:** 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, +Inf

### Cache Metrics

#### `llm_cache_hits_total`
Total number of cache hits (counter).

#### `llm_cache_misses_total`
Total number of cache misses (counter).

#### `llm_cache_size`
Current number of cached responses (gauge).

### System Metrics

#### `llm_memory_usage_bytes`
Current memory usage in bytes (gauge).

#### `llm_cpu_usage_percent`
Current CPU usage percentage (gauge).

#### `llm_model_memory_bytes`
Memory usage by the model in bytes (gauge).

### Security Metrics

#### `llm_auth_failures_total`
Total number of authentication failures (counter).

#### `llm_rate_limit_exceeded_total`
Total number of rate limit violations (counter).

#### `llm_errors_total`
Total number of errors by type (counter).

**Labels:**
- `type`: Error type (model_load, request_error)

## 📈 Dashboard

### Endpoint: `GET /dashboard`

Returns a comprehensive JSON dashboard with real-time metrics.

### Response Structure

```json
{
  "status": "healthy",
  "timestamp": "2025-08-27T04:47:03.780352",
  "model": {
    "device": "cpu",
    "dtype": "torch.float16",
    "memory_mb": 676.77,
    "parameters": 354823168
  },
  "cache": {
    "size": 1,
    "hits": 0,
    "misses": 1,
    "hit_rate": 0.0,
    "ttl_seconds": 3600,
    "max_size": 1000
  },
  "requests": {
    "active_requests": 0.0,
    "auth_failures": 1.0,
    "rate_limit_violations": 0.0
  },
  "system": {
    "memory_used_mb": 6545.38,
    "memory_total_mb": 7837.19,
    "memory_percent": 86.8,
    "cpu_percent": 0.0,
    "uptime_seconds": 204.35
  }
}
```

### Dashboard Fields

#### Model Information
- `device`: Model device (cpu/cuda)
- `dtype`: Data type (torch.float16)
- `memory_mb`: Model memory usage in MB
- `parameters`: Number of model parameters

#### Cache Statistics
- `size`: Current cache size
- `hits`: Total cache hits
- `misses`: Total cache misses
- `hit_rate`: Cache hit rate percentage
- `ttl_seconds`: Cache TTL in seconds
- `max_size`: Maximum cache size

#### Request Metrics
- `active_requests`: Currently active requests
- `auth_failures`: Total authentication failures
- `rate_limit_violations`: Total rate limit violations

#### System Information
- `memory_used_mb`: Used memory in MB
- `memory_total_mb`: Total memory in MB
- `memory_percent`: Memory usage percentage
- `cpu_percent`: CPU usage percentage
- `uptime_seconds`: Application uptime in seconds

## 🔍 Monitoring Setup

### Prometheus Configuration

Add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'llm-flask'
    static_configs:
      - targets: ['llm-flask-service:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s
```

### Grafana Dashboard

#### Key Metrics to Monitor

1. **Request Rate**
   ```
   rate(llm_requests_total[5m])
   ```

2. **Request Duration (95th percentile)**
   ```
   histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m]))
   ```

3. **Cache Hit Rate**
   ```
   rate(llm_cache_hits_total[5m]) / (rate(llm_cache_hits_total[5m]) + rate(llm_cache_misses_total[5m]))
   ```

4. **Memory Usage**
   ```
   llm_memory_usage_bytes / 1024 / 1024 / 1024
   ```

5. **CPU Usage**
   ```
   llm_cpu_usage_percent
   ```

6. **Generation Duration**
   ```
   histogram_quantile(0.95, rate(llm_generation_duration_seconds_bucket[5m]))
   ```

7. **Authentication Failures**
   ```
   rate(llm_auth_failures_total[5m])
   ```

8. **Rate Limit Violations**
   ```
   rate(llm_rate_limit_exceeded_total[5m])
   ```

### Alerting Rules

#### High Error Rate
```yaml
- alert: HighErrorRate
  expr: rate(llm_errors_total[5m]) > 0.1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value }} errors per second"
```

#### High Memory Usage
```yaml
- alert: HighMemoryUsage
  expr: llm_memory_usage_bytes / 1024 / 1024 / 1024 > 6
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High memory usage detected"
    description: "Memory usage is {{ $value }} GB"
```

#### High Authentication Failures
```yaml
- alert: HighAuthFailures
  expr: rate(llm_auth_failures_total[5m]) > 0.05
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High authentication failure rate"
    description: "Auth failure rate is {{ $value }} failures per second"
```

#### High Response Time
```yaml
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m])) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High response time detected"
    description: "95th percentile response time is {{ $value }} seconds"
```

## 🛠️ Usage Examples

### Basic Metrics Check
```bash
# Get all Prometheus metrics
curl http://localhost:8080/metrics

# Get dashboard
curl http://localhost:8080/dashboard

# Check specific metrics
curl http://localhost:8080/metrics | grep "llm_requests_total"
```

### Cache Performance Monitoring
```bash
# Check cache hit rate
curl http://localhost:8080/metrics | grep "llm_cache_hits_total"
curl http://localhost:8080/metrics | grep "llm_cache_misses_total"

# Calculate hit rate
hits=$(curl -s http://localhost:8080/metrics | grep "llm_cache_hits_total" | grep -v "#" | awk '{print $2}')
misses=$(curl -s http://localhost:8080/metrics | grep "llm_cache_misses_total" | grep -v "#" | awk '{print $2}')
total=$((hits + misses))
if [ $total -gt 0 ]; then
    hit_rate=$(echo "scale=2; $hits * 100 / $total" | bc)
    echo "Cache hit rate: ${hit_rate}%"
fi
```

### System Resource Monitoring
```bash
# Check memory usage
curl http://localhost:8080/metrics | grep "llm_memory_usage_bytes"

# Check CPU usage
curl http://localhost:8080/metrics | grep "llm_cpu_usage_percent"

# Check model memory
curl http://localhost:8080/metrics | grep "llm_model_memory_bytes"
```

### Security Monitoring
```bash
# Check authentication failures
curl http://localhost:8080/metrics | grep "llm_auth_failures_total"

# Check rate limit violations
curl http://localhost:8080/metrics | grep "llm_rate_limit_exceeded_total"

# Check error rates
curl http://localhost:8080/metrics | grep "llm_errors_total"
```

### Performance Monitoring
```bash
# Check generation duration
curl http://localhost:8080/metrics | grep "llm_generation_duration_seconds"

# Check request duration
curl http://localhost:8080/metrics | grep "llm_request_duration_seconds"

# Check active requests
curl http://localhost:8080/metrics | grep "llm_active_requests"
```

## 📊 Performance Insights

### Expected Metrics Values

#### Request Performance
- **Health endpoint**: < 100ms
- **Generate endpoint**: 5-30 seconds (first request), < 1 second (cached)
- **Cache hit rate**: > 80% (for repeated queries)

#### System Resources
- **Memory usage**: 4-8 GB (depending on model and cache size)
- **CPU usage**: 0-50% (spikes during generation)
- **Model memory**: ~676 MB (DialoGPT-medium)

#### Security Metrics
- **Auth failures**: Should be low (< 1% of requests)
- **Rate limit violations**: Should be minimal in normal usage

### Optimization Tips

1. **Cache Optimization**
   - Monitor cache hit rate
   - Adjust cache size based on memory availability
   - Consider cache TTL for different query types

2. **Performance Tuning**
   - Monitor generation duration
   - Optimize model parameters (temperature, max_tokens)
   - Consider model quantization for memory efficiency

3. **Resource Management**
   - Set appropriate memory limits
   - Monitor CPU usage patterns
   - Scale horizontally if needed

4. **Security Monitoring**
   - Track authentication patterns
   - Monitor rate limit usage
   - Set up alerts for unusual activity

## 🔄 Metrics Collection

### Background Collection
The application runs a background thread that collects system metrics every 30 seconds:
- Memory usage
- CPU usage
- Model memory usage
- Cache size

### Real-time Updates
Request metrics are updated in real-time:
- Request counts and durations
- Authentication and rate limiting events
- Cache hits and misses
- Generation performance

### Metrics Persistence
- Metrics are stored in memory during application runtime
- Reset when the application restarts
- For persistent storage, use Prometheus with persistent volumes

## 🚀 Production Deployment

### Recommended Monitoring Stack
1. **Prometheus**: Metrics collection and storage
2. **Grafana**: Visualization and dashboards
3. **AlertManager**: Alert routing and notification
4. **Node Exporter**: Host system metrics (optional)

### High Availability
- Deploy multiple Prometheus instances
- Use persistent storage for metrics
- Set up alerting for monitoring system health
- Monitor the monitoring system itself

### Security Considerations
- Secure metrics endpoints in production
- Use authentication for dashboard access
- Encrypt metrics in transit
- Regular backup of monitoring data
