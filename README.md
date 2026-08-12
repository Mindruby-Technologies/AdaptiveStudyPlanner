# Adaptive Study Planner

**Owner:** Aditi Danani
**Stack:** Python · Flask · MySQL · Bootstrap 5 · Google Gemini AI

---

## Overview

Adaptive Study Planner is a web-based application designed to help students manage their study schedule intelligently. It organizes study material into a hierarchy of Tests → Subjects → Topics, generates AI-weighted daily schedules, tracks mock test performance, and uses Google Gemini to analyze uploaded PDF score reports and generate personalized improvement insights.

The system supports multiple users, each with their own isolated data, and provides a clean dashboard-driven UI built with Bootstrap 5.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Project Structure](#project-structure)
5. [Key Modules](#key-modules)
6. [Setup Instructions](#setup-instructions)
7. [Environment Variables](#environment-variables)
8. [API Reference](#api-reference)
9. [Schedule Generation Algorithm](#schedule-generation-algorithm)
10. [AI Mock Test Analysis](#ai-mock-test-analysis)
11. [Authentication System](#authentication-system)
12. [Workflow](#workflow)

---

## Features

| Feature | Description |
|---|---|
| Multi-user Authentication | Register/Login with bcrypt-hashed passwords, session-based auth |
| Test Management | Create and manage exam tests with dates and status |
| Subject Management | Organize subjects under tests |
| Topic Management | Define topics with difficulty, priority, dates, and miss penalty |
| Adaptive Schedule Generation | AI-scored daily schedule with 4-hour daily limit |
| Missed Session Tracking | Mark sessions as missed, auto-reschedule with penalty |
| Manual Mock Test Entry | Record topic-wise marks for mock tests |
| Performance Insights | Automated analysis: highest/lowest, trends, focus areas, consistency |
| AI PDF Report Analysis | Upload PDF score reports, Gemini extracts data and generates insights |
| Dashboard | Today's schedule, stats overview, recent tests |

---

## Architecture

```
Browser (Bootstrap 5 + jQuery)
        │
        ▼
Flask Application (app.py)
        │
        ├── Auth Blueprint       (/login, /register, /logout)
        ├── Tests Blueprint      (/tests)
        ├── Subjects Blueprint   (/subjects)
        ├── Topics Blueprint     (/topics)
        ├── Schedules Blueprint  (/schedules, /schedules/generate)
        ├── MockTests Blueprint  (/mocktests, /mocktests/insights)
        └── AI MockTest Blueprint(/mocktests/ai-analyze, /mocktests/ai-reports)
                │
                ├── MySQL Database (mysql-connector-python)
                └── Google Gemini API (google-generativeai)
```

The application follows a **Blueprint-based modular architecture**. Each domain (tests, subjects, topics, schedules, mocktests, auth) is a separate Flask Blueprint registered in `app.py`. All UI routes are protected by the `login_required` decorator. API routes read `user_id` from the Flask session to scope all queries.

---

## Database Schema

```
users
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── password_hash
└── created_at

tests
├── id (PK)
├── user_id (FK → users)
├── name
├── exam_date
├── status (active/inactive)
└── created_at

subjects
├── id (PK)
├── user_id (FK → users)
├── test_id (FK → tests)
├── name
└── status

topics
├── id (PK)
├── subject_id (FK → subjects)
├── name
├── difficulty_level (1–5)
├── priority_level (1–5)
├── start_date
├── end_date
├── miss_penalty
├── status (active/inactive)
└── created_at

schedule_entries
├── id (PK)
├── user_id (FK → users)
├── topic_id (FK → topics)
├── schedule_date
├── allocated_hours (DECIMAL)
└── missed (ENUM: yes/no)

MockTests
├── id (PK)
├── user_id (FK → users)
├── test_id (FK → tests)
├── name
├── test_date
├── created_at
└── modified_at

MockTest_topics
├── id (PK)
├── mocktest_id (FK → MockTests)
├── topic_id (FK → topics)
├── marks_obtained (DECIMAL)
└── max_marks (DECIMAL)

ai_mocktest_reports
├── id (PK)
├── user_id (FK → users)
├── test_id (FK → tests)
├── student_name
├── grade
├── test_name
├── test_date
├── total_score
├── score_range
├── percentile
├── extracted_json (JSON)
├── ai_report (JSON)
├── file_name
├── uploaded_at
└── status (ENUM: pending/processed)
```

**Relationship Summary:**
- `users` → `tests` → `subjects` → `topics` (ownership chain)
- `topics` is scoped to a user via the `subjects.user_id` join
- `schedule_entries` directly carries `user_id` for fast filtering
- `MockTests` and `ai_mocktest_reports` carry `user_id` for isolation

---

## Project Structure

```
AdaptiveStudyPlanner/
├── app.py                        # Flask app entry point, blueprint registration, UI routes
├── db.py                         # MySQL connection factory
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (Gemini API key)
├── .gitignore
│
├── routes/
│   ├── auth.py                   # Login, register, logout, login_required decorator
│   ├── tests.py                  # CRUD for tests
│   ├── subjects.py               # CRUD for subjects
│   ├── topics.py                 # CRUD for topics
│   ├── schedules.py              # Schedule generation, retrieval, missed marking
│   ├── mocktests.py              # Manual mock test CRUD + performance insights
│   └── ai_mocktest.py            # PDF upload, Gemini extraction, AI report generation
│
├── templates/
│   ├── base.html                 # Shared layout: sidebar, toast, scripts
│   ├── login.html                # Standalone login page
│   ├── register.html             # Standalone register page
│   ├── index.html                # Dashboard
│   ├── tests.html                # Tests management UI
│   ├── subjects.html             # Subjects management UI
│   ├── topics.html               # Topics management UI
│   ├── schedules.html            # Schedule viewer + generator UI
│   └── mocktests.html            # Mock test management + insights UI
│
└── migrations/
    ├── create_mocktests.sql      # MockTests, MockTest_topics, ai_mocktest_reports DDL
    └── multiuser.sql             # users table + user_id columns migration
```

---

## Key Modules

### `app.py`
Entry point. Registers all blueprints, initializes bcrypt, defines UI routes with `@login_required`.

### `db.py`
Single `get_connection()` function returning a `mysql.connector` connection. Used across all routes.

### `routes/auth.py`
- `login_required` decorator checks `session["user_id"]`
- `POST /login` — validates credentials against `users` table using bcrypt
- `POST /register` — creates new user with hashed password
- `GET /logout` — clears session

### `routes/schedules.py`
Core scheduling logic lives in `_run_generate(user_id)`:
- Deletes future entries for the user
- Finds active topic date range
- Loops day by day, scores topics, distributes 4 hours proportionally
- Minimum 0.25h per topic, rounded to nearest 0.25

### `routes/ai_mocktest.py`
- `_extract_from_pdf()` — uses pdfplumber to extract raw text
- `_gemini_extract()` — sends text to Gemini, returns structured JSON
- `_fetch_history()` — fetches last 5 records from both manual and AI tables, combined and sorted by date
- `_gemini_report()` — sends current + history to Gemini, returns analysis JSON

### `routes/mocktests.py`
- Manual CRUD for mock tests and topic scores
- `_generate_insights()` — pure Python analysis: highest/lowest avg, most improved, declining, focus areas, consistency (std deviation)

---

## Setup Instructions

### Prerequisites
- Python 3.9+
- MySQL 8.0+
- Google Gemini API key

### 1. Clone and install dependencies
```bash
git clone <repo-url>
cd AdaptiveStudyPlanner
pip install -r requirements.txt
```

### 2. Create the MySQL database
```sql
CREATE DATABASE adaptive_study_planner;
```

### 3. Run migrations
```bash
# Run in order
mysql -u root -p adaptive_study_planner < migrations/create_mocktests.sql
mysql -u root -p adaptive_study_planner < migrations/multiuser.sql
```

### 4. Configure environment
Update `db.py` with your MySQL credentials:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_user",
    "password": "your_password",
    "database": "adaptive_study_planner"
}
```

Create `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 5. Run the application
```bash
python app.py
```

Visit `http://127.0.0.1:5000` — you will be redirected to `/login`.

### 6. Register your account
Navigate to `/register` to create your first user account.

---

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key for AI analysis |
| `GEMINI_MODEL` | Gemini model name (default: `gemini-2.5-flash`) |

---

## API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/login` | Login page and form submission |
| GET/POST | `/register` | Register page and form submission |
| GET | `/logout` | Clear session and redirect to login |

### Tests
| Method | Endpoint | Description |
|---|---|---|
| GET | `/tests` | Get all tests for current user |
| POST | `/tests` | Create a test |
| PUT | `/tests/<id>` | Update a test |
| DELETE | `/tests/<id>` | Delete a test |

### Subjects
| Method | Endpoint | Description |
|---|---|---|
| GET | `/subjects` | Get all subjects for current user |
| POST | `/subjects` | Create a subject |
| PUT | `/subjects/<id>` | Update a subject |
| DELETE | `/subjects/<id>` | Delete a subject |

### Topics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/topics` | Get all topics for current user |
| GET | `/topics/by-test/<test_id>` | Get topics under a specific test |
| POST | `/topics` | Create a topic |
| PUT | `/topics/<id>` | Update a topic |
| DELETE | `/topics/<id>` | Delete a topic |

### Schedules
| Method | Endpoint | Description |
|---|---|---|
| POST | `/schedules/generate` | Generate/regenerate future schedule |
| GET | `/schedules?date=YYYY-MM-DD` | Get schedule entries for a date |
| PATCH | `/schedules/<id>/missed` | Mark entry as missed + regenerate |

### Mock Tests
| Method | Endpoint | Description |
|---|---|---|
| GET | `/mocktests` | Get all mock tests |
| POST | `/mocktests` | Create mock test with topic scores |
| PUT | `/mocktests/<id>` | Update mock test |
| DELETE | `/mocktests/<id>` | Delete mock test |
| GET | `/mocktests/insights` | Get performance insights |

### AI Mock Test
| Method | Endpoint | Description |
|---|---|---|
| POST | `/mocktests/ai-analyze` | Upload PDF, extract + generate AI report |
| GET | `/mocktests/ai-reports` | Get all AI reports (filter by test_id) |

---

## Schedule Generation Algorithm

```
Score = (10 / days_left) + (difficulty × 2) + (priority × 3) + (miss_penalty × missed_count)

Where:
  days_left    = topic end_date - topic start_date (min 1)
  missed_count = COUNT of schedule_entries where missed = 'yes' for that topic
```

**Distribution:**
1. Score each active topic for the current date
2. Sort by score DESC
3. Calculate weight = topic_score / total_score
4. Allocate hours = max(weight × 4, 0.25), rounded to nearest 0.25
5. Insert all rows, move to next date

**Rules:**
- Daily limit: 4 hours
- Minimum per topic: 0.25 hours (15 minutes)
- Past entries (≤ today) are preserved on regeneration
- Missed entries within the last 7 days can be marked, which increases the topic's future score via penalty

---

## AI Mock Test Analysis

**Extraction Flow:**
1. User selects a Test and uploads a PDF score report
2. `pdfplumber` extracts raw text from all pages
3. Gemini parses the text and returns structured JSON:
   - `student_name`, `grade`, `test_name`, `test_date`
   - `total_score`, `score_range`, `percentile`
   - `section_scores[]` — section-level performance
   - `knowledge_areas[]` — topic-level marks obtained vs max

**Report Generation Flow:**
1. Fetch last 5 records from `MockTests` (manual) + `ai_mocktest_reports` (AI), combined by datetime, top 5
2. Send current extracted data + history to Gemini
3. Gemini returns analysis JSON:
   - `overall_summary`, `strengths[]`, `weaknesses[]`
   - `recommendations[]`, `trend_summary`, `focus_areas[]`
   - `section_analysis[]`, `topic_insights[]`

---

## Authentication System

- Passwords hashed with **bcrypt** (via flask-bcrypt)
- Session stores `user_id` and `username` on successful login
- `login_required` decorator on all UI routes redirects unauthenticated users to `/login`
- All API queries are scoped with `WHERE user_id = session["user_id"]`
- Topics are scoped via `JOIN subjects WHERE subjects.user_id = ?` since topics inherit ownership through subjects

---

## Workflow

```
Register / Login
      ↓
Dashboard — view today's schedule + stats
      ↓
Create Test → Add Subjects → Add Topics (with dates, difficulty, priority)
      ↓
Generate Schedule (POST /schedules/generate)
      ↓
View Schedule by day (Today / Tomorrow / This Week / Custom date)
      ↓
Mark missed sessions → auto-reschedule with penalty applied
      ↓
Add Manual Mock Test results → view Performance Insights
      ↓
Upload PDF Score Report → AI extracts marks → AI generates improvement report
```
