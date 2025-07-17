import sqlite3
import os

DB_FILE = "archive_system.db"

def get_db_connection():
    return sqlite3.connect(DB_FILE)

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS archive_config (
        archive_query_id INTEGER PRIMARY KEY,
        archive_query TEXT NOT NULL,
        history_archive_query TEXT,
        data_file_name TEXT,
        table_name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS archive_status (
        archive_schedule_config_id INTEGER PRIMARY KEY AUTOINCREMENT,
        archive_query_id INTEGER,
        schedule TEXT,
        extract_mode TEXT,
        status TEXT,
        FOREIGN KEY (archive_query_id) REFERENCES archive_config (archive_query_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM archive_config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO employee (name, department) VALUES ('Alice', 'HR'), ('Bob', 'Finance')")

        cursor.execute("""
            INSERT INTO archive_config (archive_query_id, archive_query, history_archive_query, data_file_name, table_name)
            VALUES (1, 'SELECT * FROM employee', 'Historical archive', 'employee_data', 'employee')
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
