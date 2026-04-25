"""
core/models.py - Database models for LocalHelp.

A Django model is a Python class that maps to a database table.
Each attribute of the class is a column in the table.
Django automatically creates the SQL to create/update these tables via migrations.

Tables we define here:
  1. UserProfile  → extends Django's built-in User with role, location, trust score
  2. Task         → the core entity connecting requesters and helpers
  3. Rating       → feedback after a task is completed
"""

from django.db import models
from django.contrib.auth.models import User  # Django's built-in User model


# ==============================================================================
# 1. UserProfile Model
# ==============================================================================

class UserProfile(models.Model):
    """
    Extends Django's built-in User model with LocalHelp-specific data.

    Django's User already has: username, password, email, first_name, last_name
    We add: active_role, latitude, longitude, trust_score

    OneToOneField means: one User has exactly one UserProfile, and vice versa.
    This is like adding extra columns to the User table without modifying it directly.
    """

    # Link to Django's built-in User
    # on_delete=CASCADE means: if the User is deleted, delete this profile too
    # related_name='userprofile' means: from a User object, access this as user.userprofile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')

    # The role this user is currently acting as
    # ROLE_CHOICES restricts the value to only 'requester' or 'helper'
    ROLE_CHOICES = [
        ('requester', 'Requester'),  # (stored_value, display_label)
        ('helper', 'Helper'),
    ]
    active_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='requester'  # New users start as Requester
    )

    # Location fields — stored as decimal degrees (e.g., 28.6139 for New Delhi latitude)
    # blank=True, null=True means these fields are optional (can be empty)
    latitude = models.DecimalField(
        max_digits=9,   # Total digits (e.g., 28.123456 = 8 digits)
        decimal_places=6,  # Digits after decimal point
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    # trust_score: average of all ratings received (1.0 to 5.0)
    # Starts at 0.0 (no ratings yet)
    # FloatField stores a floating-point number like 3.75
    trust_score = models.FloatField(default=0.0)

    def __str__(self):
        """
        __str__ controls what string represents this object.
        Used in Django admin and when printing the object.
        """
        return f"{self.user.username} ({self.active_role})"


# ==============================================================================
# 2. Task Model
# ==============================================================================

class Task(models.Model):
    """
    Represents a task posted by a Requester that a Helper can accept.

    Status flow (STRICT — only these transitions are allowed):
      CREATED → OPEN
      OPEN → ACCEPTED (helper accepts)
      OPEN → EXPIRED  (30 minutes passed, no helper accepted)
      OPEN → CANCELLED (requester cancelled before anyone accepted)
      ACCEPTED → COMPLETION_REQUESTED (helper says "I'm done")
      COMPLETION_REQUESTED → COMPLETED (requester confirms)
      ACCEPTED → CANCELLED (either party cancels after acceptance)
    """

    # All possible status values for a task
    STATUS_CHOICES = [
        ('CREATED', 'Created'),                             # Just created, not yet visible
        ('OPEN', 'Open'),                                   # Visible to helpers
        ('ACCEPTED', 'Accepted'),                          # A helper has taken it
        ('COMPLETION_REQUESTED', 'Completion Requested'), # Helper says done, waiting for requester
        ('COMPLETED', 'Completed'),                        # Requester confirmed, done!
        ('CANCELLED', 'Cancelled'),                        # Cancelled by either party
        ('EXPIRED', 'Expired'),                            # Nobody accepted within 30 minutes
    ]

    # ForeignKey means "many Tasks can belong to one User"
    # related_name='tasks_as_requester' → access as user.tasks_as_requester.all()
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks_as_requester'
    )

    # Helper is nullable (null=True) because no helper is assigned initially
    # blank=True means the form doesn't require this field
    helper = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # If helper account deleted, don't delete the task
        null=True,
        blank=True,
        related_name='tasks_as_helper'
    )

    # Task details
    title = models.CharField(max_length=200)  # Short title, max 200 characters
    description = models.TextField()          # Longer text, no length limit
    payment_amount = models.DecimalField(
        max_digits=8,      # Up to 99999.99
        decimal_places=2   # Always 2 decimal places (like money)
    )

    # Location where the task needs to be done
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Current status of the task
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='OPEN'  # Tasks start as OPEN immediately (skip CREATED for simplicity)
    )

    # Timestamps — auto_now_add=True means Django fills this in automatically when created
    created_at = models.DateTimeField(auto_now_add=True)

    # accepted_at and completed_at are set manually in the view logic
    # null=True, blank=True because they start empty and are filled in later
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Optional cancellation reason (filled in when task is cancelled)
    cancel_reason = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Task: {self.title} [{self.status}]"


# ==============================================================================
# 3. Rating Model
# ==============================================================================

class Rating(models.Model):
    """
    A rating given by one user (rater) to another (ratee) after a task is completed.

    Rules enforced in views:
      - Only allowed when task.status == 'COMPLETED'
      - Cannot rate yourself
      - Cannot rate twice for the same task
      - Rating must be between 1 and 5
    """

    # Which task this rating is for
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='ratings')

    # Who is giving the rating
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')

    # Who is receiving the rating
    ratee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')

    # The actual score (1 to 5 stars)
    # IntegerField stores whole numbers
    rating = models.IntegerField()

    # Optional text comment with the rating
    comment = models.TextField(blank=True, default='')

    # Timestamp for when the rating was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rater.username} rated {self.ratee.username}: {self.rating}/5 (Task: {self.task.title})"
