#!/usr/bin/env python
"""
Test runner for UniSinq
Run comprehensive tests for the application
"""

import os
import sys
import subprocess
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')

def run_django_tests():
    """Run Django's built-in test suite"""
    print("🧪 Running Django tests...")
    result = subprocess.run([
        sys.executable, 'manage.py', 'test',
        '--verbosity=2',
        '--keepdb'  # Keep test database for faster runs
    ], cwd=backend_dir)

    return result.returncode == 0

def run_pytest():
    """Run pytest for additional tests"""
    print("🧪 Running pytest tests...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            '--tb=short',
            '--cov=accounts',
            '--cov=auth_project',
            '--cov-report=term-missing'
        ], cwd=backend_dir)

        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️  pytest not installed, skipping pytest tests")
        return True

def run_security_tests():
    """Run security-focused tests"""
    print("🔒 Running security tests...")
    # Check for common security issues
    issues = []

    # Check for DEBUG=True in production
    if os.getenv('DEBUG', 'False').lower() in ('true', '1', 't', 'yes'):
        if not os.getenv('RENDER'):  # Only warn if not in development
            issues.append("DEBUG is set to True")

    # Check for missing SECRET_KEY
    if not os.getenv('SECRET_KEY'):
        issues.append("SECRET_KEY environment variable not set")

    if issues:
        print("❌ Security issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False

    print("✅ No security issues found")
    return True

def main():
    """Main test runner"""
    print("🚀 UniSinq Test Suite")
    print("=" * 50)

    # Change to backend directory
    os.chdir(backend_dir)

    results = []

    # Run security checks first
    results.append(("Security Tests", run_security_tests()))

    # Run Django tests
    results.append(("Django Tests", run_django_tests()))

    # Run pytest tests
    results.append(("Pytest Tests", run_pytest()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())