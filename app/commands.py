# app/commands.py
from app.db import get_db_connection
import datetime

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
def add_user(username, password, role, email=None, phone=None):
    if current_user['role'] != 'Admin':
        print("Permission denied. Only Admins can add users.")
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, role, email, phone) VALUES (?, ?, ?, ?, ?)",
        (username, password, role, email, phone)
    )
    conn.commit()
    print(f"User {username} added.")
    conn.close()

def list_users():
    if current_user['role'] != 'Admin':
        print("Permission denied.")
        return
    conn = get_db_connection()
    users = conn.execute("SELECT uid, username, role, email, phone FROM users").fetchall()
    for u in users:
        print(f"ID: {u[0]}, Username: {u[1]}, Role: {u[2]}, Email: {u[3]}, Phone: {u[4]}")
    conn.close()

# Expense Management
def add_expense(amount, category_name, payment_method, timestamp, description, tags):
    if not current_user['uid']:
        print("Login required.")
        return
    try:
        conn = get_db_connection()
        # Get category ID
        cid = conn.execute("SELECT cid FROM categories WHERE name = ?", 
                          (category_name,)).fetchone()[0]
        # Get payment method ID
        pid = conn.execute("SELECT pid FROM payment_methods WHERE method = ?", 
                         (payment_method,)).fetchone()[0]
        # Insert expense
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_expenses (uid, timestamp, amount, cid, description, pid)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (current_user['uid'], timestamp, amount, cid, description, pid))
        eid = cursor.lastrowid
        # Insert tags
        for tag in tags.split(','):
            if tag.strip():
                tid = conn.execute("SELECT tid FROM tags WHERE name = ?", 
                                 (tag.strip(),)).fetchone()[0]
                conn.execute("INSERT INTO expense_tag (eid, tid) VALUES (?, ?)", (eid, tid))
        conn.commit()
        print(f"Expense {eid} added.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# Group Management
def create_group(name, description=None):
    if not current_user['uid']:
        print("Login required.")
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO groups (name, description) VALUES (?, ?)", 
                      (name, description))
        gid = cursor.lastrowid
        # Add current user to group
        cursor.execute("INSERT INTO user_group (gid, uid) VALUES (?, ?)", 
                      (gid, current_user['uid']))
        conn.commit()
        print(f"Group '{name}' created with ID {gid}.")
        return gid
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def add_user_to_group(username, group_name):
    if not current_user['uid']:
        print("Login required.")
        return
    try:
        conn = get_db_connection()
        # Get group ID
        gid_result = conn.execute("SELECT gid FROM groups WHERE name = ?", 
                               (group_name,)).fetchone()
        if not gid_result:
            print(f"Error: Group '{group_name}' not found.")
            return
        gid = gid_result[0]
        
        # Check if user is in the group
        is_in_group = conn.execute(
            "SELECT 1 FROM user_group WHERE gid = ? AND uid = ?", 
            (gid, current_user['uid'])
        ).fetchone()
        if not is_in_group:
            print("Error: You are not authorized to add users to this group.")
            return
        
        # Get user ID
        uid_result = conn.execute("SELECT uid FROM users WHERE username = ?", 
                               (username,)).fetchone()
        if not uid_result:
            print(f"Error: User '{username}' not found.")
            return
        uid = uid_result[0]
        
        # Add user to group
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_group (gid, uid) VALUES (?, ?)", (gid, uid))
        conn.commit()
        print(f"User '{username}' added to group '{group_name}'.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def add_group_expense(group_name, amount, category_name, payment_method, timestamp, description, split_list=None):
    if not current_user['uid']:
        print("Login required.")
        return
    try:
        conn = get_db_connection()
        # Get group ID
        gid_result = conn.execute("SELECT gid FROM groups WHERE name = ?", (group_name,)).fetchone()
        if not gid_result:
            print(f"Error: Group '{group_name}' not found.")
            return
        gid = gid_result[0]
        
        # Check if user is in the group
        is_in_group = conn.execute(
            "SELECT 1 FROM user_group WHERE gid = ? AND uid = ?", 
            (gid, current_user['uid'])
        ).fetchone()
        if not is_in_group:
            print("Error: You are not a member of this group.")
            return
        
        # Get category ID
        cid = conn.execute("SELECT cid FROM categories WHERE name = ?", 
                          (category_name,)).fetchone()[0]
        # Get payment method ID
        pid = conn.execute("SELECT pid FROM payment_methods WHERE method = ?", 
                         (payment_method,)).fetchone()[0]
        
        # Insert group expense
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO group_expense (gid, debtor_uid, timestamp, amount, cid, description, pid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (gid, current_user['uid'], timestamp, amount, cid, description, pid))
        geid = cursor.lastrowid
        
        # Handle split if provided
        if split_list:
            for split_entry in split_list:
                username, split_amount = split_entry.split(':')
                uid_result = conn.execute("SELECT uid FROM users WHERE username = ?", 
                                      (username,)).fetchone()
                if uid_result:
                    uid = uid_result[0]
                    cursor.execute(
                        "INSERT INTO split_users (geid, uid, split) VALUES (?, ?, ?)",
                        (geid, uid, float(split_amount))
                    )
                else:
                    print(f"Warning: User '{username}' not found, skipping split entry.")
        
        conn.commit()
        print(f"Group expense {geid} added to group '{group_name}'.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# CSV Import/Export (stubs)
def import_expenses(file_path):
    print(f"Importing from {file_path}...")

def export_csv(file_path, sort_field):
    print(f"Exporting to {file_path} sorted by {sort_field}...")

# Reports
def report_category_spending(category):
    print(f"Report: Spending on {category}")
    if not current_user['uid']:
        print("Login required.")
        return
    try:
        conn = get_db_connection()
        # Get category ID
        cid_result = conn.execute("SELECT cid FROM categories WHERE name = ?", 
                               (category,)).fetchone()
        if not cid_result:
            print(f"Error: Category '{category}' not found.")
            return
        cid = cid_result[0]
        
        # Get total spending for this category
        total = conn.execute("""
            SELECT SUM(amount) FROM user_expenses 
            WHERE uid = ? AND cid = ?
        """, (current_user['uid'], cid)).fetchone()[0]
        
        if total is None:
            total = 0
            
        print(f"Total spent on {category}: ${total:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
