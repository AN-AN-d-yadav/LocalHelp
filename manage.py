#!/usr/bin/env python
"""
manage.py - Django's command-line utility for administrative tasks.

This is the file you run directly. Examples:
  python manage.py runserver         → Start the development server
  python manage.py makemigrations    → Create database migration files
  python manage.py migrate           → Apply migrations to the database
  python manage.py createsuperuser   → Create an admin user
  python manage.py shell             → Open a Python shell with Django loaded
"""
import os
import sys


def main():
    """Run administrative tasks."""
    # Tell Django which settings file to use
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localhelp.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Pass command-line arguments to Django's management system
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
