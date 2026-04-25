
from django.shortcuts import render, redirect, get_object_or_404
# render()              → renders a template and returns an HttpResponse
# redirect()            → sends the user to a different URL
# get_object_or_404()   → gets a DB object or shows 404 error if not found

from django.contrib.auth import login, logout, authenticate
# login()         → logs in a user (creates session)
# logout()        → logs out a user (destroys session)
# authenticate()  → checks username/password, returns User or None

from django.contrib.auth.models import User
# Django's built-in User model

from django.contrib import messages
# messages.success(request, "text") → shows a green success message
# messages.error(request, "text")   → shows a red error message

from django.utils import timezone
# timezone.now() → current datetime, timezone-aware

from datetime import timedelta
# timedelta(minutes=30) → a "duration" of 30 minutes

from .models import UserProfile, Task, Rating
# Import our own models from models.py


# ==============================================================================
# HELPER FUNCTION: Role Check
# ==============================================================================

def user_has_role(request, required_role):
    """
    Check if the currently logged-in user has the required role.

    Returns True if the user is logged in AND their active_role matches required_role.
    Returns False otherwise.

    Usage in a view:
        if not user_has_role(request, 'helper'):
            messages.error(request, "You must be a Helper to do this.")
            return redirect('dashboard')
    """
    # First check: is the user even logged in?
    if not request.user.is_authenticated:
        return False

    # Second check: does the user have a UserProfile?
    # hasattr checks if the attribute exists without raising an error
    if not hasattr(request.user, 'userprofile'):
        return False

    # Third check: does their active_role match what we need?
    return request.user.userprofile.active_role == required_role


# ==============================================================================
# HELPER FUNCTION: Mark Expired Tasks
# ==============================================================================

def mark_expired_tasks():
    """
    Finds all OPEN tasks older than 30 minutes and marks them as EXPIRED.

    This is called at the start of the helper's open-task listing view.
    We run it "on demand" instead of using background jobs (Celery, cron).

    Logic:
      1. Get current time
      2. Calculate the cutoff time (now - 30 minutes)
      3. Find all OPEN tasks created BEFORE the cutoff
      4. Set their status to EXPIRED and save
    """
    # Get the current time (timezone-aware)
    now = timezone.now()

    # Calculate what time was 30 minutes ago
    # timedelta represents a duration, subtracting it from 'now' gives us the cutoff
    expiry_cutoff = now - timedelta(minutes=30)

    # Find all OPEN tasks that were created before the cutoff time
    # __lt = "less than" (created_at < expiry_cutoff means older than 30 minutes)
    expired_tasks = Task.objects.filter(
        status='OPEN',
        created_at__lt=expiry_cutoff
    )

    # Loop through each expired task and update its status
    for task in expired_tasks:
        task.status = 'EXPIRED'
        task.save()  # Save changes to the database


# ==============================================================================
# VIEW: Homepage
# ==============================================================================

def view_home(request):
    """
    The homepage at URL: /

    If user is already logged in → redirect to dashboard.
    If not logged in → show the landing page with Login/Register links.
    """
    # If the user is already authenticated (logged in), send them to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Otherwise, show the homepage template
    return render(request, 'core/home.html')


# ==============================================================================
# VIEW: Register
# ==============================================================================

def view_register(request):
    """
    Registration page at URL: /register/

    GET request  → Show the registration form (empty)
    POST request → Process the form, create the user, auto-login, redirect to role selection

    After registration we create:
      1. A Django User (handles authentication)
      2. A UserProfile (handles role, location, trust score)
    """
    # If already logged in, no need to register again
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # POST means the user submitted the form
        # request.POST is a dictionary of form fields

        # Get values from the form
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # --- Validation ---

        # Check if username is provided
        if not username:
            messages.error(request, "Username is required.")
            return render(request, 'core/register.html')

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'core/register.html')

        # Check if password is long enough
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'core/register.html')

        # Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'core/register.html')

        # --- Create the User ---

        # User.objects.create_user() creates a user with a properly hashed password
        # NEVER use User.objects.create() for users — it stores password as plain text!
        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        # --- Create the UserProfile ---

        # Every user needs a profile to store their role, location, trust score
        UserProfile.objects.create(
            user=new_user,
            active_role='requester',  # Default role is Requester
            trust_score=0.0
        )

        # --- Auto-login the new user ---

        # Log them in immediately so they don't have to login again after registering
        login(request, new_user)

        # Show a success message
        messages.success(request, f"Welcome to LocalHelp, {username}! Please choose your role.")

        # Redirect to role selection page
        return redirect('select_role')

    else:
        # GET request — just show the empty registration form
        return render(request, 'core/register.html')


