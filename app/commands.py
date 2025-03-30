# app/commands.py
from app.db import get_db_connection

current_user = {'uid': None, 'username': None, 'role': None}

# User Authentication
def login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uid, password, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        print("Error: User not found.")
        return
    if password == user[1]:  # Plain text password comparison
        current_user['uid'] = user[0]
        current_user['username'] = username
        current_user['role'] = user[2]
        print(f"Logged in as {username} ({user[2]})")
    else:
        print("Error: Incorrect password.")

def logout():
    current_user.update({'uid': None, 'username': None, 'role': None})
    print("Logged out.")

# User Management
def add_user(username, password, role):
    if current_user['role'] != 'Admin':
        print("Permission denied. Only Admins can add users.")
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  (username, password, role))  # Storing plain text password
    conn.commit()
    print(f"User {username} added.")
    conn.close()

def list_users():
    if current_user['role'] != 'Admin':
        print("Permission denied.")
        return
    conn = get_db_connection()
    users = conn.execute("SELECT uid, username, role FROM users").fetchall()
    for u in users:
        print(f"ID: {u[0]}, Username: {u[1]}, Role: {u[2]}")
    conn.close()

# Expense Management
def add_expense(amount, category_name, payment_method, date, description, tags):
    if not current_user['uid']:
        print("Login required.")
        return
    try:
        conn = get_db_connection()
        # Get category ID
        cid = conn.execute("SELECT cid FROM categories WHERE category_name = ?", 
                          (category_name,)).fetchone()[0]
        # Get payment method ID
        pid = conn.execute("SELECT pid FROM payment_methods WHERE method = ?", 
                         (payment_method,)).fetchone()[0]
        # Insert expense
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_expenses (uid, date, amount, cid, description, pid)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (current_user['uid'], date, amount, cid, description, pid))
        eid = cursor.lastrowid
        # Insert tags
        for tag in tags.split(','):
            tid = conn.execute("SELECT tid FROM tags WHERE tag_name = ?", (tag,)).fetchone()[0]
            conn.execute("INSERT INTO expense_tag (eid, tid) VALUES (?, ?)", (eid, tid))
        conn.commit()
        print(f"Expense {eid} added.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# CSV Import/Export (stubs)
def import_expenses(file_path):
    print(f"Importing from {file_path}...")

def export_csv(file_path, sort_field):
    print(f"Exporting to {file_path} sorted by {sort_field}...")

# Reports (stubs)
def report_category_spending(category):
    print(f"Report: Spending on {category}")

# Helper functions
def get_category_id(name):
    conn = get_db_connection()
    cid = conn.execute("SELECT cid FROM categories WHERE category_name = ?", (name,)).fetchone()[0]
    conn.close()
    return cid
