from flask import Blueprint, request, jsonify, session
from db import get_connection

topics_bp = Blueprint("topics", __name__)


@topics_bp.route("/topics", methods=["GET"])
def get_topics():
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.* FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE s.user_id = %s
    """, (user_id,))
    topics = cursor.fetchall()
    cursor.close()
    conn.close()
    for t in topics:
        for field in ("start_date", "end_date", "created_at"):
            if t.get(field):
                t[field] = str(t[field])[:10]
    return jsonify(topics)


@topics_bp.route("/topics/by-test/<int:test_id>", methods=["GET"])
def get_topics_by_test(test_id):
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.* FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE s.test_id = %s AND s.user_id = %s
    """, (test_id, user_id))
    topics = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(topics)


@topics_bp.route("/topics/<int:topic_id>", methods=["GET"])
def get_topic(topic_id):
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.* FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.id = %s AND s.user_id = %s
    """, (topic_id, user_id))
    topic = cursor.fetchone()
    cursor.close()
    conn.close()
    if not topic:
        return jsonify({"error": "Topic not found"}), 404
    return jsonify(topic)


@topics_bp.route("/topics", methods=["POST"])
def create_topic():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO topics (subject_id, name, difficulty_level, priority_level, start_date, end_date, miss_penalty, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (data["subject_id"], data["name"], data["difficulty_level"], data["priority_level"],
         data["start_date"], data["end_date"], data.get("miss_penalty", 0), data.get("status", "active"))
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Topic created"}), 201


@topics_bp.route("/topics/<int:topic_id>", methods=["PUT"])
def update_topic(topic_id):
    user_id = session.get("user_id")
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE topics t JOIN subjects s ON t.subject_id = s.id
        SET t.subject_id = %s, t.name = %s, t.difficulty_level = %s, t.priority_level = %s,
            t.start_date = %s, t.end_date = %s, t.miss_penalty = %s, t.status = %s
        WHERE t.id = %s AND s.user_id = %s
    """, (data["subject_id"], data["name"], data["difficulty_level"], data["priority_level"],
          data["start_date"], data["end_date"], data.get("miss_penalty", 0), data.get("status", "active"),
          topic_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Topic updated"})


@topics_bp.route("/topics/<int:topic_id>", methods=["DELETE"])
def delete_topic(topic_id):
    user_id = session.get("user_id")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE t FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.id = %s AND s.user_id = %s
    """, (topic_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Topic deleted"})
