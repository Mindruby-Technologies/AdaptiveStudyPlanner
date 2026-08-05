# Knowledge Base — Project Initiation

**Project:** Adaptive Study Planner
**Owner:** Aditi Danani
**Document Type:** Project Initiation — Initial Version Overview

---

## 1. What Was the Project About

Adaptive Study Planner started as a personal study management tool. The core idea was simple: a student preparing for exams needs to organize their study material, track what they have studied, and get a structured daily plan rather than manually deciding what to study each day.

The initial version focused on three things:

- Organizing study material into a hierarchy (Tests → Subjects → Topics)
- Generating a daily study schedule based on topic priority and difficulty
- Tracking mock test performance manually

---

## 2. Initial Architecture

The project was built as a **monolithic Flask web application** with a MySQL backend and a Bootstrap 5 frontend. There was no separation between frontend and backend — Flask served both the HTML pages and the JSON API endpoints from the same server.

```
Browser
   │
   ▼
Flask App (app.py)
   ├── UI Routes → render HTML templates
   ├── API Routes → return JSON
   └── MySQL Database
```

All routes were registered in `app.py` using Flask Blueprints, one per domain. Templates used Jinja2 for server-side rendering with jQuery handling all dynamic API calls on the client side.

---

## 3. Core Data Model

The initial schema was built around a simple hierarchy:

```
tests
  └── subjects (linked to a test)
        └── topics (linked to a subject)
              └── schedule_entries (generated per topic per day)

MockTests (linked to a test)
  └── MockTest_topics (topic-wise marks per mock test)
```

Each topic carried:

- `difficulty_level` (1–5) — how hard the topic is
- `priority_level` (1–5) — how important it is for the exam
- `start_date` / `end_date` — the window in which it should be studied
- `miss_penalty` — a penalty value applied when a session is missed
- `status` — active or inactive

---

## 4. Single-User Login System

The initial authentication was intentionally simple — a **single hardcoded user** stored as constants in `auth.py`:

```python
USERNAME = "******"
PASSWORD = "******"
```

The login flow was:

1. User visits any page
2. `login_required` decorator checks `session["logged_in"]`
3. If not set, redirect to `/login`
4. On form submit, compare against hardcoded credentials
5. Set `session["logged_in"] = True` and `session["username"] = USERNAME`
6. Redirect to dashboard

There was no registration page, no database lookup, and no password hashing. This was a deliberate decision to keep the initial version simple and focus on the core scheduling and tracking features first.

The `login_required` decorator was implemented using Python's `functools.wraps`:

```python
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
```

---

## 5. Schedule Generation — Initial Implementation

The schedule generator was the most important feature of the initial version. It used a scoring algorithm to decide how many hours to allocate to each topic per day.

**Score Formula:**

```
Score = (10 / days_left) + (difficulty × 2) + (priority × 3) + miss_penalty
```

Where `days_left = end_date - start_date` (minimum 1 to avoid division by zero).

**Generation Flow:**

1. Delete all future schedule entries (keep today and past)
2. Find the date range: `MIN(start_date)` to `MAX(end_date)` across all active topics
3. Loop day by day through the range
4. For each day, find active topics (where `start_date <= day <= end_date`)
5. Score each topic, sort descending
6. Distribute 4 hours proportionally by weight
7. Minimum 0.25 hours per topic, rounded to nearest 0.25
8. Insert all rows in a single `executemany` call

The `miss_penalty` in the initial version was simply the raw value from the topics table — it was later enhanced to multiply by the actual count of missed sessions.

---

## 6. Mock Test Performance Tracking

The initial mock test feature was entirely manual. A user would:

1. Create a `MockTest` record linked to a test, with a date
2. Add topic-wise scores (marks obtained vs max marks)
3. View auto-generated performance insights

The insights were calculated in pure Python (no AI) inside `_generate_insights()`:

- **Highest/Lowest** scoring topic by average percentage
- **Most Improved** — biggest positive delta between first and last attempt
- **Declining** — topics where last attempt was worse than first
- **Focus Areas** — topics averaging below 60%
- **Consistency** — standard deviation per topic across attempts

---

## 7. Frontend Architecture

The UI was built on **Bootstrap 5** with **jQuery** for all dynamic interactions. The base template (`base.html`) provided:

- A fixed left sidebar with navigation links
- A toast notification system (`showToast()`)
- Shared CSS for consistent styling

Each page extended `base.html` and used `$.get()` / `$.ajax()` calls to interact with the Flask API. No page reloads were needed for CRUD operations — everything was handled via AJAX and DOM manipulation.

---

## 8. Database Connection

The database connection was managed through a simple factory function in `db.py`:

```python
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
```

Each route opened a connection, executed queries, and closed it manually. There was no connection pooling in the initial version.

---

## 9. What Was Intentionally Left Out Initially

| Feature            | Reason Deferred                                                 |
| ------------------ | --------------------------------------------------------------- |
| Multi-user support | Complexity — single user was sufficient to validate the concept |
| Password hashing   | Not needed for a single hardcoded credential                    |
| AI analysis        | Planned as a future enhancement                                 |
| PDF upload         | Dependent on AI integration                                     |
| Role-based access  | Out of scope for a personal tool                                |

---

## 10. Initial File Structure

```
AdaptiveStudyPlanner/
├── app.py
├── db.py
├── requirements.txt          # flask, mysql-connector-python only
├── routes/
│   ├── auth.py               # Hardcoded single-user auth
│   ├── tests.py
│   ├── subjects.py
│   ├── topics.py
│   ├── schedules.py
│   └── mocktests.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── index.html
│   ├── tests.html
│   ├── subjects.html
│   ├── topics.html
│   ├── schedules.html
│   └── mocktests.html
└── migrations/
    └── create_mocktests.sql
```

---

## 11. Summary

The initial version established the full foundation of the application:

- A clean modular Flask architecture using Blueprints
- A well-designed relational schema with proper foreign keys
- A working adaptive scheduling algorithm
- A manual mock test tracking system with automated insights
- A simple but functional single-user authentication system
- A consistent Bootstrap 5 UI with AJAX-driven interactions

This foundation made it straightforward to later add multi-user support, AI-powered analysis, and PDF report processing without restructuring the core architecture.
