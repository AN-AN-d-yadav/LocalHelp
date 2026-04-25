"""
core/migrations/0001_initial.py - Initial database migration.

Django migrations describe changes to the database schema.
This file creates the three tables: UserProfile, Task, Rating.

How migrations work:
  1. You define/change a model in models.py
  2. Run: python manage.py makemigrations   → creates this file
  3. Run: python manage.py migrate          → applies this file to the database

You can also run these two commands on a fresh project to generate & apply them.
This file is included for reference — you still need to run 'python manage.py migrate'.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    # initial=True means this is the first migration for this app
    initial = True

    # dependencies: other migrations that must run before this one
    dependencies = [
        # We depend on Django's built-in auth system (for the User model)
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    # operations: list of database changes to apply
    operations = [

        # ===== Create UserProfile table =====
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_role', models.CharField(
                    choices=[('requester', 'Requester'), ('helper', 'Helper')],
                    default='requester',
                    max_length=20
                )),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('trust_score', models.FloatField(default=0.0)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='userprofile',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
        ),

        # ===== Create Task table =====
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('status', models.CharField(
                    choices=[
                        ('CREATED', 'Created'),
                        ('OPEN', 'Open'),
                        ('ACCEPTED', 'Accepted'),
                        ('COMPLETION_REQUESTED', 'Completion Requested'),
                        ('COMPLETED', 'Completed'),
                        ('CANCELLED', 'Cancelled'),
                        ('EXPIRED', 'Expired'),
                    ],
                    default='OPEN',
                    max_length=30
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('cancel_reason', models.TextField(blank=True, default='')),
                ('requester', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tasks_as_requester',
                    to=settings.AUTH_USER_MODEL
                )),
                ('helper', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='tasks_as_helper',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
        ),

        # ===== Create Rating table =====
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('comment', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ratings',
                    to='core.task'
                )),
                ('rater', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ratings_given',
                    to=settings.AUTH_USER_MODEL
                )),
                ('ratee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ratings_received',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
    ]
