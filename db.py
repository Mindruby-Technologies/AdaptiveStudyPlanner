import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "adaptive_study_planner",
    "use_pure": True
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
