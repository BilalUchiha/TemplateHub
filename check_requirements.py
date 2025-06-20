#!/usr/bin/env python3
"""
TemplateHub Requirements Checker
Verifies that all required packages are installed and working correctly.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed and can be imported."""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"✅ {package_name} ({version})")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def check_django_setup():
    """Check if Django is properly configured."""
    print("\n🔧 Checking Django setup...")
    try:
        import django
        from django.conf import settings
        from django.core.management import execute_from_command_line
        
        # Try to import our Django project
        import templatehub.settings
        print("✅ Django project configuration found")
        
        # Check if we can run Django commands
        try:
            from django.core.management import call_command
            print("✅ Django management commands available")
        except Exception as e:
            print(f"⚠️  Django management issue: {e}")
        
        return True
    except ImportError as e:
        print(f"❌ Django setup issue: {e}")
        return False

def check_database():
    """Check database connectivity."""
    print("\n🗄️  Checking database...")
    try:
        import django
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # This will fail if database is not accessible
        cursor = connection.cursor()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Database issue (may need migration): {e}")
        return False

def main():
    """Main requirements checker."""
    print("🔍 TemplateHub Requirements Checker")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Checking Core Packages...")
    
    # Core packages
    core_packages = [
        ('django', 'django'),
        ('pillow', 'PIL'),
        ('crispy_forms', 'crispy_forms'),
        ('crispy_bootstrap4', 'crispy_bootstrap4'),
    ]
    
    all_good = True
    for package_name, import_name in core_packages:
        if not check_package(package_name, import_name):
            all_good = False
    
    # Check Django setup
    if all_good:
        django_ok = check_django_setup()
        if not django_ok:
            all_good = False
    
    # Check database (optional)
    if all_good:
        check_database()
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All core requirements are satisfied!")
        print("\n📋 Next steps:")
        print("1. Run: python manage.py migrate")
        print("2. Run: python manage.py createsuperuser")
        print("3. Run: python manage.py runserver")
    else:
        print("❌ Some requirements are missing!")
        print("\n🔧 To fix:")
        print("1. Activate your virtual environment")
        print("2. Run: pip install -r requirements-minimal.txt")
        print("3. Run this checker again")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
