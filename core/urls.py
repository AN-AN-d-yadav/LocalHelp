"""
core/urls.py - URL patterns for the LocalHelp core app.

Each path() connects a URL pattern to a view function.
The 'name' parameter gives each URL a name so we can use
{% url 'name' %} in templates instead of hardcoding paths.

URL patterns:
  /                          → homepage
  /register/                 → registration
  /login/                    → login
  /logout/                   → logout
  /role/                     → role selection
  /dashboard/                → main dashboard (role-based)
  /task/create/              → create a new task
  /task/<id>/                → task detail page
  /task/<id>/accept/         → helper accepts task
  /task/<id>/complete/       → helper requests completion
  /task/<id>/approve/        → requester approves completion
  /task/<id>/cancel/         → cancel a task
  /task/<id>/rate/           → rate the other user after completion
  /profile/<username>/       → view a user's profile
"""

from django.urls import path
from . import views  # Import all view functions from views.py

urlpatterns = [
    # --- Authentication URLs ---
    path('', views.view_home, name='home'),                     # Homepage
    path('register/', views.view_register, name='register'),    # Register
    path('login/', views.view_login, name='login'),             # Login
    path('logout/', views.view_logout, name='logout'),          # Logout

    # --- Role & Dashboard URLs ---
    path('role/', views.view_select_role, name='select_role'),  # Choose role
    path('dashboard/', views.view_dashboard, name='dashboard'), # Main dashboard

    # --- Task URLs ---
    # Create task form
    path('task/create/', views.view_create_task, name='create_task'),

    # Task detail — <int:task_id> captures the task ID from the URL
    # Example: /task/5/ → task_id=5
    path('task/<int:task_id>/', views.view_task_detail, name='task_detail'),

    # Helper actions on a task
    path('task/<int:task_id>/accept/', views.view_accept_task, name='accept_task'),
    path('task/<int:task_id>/complete/', views.view_request_completion, name='request_completion'),

    # Requester actions on a task
    path('task/<int:task_id>/approve/', views.view_approve_completion, name='approve_completion'),

    # Either party can cancel
    path('task/<int:task_id>/cancel/', views.view_cancel_task, name='cancel_task'),

    # Rating
    path('task/<int:task_id>/rate/', views.view_rate_user, name='rate_user'),

    # --- Profile URLs ---
    # <str:username> captures the username from the URL
    # Example: /profile/john_doe/ → username='john_doe'
    path('profile/<str:username>/', views.view_profile, name='profile'),

 
]
