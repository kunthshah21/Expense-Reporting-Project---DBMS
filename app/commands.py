import sqlite3
from app.db import get_db_connection
import csv
from datetime import datetime

current_user = {'uid': None, 'username': None, 'role': None}

#region Authentication
def login(username, password):
    try:
        conn = get_db_connection()
        user = conn.execute("""
            SELECT * FROM users 
            WHERE username = ? AND password = ?
        """, (username, password)).fetchone()
        
        if user:
            current_user.update({
                'uid': user['uid'],
                'username': user['username'],
                'role': user['role']
            })
            return True
        return False
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False
    finally:
        conn.close()

def logout():
    current_user.clear()
#endregion

#region User Management
def add_user(username, password, role):
    try:
        if current_user.get('role') != 'Admin':
            return False
        
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (username, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Username already exists")
        return False
    finally:
        conn.close()

def list_users():
    try:
        if current_user.get('role') != 'Admin':
            return []
        
        conn = get_db_connection()
        return conn.execute("SELECT uid, username, role FROM users").fetchall()
    finally:
        conn.close()
#endregion

#region Category/Payment Methods
def add_category(name):
    try:
        if current_user.get('role') != 'Admin':
            return False
        
        conn = get_db_connection()
        conn.execute("INSERT INTO categories (category_name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Category already exists")
        return False
    finally:
        conn.close()

def add_payment_method(method):
    try:
        if current_user.get('role') != 'Admin':
            return False
        
        conn = get_db_connection()
        conn.execute("INSERT INTO payment_methods (method) VALUES (?)", (method,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Payment method already exists")
        return False
    finally:
        conn.close()
#endregion

#region Expense Management
def add_expense(amount, category, payment_method, date, description, tags):
    
    # category = category.strip().lower()
    # print(category)
    # payment_method = payment_method.strip().lower()
    # print(amount, category, payment_method, date, description, tags)

    try:
        if not current_user.get('uid'):
            print("Error: User not logged in.")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get category ID
        cid_result = conn.execute("""
            SELECT cid FROM categories 
            WHERE LOWER(category_name) = ?
        """, (category,)).fetchone()

        if not cid_result:
            print(f"Error: Category '{category}' not found.")
            return False

        print(f"Category Result: {cid_result}")        
        cid = cid_result[0]
        
        # Get payment method ID
        pid_result = conn.execute("""
            SELECT pid FROM payment_methods 
            WHERE LOWER(method) = ?
        """, (payment_method,)).fetchone()

        if not pid_result:
            print(f"Error: Payment method '{payment_method}' not found.")
            return False
        
        print(f"Payment Method Result: {pid_result}")       
        pid = pid_result[0]

        # Insert expense
        cursor.execute("""
            INSERT INTO expenses 
            (uid, amount, cid, pid, date, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (current_user['uid'], amount, cid, pid, date, description))

        eid = cursor.lastrowid

        # Handle multiple tags
        for tag in tags:
            tag_result = conn.execute("""
                SELECT tid FROM tags WHERE tag_name = ?
            """, (tag,)).fetchone()
            
            if not tag_result:
                conn.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag,))
                tid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            else:
                tid = tag_result[0]

            # Insert into expenses_tags table
            conn.execute("""
                INSERT INTO expenses_tags (eid, tid)
                VALUES (?, ?)
            """, (eid, tid))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding expense: {str(e)}")
        return False
    finally:
        conn.close()

def update_expense(expense_id, field, new_value):
    try:
        conn = get_db_connection()
        valid_fields = ['amount', 'date', 'description', 'tag']
        
        if field not in valid_fields:
            print("Invalid field")
            return False
        
        # Verify ownership
        expense = conn.execute("""
            SELECT uid FROM expenses 
            WHERE eid = ?
        """, (expense_id,)).fetchone()
        
        if not expense or expense['uid'] != current_user.get('uid'):
            print("Expense not found or permission denied")
            return False
        
        conn.execute(f"""
            UPDATE expenses 
            SET {field} = ?
            WHERE eid = ?
        """, (new_value, expense_id))
        conn.commit()
        return True
    finally:
        conn.close()

def delete_expense(expense_id):
    try:
        conn = get_db_connection()
        
        # Verify ownership
        expense = conn.execute("""
            SELECT uid FROM expenses 
            WHERE eid = ?
        """, (expense_id,)).fetchone()
        
        if not expense or expense['uid'] != current_user.get('uid'):
            print("Expense not found or permission denied")
            return False
        
        conn.execute("DELETE FROM expenses WHERE eid = ?", (expense_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def list_expenses(filters=None):
    try:
        conn = get_db_connection()
        query = """
            SELECT e.*, c.category_name, p.method 
            FROM expenses e
            JOIN categories c ON e.cid = c.cid
            JOIN payment_methods p ON e.pid = p.pid
            WHERE e.uid = ?
        """
        params = [current_user['uid']]
        
        if filters:
            query += " AND " + " AND ".join(f"{k} = ?" for k in filters.keys())
            params.extend(filters.values())
            
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()
#endregion

def add_tag(tag_name):
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag_name.strip().lower(),))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Tag '{tag_name}' already exists.")
        return False
    finally:
        conn.close()

def list_tags():
    try:
        conn = get_db_connection()
        tags = conn.execute("SELECT * FROM tags").fetchall()
        return tags
    finally:
        conn.close()

def delete_tag(tag_name):
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM tags WHERE tag_name = ?", (tag_name.strip().lower(),))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting tag: {str(e)}")
        return False
    finally:
        conn.close()
#endregion


#region Group Management
def create_group(group_name, description):
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO groups (group_name, description, date_created) VALUES (?, ?, date('now'))", (group_name, description))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Group '{group_name}' already exists.")
        return False
    finally:
        conn.close()

def add_user_to_group(username, group_name):
    try:
        # Check if current_user is logged in
        if not current_user or not current_user.get('uid'):
            print("Access denied: No user logged in.")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user ID and group ID
        uid = cursor.execute("SELECT uid FROM users WHERE username = ?", (username,)).fetchone()
        gid = cursor.execute("SELECT gid FROM groups WHERE group_name = ?", (group_name,)).fetchone()

        if not uid or not gid:
            print("User or Group not found.")
            return False

        uid, gid = uid[0], gid[0]

        # Check if the group is empty
        user_count = cursor.execute("SELECT COUNT(*) FROM user_group WHERE gid = ?", (gid,)).fetchone()[0]

        if user_count > 0:
            # If the group is not empty, check if current_user is in the group
            user_in_group = cursor.execute("SELECT 1 FROM user_group WHERE uid = ? AND gid = ?", 
                                           (current_user['uid'], gid)).fetchone()
            
            if not user_in_group:
                print("Access denied: Only group members can add new users.")
                return False

        # Add the user to the group
        cursor.execute("INSERT INTO user_group (uid, gid) VALUES (?, ?)", (uid, gid))
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        print(f"User '{username}' is already in group '{group_name}'.")
        return False

    finally:
        conn.close()

def delete_group(group_name):
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM groups WHERE group_name = ?", (group_name,))
        conn.commit()
        print(f"Group '{group_name}' deleted.")
        return True
    except Exception as e:
        print(f"Error deleting group: {str(e)}")
        return False
    finally:
        conn.close()
#endregion


def add_group_expense(amount, group_name, category, payment_method, description, tags, split_usernames):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get group ID, category ID, and payment method ID
        gid = cursor.execute("SELECT gid FROM groups WHERE group_name = ?", (group_name,)).fetchone()
        cid = cursor.execute("SELECT cid FROM categories WHERE category_name = ?", (category,)).fetchone()
        pid = cursor.execute("SELECT pid FROM payment_methods WHERE method = ?", (payment_method,)).fetchone()

        if not gid or not cid or not pid:
            print("Invalid group, category, or payment method.")
            return False

        gid, cid, pid = gid[0], cid[0], pid[0]

        # Add expense to group_expenses table
        cursor.execute(
            "INSERT INTO group_expenses (gid, d_uid, amount, cid, pid, date, description) VALUES (?, ?, ?, ?, ?, date('now'), ?)",
            (gid, current_user['uid'], amount, cid, pid, description)
        )
        geid = cursor.lastrowid  # Get the newly inserted expense ID

        # Add tags to the expense
        for tag in tags:
            tag_result = cursor.execute("SELECT tid FROM tags WHERE tag_name = ?", (tag.strip().lower(),)).fetchone()
            if not tag_result:
                cursor.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag.strip().lower(),))
                tid = cursor.lastrowid
            else:
                tid = tag_result[0]
            cursor.execute("INSERT INTO group_expense_tags (geid, tid) VALUES (?, ?)", (geid, tid))

        # Add users to the split_users table (including the expense creator)
        split_usernames.append(current_user['username'])  # Ensure the expense creator is included
        unique_usernames = list(set(split_usernames))  # Remove duplicates if any

        # Fetch UIDs for all users
        user_ids = []
        for username in unique_usernames:
            uid_result = cursor.execute("SELECT uid FROM users WHERE username = ?", (username,)).fetchone()
            if uid_result:
                user_ids.append(uid_result[0])
            else:
                print(f"Warning: User '{username}' not found, skipping.")

        if not user_ids:
            print("Error: No valid users found to split the expense.")
            return False

        # Calculate split amount
        split_amount = amount / len(user_ids)

        # Insert split details into split_users table
        for uid in user_ids:
            cursor.execute(
                "INSERT INTO split_users (geid, uid, split_amount) VALUES (?, ?, ?)",
                (geid, uid, split_amount)
            )

        conn.commit()
        print(f"Group expense added to '{group_name}' and split among {len(user_ids)} users.")
        return True

    except Exception as e:
        print(f"Error adding group expense: {str(e)}")
        return False

    finally:
        conn.close()


#region User Management Updates
def update_user(username, field, new_value):
    try:
        if current_user.get('role') != 'Admin':
            print("Only Admin can update users.")
            return False

        valid_fields = ['password', 'role']
        if field not in valid_fields:
            print("Invalid field.")
            return False

        conn = get_db_connection()
        conn.execute(f"UPDATE users SET {field} = ? WHERE username = ?", (new_value, username))
        conn.commit()
        print(f"User '{username}' updated.")
        return True
    finally:
        conn.close()

def delete_user(username):
    try:
        if current_user.get('role') != 'Admin':
            print("Only Admin can delete users.")
            return False

        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        print(f"User '{username}' deleted.")
        return True
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return False
    finally:
        conn.close()
#endregion

#region Import/Export
def import_expenses(file_path):
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                add_expense(
                    float(row['amount']),
                    row['category'],
                    row['payment_method'],
                    row['date'],
                    row['description'],
                    row['tag']
                )
        return True
    except Exception as e:
        print(f"Import error: {str(e)}")
        return False

def export_csv(file_path, sort_field):
    try:
        valid_fields = ['date', 'amount', 'category', 'payment_method']
        if sort_field not in valid_fields:
            print("Invalid sort field")
            return False
        
        expenses = list_expenses()
        sorted_expenses = sorted(expenses, key=lambda x: x[sort_field])
        
        with open(file_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Amount', 'Category', 'Payment Method', 'Description', 'Tag'])
            for exp in sorted_expenses:
                writer.writerow([
                    exp['date'],
                    exp['amount'],
                    exp['category_name'],
                    exp['method'],
                    exp['description'],
                    exp['tag']
                ])
        return True
    except Exception as e:
        print(f"Export error: {str(e)}")
        return False
#endregion