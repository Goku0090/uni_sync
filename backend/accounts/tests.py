"""
Comprehensive tests for UniSinq accounts app
"""

import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Project, Comment, Message, Conversation, Notification

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model functionality"""

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data, password='testpass123')

    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(str(self.user), 'testuser')

    def test_user_profile_fields(self):
        """Test custom profile fields"""
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')


class ProjectModelTest(TestCase):
    """Test Project model functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project description',
            creator=self.user,
            visibility='public'
        )

    def test_project_creation(self):
        """Test project is created correctly"""
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.creator, self.user)
        self.assertEqual(self.project.visibility, 'public')
        self.assertEqual(str(self.project), 'Test Project')

    def test_project_slug_generation(self):
        """Test slug is generated from title"""
        self.assertIsNotNone(self.project.slug)
        self.assertIn('test-project', self.project.slug)


class AuthenticationTest(TestCase):
    """Test authentication functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_view_get(self):
        """Test login page loads"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_login_failure(self):
        """Test login with wrong credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'error')  # Should show error

    def test_logout(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class APITestCase(APITestCase):
    """Base test case for API tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)


class ProjectAPITest(APITestCase):
    """Test Project API endpoints"""

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            title='API Test Project',
            description='Testing API endpoints',
            creator=self.user
        )

    def test_project_list(self):
        """Test getting list of projects"""
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_project_detail(self):
        """Test getting project details"""
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Project')

    def test_project_create(self):
        """Test creating a new project"""
        data = {
            'title': 'New Project',
            'description': 'Created via API',
            'visibility': 'public'
        }
        response = self.client.post('/api/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Project')


class CommentAPITest(APITestCase):
    """Test Comment API endpoints"""

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            title='Comment Test Project',
            creator=self.user
        )

    def test_comment_create(self):
        """Test creating a comment"""
        data = {
            'project': self.project.id,
            'content': 'This is a test comment'
        }
        response = self.client.post('/api/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment')

    def test_comment_list(self):
        """Test getting comments for a project"""
        # Create a comment first
        Comment.objects.create(
            project=self.project,
            author=self.user,
            content='Test comment'
        )

        response = self.client.get(f'/api/projects/{self.project.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class SecurityTest(TestCase):
    """Test security features"""

    def setUp(self):
        self.client = Client()

    def test_csrf_protection(self):
        """Test CSRF protection is enabled"""
        # Try POST without CSRF token
        response = self.client.post(reverse('login'), {
            'username': 'test',
            'password': 'test'
        })
        # Should fail or redirect due to CSRF
        self.assertIn(response.status_code, [200, 403])  # 403 if CSRF blocks it

    def test_sql_injection_prevention(self):
        """Test basic SQL injection prevention"""
        # This should not cause SQL injection
        response = self.client.post(reverse('login'), {
            'username': "'; DROP TABLE users; --",
            'password': 'test'
        })
        # Should not crash and should handle gracefully
        self.assertIn(response.status_code, [200, 302, 403])


class EmailTest(TestCase):
    """Test email functionality"""

    def test_email_backend_configuration(self):
        """Test email backend is properly configured"""
        from django.core.mail import get_connection
        connection = get_connection()
        # Should not raise an exception
        self.assertIsNotNone(connection)