# ==============================================================================
# VIEW: Login
# ==============================================================================

def view_login(request):
    """
    Login page at URL: /login/

    GET  → Show empty login form
    POST → Check credentials, log in if correct, redirect to dashboard
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # authenticate() checks if username+password is correct
        # Returns the User object if valid, or None if invalid
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Credentials are valid — log the user in
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('dashboard')
        else:
            # Invalid credentials
            messages.error(request, "Invalid username or password.")
            return render(request, 'core/login.html')

    else:
        return render(request, 'core/login.html')


# ==============================================================================
# VIEW: Logout
# ==============================================================================

def view_logout(request):
    """    
    Logout at URL: /logout/

    Destroys the session and redirects to homepage.
    Accepts POST only (for security — GET logout can be triggered by image tags etc.)
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


# ==============================================================================
# VIEW: Select Role
# ==============================================================================

def view_select_role(request):
    """
    Role selection page at URL: /role/

    GET  → Show the current role and options to switch
    POST → Update the user's active_role in UserProfile

    Users can switch roles anytime.
    """
    # Must be logged in to select a role
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the user's profile
    profile = request.user.userprofile

    if request.method == 'POST':
        # Get the chosen role from the form
        chosen_role = request.POST.get('role', '')

        # Validate: role must be one of the allowed values
        if chosen_role not in ['requester', 'helper']:
            messages.error(request, "Invalid role selected.")
            return render(request, 'core/select_role.html', {'profile': profile})

        # Update the role in the database
        profile.active_role = chosen_role
        profile.save()  # Save to database

        messages.success(request, f"Role updated to: {chosen_role.capitalize()}")
        return redirect('dashboard')

    else:
        # GET — show current role and let user pick
        return render(request, 'core/select_role.html', {'profile': profile})


# ==============================================================================
# VIEW: Dashboard (role-based)
# ==============================================================================

