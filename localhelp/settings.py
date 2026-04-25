"""
settings.py - Django project configuration for LocalHelp
This file controls all major settings like database, installed apps, templates etc.
"""

import os
from pathlib import Path

# BASE_DIR is the root folder of the entire project
# Path(__file__) = this settings.py file
# .resolve() = get the absolute path
# .parent.parent = go up two levels to reach the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY is used by Django for security (sessions, CSRF tokens etc.)
# In production this should be a long random string stored in environment variables
# For development/learning, this hardcoded value is fine
SECRET_KEY = 'django-insecure-localhelp-secret-key-for-development-only-change-in-production'

# DEBUG=True means Django will show detailed error pages when something breaks
# NEVER set DEBUG=True in production — it exposes your code to the world
DEBUG = True

# ALLOWED_HOSTS controls which domain names can access this app
# Empty list in DEBUG mode means only localhost is allowed
ALLOWED_HOSTS = ['*']

# INSTALLED_APPS tells Django which apps are active in this project
# Django has several built-in apps, plus we add our own 'core' app
INSTALLED_APPS = [
    'django.contrib.admin',        # Admin interface at /admin/
    'django.contrib.auth',         # Built-in user login/logout/registration system
    'django.contrib.contenttypes', # Required by other apps
    'django.contrib.sessions',     # Handles user sessions (keeps users logged in)
    'django.contrib.messages',     # Flash messages (like "Task created successfully!")
    'django.contrib.staticfiles',  # Serves CSS, JS, images in development
    'core',                        # Our custom app with all the LocalHelp logic
]

# MIDDLEWARE is a list of "filters" that every request/response passes through
# Think of it like layers of an onion — request goes in, response comes out
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Enables sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',             # Protects against CSRF attacks
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Attaches user to request
    'django.contrib.messages.middleware.MessageMiddleware',   # Enables flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ROOT_URLCONF tells Django where to find the main URL patterns file
ROOT_URLCONF = 'localhelp.urls'

# TEMPLATES controls how Django finds and renders HTML template files
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS: list of folders where Django looks for templates first
        # We have a global 'templates' folder at the project root
        'DIRS': [BASE_DIR / 'templates'],
        # APP_DIRS=True: also look for templates inside each app's 'templates' folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Adds 'request' to templates
                'django.contrib.auth.context_processors.auth', # Adds 'user' to templates
                'django.contrib.messages.context_processors.messages', # Adds 'messages' to templates
            ],
        },
    },
]

# WSGI_APPLICATION points to the WSGI entry point for production servers
WSGI_APPLICATION = 'localhelp.wsgi.application'

# DATABASES configures which database to use
# We're using SQLite — it's a single file, perfect for learning and small projects
# No installation needed, Django creates the file automatically
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # The database file will be created at BASE_DIR/db.sqlite3
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# AUTH_PASSWORD_VALIDATORS enforces password strength rules
# We're keeping the defaults which require minimum 8 characters etc.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Language and timezone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'     # Store all times in UTC — safest practice
USE_I18N = True       # Enable translations (not used but good to have)
USE_TZ = True         # Make Django timezone-aware

# STATIC_URL is the URL prefix for static files (CSS, JS, images)
# When you write {% static 'css/style.css' %} in a template,
# Django will serve it from /static/css/style.css
STATIC_URL = 'static/'

# STATICFILES_DIRS tells Django where to find static files in development
STATICFILES_DIRS = [BASE_DIR / 'static']

# DEFAULT_AUTO_FIELD sets the type of auto-generated primary key for models
# BigAutoField = 64-bit integer (can handle billions of records)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LOGIN_URL: Where Django redirects when @login_required fails
# We point to our custom login page
LOGIN_URL = '/login/'

# LOGIN_REDIRECT_URL: Where to go after successful login
LOGIN_REDIRECT_URL = '/dashboard/'
