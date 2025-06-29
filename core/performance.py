"""
Performance monitoring middleware and utilities.
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
import threading
from collections import defaultdict, deque
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor request performance and detect slow requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_request_threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD', 2.0)  # seconds
        super().__init__(get_response)
    
    def process_request(self, request):
        request._performance_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_performance_start_time'):
            duration = time.time() - request._performance_start_time
            
            # Log slow requests
            if duration > self.slow_request_threshold:
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.2f}s (User: {getattr(request.user, 'username', 'Anonymous')})"
                )
            
            # Store performance metrics
            self._record_performance_metric(request, duration)
            
            # Add performance header for debugging
            if settings.DEBUG:
                response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def _record_performance_metric(self, request, duration):
        """Record performance metrics for analysis."""
        try:
            metric_data = {
                'path': request.path,
                'method': request.method,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'user': getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'anonymous',
                'status_code': getattr(request, '_status_code', 'unknown'),
            }
            
            # Store in cache for short-term analysis
            cache_key = f"performance_metrics:{datetime.now().strftime('%Y%m%d%H')}"
            metrics = cache.get(cache_key, [])
            metrics.append(metric_data)
            
            # Keep only last 1000 metrics per hour
            if len(metrics) > 1000:
                metrics = metrics[-1000:]
            
            cache.set(cache_key, metrics, 3600)  # Store for 1 hour
            
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")


class DatabaseQueryMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor database query performance.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_query_threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD', 0.5)  # seconds
        super().__init__(get_response)
    
    def process_request(self, request):
        if settings.DEBUG:
            from django.db import connection
            request._db_query_count_start = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        if settings.DEBUG and hasattr(request, '_db_query_count_start'):
            from django.db import connection
            
            query_count = len(connection.queries) - request._db_query_count_start
            
            # Check for slow queries
            slow_queries = []
            for query in connection.queries[request._db_query_count_start:]:
                if float(query['time']) > self.slow_query_threshold:
                    slow_queries.append({
                        'sql': query['sql'][:200] + '...' if len(query['sql']) > 200 else query['sql'],
                        'time': query['time']
                    })
            
            if slow_queries:
                logger.warning(
                    f"Slow database queries detected for {request.path}: "
                    f"{len(slow_queries)} slow queries out of {query_count} total"
                )
            
            # Add debug headers
            response['X-DB-Query-Count'] = str(query_count)
            if slow_queries:
                response['X-DB-Slow-Queries'] = str(len(slow_queries))
        
        return response


class MemoryMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor memory usage during request processing.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        try:
            import psutil
            process = psutil.Process()
            request._memory_start = process.memory_info().rss
        except ImportError:
            pass
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_memory_start'):
            try:
                import psutil
                process = psutil.Process()
                memory_end = process.memory_info().rss
                memory_diff = memory_end - request._memory_start
                
                # Convert to MB
                memory_diff_mb = memory_diff / (1024 * 1024)
                
                if memory_diff_mb > 10:  # Alert if request used more than 10MB
                    logger.warning(
                        f"High memory usage request: {request.path} "
                        f"used {memory_diff_mb:.2f} MB"
                    )
                
                if settings.DEBUG:
                    response['X-Memory-Usage'] = f"{memory_diff_mb:.2f}MB"
                    
            except ImportError:
                pass
        
        return response


class PerformanceAnalyzer:
    """
    Utility class for analyzing performance metrics.
    """
    
    @staticmethod
    def get_slow_endpoints(hours=24):
        """Get endpoints with slowest average response times."""
        try:
            endpoint_stats = defaultdict(list)
            
            # Collect metrics from cache
            now = datetime.now()
            for hour_offset in range(hours):
                timestamp = now - timedelta(hours=hour_offset)
                cache_key = f"performance_metrics:{timestamp.strftime('%Y%m%d%H')}"
                metrics = cache.get(cache_key, [])
                
                for metric in metrics:
                    endpoint = f"{metric['method']} {metric['path']}"
                    endpoint_stats[endpoint].append(metric['duration'])
            
            # Calculate averages
            slow_endpoints = []
            for endpoint, durations in endpoint_stats.items():
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                request_count = len(durations)
                
                slow_endpoints.append({
                    'endpoint': endpoint,
                    'avg_duration': avg_duration,
                    'max_duration': max_duration,
                    'request_count': request_count,
                })
            
            # Sort by average duration
            slow_endpoints.sort(key=lambda x: x['avg_duration'], reverse=True)
            
            return slow_endpoints[:10]  # Top 10 slowest
            
        except Exception as e:
            logger.error(f"Failed to analyze slow endpoints: {e}")
            return []
    
    @staticmethod
    def get_performance_summary(hours=24):
        """Get overall performance summary."""
        try:
            all_durations = []
            request_count = 0
            error_count = 0
            
            # Collect metrics from cache
            now = datetime.now()
            for hour_offset in range(hours):
                timestamp = now - timedelta(hours=hour_offset)
                cache_key = f"performance_metrics:{timestamp.strftime('%Y%m%d%H')}"
                metrics = cache.get(cache_key, [])
                
                for metric in metrics:
                    all_durations.append(metric['duration'])
                    request_count += 1
                    
                    # Count errors (assuming status codes >= 400 are errors)
                    if isinstance(metric.get('status_code'), int) and metric['status_code'] >= 400:
                        error_count += 1
            
            if not all_durations:
                return {
                    'request_count': 0,
                    'avg_response_time': 0,
                    'p95_response_time': 0,
                    'p99_response_time': 0,
                    'error_rate': 0,
                }
            
            # Calculate percentiles
            sorted_durations = sorted(all_durations)
            p95_index = int(len(sorted_durations) * 0.95)
            p99_index = int(len(sorted_durations) * 0.99)
            
            return {
                'request_count': request_count,
                'avg_response_time': sum(all_durations) / len(all_durations),
                'p95_response_time': sorted_durations[p95_index] if p95_index < len(sorted_durations) else 0,
                'p99_response_time': sorted_durations[p99_index] if p99_index < len(sorted_durations) else 0,
                'error_rate': (error_count / request_count) * 100 if request_count > 0 else 0,
                'min_response_time': min(all_durations),
                'max_response_time': max(all_durations),
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance summary: {e}")
            return {}


class RequestRateLimiter:
    """
    Simple rate limiter to prevent abuse.
    """
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_rate_limited(self, identifier, max_requests=100, window_seconds=60):
        """
        Check if identifier is rate limited.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            bool: True if rate limited, False otherwise
        """
        now = time.time()
        window_start = now - window_seconds
        
        with self.lock:
            # Clean old requests
            request_times = self.requests[identifier]
            while request_times and request_times[0] < window_start:
                request_times.popleft()
            
            # Check if rate limited
            if len(request_times) >= max_requests:
                return True
            
            # Add current request
            request_times.append(now)
            
            return False


# Global rate limiter instance
rate_limiter = RequestRateLimiter()


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to implement rate limiting.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        self.window_seconds = getattr(settings, 'RATE_LIMIT_WINDOW', 60)
        super().__init__(get_response)
    
    def process_request(self, request):
        # Use IP address as identifier
        identifier = self._get_client_ip(request)
        
        if rate_limiter.is_rate_limited(
            identifier, 
            self.max_requests, 
            self.window_seconds
        ):
            from django.http import HttpResponseTooManyRequests
            logger.warning(f"Rate limit exceeded for {identifier}")
            return HttpResponseTooManyRequests("Rate limit exceeded")
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
