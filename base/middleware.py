"""
Custom middleware for Issue Management System
"""

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """
    Enhanced security middleware for the Issue Management System
    """
    
    def process_request(self, request):
        """Process incoming requests for security checks"""
        
        # Set security headers
        if not request.path.startswith('/admin/'):
            request.META['HTTP_X_FRAME_OPTIONS'] = 'DENY'
            request.META['HTTP_X_CONTENT_TYPE_OPTIONS'] = 'nosniff'
            request.META['HTTP_X_XSS_PROTECTION'] = '1; mode=block'
        
        # Log suspicious activity
        if request.method == 'POST':
            # Check for potential CSRF bypass attempts
            if not request.META.get('HTTP_REFERER'):
                logger.warning(f"Potential CSRF attack from IP: {self.get_client_ip(request)}")
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing responses for security headers"""
        
        # Add security headers
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data:;"
        
        return response
    
    def get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PermissionMiddleware(MiddlewareMixin):
    """
    Middleware to handle permissions and access control
    """
    
    def process_request(self, request):
        """Check permissions for protected views"""
        # Enforce a strict whitelist: only allow non-superusers to access a small set of public paths.
        # Superusers bypass this middleware and have full access.

        # Paths that should always be accessible (public resources, auth, welcome, static/media, admin login)
        allowed_prefixes = [
            '/welcome/',
            '/login/',
            '/logout/',
            '/register/',
            '/pending-approval/',
            '/rejected-user/',
            '/password',
            '/reset',
            '/admin/login/',
            '/admin/',
            '/api/',  # Allow all API endpoints for authenticated users
        ]

        # include static/media from settings if present
        try:
            static_url = settings.STATIC_URL or '/static/'
        except Exception:
            static_url = '/static/'

        try:
            media_url = settings.MEDIA_URL or '/media/'
        except Exception:
            media_url = '/media/'

        allowed_prefixes.append(static_url)
        allowed_prefixes.append(media_url)

        # Allow any path that starts with an allowed prefix
        for prefix in allowed_prefixes:
            if prefix and request.path.startswith(prefix):
                return None

        # If user is a superuser, allow everything
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser:
            return None

        # If user is not authenticated, only allow the welcome/login/register pages
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            # If request is for a path not in allowed_prefixes, send to welcome
            return redirect('welcome')

        # If we reach here the user is authenticated but not a superuser.
        
        # Superuser-only paths - redirect non-superusers
        superuser_only_paths = ['/users/']
        if any(request.path.startswith(path) for path in superuser_only_paths):
            return redirect('welcome')
        
        # Check if user has an approved profile for accessing main application areas
        protected_prefixes = [
            '/dashboard/',
            '/tasks/',
            '/task-',
            '/issues/',
            '/issue',
            '/statistics/',
            '/profile/',
            '/export-',
            '/import-',
            '/cr/',  # Change Request URLs
        ]
        
        # Check if path matches protected areas that require approval
        path_requires_approval = any(
            request.path.startswith(prefix) for prefix in protected_prefixes
        )
        
        if path_requires_approval:
            try:
                profile = request.user.profile
                if profile.is_approved:
                    return None  # Allow access for approved users
            except Exception:
                pass
            # If not approved, redirect to pending-approval page
            return redirect('pending-approval')

        # For other non-whitelisted paths, redirect to welcome
        return redirect('welcome')


class ActivityLogMiddleware(MiddlewareMixin):
    """
    Middleware to log user activities
    """
    
    def process_request(self, request):
        """Log user activities"""
        
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'DELETE']:
            # Log significant activities
            activity_data = {
                'user': request.user.username,
                'ip': self.get_client_ip(request),
                'method': request.method,
                'path': request.path,
                'timestamp': timezone.now(),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
            
            # Log different types of activities
            if '/issue-create' in request.path:
                logger.info(f"User {request.user.username} created a new issue from IP {activity_data['ip']}")
            elif '/issue-update' in request.path:
                logger.info(f"User {request.user.username} updated an issue from IP {activity_data['ip']}")
            elif '/issue-delete' in request.path:
                logger.warning(f"User {request.user.username} deleted an issue from IP {activity_data['ip']}")
            elif '/export-issues' in request.path:
                logger.info(f"User {request.user.username} exported issues from IP {activity_data['ip']}")
            elif '/import-issues' in request.path:
                logger.info(f"User {request.user.username} imported issues from IP {activity_data['ip']}")
        
        return None
    
    def get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware to handle session timeout
    """
    
    def process_request(self, request):
        """Check for session timeout"""
        
        if request.user.is_authenticated:
            # Check if session is expired
            if '_session_expiry' in request.session:
                expiry_value = request.session['_session_expiry']
                current_ts = int(timezone.now().timestamp())

                # Support legacy values that might be datetime or ISO strings
                expiry_ts = None
                if isinstance(expiry_value, (int, float)):
                    expiry_ts = int(expiry_value)
                else:
                    try:
                        # Try to parse ISO string
                        from datetime import datetime as _dt
                        if isinstance(expiry_value, str):
                            parsed = _dt.fromisoformat(expiry_value)
                        else:
                            # If it's a datetime object
                            parsed = expiry_value
                        # Make naive datetimes aware in current timezone
                        if hasattr(parsed, 'tzinfo') and parsed.tzinfo is None:
                            parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
                        expiry_ts = int(parsed.timestamp())
                    except Exception:
                        # Fallback: force re-login if value is invalid
                        expiry_ts = 0

                if current_ts > expiry_ts:
                    # Session expired, logout user
                    from django.contrib.auth import logout
                    logout(request)
                    messages.warning(request, 'Your session has expired. Please login again.')
                    return redirect('login')
            
            # Update session expiry time (store as Unix timestamp to avoid JSON serialization issues)
            request.session['_session_expiry'] = int(timezone.now().timestamp()) + int(8 * 60 * 60)
        
        return None


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware for audit logging
    """
    
    def process_request(self, request):
        """Log audit information"""
        
        if request.user.is_authenticated:
            # Store request information for audit
            request.audit_info = {
                'user': request.user.username,
                'ip': self.get_client_ip(request),
                'timestamp': timezone.now(),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'path': request.path,
                'method': request.method,
            }
        
        return None
    
    def get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
