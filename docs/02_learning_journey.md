# Knowledge Base — Learning Journey: Intern to Contributor

**Project:** Adaptive Study Planner
**Owner:** Aditi Danani
**Document Type:** Developer Learning Journey

---

## Overview

This document outlines the learning path of a developer who joined as an intern and contributed to the Adaptive Study Planner project. It covers the engineering concepts, best practices, and real decisions encountered while building and evolving this project — from the initial single-user Flask app to a multi-user, AI-powered study platform.

---

## 1. Understanding the Project Structure

### What Was Learned

The first task was understanding how a real Flask project is organized. Unlike tutorial projects where everything lives in a single file, this project used **Flask Blueprints** to separate concerns.

```
app.py              ← entry point, registers blueprints
routes/auth.py      ← authentication logic
routes/tests.py     ← tests CRUD
routes/subjects.py  ← subjects CRUD
routes/topics.py    ← topics CRUD
routes/schedules.py ← schedule generation
routes/mocktests.py ← mock test tracking
routes/ai_mocktest.py ← AI PDF analysis
templates/          ← Jinja2 HTML templates
migrations/         ← SQL schema files
```

### Key Takeaway

Each Blueprint is a self-contained module. `app.py` is kept clean — it only registers blueprints and defines UI routes. Business logic never lives in `app.py`.

### Coding Standards Observed

- Snake_case for Python functions and variables
- Blueprint names match their file names (`tests_bp`, `subjects_bp`)
- Helper functions prefixed with `_` (e.g., `_run_generate`, `_generate_insights`) to indicate they are internal
- No inline SQL strings longer than necessary — multi-line triple-quoted strings for readability

---

## 2. GitHub Version Control and Collaboration Workflow

### What Was Learned

Working on a shared codebase requires discipline with Git. The practices followed on this project:

**Branch Strategy:**

```
main          ← stable, production-ready code
feature/*     ← new features (e.g., feature/ai-mocktest)
fix/*         ← bug fixes
```

**Commit Message Convention:**

```
feat: add schedule generation endpoint
fix: correct timezone issue in schedule date comparison
refactor: extract _run_generate as shared helper
docs: add README and knowledge base documents
```

**Pull Request Practice:**

- Never push directly to `main`
- Every feature branch gets a PR with a description of what changed and why
- Self-review before requesting a review — check for hardcoded values, missing error handling, and unused imports

**`.gitignore` Discipline:**
The project's `.gitignore` excluded:

- `.env` — never commit API keys or credentials
- `__pycache__/` — Python bytecode
- `*.pyc` — compiled Python files

### Key Takeaway

The `.env` file containing the `GEMINI_API_KEY` was never committed to the repository. Credentials always go in environment variables, never in source code.

---

## 3. Authentication and Authorization

### Evolution on This Project

**Phase 1 — Hardcoded Single User:**

```python
USERNAME = "****"
PASSWORD = "****"

if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
    session["logged_in"] = True
```

This was acceptable for a personal tool but had obvious problems: the password was in plain text in source code, and there was no way to add more users.

**Phase 2 — Database-Backed Multi-User:**

```python
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
user = cursor.fetchone()
if user and bcrypt.check_password_hash(user["password_hash"], password):
    session["user_id"] = user["id"]
    session["username"] = user["username"]
```

### What Was Learned

- **Never store plain text passwords** — always hash with a strong algorithm like bcrypt
- **bcrypt is slow by design** — it uses a cost factor that makes brute-force attacks expensive
- **Session stores minimal data** — only `user_id` and `username`, never the full user object or password hash
- **`login_required` as a decorator** — applying auth protection at the route level using `functools.wraps` keeps route functions clean

```python
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
```

### Key Takeaway

Authentication is a cross-cutting concern. The decorator pattern is the right way to apply it — not repeating the session check inside every route function.

---

## 4. Session Management

### What Was Learned

Flask sessions are **signed cookies** stored on the client. The `secret_key` is what makes them tamper-proof.

```python
app.secret_key = "asp_secret_key_2025"
```

**Important practices observed:**

- `session.clear()` on logout — removes all session data, not just `user_id`
- Session data is minimal — only what is needed for every request (`user_id`, `username`)
- Redirect already-logged-in users away from `/login` and `/register` to avoid confusion

```python
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
```

### Key Takeaway

The `secret_key` should be a long random string in production, stored in an environment variable — not hardcoded. In this project it was hardcoded for simplicity, which is a known improvement area.

---

## 5. Security Best Practices

### What Was Learned on This Project

**1. Parameterized Queries — SQL Injection Prevention**

Every database query used parameterized statements:

```python
# Correct
cursor.execute("SELECT * FROM tests WHERE id = %s AND user_id = %s", (test_id, user_id))

# Never do this
cursor.execute(f"SELECT * FROM tests WHERE id = {test_id}")
```

