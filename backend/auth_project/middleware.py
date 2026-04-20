"""
Security middleware for UniSinq
Adds security headers and protections
"""

from django.conf import settings
from django.http import HttpResponse


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy
        csp_parts = []

        # Default sources
        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            csp_parts.append(f"default-src {' '.join(settings.CSP_DEFAULT_SRC)}")

        # Style sources
        if hasattr(settings, 'CSP_STYLE_SRC'):
            csp_parts.append(f"style-src {' '.join(settings.CSP_STYLE_SRC)}")

        # Script sources
        if hasattr(settings, 'CSP_SCRIPT_SRC'):
            csp_parts.append(f"script-src {' '.join(settings.CSP_SCRIPT_SRC)}")

        # Font sources
        if hasattr(settings, 'CSP_FONT_SRC'):
            csp_parts.append(f"font-src {' '.join(settings.CSP_FONT_SRC)}")

        # Image sources
        if hasattr(settings, 'CSP_IMG_SRC'):
            csp_parts.append(f"img-src {' '.join(settings.CSP_IMG_SRC)}")

        # Connect sources (for WebSockets, AJAX)
        if hasattr(settings, 'CSP_CONNECT_SRC'):
            csp_parts.append(f"connect-src {' '.join(settings.CSP_CONNECT_SRC)}")

        if csp_parts:
            response['Content-Security-Policy'] = '; '.join(csp_parts)

        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = getattr(settings, 'SECURE_REFERRER_POLICY', 'strict-origin-when-cross-origin')
        response['Cross-Origin-Opener-Policy'] = getattr(settings, 'SECURE_CROSS_ORIGIN_OPENER_POLICY', 'same-origin')

        # Remove server header for security
        if 'Server' in response:
            del response['Server']

        return response


class InputValidationMiddleware:
    """
    Middleware to validate and sanitize input data
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Basic input validation for common attack vectors
        if request.method in ['POST', 'PUT', 'PATCH']:
            self._validate_input(request)

        response = self.get_response(request)
        return response

    def _validate_input(self, request):
        """
        Basic input validation to prevent common attacks
        """
        # Check for suspicious patterns in POST data
        dangerous_patterns = [
            '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            'eval(', 'alert(', 'document.cookie', 'document.location'
        ]

        def check_value(value):
            if isinstance(value, str):
                value_lower = value.lower()
                for pattern in dangerous_patterns:
                    if pattern in value_lower:
                        # Log suspicious input (in production, you might want to block)
                        print(f"[SECURITY WARNING] Suspicious input detected: {pattern}")
                        break
            elif isinstance(value, (list, tuple)):
                for item in value:
                    check_value(item)
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(k)
                    check_value(v)

        # Check POST data
        if hasattr(request, 'POST') and request.POST:
            for key, value in request.POST.items():
                check_value(key)
                check_value(value)

        # Check GET data
        if hasattr(request, 'GET') and request.GET:
            for key, value in request.GET.items():
                check_value(key)
                check_value(value)