def view_dashboard(request):
    """
    Main dashboard at URL: /dashboard/

    Shows different content based on active_role:
      - Requester → their tasks list
      - Helper    → available open tasks + their accepted task

    This is one view that serves two purposes based on role.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the user's profile to check their role
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if profile.active_role == 'requester':
        # Requester sees their own tasks, ordered newest first
        my_tasks = Task.objects.filter(requester=request.user).order_by('-created_at')
        return render(request, 'core/dashboard_requester.html', {
            'tasks': my_tasks,
            'profile': profile,
        })

    elif profile.active_role == 'helper':
        # Before showing open tasks, expire any that are too old
        mark_expired_tasks()

        # Helper sees all OPEN tasks (not their own tasks posted as requester)
        open_tasks = Task.objects.filter(status='OPEN').order_by('-created_at')

        # Also show the task the helper has currently accepted (if any)
        my_accepted_task = Task.objects.filter(
            helper=request.user,
            status='ACCEPTED'
        ).first()  # .first() returns one object or None

        # Also show completion_requested tasks where this helper is involved
        my_completion_task = Task.objects.filter(
            helper=request.user,
            status='COMPLETION_REQUESTED'
        ).first()

        return render(request, 'core/dashboard_helper.html', {
            'open_tasks': open_tasks,
            'my_accepted_task': my_accepted_task,
            'my_completion_task': my_completion_task,
            'profile': profile,
        })

    else:
        # Fallback — shouldn't happen, but just in case
        return redirect('select_role')


# ==============================================================================
# VIEW: Create Task (Requester only)
# ==============================================================================

def view_create_task(request):
    """
    Create a new task at URL: /task/create/

    Only Requesters can create tasks.

    GET  → Show the empty task form
    POST → Validate and save the task, redirect to dashboard
    """
    if not request.user.is_authenticated:
        return redirect('login')

    # Role check: only requesters can create tasks
    if not user_has_role(request, 'requester'):
        messages.error(request, "Only Requesters can create tasks.")
        return redirect('dashboard')

    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        payment_str = request.POST.get('payment_amount', '0').strip()
        latitude_str = request.POST.get('latitude', '').strip()
        longitude_str = request.POST.get('longitude', '').strip()

        # --- Validation ---

        if not title:
            messages.error(request, "Task title is required.")
            return render(request, 'core/create_task.html')

        if not description:
            messages.error(request, "Task description is required.")
            return render(request, 'core/create_task.html')

        # Try to convert payment to a number
        try:
            payment_amount = float(payment_str)
            if payment_amount < 0:
                raise ValueError("Payment cannot be negative")
        except ValueError:
            messages.error(request, "Please enter a valid payment amount.")
            return render(request, 'core/create_task.html')

        # Convert latitude/longitude if provided
        latitude = None
        longitude = None
        if latitude_str and longitude_str:
            try:
                latitude = float(latitude_str)
                longitude = float(longitude_str)
            except ValueError:
                messages.error(request, "Invalid latitude or longitude values.")
                return render(request, 'core/create_task.html')

        # --- Create the Task in the database ---

        task = Task.objects.create(
            requester=request.user,   # The logged-in user is the requester
            title=title,
            description=description,
            payment_amount=payment_amount,
            latitude=latitude,
            longitude=longitude,
            status='OPEN'             # Task starts as OPEN immediately
        )

        messages.success(request, f"Task '{task.title}' created successfully!")
        return redirect('dashboard')

    else:
        # GET → show empty form
        return render(request, 'core/create_task.html')


# ==============================================================================
# VIEW: View Task Detail
# ==============================================================================

def view_task_detail(request, task_id):
    """
    Task detail page at URL: /task/<task_id>/

    Shows full details of a task.
    Both requesters and helpers can view task details.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the task or return 404 if not found
    task = get_object_or_404(Task, id=task_id)

    # Check if the current user has already rated for this task
    # We'll use this to show/hide the rating button
    user_already_rated = Rating.objects.filter(
        task=task,
        rater=request.user
    ).exists()  # .exists() returns True/False without fetching all data

    # Get all ratings for this task (to display them)
    task_ratings = Rating.objects.filter(task=task)

    return render(request, 'core/task_detail.html', {
        'task': task,
        'user_already_rated': user_already_rated,
        'task_ratings': task_ratings,
        'profile': request.user.userprofile,
    })


# ==============================================================================
# VIEW: Accept Task (Helper only)
# ==============================================================================

def view_accept_task(request, task_id):
    """
    Accept a task at URL: /task/<task_id>/accept/

    Business Rules:
      - Only Helpers can accept tasks
      - Task must be OPEN
      - Helper cannot already have an ACCEPTED task (one task at a time)
      - Helper cannot accept their own task (if they posted it as a requester)

    Only handles POST (action, not a display page).
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if not user_has_role(request, 'helper'):
        messages.error(request, "Only Helpers can accept tasks.")
        return redirect('dashboard')

    # Get the task
    task = get_object_or_404(Task, id=task_id)

    # --- Business Rule Checks ---

    # Check 1: Task must be OPEN
    if task.status != 'OPEN':
        messages.error(request, f"Cannot accept this task. Current status: {task.status}")
        return redirect('dashboard')

    # Check 2: Helper cannot accept their own task
    if task.requester == request.user:
        messages.error(request, "You cannot accept your own task.")
        return redirect('dashboard')

    # Check 3: Helper cannot have more than one accepted task at a time
    # Look for any task where this helper is assigned and status is ACCEPTED
    already_has_task = Task.objects.filter(
        helper=request.user,
        status='ACCEPTED'
    ).exists()

    if already_has_task:
        messages.error(request, "You already have an active task. Complete or cancel it first.")
        return redirect('dashboard')

    # --- All checks passed → Accept the task ---

    task.helper = request.user          # Assign this helper to the task
    task.status = 'ACCEPTED'            # Update status
    task.accepted_at = timezone.now()   # Record when it was accepted
    task.save()                         # Save all changes to database

    messages.success(request, f"You have accepted the task: '{task.title}'")
    return redirect('dashboard')


# ==============================================================================
# VIEW: Request Completion (Helper only)
# ==============================================================================

def view_request_completion(request, task_id):
    """
    Helper marks task as done at URL: /task/<task_id>/complete/

    Status change: ACCEPTED → COMPLETION_REQUESTED

    After this, the Requester needs to confirm/approve.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if not user_has_role(request, 'helper'):
        messages.error(request, "Only Helpers can mark tasks as complete.")
        return redirect('dashboard')

    task = get_object_or_404(Task, id=task_id)

    # Check: this helper must be the assigned helper for this task
    if task.helper != request.user:
        messages.error(request, "You are not the helper for this task.")
        return redirect('dashboard')

    # Check: task must be in ACCEPTED status
    if task.status != 'ACCEPTED':
        messages.error(request, f"Cannot request completion. Current status: {task.status}")
        return redirect('dashboard')

    # Update status
    task.status = 'COMPLETION_REQUESTED'
    task.save()

    messages.success(request, "Completion requested! Waiting for requester to approve.")
    return redirect('dashboard')


