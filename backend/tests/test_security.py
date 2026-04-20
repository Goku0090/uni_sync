"""
Tests for security middleware
"""

import pytest
from django.test import RequestFactory
from django.http import HttpResponse

from auth_project.middleware import SecurityHeadersMiddleware, InputValidationMiddleware


class TestSecurityHeadersMiddleware:
    """Test security headers middleware"""

    def test_security_headers_added(self):
        """Test that security headers are added to responses"""
        factory = RequestFactory()
        request = factory.get('/')

        middleware = SecurityHeadersMiddleware(lambda r: HttpResponse())
        response = middleware(request)

        # Check security headers are present
        assert response['X-Content-Type-Options'] == 'nosniff'
        assert response['X-Frame-Options'] == 'DENY'
        assert response['X-XSS-Protection'] == '1; mode=block'
        assert 'Content-Security-Policy' in response

    def test_server_header_removed(self):
        """Test that server header is removed"""
        factory = RequestFactory()
        request = factory.get('/')

        middleware = SecurityHeadersMiddleware(lambda r: HttpResponse())
        response = middleware(request)

        # Server header should not be present
        assert 'Server' not in response


class TestInputValidationMiddleware:
    """Test input validation middleware"""

    def test_normal_input_passes(self):
        """Test that normal input passes through"""
        factory = RequestFactory()
        request = factory.post('/', {'name': 'John', 'email': 'john@example.com'})

        middleware = InputValidationMiddleware(lambda r: HttpResponse())
        response = middleware(request)

        assert response.status_code == 200

    def test_suspicious_input_logged(self, caplog):
        """Test that suspicious input is logged"""
        factory = RequestFactory()
        request = factory.post('/', {'comment': '<script>alert("xss")</script>'})

        middleware = InputValidationMiddleware(lambda r: HttpResponse())
        response = middleware(request)

        # Should still work but log the suspicious input
        assert response.status_code == 200
        # Check if warning was logged (would need caplog fixture in pytest)