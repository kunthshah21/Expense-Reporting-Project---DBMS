# db/init_db.py

import sys
import os
# Add the project root directory to the system path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db import get_db_connection, initialize_db

def init():
    print("Initializing the SQLite database...")
    conn = get_db_connection()
    initialize_db(conn)
    conn.close()
    print("SQLite database initialized successfully.")

if __name__ == "__main__":
    init()