# ==============================================================================
# VIEW: Approve Completion (Requester only)
# ==============================================================================

def view_approve_completion(request, task_id):
    """
    Requester confirms task is done at URL: /task/<task_id>/approve/

    Status change: COMPLETION_REQUESTED → COMPLETED

    After this, both parties can rate each other.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if not user_has_role(request, 'requester'):
        messages.error(request, "Only Requesters can approve completion.")
        return redirect('dashboard')

    task = get_object_or_404(Task, id=task_id)

    # Check: this requester must own this task
    if task.requester != request.user:
        messages.error(request, "You are not the requester for this task.")
        return redirect('dashboard')

    # Check: task must be in COMPLETION_REQUESTED status
    if task.status != 'COMPLETION_REQUESTED':
        messages.error(request, f"Cannot approve. Current status: {task.status}")
        return redirect('dashboard')

    # Update status to COMPLETED
    task.status = 'COMPLETED'
    task.completed_at = timezone.now()  # Record completion time
    task.save()

    messages.success(request, f"Task '{task.title}' marked as COMPLETED! You can now rate each other.")
    return redirect('task_detail', task_id=task.id)


# ==============================================================================
# VIEW: Cancel Task
# ==============================================================================

def view_cancel_task(request, task_id):
    """
    Cancel a task at URL: /task/<task_id>/cancel/

    Who can cancel:
      - Requester: can cancel OPEN tasks
      - Helper: can cancel ACCEPTED tasks (with a reason)

    GET  → Show cancellation form (with optional reason input)
    POST → Process cancellation
    """
    if not request.user.is_authenticated:
        return redirect('login')

    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        cancel_reason = request.POST.get('cancel_reason', '').strip()
        profile = request.user.userprofile

        # --- Determine who is cancelling and validate ---

        if profile.active_role == 'requester':
            # Requester can cancel if they own the task and it's OPEN
            if task.requester != request.user:
                messages.error(request, "You don't own this task.")
                return redirect('dashboard')

            if task.status not in ['OPEN', 'ACCEPTED']:
                messages.error(request, f"Cannot cancel. Current status: {task.status}")
                return redirect('dashboard')

        elif profile.active_role == 'helper':
            # Helper can cancel if they are the assigned helper and task is ACCEPTED
            if task.helper != request.user:
                messages.error(request, "You are not the helper for this task.")
                return redirect('dashboard')

            if task.status != 'ACCEPTED':
                messages.error(request, f"Cannot cancel. Current status: {task.status}")
                return redirect('dashboard')

        else:
            messages.error(request, "Invalid role.")
            return redirect('dashboard')

        # --- Cancel the task ---

        task.status = 'CANCELLED'
        task.cancel_reason = cancel_reason  # Save the reason (can be empty)
        task.save()

        messages.success(request, "Task cancelled successfully.")
        return redirect('dashboard')

    else:
        # GET → show cancellation form
        return render(request, 'core/cancel_task.html', {
            'task': task,
            'profile': request.user.userprofile,
        })


# ==============================================================================
# VIEW: Rate User
# ==============================================================================

def view_rate_user(request, task_id):
    """
    Rating form at URL: /task/<task_id>/rate/

    Rules:
      - Task must be COMPLETED
      - Cannot rate yourself
      - Cannot rate twice for the same task
      - Rating must be 1–5

    After saving the rating:
      → Recalculate the ratee's trust_score (average of all ratings received)

    GET  → Show rating form
    POST → Save rating and update trust score
    """
    if not request.user.is_authenticated:
        return redirect('login')

    task = get_object_or_404(Task, id=task_id)

    # --- Validations ---

    # Task must be completed before rating
    if task.status != 'COMPLETED':
        messages.error(request, "You can only rate after a task is completed.")
        return redirect('task_detail', task_id=task.id)

    # Figure out who the current user is rating
    # If current user is the requester → they rate the helper
    # If current user is the helper → they rate the requester
    if request.user == task.requester:
        ratee = task.helper  # Requester rates Helper
    elif request.user == task.helper:
        ratee = task.requester  # Helper rates Requester
    else:
        # This person is neither the requester nor the helper for this task
        messages.error(request, "You are not involved in this task.")
        return redirect('dashboard')

    # Cannot rate yourself (edge case safety check)
    if ratee == request.user:
        messages.error(request, "You cannot rate yourself.")
        return redirect('task_detail', task_id=task.id)

    # Check if already rated
    already_rated = Rating.objects.filter(task=task, rater=request.user).exists()
    if already_rated:
        messages.error(request, "You have already rated for this task.")
        return redirect('task_detail', task_id=task.id)

    if request.method == 'POST':
        rating_value_str = request.POST.get('rating', '0')
        comment = request.POST.get('comment', '').strip()

        # Validate rating is a number between 1 and 5
        try:
            rating_value = int(rating_value_str)
        except ValueError:
            messages.error(request, "Invalid rating value.")
            return render(request, 'core/rate_user.html', {'task': task, 'ratee': ratee})

        if rating_value < 1 or rating_value > 5:
            messages.error(request, "Rating must be between 1 and 5.")
            return render(request, 'core/rate_user.html', {'task': task, 'ratee': ratee})

        # --- Save the Rating ---

        Rating.objects.create(
            task=task,
            rater=request.user,
            ratee=ratee,
            rating=rating_value,
            comment=comment
        )

        # --- Update Trust Score (manually, no signals) ---

        # Fetch all ratings where this user was the ratee
        all_ratings_for_ratee = Rating.objects.filter(ratee=ratee)

        # Count how many ratings there are
        total_ratings = all_ratings_for_ratee.count()

        if total_ratings > 0:
            # Calculate the sum of all rating values
            # This is a simple Python loop — easy to understand
            total_score = 0
            for r in all_ratings_for_ratee:
                total_score = total_score + r.rating

            # Average = sum / count
            average_score = total_score / total_ratings

            # Update the ratee's trust score in their profile
            ratee_profile = ratee.userprofile
            ratee_profile.trust_score = round(average_score, 2)  # Round to 2 decimal places
            ratee_profile.save()

        messages.success(request, f"Rating submitted! {ratee.username} received {rating_value}/5 stars.")
        return redirect('task_detail', task_id=task.id)

    else:
        # GET → show the rating form
        return render(request, 'core/rate_user.html', {
            'task': task,
            'ratee': ratee,
        })


# ==============================================================================
# VIEW: User Profile Page
# ==============================================================================

def view_profile(request, username):
    """
    Public profile page at URL: /profile/<username>/

    Shows user's trust score, role, and completed tasks.
    Anyone can view any user's profile.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the user whose profile we're viewing
    # get_object_or_404 returns 404 if the username doesn't exist
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.userprofile

    # Get ratings this user has received
    received_ratings = Rating.objects.filter(ratee=profile_user).order_by('-created_at')

    # Count completed tasks (as requester or helper)
    tasks_as_requester = Task.objects.filter(
        requester=profile_user,
        status='COMPLETED'
    ).count()

    tasks_as_helper = Task.objects.filter(
        helper=profile_user,
        status='COMPLETED'
    ).count()

    return render(request, 'core/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'received_ratings': received_ratings,
        'tasks_as_requester': tasks_as_requester,
        'tasks_as_helper': tasks_as_helper,
    })