**2. User Data Isolation**

Every query was scoped to the logged-in user's `user_id`. A user can never read or modify another user's data:

```python
cursor.execute("DELETE FROM tests WHERE id = %s AND user_id = %s", (test_id, user_id))
```

Even if a user guesses another user's record ID, the `AND user_id = %s` clause prevents access.

**3. Environment Variables for Secrets**

The Gemini API key was stored in `.env` and loaded with `python-dotenv`:

```python
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```

**4. Input Validation**

Required fields were validated before database operations:

```python
if not username or not email or not password:
    error = "All fields are required."
elif password != confirm:
    error = "Passwords do not match."
```

### Key Takeaway

Security is not a feature added at the end — it is built into every query, every route, and every data access pattern from the start.

---

## 6. Database Design, Constraints, and Relationships

### What Was Learned

**Foreign Key Constraints with CASCADE:**

```sql
FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
```

`ON DELETE CASCADE` means deleting a test automatically deletes all its subjects, topics, and schedule entries. This prevents orphaned records without needing application-level cleanup.

**Data Ownership Pattern:**
The multi-user migration taught an important pattern — not every table needs a direct `user_id`. Topics are owned by subjects, which are owned by users. So topics are scoped via a JOIN:

```python
cursor.execute("""
    SELECT t.* FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE s.user_id = %s
""", (user_id,))
```

This avoids redundant `user_id` columns while maintaining correct data isolation.

**Migration Strategy:**
When adding `user_id` to existing tables, the migration used `DEFAULT 1` to assign existing data to the first user without breaking anything:

```sql
ALTER TABLE tests ADD COLUMN user_id INT NOT NULL DEFAULT 1,
    ADD CONSTRAINT fk_tests_user FOREIGN KEY (user_id) REFERENCES users(id);
```

**ENUM vs VARCHAR:**
The `missed` field used `ENUM('yes', 'no')` instead of a boolean. This was a deliberate schema decision to make the value self-documenting in the database.

**JSON Columns:**
`extracted_json` and `ai_report` in `ai_mocktest_reports` used MySQL's native `JSON` type, allowing structured data to be stored and queried without a separate table.

### Key Takeaway

Good database design reduces application complexity. Constraints, cascades, and proper relationships mean the database enforces data integrity — not just the application code.

---

## 7. Error Handling and Logging

### What Was Learned

**404 Responses for Missing Records:**

```python
if not topic:
    return jsonify({"error": "Topic not found"}), 404
```

**400 Responses for Invalid Input:**

```python
if entry_date > today or entry_date < week_ago:
    return jsonify({"error": "Missed can only be applied to entries within the past 7 days"}), 400
```

**Gemini API Error Handling:**

```python
if not response.text:
    raise ValueError("Gemini returned an empty response while extracting report data")
```

**PDF Extraction Guard:**

```python
raw_text = _extract_from_pdf(file)
if not raw_text:
    return jsonify({"error": "Could not extract text from PDF"}), 400
```

### What Could Be Improved

The current implementation does not have centralized logging. In a production system, every error should be logged with a timestamp, user context, and stack trace using Python's `logging` module or a service like AWS CloudWatch.

### Key Takeaway

Every external call (database, AI API, file parsing) can fail. Always validate the result before proceeding, and return meaningful HTTP status codes with descriptive error messages.

---

## 8. Code Review Practices

### What Was Learned on This Project

During development, several patterns emerged as common review feedback:

**1. Don't repeat yourself — extract shared logic**

The schedule generation logic was initially duplicated between `generate_schedule()` and `mark_missed()`. The fix was extracting it into `_run_generate(user_id)`:

```python
# Before — duplicated logic in two places
# After — single shared helper
def _run_generate(user_id):
    ...

@schedules_bp.route("/schedules/generate", methods=["POST"])
def generate_schedule():
    count = _run_generate(session.get("user_id"))
    return jsonify({"message": "Schedule generated", "entries_created": count}), 201
```

**2. Avoid using test_request_context as a workaround**

An early implementation tried to call `generate_schedule()` from `mark_missed()` using Flask's `test_request_context`. This was identified as a code smell — the correct fix was extracting the logic into a plain Python function.

**3. Batch database operations**

Instead of inserting schedule rows one at a time in a loop, `executemany` was used:

```python
cursor.executemany(
    "INSERT INTO schedule_entries (...) VALUES (%s, %s, %s, %s, %s)",
    rows_to_insert
)
```

**4. Close connections in all code paths**

Every route that opens a database connection must close it — including early return paths for error cases.

### Key Takeaway

Code review is not about finding fault — it is about sharing knowledge. Every review comment is a learning opportunity.

