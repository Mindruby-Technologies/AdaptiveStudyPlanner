from flask import Blueprint, request, jsonify
from db import get_connection

topics_bp = Blueprint("topics", __name__)

@topics_bp.route("/topics", methods=["GET"])
def get_topics():
    """
    GET /topics
    Retrieve all topics from the database.
    Returns a list of topic records.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM topics")
    topics = cursor.fetchall()
    cursor.close()
    conn.close()
    for t in topics:
        for field in ("start_date", "end_date", "created_at"):
            if t.get(field):
                t[field] = str(t[field])[:10]
    return jsonify(topics)


@topics_bp.route("/topics/<int:topic_id>", methods=["GET"])
def get_topic(topic_id):
    """
    GET /topics/<topic_id>
    Retrieve a single topic by its ID.
    Returns 404 if the topic does not exist.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM topics WHERE id = %s", (topic_id,))
    topic = cursor.fetchone()
    cursor.close()
    conn.close()
    if not topic:
        return jsonify({"error": "Topic not found"}), 404
    return jsonify(topic)


@topics_bp.route("/topics", methods=["POST"])
def create_topic():
    """
    POST /topics
    Create a new topic linked to a subject.
    Request body: {
        "subject_id": int,
        "name": str,
        "difficulty_level": int (tinyint),
        "priority_level": int (tinyint),
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "miss_penalty": int (optional, default 0),
        "status": "active"|"inactive" (optional, default "active")
    }
    Returns the new record's ID on success with 201 status.
    """
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
    """
    PUT /topics/<topic_id>
    Update an existing topic by its ID.
    Request body: {
        "subject_id": int,
        "name": str,
        "difficulty_level": int (tinyint),
        "priority_level": int (tinyint),
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "miss_penalty": int (optional, default 0),
        "status": "active"|"inactive" (optional, default "active")
    }
    """
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE topics SET subject_id = %s, name = %s, difficulty_level = %s, priority_level = %s,
           start_date = %s, end_date = %s, miss_penalty = %s, status = %s WHERE id = %s""",
        (data["subject_id"], data["name"], data["difficulty_level"], data["priority_level"],
         data["start_date"], data["end_date"], data.get("miss_penalty", 0), data.get("status", "active"), topic_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Topic updated"})


@topics_bp.route("/topics/<int:topic_id>", methods=["DELETE"])
def delete_topic(topic_id):
    """
    DELETE /topics/<topic_id>
    Delete a topic record by its ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM topics WHERE id = %s", (topic_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Topic deleted"})
