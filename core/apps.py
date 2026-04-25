"""
core/apps.py - App configuration for the 'core' app.
Django uses this to identify and configure the app.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    # The type of auto-generated primary key for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    # The name of the app — must match the folder name
    name = 'core'
