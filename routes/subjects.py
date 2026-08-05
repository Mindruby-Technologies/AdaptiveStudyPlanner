from flask import Blueprint, request, jsonify, session
from db import get_connection

subjects_bp = Blueprint("subjects", __name__)


@subjects_bp.route("/subjects", methods=["GET"])
def get_subjects():
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM subjects WHERE user_id = %s", (user_id,))
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(subjects)


@subjects_bp.route("/subjects/<int:subject_id>", methods=["GET"])
def get_subject(subject_id):
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM subjects WHERE id = %s AND user_id = %s", (subject_id, user_id))
    subject = cursor.fetchone()
    cursor.close()
    conn.close()
    if not subject:
        return jsonify({"error": "Subject not found"}), 404
    return jsonify(subject)


@subjects_bp.route("/subjects", methods=["POST"])
def create_subject():
    user_id = session.get("user_id")
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subjects (test_id, name, status, user_id) VALUES (%s, %s, %s, %s)",
        (data["test_id"], data["name"], data["status"], user_id)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Subject created"}), 201


@subjects_bp.route("/subjects/<int:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    user_id = session.get("user_id")
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE subjects SET test_id = %s, name = %s, status = %s WHERE id = %s AND user_id = %s",
        (data["test_id"], data["name"], data["status"], subject_id, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Subject updated"})


@subjects_bp.route("/subjects/<int:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id = %s AND user_id = %s", (subject_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Subject deleted"})
