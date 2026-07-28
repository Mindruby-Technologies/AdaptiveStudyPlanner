from flask import Blueprint, request, jsonify
from db import get_connection

mocktests_bp = Blueprint("mocktests", __name__)


@mocktests_bp.route("/mocktests", methods=["GET"])
def get_mocktests():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT mt.*, t.name AS test_name,
               COALESCE(SUM(mtt.marks_obtained), 0) AS total_obtained,
               COALESCE(SUM(mtt.max_marks), 0) AS total_max
        FROM MockTests mt
        JOIN tests t ON mt.test_id = t.id
        LEFT JOIN MockTest_topics mtt ON mtt.mocktest_id = mt.id
        GROUP BY mt.id
        ORDER BY mt.id DESC
    """)
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
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM MockTests WHERE id = %s", (mocktest_id,))
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
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO MockTests (name, test_date, test_id) VALUES (%s, %s, %s)",
        (data["name"], data["test_date"], data["test_id"])
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
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE MockTests SET name = %s, test_date = %s, test_id = %s WHERE id = %s",
        (data["name"], data["test_date"], data["test_id"], mocktest_id)
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM MockTests WHERE id = %s", (mocktest_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Mock test deleted"})
