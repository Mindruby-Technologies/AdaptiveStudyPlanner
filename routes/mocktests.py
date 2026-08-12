from flask import Blueprint, request, jsonify, session
from db import get_connection

mocktests_bp = Blueprint("mocktests", __name__)


@mocktests_bp.route("/mocktests/insights", methods=["GET"])
def get_insights():
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT tp.id AS topic_id, tp.name AS topic_name,
               mt.id AS mocktest_id, mt.name AS mocktest_name,
               mt.test_date, mtt.marks_obtained, mtt.max_marks
        FROM MockTest_topics mtt
        JOIN MockTests mt ON mtt.mocktest_id = mt.id
        JOIN topics tp ON mtt.topic_id = tp.id
        WHERE mt.user_id = %s
        ORDER BY tp.id, mt.test_date ASC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    score_map = {}
    for r in rows:
        tid = r["topic_id"]
        if tid not in score_map:
            score_map[tid] = {"topic_name": r["topic_name"], "entries": []}
        mo = float(r["marks_obtained"])
        mm = float(r["max_marks"])
        pct = round((mo / mm) * 100, 2) if mm else 0
        score_map[tid]["entries"].append({
            "mocktest_id": r["mocktest_id"],
            "mocktest_name": r["mocktest_name"],
            "test_date": str(r["test_date"])[:10],
            "marks_obtained": mo,
            "max_marks": mm,
            "pct": pct
        })

    insights = _generate_insights(score_map)
    return jsonify({"score_map": score_map, "insights": insights})


def _generate_insights(score_map):
    if not score_map:
        return {}

    avg_scores = {}
    for tid, data in score_map.items():
        entries = data["entries"]
        avg_scores[tid] = {
            "topic_name": data["topic_name"],
            "avg": round(sum(e["pct"] for e in entries) / len(entries), 2),
            "entries": entries
        }

    sorted_by_avg = sorted(avg_scores.values(), key=lambda x: x["avg"])
    highest = sorted_by_avg[-1]
    lowest = sorted_by_avg[0]

    most_improved = None
    most_improved_delta = None
    for tid, data in score_map.items():
        entries = data["entries"]
        if len(entries) >= 2:
            delta = entries[-1]["pct"] - entries[0]["pct"]
            if most_improved_delta is None or delta > most_improved_delta:
                most_improved_delta = delta
                most_improved = {"topic_name": data["topic_name"], "delta": round(delta, 2)}

    declining = [
        {"topic_name": data["topic_name"],
         "delta": round(data["entries"][-1]["pct"] - data["entries"][0]["pct"], 2)}
        for data in score_map.values()
        if len(data["entries"]) >= 2 and data["entries"][-1]["pct"] < data["entries"][0]["pct"]
    ]

    focus_areas = [
        {"topic_name": d["topic_name"], "avg": d["avg"]}
        for d in sorted_by_avg if d["avg"] < 60
    ]

    consistency = []
    for tid, data in score_map.items():
        entries = data["entries"]
        if len(entries) >= 2:
            avg = sum(e["pct"] for e in entries) / len(entries)
            std = round((sum((e["pct"] - avg) ** 2 for e in entries) / len(entries)) ** 0.5, 2)
            consistency.append({"topic_name": data["topic_name"], "std": std, "avg": round(avg, 2)})
    consistency.sort(key=lambda x: x["std"])

    return {
        "highest": {"topic_name": highest["topic_name"], "avg": highest["avg"]},
        "lowest": {"topic_name": lowest["topic_name"], "avg": lowest["avg"]},
        "averages": [{"topic_name": d["topic_name"], "avg": d["avg"]} for d in sorted_by_avg],
        "most_improved": most_improved,
        "declining": declining,
        "focus_areas": focus_areas,
        "consistency": consistency
    }


@mocktests_bp.route("/mocktests", methods=["GET"])
def get_mocktests():
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT mt.*, t.name AS test_name,
               COALESCE(SUM(mtt.marks_obtained), 0) AS total_obtained,
               COALESCE(SUM(mtt.max_marks), 0) AS total_max
        FROM MockTests mt
        JOIN tests t ON mt.test_id = t.id
        LEFT JOIN MockTest_topics mtt ON mtt.mocktest_id = mt.id
        WHERE mt.user_id = %s
        GROUP BY mt.id
        ORDER BY mt.id DESC
    """, (user_id,))
    mocktests = cursor.fetchall()
    for m in mocktests:
        for field in ("test_date", "created_at", "modified_at"):
            if m.get(field):
                m[field] = str(m[field])[:10]
    cursor.close()
    conn.close()
    return jsonify(mocktests)


@mocktests_bp.route("/mocktests/<int:mocktest_id>", methods=["GET"])
def get_mocktest(mocktest_id):
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM MockTests WHERE id = %s AND user_id = %s", (mocktest_id, user_id))
    mocktest = cursor.fetchone()
    if not mocktest:
        cursor.close()
        conn.close()
        return jsonify({"error": "Mock test not found"}), 404
    for field in ("test_date", "created_at", "modified_at"):
        if mocktest.get(field):
            mocktest[field] = str(mocktest[field])[:10]
    cursor.execute("SELECT * FROM MockTest_topics WHERE mocktest_id = %s", (mocktest_id,))
    mocktest["topics"] = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(mocktest)


@mocktests_bp.route("/mocktests", methods=["POST"])
def create_mocktest():
    user_id = session.get("user_id")
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO MockTests (name, test_date, test_id, user_id) VALUES (%s, %s, %s, %s)",
        (data["name"], data["test_date"], data["test_id"], user_id)
    )
    mocktest_id = cursor.lastrowid
    for topic in data.get("topics", []):
        cursor.execute(
            "INSERT INTO MockTest_topics (mocktest_id, topic_id, marks_obtained, max_marks) VALUES (%s, %s, %s, %s)",
            (mocktest_id, topic["topic_id"], topic["marks_obtained"], topic["max_marks"])
        )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"id": mocktest_id, "message": "Mock test created"}), 201


@mocktests_bp.route("/mocktests/<int:mocktest_id>", methods=["PUT"])
def update_mocktest(mocktest_id):
    user_id = session.get("user_id")
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE MockTests SET name = %s, test_date = %s, test_id = %s WHERE id = %s AND user_id = %s",
        (data["name"], data["test_date"], data["test_id"], mocktest_id, user_id)
    )
    cursor.execute("DELETE FROM MockTest_topics WHERE mocktest_id = %s", (mocktest_id,))
    for topic in data.get("topics", []):
        cursor.execute(
            "INSERT INTO MockTest_topics (mocktest_id, topic_id, marks_obtained, max_marks) VALUES (%s, %s, %s, %s)",
            (mocktest_id, topic["topic_id"], topic["marks_obtained"], topic["max_marks"])
        )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Mock test updated"})


@mocktests_bp.route("/mocktests/<int:mocktest_id>", methods=["DELETE"])
def delete_mocktest(mocktest_id):
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM MockTests WHERE id = %s AND user_id = %s", (mocktest_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Mock test deleted"})
