"""
localhelp/urls.py - The MAIN URL router for the entire project.

Every URL the user visits passes through here first.
Django matches the URL against each pattern in urlpatterns top-to-bottom.
When a match is found, it delegates to the corresponding view or sub-router.

URL pattern syntax:
  path('some/url/', view_function)
  <int:pk> = captures an integer from the URL and passes it as 'pk' to the view
  <str:name> = captures a string
"""

from django.contrib import admin
from django.urls import path, include  # include() lets us point to another urls.py

urlpatterns = [
    # Django admin panel — useful for debugging, access at /admin/
    path('admin/', admin.site.urls),

    # All our app URLs are defined in core/urls.py
    # include('core.urls') means: for ANY URL, check core/urls.py for a match
    # The empty string '' means no prefix — URLs start directly from the root
    path('', include('core.urls')),
]
