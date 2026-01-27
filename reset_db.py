
import sqlite3
import os
import sys

# Get DB path logic from config.py (simplified to avoid imports)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'contest_v2.db')

def reset_records():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}. Nothing to clear.")
        return

    print(f"Connecting to database at {DB_PATH}...", flush=True)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        
        if not tables:
            print("No tables found. Database usage assumes schema exists.")
        
        for table in tables:
            print(f"Clearing records from table: {table}")
            cursor.execute(f"DELETE FROM {table}")
            
        conn.commit()
        conn.close()
        print("Done! All records deleted successfully (Schema preserved).", flush=True)
        
    except Exception as e:
        print(f"Error clearing database: {e}")

if __name__ == "__main__":
    reset_records()
