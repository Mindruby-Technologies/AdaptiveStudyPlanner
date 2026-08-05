# Knowledge Base — Learning Journey: Intern to Contributor

**Project:** Adaptive Study Planner
**Owner:** Aditi Danani
**Document Type:** Developer Learning Journey

---

## Overview

This document captures my learning journey as an intern while contributing to the Adaptive Study Planner project. It highlights the engineering concepts, best practices, and real-world development experience I gained throughout the project—from understanding the initial single-user Flask application to helping build and enhance it into a scalable, multi-user, AI-powered study platform.

---

## 1. Understanding the Project Structure

### What Was Learned

The first task was understanding how a real Flask project is organized. Unlike tutorial projects where everything lives in a single file, this project used **Flask Blueprints** to separate concerns.

```
app.py                ← entry point, registers blueprints
routes/auth.py        ← authentication logic
routes/tests.py       ← tests CRUD
routes/subjects.py    ← subjects CRUD
routes/topics.py      ← topics CRUD
routes/schedules.py   ← schedule generation
routes/mocktests.py   ← mock test tracking and insights
routes/ai_mocktest.py ← AI PDF analysis (added later)
templates/            ← Jinja2 HTML templates
migrations/           ← SQL schema files
```

### Key Takeaway

Each Blueprint is a self-contained module. `app.py` is kept clean — it only registers blueprints and defines UI routes. Business logic never lives in `app.py`.

### Coding Standards Observed

- Snake_case for Python functions and variables
- Blueprint names match their file names (`tests_bp`, `subjects_bp`)
- Helper functions prefixed with `_` (e.g., `_run_generate`, `_generate_insights`) to indicate they are internal
- Multi-line triple-quoted strings for all SQL — no inline one-liners for complex queries

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
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
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

## 11. Building the LLM-Based Test Report Analyzer

This was the most complex feature added during the internship. It replaced the need to manually type marks from a PDF score report by letting Gemini read the PDF and extract the data automatically, then generate a personalized improvement report by comparing it against historical records.

### 11.1 Why This Feature Was Added

The manual mock test entry system worked well but had a friction point: students receive PDF score reports (e.g., PSAT practice reports) and had to manually re-enter every topic score into the system. This was tedious and error-prone. The goal was to upload the PDF directly and let the AI handle extraction and analysis.

Importantly, the manual entry system was **not replaced** — it was kept as-is. The AI analyzer was added as a second tab on the same Performance Analyzer page, so users could choose either approach. Manual records and AI-extracted records both feed into the same historical comparison pool.

### 11.2 The Two-Step AI Pipeline

The feature was designed as a two-step pipeline, each step being a separate Gemini call:

```
Step 1 — Extraction
PDF file → pdfplumber → raw text → Gemini → structured JSON
(student_name, grade, test_name, test_date, total_score,
 score_range, percentile, section_scores[], knowledge_areas[])

Step 2 — Analysis
extracted JSON + last 5 historical records → Gemini → AI report JSON
(overall_summary, strengths[], weaknesses[],
 recommendations[], trend_summary, focus_areas[],
 section_analysis[], topic_insights[])
```

Separating extraction from analysis was a deliberate design decision — if extraction succeeds but analysis fails, the extracted data is already saved with `status = 'pending'` and the analysis can be retried without re-parsing the PDF.

### 11.3 PDF Parsing with pdfplumber

```python
def _extract_from_pdf(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
```

`pdfplumber` extracts raw text from each page. The text is then passed to Gemini — the LLM handles interpretation of the layout, so no custom table parsing logic was needed.

### 11.4 Designing the Extraction Prompt

The extraction prompt was strict and explicit:

```
You are a score report parser. Extract the following fields from the test
report text below and return ONLY valid JSON, no explanation.

Extract:
- student_name
- grade
- test_name
- test_date (YYYY-MM-DD format)
- total_score (integer)
- score_range (e.g. "320-1520")
- percentile (e.g. "66th")
- section_scores: array of { section, score, range, percentile }
- knowledge_areas: array of { topic, marks_obtained, max_marks, percentage }

Return ONLY JSON.
```

Key lessons from prompt design:

- Say "Return ONLY JSON" explicitly — without this, Gemini adds explanatory text before the JSON
- Specify date format (`YYYY-MM-DD`) — otherwise dates come back in inconsistent formats
- Define the exact array structure with field names — Gemini follows schemas reliably when given examples

### 11.5 Combining Manual and AI History

The most interesting engineering challenge was the history fetch. The last 5 records needed to come from **both** the manual `MockTests` table and the `ai_mocktest_reports` table, combined and sorted by datetime, scoped to the same `test_id` and `user_id`:

