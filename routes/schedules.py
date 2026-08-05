from flask import Blueprint, jsonify, request, session
from db import get_connection
from datetime import date, timedelta

schedules_bp = Blueprint("schedules", __name__)

DAILY_HOUR_LIMIT = 4
MIN_HOURS = 0.25


def _run_generate(user_id):
    today = date.today()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("DELETE FROM schedule_entries WHERE schedule_date > %s AND user_id = %s", (today, user_id))

    cursor.execute("""
        SELECT MIN(t.start_date) AS range_start, MAX(t.end_date) AS range_end
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.status = 'active' AND s.user_id = %s
    """, (user_id,))
    range_row = cursor.fetchone()
    if not range_row["range_start"]:
        conn.commit()
        cursor.close()
        conn.close()
        return 0

    range_start = max(range_row["range_start"], today)
    range_end = range_row["range_end"]

    if range_start > range_end:
        conn.commit()
        cursor.close()
        conn.close()
        return 0

    rows_to_insert = []
    current_date = range_start

    while current_date <= range_end:
        cursor.execute("""
            SELECT t.id, t.difficulty_level, t.priority_level, t.miss_penalty, t.start_date, t.end_date,
                   COUNT(se.id) AS missed_count
            FROM topics t
            JOIN subjects s ON t.subject_id = s.id
            LEFT JOIN schedule_entries se ON se.topic_id = t.id AND se.missed = 'yes' AND se.user_id = %s
            WHERE t.status = 'active' AND t.start_date <= %s AND t.end_date >= %s AND s.user_id = %s
            GROUP BY t.id
        """, (user_id, current_date, current_date, user_id))
        topics = cursor.fetchall()

        if topics:
            scored = []
            for t in topics:
                days_left = max((t["end_date"] - t["start_date"]).days, 1)
                score = (10 / days_left) + (t["difficulty_level"] * 2) + (t["priority_level"] * 3) + (t["miss_penalty"] * t["missed_count"])
                scored.append((t["id"], score))

            scored.sort(key=lambda x: x[1], reverse=True)
            total_score = sum(s for _, s in scored)

            for topic_id, score in scored:
                weight = score / total_score
                allocated = round(max(weight * DAILY_HOUR_LIMIT, MIN_HOURS) * 4) / 4
                rows_to_insert.append((topic_id, current_date, allocated, 'no', user_id))

        current_date += timedelta(days=1)

    if rows_to_insert:
        cursor.executemany(
            "INSERT INTO schedule_entries (topic_id, schedule_date, allocated_hours, missed, user_id) VALUES (%s, %s, %s, %s, %s)",
            rows_to_insert
        )

    conn.commit()
    cursor.close()
    conn.close()
    return len(rows_to_insert)


@schedules_bp.route("/schedules/generate", methods=["POST"])
def generate_schedule():
    count = _run_generate(session.get("user_id"))
    return jsonify({"message": "Schedule generated", "entries_created": count}), 201


@schedules_bp.route("/schedules", methods=["GET"])
def get_schedules():
    user_id = session.get("user_id")
    schedule_date = request.args.get("date", str(date.today()))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT se.id, se.topic_id, t.name AS topic_name, se.allocated_hours, se.missed
        FROM schedule_entries se
        JOIN topics t ON t.id = se.topic_id
        WHERE se.schedule_date = %s AND se.user_id = %s
        ORDER BY se.allocated_hours DESC
    """, (schedule_date, user_id))
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(entries)


@schedules_bp.route("/schedules/<int:entry_id>/missed", methods=["PATCH"])
def mark_missed(entry_id):
    user_id = session.get("user_id")
    today = date.today()
    week_ago = today - timedelta(days=7)
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT schedule_date FROM schedule_entries WHERE id = %s AND user_id = %s", (entry_id, user_id))
    entry = cursor.fetchone()
    if not entry:
        cursor.close()
        conn.close()
        return jsonify({"error": "Entry not found"}), 404

    entry_date = entry["schedule_date"]
    if entry_date > today or entry_date < week_ago:
        cursor.close()
        conn.close()
        return jsonify({"error": "Missed can only be applied to entries within the past 7 days"}), 400

    cursor.execute("UPDATE schedule_entries SET missed = 'yes' WHERE id = %s AND user_id = %s", (entry_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    _run_generate(user_id)
    return jsonify({"message": "Marked as missed and schedule regenerated"})
