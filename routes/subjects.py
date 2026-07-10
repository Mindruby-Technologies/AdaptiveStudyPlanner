from flask import Blueprint, request, jsonify
from db import get_connection

subjects_bp = Blueprint("subjects", __name__)


@subjects_bp.route("/subjects", methods=["GET"])
def get_subjects():
    """
    GET /subjects
    Retrieve all subjects from the database.
    Returns a list of subject records.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(subjects)


@subjects_bp.route("/subjects/<int:subject_id>", methods=["GET"])
def get_subject(subject_id):
    """
    GET /subjects/<subject_id>
    Retrieve a single subject by its ID.
    Returns 404 if the subject does not exist.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM subjects WHERE id = %s", (subject_id,))
    subject = cursor.fetchone()
    cursor.close()
    conn.close()
    if not subject:
        return jsonify({"error": "Subject not found"}), 404
    return jsonify(subject)


@subjects_bp.route("/subjects", methods=["POST"])
def create_subject():
    """
    POST /subjects
    Create a new subject linked to a test.
    Request body: { "test_id": int, "name": str, "status": "active"|"inactive" }
    Returns the new record's ID on success with 201 status.
    """
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subjects (test_id, name, status) VALUES (%s, %s, %s)",
        (data["test_id"], data["name"], data["status"])
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Subject created"}), 201


@subjects_bp.route("/subjects/<int:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    """
    PUT /subjects/<subject_id>
    Update an existing subject by its ID.
    Request body: { "test_id": int, "name": str, "status": "active"|"inactive" }
    """
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE subjects SET test_id = %s, name = %s, status = %s WHERE id = %s",
        (data["test_id"], data["name"], data["status"], subject_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Subject updated"})


@subjects_bp.route("/subjects/<int:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    """
    DELETE /subjects/<subject_id>
    Delete a subject record by its ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id = %s", (subject_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Subject deleted"})
