import os
import json
import pdfplumber
from google import genai
from flask import Blueprint, request, jsonify, session
from db import get_connection
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL","gemini-2.5-flash")

ai_mocktest_bp = Blueprint("ai_mocktest", __name__)


def _extract_from_pdf(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def _gemini_extract(raw_text: str) -> dict:
    prompt = f"""
You are a score report parser. Extract the following fields from the test report text below and return ONLY valid JSON, no explanation.

Extract:
- student_name
- grade
- test_name
- test_date (YYYY-MM-DD format)
- total_score (integer)
- score_range (e.g. "320-1520")
- percentile (e.g. "66th")
- section_scores: array of {{ section, score, range, percentile }}
- knowledge_areas: array of {{ topic, marks_obtained, max_marks, percentage }}

Report Text:
{raw_text}

Return ONLY JSON.
"""
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    if not response.text:
        raise ValueError("Gemini returned an empty response while extracting report data")
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _fetch_history(test_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    user_id = session.get("user_id")

    # Last 5 from manual MockTests
    cursor.execute("""
        SELECT mt.id, mt.name AS test_name, mt.test_date AS record_date,
               'manual' AS source,
               JSON_ARRAYAGG(JSON_OBJECT(
                   'topic', tp.name,
                   'marks_obtained', mtt.marks_obtained,
                   'max_marks', mtt.max_marks,
                   'percentage', ROUND((mtt.marks_obtained / mtt.max_marks) * 100, 1)
               )) AS topics_json
        FROM MockTests mt
        JOIN MockTest_topics mtt ON mtt.mocktest_id = mt.id
        JOIN topics tp ON tp.id = mtt.topic_id
        WHERE mt.test_id = %s AND mt.user_id = %s
        GROUP BY mt.id
        ORDER BY mt.test_date DESC
        LIMIT 5
    """, (test_id, user_id))
    manual = cursor.fetchall()

    # Last 5 from ai_mocktest_reports
    cursor.execute("""
        SELECT id, test_name, uploaded_at AS record_date,
               'ai' AS source, extracted_json AS topics_json
        FROM ai_mocktest_reports
        WHERE test_id = %s AND user_id = %s AND status = 'processed'
        ORDER BY uploaded_at DESC
        LIMIT 5
    """, (test_id, user_id))
    ai_records = cursor.fetchall()

    cursor.close()
    conn.close()

    # Combine, sort by date, take top 5
    combined = []
    for r in manual:
        combined.append({
            "source": "manual",
            "test_name": r["test_name"],
            "record_date": str(r["record_date"]),
            "topics": json.loads(r["topics_json"]) if isinstance(r["topics_json"], str) else r["topics_json"]
        })
    for r in ai_records:
        extracted = r["topics_json"]
        if isinstance(extracted, str):
            extracted = json.loads(extracted)
        combined.append({
            "source": "ai",
            "test_name": r["test_name"],
            "record_date": str(r["record_date"]),
            "topics": extracted.get("knowledge_areas", []) if isinstance(extracted, dict) else [],
            "section_scores": extracted.get("section_scores", []) if isinstance(extracted, dict) else [],
            "total_score": extracted.get("total_score"),
            "percentile": extracted.get("percentile")
        })

    combined.sort(key=lambda x: x["record_date"], reverse=True)
    return combined[:5]


def _gemini_report(extracted: dict, history: list) -> dict:
    history_text = json.dumps(history, indent=2) if history else "No previous records available."
    prompt = f"""
You are an expert academic performance analyzer. Analyze the student's current test report and compare it with their historical records.

Current Report:
{json.dumps(extracted, indent=2)}

Historical Records (last 5, mixed manual and AI-extracted):
{history_text}

Note: Manual records contain only topic-level marks. AI records contain topic-level marks, section scores and percentile. Use available data for comparison and skip missing fields gracefully.

Return ONLY valid JSON in this exact format:
{{
  "overall_summary": "2-3 sentence summary of overall performance",
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "trend_summary": "comparison with previous attempts",
  "focus_areas": ["topic1", "topic2"],
  "section_analysis": [
    {{"section": "Reading and Writing", "analysis": "brief analysis"}},
    {{"section": "Math", "analysis": "brief analysis"}}
  ],
  "topic_insights": [
    {{"topic": "Algebra", "status": "improving|declining|stable", "note": "brief note"}}
  ]
}}
"""
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    if not response.text:
        raise ValueError("Gemini returned an empty response while generating the AI report")
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


@ai_mocktest_bp.route("/mocktests/ai-analyze", methods=["POST"])
def ai_analyze():
    test_id = request.form.get("test_id")
    file = request.files.get("file")

    if not test_id or not file:
        return jsonify({"error": "test_id and file are required"}), 400

    # Extract text from PDF
    raw_text = _extract_from_pdf(file)
    if not raw_text:
        return jsonify({"error": "Could not extract text from PDF"}), 400

    # Gemini: extract structured data
    extracted = _gemini_extract(raw_text)

    user_id = session.get("user_id")

    # Save as pending
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ai_mocktest_reports
        (test_id, user_id, student_name, grade, test_name, test_date, total_score, score_range, percentile, extracted_json, file_name, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
    """, (
        test_id,
        user_id,
        extracted.get("student_name"),
        extracted.get("grade"),
        extracted.get("test_name"),
        extracted.get("test_date"),
        extracted.get("total_score"),
        extracted.get("score_range"),
        extracted.get("percentile"),
        json.dumps(extracted),
        file.filename
    ))
    report_id = cursor.lastrowid
    conn.commit()

    # Fetch history for this test
    history = _fetch_history(int(test_id))

    # Gemini: generate AI report
    ai_report = _gemini_report(extracted, history)

    # Update with report
    cursor.execute("""
        UPDATE ai_mocktest_reports SET ai_report = %s, status = 'processed' WHERE id = %s
    """, (json.dumps(ai_report), report_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "report_id": report_id,
        "extracted": extracted,
        "ai_report": ai_report
    }), 201


@ai_mocktest_bp.route("/mocktests/ai-reports", methods=["GET"])
def get_ai_reports():
    test_id = request.args.get("test_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    user_id = session.get("user_id")
    query = """
        SELECT r.id, r.student_name, r.grade, r.test_name, r.test_date,
               r.total_score, r.score_range, r.percentile,
               r.extracted_json, r.ai_report, r.file_name, r.uploaded_at, r.status,
               t.name AS linked_test_name
        FROM ai_mocktest_reports r
        JOIN tests t ON t.id = r.test_id
        WHERE r.user_id = %s
    """
    params = [user_id]
    if test_id:
        query += " AND r.test_id = %s"
        params.append(test_id)
    query += " ORDER BY r.uploaded_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    for r in rows:
        for f in ("extracted_json", "ai_report"):
            if r.get(f) and isinstance(r[f], str):
                r[f] = json.loads(r[f])
        for f in ("test_date", "uploaded_at"):
            if r.get(f):
                r[f] = str(r[f])[:10]
    cursor.close()
    conn.close()
    return jsonify(rows)
