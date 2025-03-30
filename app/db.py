import sqlite3

def get_db_connection():
    conn = sqlite3.connect("expense_report.db")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        uid INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('Admin', 'User')) NOT NULL
    )
    """)

    # Check if an admin already exists
    cursor.execute("SELECT * FROM users WHERE role='Admin'")
    admin_exists = cursor.fetchone()

    if not admin_exists:
        # Insert default admin (Username: admin, Password: admin123)
        cursor.execute("""
        INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'Admin')
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized with default admin (Username: admin, Password: admin123)")
