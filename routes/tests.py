from flask import Blueprint, request, jsonify
from db import get_connection

tests_bp = Blueprint("tests", __name__)


@tests_bp.route("/tests", methods=["GET"])
def get_tests():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tests")
    tests = cursor.fetchall()
    cursor.close()
    conn.close()
    for t in tests:
        if t.get("exam_date"):
            t["exam_date"] = str(t["exam_date"])
        if t.get("created_at"):
            t["created_at"] = str(t["created_at"])[:10]
    return jsonify(tests)


@tests_bp.route("/tests/<int:test_id>", methods=["GET"])
def get_test(test_id):
    """
    GET /tests/<test_id>
    Retrieve a single test by its ID.
    Returns 404 if the test does not exist.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tests WHERE id = %s", (test_id,))
    test = cursor.fetchone()
    cursor.close()
    conn.close()
    if not test:
        return jsonify({"error": "Test not found"}), 404
    return jsonify(test)


@tests_bp.route("/tests", methods=["POST"])
def create_test():
    """
    POST /tests
    Create a new test record.
    Request body: { "name": str, "exam_date": "YYYY-MM-DD", "status": str }
    Returns the new record's ID on success with 201 status.
    """
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tests (name, exam_date, status) VALUES (%s, %s, %s)",
        (data["name"], data["exam_date"], data["status"])
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Test created"}), 201


@tests_bp.route("/tests/<int:test_id>", methods=["PUT"])
def update_test(test_id):
    """
    PUT /tests/<test_id>
    Update an existing test by its ID.
    Request body: { "name": str, "exam_date": "YYYY-MM-DD", "status": str }
    """
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tests SET name = %s, exam_date = %s, status = %s WHERE id = %s",
        (data["name"], data["exam_date"], data["status"], test_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Test updated"})


@tests_bp.route("/tests/<int:test_id>", methods=["DELETE"])
def delete_test(test_id):
    """
    DELETE /tests/<test_id>
    Delete a test record by its ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tests WHERE id = %s", (test_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Test deleted"})
