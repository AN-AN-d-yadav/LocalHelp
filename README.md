# 🤝 LocalHelp — Role-Based Task Marketplace

A Django web application where **Requesters** post tasks and **Helpers** complete them.
Built for learning — every line of code is heavily commented.

---

## 📁 Project Structure

```
LocalHelp/
│
├── manage.py                    # Django CLI entry point
├── db.sqlite3                   # Database (created on first run)
├── setup.bat                    # Windows one-click setup
├── README.md
│
├── localhelp/                   # Project config package
│   ├── settings.py              # All Django settings
│   ├── urls.py                  # Root URL router
│   └── wsgi.py                  # Production server entry point
│
├── core/                        # Main app with all the logic
│   ├── models.py                # Database models (UserProfile, Task, Rating)
│   ├── views.py                 # All view functions (business logic)
│   ├── urls.py                  # App-level URL patterns
│   ├── admin.py                 # Register models in Django admin
│   ├── apps.py                  # App config
│   ├── migrations/
│   │   └── 0001_initial.py      # Database schema migration
│   └── templates/core/          # HTML templates
│       ├── home.html
│       ├── register.html
│       ├── login.html
│       ├── select_role.html
│       ├── dashboard_requester.html
│       ├── dashboard_helper.html
│       ├── create_task.html
│       ├── task_detail.html
│       ├── cancel_task.html
│       ├── rate_user.html
│       └── profile.html
│
├── templates/
│   └── base.html                # Master layout template (all pages extend this)
│
└── static/
    └── css/
        └── style.css            # All styles
```

---

## 🚀 Quick Start (Windows)

### Prerequisites
- Python 3.10 or higher installed
- pip available
- VS Code (recommended)

### Option 1 — One-Click Setup
Double-click `setup.bat`

### Option 2 — Manual Setup

Open Command Prompt in the `LocalHelp/` folder:

```bash
# Install Django
pip install django==4.2

# Create database tables
python manage.py migrate

# (Optional) Create admin user to access /admin/
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

Open your browser: **http://127.0.0.1:8000/**

---

## 🎮 How to Use the App

### 1. Register
- Go to `/register/`
- Create an account (username + password)
- You'll be redirected to role selection

### 2. Choose a Role
- **Requester** → Post tasks for helpers to do
- **Helper** → Browse and accept tasks posted by requesters
- You can switch roles anytime from the navbar

### 3. As a Requester
1. Click **+ Create New Task**
2. Fill in: title, description, payment amount
3. Your task goes OPEN — helpers can now see it
4. When a helper finishes and requests completion → click **Approve Completion**
5. Rate the helper ⭐

### 4. As a Helper
1. Browse OPEN tasks on your dashboard
2. Click **Accept Task** (only one at a time!)
3. Do the work, then click **Mark as Done**
4. Wait for the requester to approve
5. Rate the requester ⭐

---

## 📊 Task Status Flow

```
OPEN ──────────────────────┐
 │                         │
 │ Helper accepts           │ 30 min passes
 ▼                         ▼
ACCEPTED              EXPIRED
 │
 │ Helper marks done
 ▼
COMPLETION_REQUESTED
 │
 │ Requester approves
 ▼
COMPLETED ──→ Both can rate each other

