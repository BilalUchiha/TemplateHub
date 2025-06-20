# TemplateHub Requirements Guide

This document explains the different requirements files and how to use them for different environments.

## 📁 Requirements Files Overview

### 1. `requirements.txt` - Complete Package List
- **Purpose**: Comprehensive list with all possible dependencies
- **Use Case**: Reference for all available packages
- **Contains**: Core + Optional packages (commented out)

### 2. `requirements-minimal.txt` - Essential Only
- **Purpose**: Minimal dependencies for basic functionality
- **Use Case**: Quick setup, testing, or resource-constrained environments
- **Contains**: Django + Crispy Forms + Pillow + Core dependencies

### 3. `requirements-dev.txt` - Development Environment
- **Purpose**: Development tools and testing frameworks
- **Use Case**: Local development, testing, debugging
- **Contains**: Minimal + Debug tools + Testing + Code quality tools

### 4. `requirements-prod.txt` - Production Environment
- **Purpose**: Production-ready deployment
- **Use Case**: Live server deployment
- **Contains**: Minimal + Production server + Database + Monitoring

## 🚀 Quick Start Guide

### For Basic Usage (Minimal Setup)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install minimal requirements
pip install -r requirements-minimal.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### For Development
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install development requirements
pip install -r requirements-dev.txt

# Run migrations
python manage.py migrate

# Create sample data
python manage.py create_categories
python manage.py create_sample_templates

# Run tests
pytest

# Start development server
python manage.py runserver
```

### For Production
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install production requirements
pip install -r requirements-prod.txt

# Set environment variables
export DEBUG=False
export SECRET_KEY=your-secret-key
export DATABASE_URL=postgres://user:pass@localhost/dbname

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser

# Start with Gunicorn
gunicorn templatehub.wsgi:application
```

## 📦 Core Dependencies Explained

### Essential Packages (in all requirements)
- **Django==5.0.1**: Main web framework
- **django-crispy-forms==2.1**: Enhanced form rendering
- **crispy-bootstrap4==2023.1**: Bootstrap 4 integration for forms
- **Pillow==11.0.0**: Image processing for template previews and avatars

### Development Packages (requirements-dev.txt)
- **django-debug-toolbar**: SQL query debugging and performance analysis
- **pytest**: Modern testing framework
- **black**: Code formatting
- **flake8**: Code linting

### Production Packages (requirements-prod.txt)
- **gunicorn**: WSGI HTTP Server for production
- **psycopg2-binary**: PostgreSQL database adapter
- **whitenoise**: Static file serving
- **sentry-sdk**: Error tracking and monitoring

## 🔧 Environment-Specific Setup

### Development Environment
```bash
pip install -r requirements-dev.txt
export DEBUG=True
export SECRET_KEY=dev-secret-key
python manage.py runserver
```

### Testing Environment
```bash
pip install -r requirements-dev.txt
pytest
coverage run -m pytest
coverage report
```

### Production Environment
```bash
pip install -r requirements-prod.txt
export DEBUG=False
export SECRET_KEY=production-secret-key
export DATABASE_URL=postgres://...
gunicorn templatehub.wsgi:application
```

## 🗄️ Database Options

### SQLite (Default - Development)
- No additional packages needed
- Included with Django
- Good for development and testing

### PostgreSQL (Recommended for Production)
```bash
# Add to requirements
psycopg2-binary==2.9.9

# Environment variable
DATABASE_URL=postgres://user:password@localhost:5432/templatehub
```

### MySQL
```bash
# Add to requirements
mysqlclient==2.2.4

# Environment variable
DATABASE_URL=mysql://user:password@localhost:3306/templatehub
```

## 🚀 Deployment Options

### Local Development
- Use `requirements-minimal.txt` or `requirements-dev.txt`
- SQLite database
- Django development server

### Production Server
- Use `requirements-prod.txt`
- PostgreSQL/MySQL database
- Gunicorn + Nginx
- Environment variables for configuration

### Docker Deployment
```dockerfile
FROM python:3.11
COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt
# ... rest of Dockerfile
```

### Cloud Deployment (Heroku, AWS, etc.)
- Use `requirements-prod.txt`
- Configure environment variables
- Set up database and static file storage

## 🔍 Troubleshooting

### Common Issues

1. **Pillow Installation Issues**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install libjpeg-dev zlib1g-dev
   
   # On macOS
   brew install libjpeg
   ```

2. **PostgreSQL Issues**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install libpq-dev
   
   # On macOS
   brew install postgresql
   ```

3. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-minimal.txt
   ```

## 📝 Notes

- Always use virtual environments to avoid package conflicts
- Update package versions regularly for security patches
- Test thoroughly when upgrading Django versions
- Keep production and development requirements in sync
- Use environment variables for sensitive configuration

## 🆘 Support

If you encounter issues with package installation:
1. Check Python version (3.8+ required)
2. Ensure virtual environment is activated
3. Update pip: `pip install --upgrade pip`
4. Check system dependencies for packages like Pillow and psycopg2
