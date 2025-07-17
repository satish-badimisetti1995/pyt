import pandas as pd
import uuid
import os
import sqlite3
import sys
from datetime import datetime
from db_setup import get_db_connection

OUTPUT_FOLDER = "parquet_outputs"

def run_query_by_id(archive_query_id):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch query details for provided ID
    cursor.execute("SELECT archive_query, data_file_name FROM archive_config WHERE archive_query_id = ?", (archive_query_id,))
    result = cursor.fetchone()

    if not result:
        print(f"No archive_config found with archive_query_id {archive_query_id}")
        conn.close()
        return

    query, base_filename = result

    try:
        df = pd.read_sql_query(query, conn)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{base_filename}_{timestamp}_{uuid.uuid4().hex}.parquet"
        filepath = os.path.join(OUTPUT_FOLDER, unique_filename)

        df.to_parquet(filepath)
        print(f"Data written to {filepath}")

        # Insert status record
        cursor.execute("""
            INSERT INTO archive_status (archive_query_id, schedule, extract_mode, status)
            VALUES (?, ?, ?, ?)
        """, (archive_query_id, 'Manual', 'Full', 'Completed'))

        conn.commit()
        print(f"Status inserted for archive_query_id: {archive_query_id}")

    except Exception as e:
        print(f"Error executing query {query}: {e}")

    conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_queries_to_parquet.py <archive_query_id>")
        sys.exit(1)

    try:
        archive_query_id = int(sys.argv[1])
        run_query_by_id(archive_query_id)
    except ValueError:
        print("Please provide a valid integer archive_query_id.")