---

## 9. Performance Optimization

### What Was Learned

**1. Batch Inserts**
Schedule generation could insert hundreds of rows (one per topic per day across a date range). Using `executemany` instead of a loop of `execute` calls reduced database round trips significantly.

**2. Single Query with JOIN Instead of Multiple Queries**
The insights endpoint fetched all mock test data in a single JOIN query rather than fetching mock tests first and then looping to fetch topics:

```python
cursor.execute("""
    SELECT tp.id, tp.name, mt.test_date, mtt.marks_obtained, mtt.max_marks
    FROM MockTest_topics mtt
    JOIN MockTests mt ON mtt.mocktest_id = mt.id
    JOIN topics tp ON mtt.topic_id = tp.id
    WHERE mt.user_id = %s
    ORDER BY tp.id, mt.test_date ASC
""", (user_id,))
```

**3. Parallel API Calls in Frontend**
The dashboard used `$.when()` to fire multiple API calls in parallel instead of sequentially:

```javascript
$.when(
    $.get("/tests"),
    $.get("/mocktests")
).done(function(testsRes, mocktestsRes) { ... });
```

**4. Timezone-Safe Date Comparisons**
An early bug showed "Today" appearing twice in the schedule UI. The root cause was JavaScript's `new Date("2026-07-15")` parsing as UTC midnight while `new Date()` used local time. The fix was to work entirely with `YYYY-MM-DD` strings:

```javascript
function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
```

### Key Takeaway

Performance issues often come from N+1 query patterns (one query per item in a loop) and unnecessary sequential operations. Always look for opportunities to batch and parallelize.

---

## 10. Working with External APIs (Google Gemini)

### What Was Learned

**Prompt Engineering:**
The quality of Gemini's output depends entirely on the prompt. Two separate prompts were designed for this project:

- **Extraction prompt** — strict, asks for specific fields, instructs to return ONLY JSON
- **Analysis prompt** — contextual, provides current data + history, specifies exact output JSON structure

**Handling Markdown-Wrapped JSON:**
Gemini sometimes wraps JSON in markdown code blocks. A defensive parser was needed:

````python
raw = response.text.strip()
if raw.startswith("```"):
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
return json.loads(raw.strip())
````

**Validating API Responses:**

```python
if not response.text:
    raise ValueError("Gemini returned an empty response")
```

**Model Configuration via Environment:**

```python
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
```

Using an environment variable for the model name means switching models requires no code change.

### Key Takeaway

When integrating LLMs, always validate the response, handle formatting variations defensively, and keep prompts version-controlled alongside the code.

---

## 11. Feature Evolution — Key Decisions

| Decision                                                  | What Was Done                                                | Why                                                          |
| --------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Single user → Multi-user                                  | Added `users` table, `user_id` FK on all tables, bcrypt auth | Scale the tool for multiple students                         |
| `miss_penalty` as raw value → multiplied by missed count  | `miss_penalty * missed_count` in score formula               | More missed sessions = higher urgency = more hours allocated |
| `generate_schedule` duplicated → `_run_generate(user_id)` | Extracted shared helper                                      | DRY principle, called from both endpoint and `mark_missed`   |
| Manual mock test only → AI PDF upload                     | Added `ai_mocktest.py` with pdfplumber + Gemini              | Reduce manual data entry, enable richer analysis             |
| Hardcoded schedule start from tomorrow → include today    | Changed `today + timedelta(days=1)` to `today`               | Users wanted today's schedule generated immediately          |
| Boolean `missed` → `ENUM('yes','no')`                     | Schema used ENUM                                             | Self-documenting, matches MySQL convention in this schema    |

---

## 12. Summary of Engineering Practices Learned

| Practice               | How It Appeared in This Project                             |
| ---------------------- | ----------------------------------------------------------- |
| Modular architecture   | Flask Blueprints, one per domain                            |
| DRY principle          | `_run_generate()`, `_generate_insights()` as shared helpers |
| Parameterized SQL      | Every query uses `%s` placeholders                          |
| Data isolation         | `WHERE user_id = %s` on every query                         |
| Password security      | bcrypt hashing via flask-bcrypt                             |
| Environment variables  | `.env` for API keys, never in source code                   |
| Defensive API handling | Validate Gemini response, strip markdown wrappers           |
| Batch DB operations    | `executemany` for bulk inserts                              |
| HTTP semantics         | 200/201/400/404 used correctly                              |
| Frontend performance   | `$.when()` for parallel API calls                           |
| Timezone safety        | String-based date comparison in JavaScript                  |
| Migration strategy     | `DEFAULT 1` backfill for zero-downtime schema changes       |
| Code review mindset    | Extract logic, avoid workarounds, close all connections     |
