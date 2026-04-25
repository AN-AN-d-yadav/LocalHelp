"""
core/admin.py - Register models with Django's admin interface.

After running the server, visit /admin/ (login with superuser credentials)
to view and manage all database records directly — very useful for debugging!

Command to create a superuser:
  python manage.py createsuperuser
"""

from django.contrib import admin
from .models import UserProfile, Task, Rating

# Register models with the admin — this makes them appear at /admin/
admin.site.register(UserProfile)
admin.site.register(Task)
admin.site.register(Rating)
