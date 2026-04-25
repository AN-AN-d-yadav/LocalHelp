"""
localhelp/wsgi.py - WSGI entry point for production web servers.
You don't need to change this file. It's used when deploying to production.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localhelp.settings')
application = get_wsgi_application()