```python
# Fetch up to 5 from manual MockTests for this test + user
# Fetch up to 5 from ai_mocktest_reports for this test + user
# Combine both lists into one
# Sort by record_date descending
# Return top 5 only
combined.sort(key=lambda x: x["record_date"], reverse=True)
return combined[:5]
```

Manual records only have topic-level marks. AI records have topic marks, section scores, and percentile. The analysis prompt instructed Gemini to use available data and skip missing fields gracefully — this avoided needing to normalize the two data sources before sending them to the LLM.

### 11.6 Scoping Reports to a Test

A key UX decision was requiring the user to select a **Test** from the dropdown before uploading a PDF. This meant:

- AI reports were linked to a specific `test_id` via FK
- History comparison was test-scoped — reports for one exam only compared with previous attempts of the same exam
- The `ai_mocktest_reports` table carried `test_id` as a FK to `tests`

Without this scoping, history from different exams would be mixed together, making trend analysis meaningless.

### 11.7 Storing Student Name and Grade

Even though the system is per-user, the PDF reports contain `student_name` and `grade` fields. These were stored in `ai_mocktest_reports` because:

- The PDF is the source of truth for who took the test and at what grade level
- It allows the AI report to reference the student by name in its analysis
- It preserves the original report metadata for future reference and audit

### 11.8 The status Field — pending/processed

The `status ENUM('pending', 'processed')` field in `ai_mocktest_reports` served as a processing state tracker:

```python
# Immediately after PDF extraction succeeds
INSERT INTO ai_mocktest_reports (..., status) VALUES (..., 'pending')

# After AI report generation succeeds
UPDATE ai_mocktest_reports SET ai_report = %s, status = 'processed' WHERE id = %s
```

This pattern ensures:

- If Gemini report generation fails after extraction, the record is preserved with `status = 'pending'`
- The history fetch only pulls `status = 'processed'` records — incomplete records are excluded from comparisons
- The processing state is always visible in the database for debugging

### Key Takeaway

Building an AI feature is not just about calling an API. It requires careful pipeline design, defensive response handling, thoughtful data modeling, and clear separation between extraction and analysis responsibilities.

---

## 12. Feature Evolution — Key Decisions

| Decision                                                    | What Was Done                                                | Why                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------- |
| Single user → Multi-user                                    | Added `users` table, `user_id` FK on all tables, bcrypt auth | Scale the tool for multiple students                          |
| `miss_penalty` as raw value → multiplied by missed count    | `miss_penalty * missed_count` in score formula               | More missed sessions = higher urgency = more hours allocated  |
| `generate_schedule` duplicated → `_run_generate(user_id)`   | Extracted shared helper                                      | DRY principle, called from both endpoint and `mark_missed`    |
| Manual mock test entry kept + AI PDF upload added           | Added `ai_mocktest.py` as a second tab, not a replacement    | Preserve existing workflow, add AI as an optional enhancement |
| Hardcoded schedule start from tomorrow → include today      | Changed `today + timedelta(days=1)` to `today`               | Users wanted today's schedule generated immediately           |
| Boolean `missed` → `ENUM('yes','no')`                       | Schema used ENUM                                             | Self-documenting, matches MySQL convention in this schema     |
| AI report history from one table → combined from two tables | `_fetch_history()` merges manual + AI records, top 5 by date | Richer comparison context regardless of how data was entered  |
| AI report scoped globally → scoped by test_id               | User selects Test before uploading PDF                       | Prevents cross-exam history mixing, makes trends meaningful   |

---

## 13. Summary of Engineering Practices Learned

| Practice               | How It Appeared in This Project                               |
| ---------------------- | ------------------------------------------------------------- |
| Modular architecture   | Flask Blueprints, one per domain                              |
| DRY principle          | `_run_generate()`, `_generate_insights()` as shared helpers   |
| Parameterized SQL      | Every query uses `%s` placeholders                            |
| Data isolation         | `WHERE user_id = %s` on every query                           |
| Password security      | bcrypt hashing via flask-bcrypt                               |
| Environment variables  | `.env` for API keys, never in source code                     |
| Defensive API handling | Validate Gemini response, strip markdown wrappers             |
| Batch DB operations    | `executemany` for bulk inserts                                |
| HTTP semantics         | 200/201/400/404 used correctly                                |
| Frontend performance   | `$.when()` for parallel API calls                             |
| Timezone safety        | String-based date comparison in JavaScript                    |
| Migration strategy     | `DEFAULT 1` backfill for zero-downtime schema changes         |
| Code review mindset    | Extract logic, avoid workarounds, close all connections       |
| AI pipeline design     | Separate extraction from analysis, use status field for state |
| Prompt engineering     | Explicit JSON-only instructions, typed field definitions      |
| Mixed data sources     | Normalize at the application layer, let LLM handle gaps       |
