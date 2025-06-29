import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger('glad_tidings.requests')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses for monitoring and debugging.
    """
    
    def process_request(self, request):
        """Log incoming request details"""
        request._start_time = time.time()
        
        # Log request details (but be careful not to log sensitive data)
        request_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],  # Limit length
        }
        
        logger.info(f"Request started: {request_data}")
        
        return None
    
    def process_response(self, request, response):
        """Log response details and request duration"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            response_data = {
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'path': request.path,
                'method': request.method,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            }
            
            # Log level based on response status
            if response.status_code >= 500:
                logger.error(f"Request completed with error: {response_data}")
            elif response.status_code >= 400:
                logger.warning(f"Request completed with client error: {response_data}")
            elif duration > 5:  # Log slow requests (>5 seconds)
                logger.warning(f"Slow request detected: {response_data}")
            else:
                logger.info(f"Request completed: {response_data}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log unhandled exceptions"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            exception_data = {
                'exception': str(exception),
                'exception_type': type(exception).__name__,
                'path': request.path,
                'method': request.method,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'duration_ms': round(duration * 1000, 2),
            }
            
            logger.error(f"Request failed with exception: {exception_data}", exc_info=True)
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    
    def process_response(self, request, response):
        """Add security headers to response"""
        if not settings.DEBUG:
            # Add security headers only in production
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Add Strict-Transport-Security if using HTTPS
            if request.is_secure():
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity for analytics and security.
    """
    
    def process_request(self, request):
        """Track user activity"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Update user's last activity (you might want to do this in a signal instead for performance)
            from django.utils import timezone
            request.user.last_login = timezone.now()
            # Note: Saving on every request can be expensive, consider using signals or periodic updates
        
        return None
