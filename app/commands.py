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
def add_expense(amount, category, payment_method, date, description, tag):
    try:
        if not current_user.get('uid'):
            return False
        
        conn = get_db_connection()
        
        # Get category ID
        cid = conn.execute("""
            SELECT cid FROM categories 
            WHERE category_name = ?
        """, (category,)).fetchone()[0]
        
        # Get payment method ID
        pid = conn.execute("""
            SELECT pid FROM payment_methods 
            WHERE method = ?
        """, (payment_method,)).fetchone()[0]
        
        # Insert expense
        conn.execute("""
            INSERT INTO expenses 
            (uid, amount, cid, pid, date, description, tag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (current_user['uid'], amount, cid, pid, date, description, tag))
        
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