(OPEN or ACCEPTED can also be CANCELLED)
```

---

## 🗃️ Database Models

### UserProfile
| Field | Type | Description |
|---|---|---|
| user | OneToOneField(User) | Link to Django's User |
| active_role | CharField | 'requester' or 'helper' |
| latitude | DecimalField | Optional location |
| longitude | DecimalField | Optional location |
| trust_score | FloatField | Average of all ratings received |

### Task
| Field | Type | Description |
|---|---|---|
| requester | ForeignKey(User) | Who posted the task |
| helper | ForeignKey(User, null) | Who accepted (null until accepted) |
| title | CharField | Short title |
| description | TextField | Full description |
| payment_amount | DecimalField | How much the helper earns |
| status | CharField | Current task state |
| created_at | DateTimeField | When posted |
| accepted_at | DateTimeField | When a helper accepted |
| completed_at | DateTimeField | When marked as done |

### Rating
| Field | Type | Description |
|---|---|---|
| task | ForeignKey(Task) | Which task this is for |
| rater | ForeignKey(User) | Who gave the rating |
| ratee | ForeignKey(User) | Who received the rating |
| rating | IntegerField | 1 to 5 |
| comment | TextField | Optional text |

---

## ⚙️ Business Rules

1. **One task at a time** — A helper cannot accept a new task while they have an ACTIVE task
2. **Auto-expiry** — OPEN tasks older than 30 minutes are marked EXPIRED when the helper views available tasks
3. **Rating rules**:
   - Only after task is COMPLETED
   - Cannot rate twice for the same task
   - Cannot rate yourself
4. **Trust Score** = Average of all ratings received (recalculated after every rating)
5. **Status transitions** are strictly validated — invalid transitions show an error

---

## 🔗 All URLs

| URL | Page |
|---|---|
| `/` | Homepage |
| `/register/` | Register |
| `/login/` | Login |
| `/logout/` | Logout |
| `/role/` | Select / switch role |
| `/dashboard/` | Main dashboard (role-based) |
| `/task/create/` | Create a new task |
| `/task/<id>/` | Task detail page |
| `/task/<id>/accept/` | Accept a task (POST) |
| `/task/<id>/complete/` | Request completion (POST) |
| `/task/<id>/approve/` | Approve completion (POST) |
| `/task/<id>/cancel/` | Cancel task page |
| `/task/<id>/rate/` | Rate the other user |
| `/profile/<username>/` | User profile page |
| `/admin/` | Django admin panel |

---

## 🐛 Debugging Tips

1. **Django Admin** — Go to `/admin/` and log in with your superuser account.
   You can see all database records, edit them, delete them — great for debugging!

2. **Debug toolbar** — In `settings.py`, `DEBUG=True` means Django shows detailed
   error pages with the full traceback when something breaks.

3. **Shell** — Open a Python shell with Django loaded:
   ```bash
   python manage.py shell
   ```
   Then interact with models directly:
   ```python
   from core.models import Task
   Task.objects.all()  # See all tasks
   Task.objects.filter(status='OPEN')  # Filter by status
   ```

4. **Check logs** — The terminal where you ran `python manage.py runserver`
   shows every HTTP request and any error messages.

---

## 🧪 Manual Test Scenarios

Test these to verify all business rules work:

| Scenario | Expected Result |
|---|---|
| Register two users | Both get UserProfiles |
| User A creates task | Task appears as OPEN for User B |
| User B (Helper) accepts task | Task status → ACCEPTED |
| User B tries to accept ANOTHER task | Error: "already have active task" |
| User B marks task done | Status → COMPLETION_REQUESTED |
| User A approves | Status → COMPLETED |
| User A rates User B | Rating saved, trust score updated |
| User A tries to rate again | Error: "already rated" |
| Create task, wait 30 min (or set `created_at` back in admin) | Status → EXPIRED |
| Try accepting an EXPIRED task | Error |

---

## 📚 Key Django Concepts Used

- **Models** — Python classes that map to database tables
- **Views** — Functions that handle requests and return responses  
- **Templates** — HTML files with Django template language (`{% %}`, `{{ }}`)
- **URL routing** — `urls.py` maps URLs to view functions
- **ORM** — `Task.objects.filter(status='OPEN')` instead of raw SQL
- **Sessions** — How Django keeps users logged in
- **CSRF protection** — `{% csrf_token %}` in every POST form
- **Messages framework** — Flash messages for user feedback
- **Static files** — CSS served via `{% static %}` template tag
- **Migrations** — Version control for your database schema

---

*Built with ❤️ for learning Django | No Docker, No Redis, No DRF — just plain Django*
#   L o c a l H e l p  
 