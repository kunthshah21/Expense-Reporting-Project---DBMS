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
        valid_fields = ['amount', 'date', 'description', 'category', 'payment_method', 'tags']
        
        if field not in valid_fields:
            print(f"Invalid field. Valid fields: {', '.join(valid_fields)}")
            return False

        # Verify ownership
        expense = conn.execute("SELECT uid FROM expenses WHERE eid = ?", 
                              (expense_id,)).fetchone()
        if not expense or expense['uid'] != current_user.get('uid'):
            print("Expense not found or permission denied")
            return False

        if field == 'category':
            category = conn.execute("SELECT cid FROM categories WHERE category_name = ?",
                                  (new_value.lower(),)).fetchone()
            if not category:
                print("Invalid category")
                return False
            conn.execute("UPDATE expenses SET cid = ? WHERE eid = ?",
                       (category['cid'], expense_id))
        
        elif field == 'payment_method':
            method = conn.execute("SELECT pid FROM payment_methods WHERE method = ?",
                                (new_value.lower(),)).fetchone()
            if not method:
                print("Invalid payment method")
                return False
            conn.execute("UPDATE expenses SET pid = ? WHERE eid = ?",
                       (method['pid'], expense_id))
        
        elif field == 'tags':
            # Clear existing tags
            conn.execute("DELETE FROM expenses_tags WHERE eid = ?", (expense_id,))
            # Add new tags
            for tag in new_value.split(','):
                tag = tag.strip().lower()
                tid = conn.execute("SELECT tid FROM tags WHERE tag_name = ?",
                                 (tag,)).fetchone()
                if not tid:
                    conn.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag,))
                    tid = conn.lastrowid
                else:
                    tid = tid[0]
                conn.execute("INSERT INTO expenses_tags (eid, tid) VALUES (?, ?)",
                            (expense_id, tid))
        
        else:
            # For amount/date/description
            if field == 'amount':
                new_value = float(new_value)
            elif field == 'date':
                datetime.strptime(new_value, '%Y-%m-%d')  # Validate format
            
            conn.execute(f"UPDATE expenses SET {field} = ? WHERE eid = ?",
                       (new_value, expense_id))
        
        conn.commit()
        return True
    except ValueError as e:
        print(f"Invalid value: {str(e)}")
        return False
    finally:
        conn.close()

def delete_expense(expense_id):
    try:
        conn = get_db_connection()
        # Verify ownership
        expense = conn.execute("SELECT uid FROM expenses WHERE eid = ?", 
                             (expense_id,)).fetchone()
        if not expense or expense['uid'] != current_user.get('uid'):
            print("Expense not found or permission denied")
            return False
        
        # Delete associated tags
        conn.execute("DELETE FROM expenses_tags WHERE eid = ?", (expense_id,))
        # Delete expense
        conn.execute("DELETE FROM expenses WHERE eid = ?", (expense_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def list_expenses(filters=None):
    try:
        conn = get_db_connection()
        base_query = """
            SELECT e.eid, e.amount, c.category_name, p.method, e.date, e.description,
                   GROUP_CONCAT(t.tag_name, ', ') AS tags
            FROM expenses e
            JOIN categories c ON e.cid = c.cid
            JOIN payment_methods p ON e.pid = p.pid
            LEFT JOIN expenses_tags et ON e.eid = et.eid
            LEFT JOIN tags t ON et.tid = t.tid
            WHERE e.uid = ?
        """
        params = [current_user['uid']]
        conditions = []

        if filters:
            for key, value in filters.items():
                if key == 'category':
                    conditions.append("c.category_name = ?")
                    params.append(value.lower())
                elif key == 'payment_method':
                    conditions.append("p.method = ?")
                    params.append(value.lower())
                elif key == 'min_amount':
                    conditions.append("e.amount >= ?")
                    params.append(float(value))
                elif key == 'max_amount':
                    conditions.append("e.amount <= ?")
                    params.append(float(value))
                elif key == 'date':
                    conditions.append("e.date = ?")
                    params.append(value)
                elif key == 'tag':
                    conditions.append("t.tag_name = ?")
                    params.append(value.lower())

        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " GROUP BY e.eid ORDER BY e.date DESC"
        
        expenses = conn.execute(base_query, params).fetchall()
        
        if not expenses:
            print("No expenses found")
            return
        
        print("\n{:<5} {:<10} {:<15} {:<12} {:<15} {:<30} {:<20}".format(
            "ID", "Amount", "Category", "Payment", "Date", "Description", "Tags"))
        print("-"*110)
        for exp in expenses:
            print("{:<5} ₹{:<9.2f} {:<15} {:<12} {:<15} {:<30} {:<20}".format(
                exp['eid'],
                exp['amount'],
                exp['category_name'],
                exp['method'],
                exp['date'],
                exp['description'] or "-",
                exp['tags'] or "-"
            ))
        print()
        
    finally:
        conn.close()

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

# region Import/Export
def import_expenses(file_path):
    try:
        if not current_user.get('uid'):
            print("You must be logged in to import expenses")
            return False

        conn = get_db_connection()
        imported_count = 0

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 1):
                try:
                    # Validate required fields
                    required_fields = ['amount', 'category', 'payment_method', 'date']
                    if not all(field in row for field in required_fields):
                        print(f"Row {row_num}: Missing required fields")
                        continue

                    # Convert data types
                    amount = float(row['amount'])
                    date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    category = row['category'].strip().lower()
                    payment_method = row['payment_method'].strip().lower()
                    description = row.get('description', '')
                    tags = [tag.strip() for tag in row.get('tag', '').split(',') if tag.strip()]

                    # Check category exists
                    category_id = conn.execute("""
                        SELECT cid FROM categories 
                        WHERE category_name = ?
                    """, (category,)).fetchone()
                    if not category_id:
                        print(f"Row {row_num}: Invalid category '{category}'")
                        continue

                    # Check payment method exists
                    payment_id = conn.execute("""
                        SELECT pid FROM payment_methods 
                        WHERE method = ?
                    """, (payment_method,)).fetchone()
                    if not payment_id:
                        print(f"Row {row_num}: Invalid payment method '{payment_method}'")
                        continue

                    # Add expense
                    if add_expense(amount, category, payment_method, 
                                  date.isoformat(), description, tags):
                        imported_count += 1
                    else:
                        print(f"Row {row_num}: Failed to add expense")

                except ValueError as e:
                    print(f"Row {row_num}: Invalid data - {str(e)}")
                except Exception as e:
                    print(f"Row {row_num}: Error - {str(e)}")

        print(f"Successfully imported {imported_count}/{row_num} expenses")
        return True

    except FileNotFoundError:
        print("File not found")
        return False
    except Exception as e:
        print(f"Import error: {str(e)}")
        return False

def export_csv(file_path, sort_field):
    valid_fields = ['date', 'amount', 'category', 'payment_method', 'tags', 'user']
    sort_field = sort_field.lower()
    
    if sort_field not in valid_fields:
        print(f"Invalid sort field. Valid options: {', '.join(valid_fields)}")
        return False

    try:
        conn = get_db_connection()
        
        # Different queries for admin and regular users
        if current_user.get('role') == 'Admin':
            query = """
                SELECT e.eid, e.amount, c.category_name, p.method, e.date, e.description,
                       GROUP_CONCAT(t.tag_name, ', ') AS tags, u.username as user
                FROM expenses e
                JOIN categories c ON e.cid = c.cid
                JOIN payment_methods p ON e.pid = p.pid
                JOIN users u ON e.uid = u.uid
                LEFT JOIN expenses_tags et ON e.eid = et.eid
                LEFT JOIN tags t ON et.tid = t.tid
                GROUP BY e.eid
            """
            expenses = conn.execute(query).fetchall()
        else:
            query = """
                SELECT e.eid, e.amount, c.category_name, p.method, e.date, e.description,
                       GROUP_CONCAT(t.tag_name, ', ') AS tags
                FROM expenses e
                JOIN categories c ON e.cid = c.cid
                JOIN payment_methods p ON e.pid = p.pid
                LEFT JOIN expenses_tags et ON e.eid = et.eid
                LEFT JOIN tags t ON et.tid = t.tid
                WHERE e.uid = ?
                GROUP BY e.eid
            """
            expenses = conn.execute(query, (current_user['uid'],)).fetchall()

        # Sort expenses
        sorted_expenses = sorted(
            expenses,
            key=lambda x: (
                x['date'] if sort_field == 'date' else
                float(x['amount']) if sort_field == 'amount' else
                x['category_name'] if sort_field == 'category' else
                x['method'] if sort_field == 'payment_method' else
                x['tags'] if sort_field == 'tags' else
                x.get('user', '') if sort_field == 'user' else
                ""
            )
        )

        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            # Different headers for admin and regular users
            if current_user.get('role') == 'Admin':
                writer.writerow(['ID', 'User', 'Amount', 'Category', 'Payment Method', 
                               'Date', 'Description', 'Tags'])
                
                for exp in sorted_expenses:
                    writer.writerow([
                        exp['eid'],
                        exp['user'],
                        exp['amount'],
                        exp['category_name'],
                        exp['method'],
                        exp['date'],
                        exp['description'],
                        exp['tags'] or ''
                    ])
            else:
                writer.writerow(['ID', 'Amount', 'Category', 'Payment Method', 
                               'Date', 'Description', 'Tags'])
                
                for exp in sorted_expenses:
                    writer.writerow([
                        exp['eid'],
                        exp['amount'],
                        exp['category_name'],
                        exp['method'],
                        exp['date'],
                        exp['description'],
                        exp['tags'] or ''
                    ])

        return True
    except Exception as e:
        print(f"Export error: {str(e)}")
        return False
# endregion

def list_categories():
    try:
        conn = get_db_connection()
        categories = conn.execute("SELECT category_name FROM categories").fetchall()
        return categories
    finally:
        conn.close()

def list_payment_methods():
    try:
        conn = get_db_connection()
        methods = conn.execute("SELECT method FROM payment_methods").fetchall()
        return methods
    finally:
        conn.close()

# region Reports
def report_top_expenses(n, start_date, end_date):
    try:
        conn = get_db_connection()
        query = """
            SELECT e.eid, e.amount, c.category_name, p.method, e.date, e.description,
                   GROUP_CONCAT(t.tag_name, ', ') AS tags
            FROM expenses e
            JOIN categories c ON e.cid = c.cid
            JOIN payment_methods p ON e.pid = p.pid
            LEFT JOIN expenses_tags et ON e.eid = et.eid
            LEFT JOIN tags t ON et.tid = t.tid
            WHERE e.uid = ? 
            AND e.date BETWEEN ? AND ?
            GROUP BY e.eid
            ORDER BY e.amount DESC
            LIMIT ?
        """
        expenses = conn.execute(query, (current_user['uid'], start_date, end_date, n)).fetchall()
        
        if not expenses:
            print("No expenses found in this date range")
            return
        
        print(f"\nTop {n} Expenses ({start_date} to {end_date}):")
        print("{:<5} {:<10} {:<15} {:<12} {:<15} {:<30} {:<20}".format(
            "ID", "Amount", "Category", "Payment", "Date", "Description", "Tags"))
        print("-"*110)
        for exp in expenses:
            print("{:<5} ₹{:<9.2f} {:<15} {:<12} {:<15} {:<30} {:<20}".format(
                exp['eid'],
                exp['amount'],
                exp['category_name'],
                exp['method'],
                exp['date'],
                exp['description'] or "-",
                exp['tags'] or "-"
            ))
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return False

def report_category_spending(category):
    try:
        conn = get_db_connection()
        query = """
            SELECT SUM(e.amount) AS total, c.category_name
            FROM expenses e
            JOIN categories c ON e.cid = c.cid
            WHERE e.uid = ? AND LOWER(c.category_name) = ?
        """
        result = conn.execute(query, (current_user['uid'], category.lower())).fetchone()
        
        if not result or not result['total']:
            print(f"No spending found in category '{category}'")
            return False
            
        print(f"\nTotal spending in {category}: ₹{result['total']:.2f}")
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return False

def report_above_average_expenses():
    try:
        conn = get_db_connection()
        query = """
            SELECT e.*, c.category_name, p.method, 
                   (SELECT AVG(amount) 
                    FROM expenses e2 
                    WHERE e2.cid = e.cid) AS category_avg
            FROM expenses e
            JOIN categories c ON e.cid = c.cid
            JOIN payment_methods p ON e.pid = p.pid
            WHERE e.uid = ? 
            AND e.amount > category_avg
            ORDER BY c.category_name, e.amount DESC
        """
        expenses = conn.execute(query, (current_user['uid'],)).fetchall()
        
        if not expenses:
            print("No expenses above category averages")
            return
        
        print("\nExpenses Above Category Averages:")
        print("{:<5} {:<10} {:<15} {:<12} {:<15} {:<30} {:<20}".format(
            "ID", "Amount", "Category", "Payment", "Date", "Description", "Category Avg"))
        print("-"*110)
        for exp in expenses:
            print("{:<5} ₹{:<9.2f} {:<15} {:<12} {:<15} {:<30} ₹{:<9.2f}".format(
                exp['eid'],
                exp['amount'],
                exp['category_name'],
                exp['method'],
                exp['date'],
                exp['description'] or "-",
                exp['category_avg']
            ))
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return False

def report_monthly_category_spending():
    try:
        conn = get_db_connection()
        query = """
            SELECT 
                strftime('%Y-%m', e.date) AS month,
                c.category_name,
                SUM(e.amount) AS total,
                COUNT(e.eid) AS count
            FROM expenses e
            JOIN categories c ON e.cid = c.cid
            WHERE e.uid = ?
            GROUP BY month, c.category_name
            ORDER BY month DESC, total DESC
        """
        results = conn.execute(query, (current_user['uid'],)).fetchall()
        
        if not results:
            print("No spending data available")
            return

        print("\nMonthly Category Spending:")
        print("{:<10} {:<15} {:<15} {:<10}".format(
            "Month", "Category", "Total Amount", "Expenses Count"))
        print("-" * 50)
        for row in results:
            print("{:<10} {:<15} ₹{:<13.2f} {:<10}".format(
                row['month'],
                row['category_name'],
                row['total'],
                row['count']
            ))
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return False

def report_highest_spender_per_month():
    try:
        conn = get_db_connection()
        query = """
            WITH monthly_spending AS (
                SELECT
                    strftime('%Y-%m', e.date) AS month,
                    u.username,
                    SUM(e.amount) AS total,
                    RANK() OVER (PARTITION BY strftime('%Y-%m', e.date) 
                                 ORDER BY SUM(e.amount) DESC) AS rank
                FROM expenses e
                JOIN users u ON e.uid = u.uid
                GROUP BY month, u.username
            )
            SELECT month, username, total
            FROM monthly_spending
            WHERE rank = 1
            ORDER BY month DESC
        """
        results = conn.execute(query).fetchall()
        
        if not results:
            print("No spending data available")
            return

        print("\nHighest Spender Per Month:")
        print("{:<10} {:<15} {:<15}".format(
            "Month", "Username", "Total Spending"))
        print("-" * 40)
        for row in results:
            print("{:<10} {:<15} ₹{:<13.2f}".format(
                row['month'],
                row['username'],
                row['total']
            ))
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return False

def report_frequent_category():
    try:
        conn = get_db_connection()
        query = """
            SELECT c.category_name, COUNT(*) AS count
            FROM expenses e
            JOIN categories c ON e.cid = c.cid
            WHERE e.uid = ?
            GROUP BY c.category_name
            ORDER BY count DESC
            LIMIT 1
        """
        result = conn.execute(query, (current_user['uid'],)).fetchone()
        
        if not result:
            print("No expense data available")
            return

        print(f"\nMost Frequent Category: {result['category_name']}")
        print(f"Number of Expenses: {result['count']}")
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return False

def report_payment_method_usage():
    try:
        conn = get_db_connection()
        query = """
            SELECT 
                p.method,
                SUM(e.amount) AS total_spent,
                COUNT(e.eid) AS expense_count
            FROM expenses e
            JOIN payment_methods p ON e.pid = p.pid
            WHERE e.uid = ?
            GROUP BY p.method
            ORDER BY total_spent DESC
        """
        results = conn.execute(query, (current_user['uid'],)).fetchall()
        
        if not results:
            print("No payment method usage data available")
            return

        print("\nPayment Method Usage Breakdown:")
        print("{:<15} {:<15} {:<15}".format(
            "Method", "Total Spent", "Expense Count"))
        print("-" * 45)
        for row in results:
            print("{:<15} ₹{:<13.2f} {:<15}".format(
                row['method'],
                row['total_spent'],
                row['expense_count']
            ))
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return False

def report_tag_expenses():
    try:
        conn = get_db_connection()
        query = """
            SELECT 
                t.tag_name,
                COUNT(et.eid) AS expense_count
            FROM tags t
            LEFT JOIN expenses_tags et ON t.tid = et.tid
            WHERE EXISTS (
                SELECT 1 FROM expenses e
                WHERE e.eid = et.eid AND e.uid = ?
            )
            GROUP BY t.tag_name
            ORDER BY expense_count DESC
        """
        results = conn.execute(query, (current_user['uid'],)).fetchall()
        
        if not results:
            print("No tag usage data available")
            return

        print("\nTag Expense Counts:")
        print("{:<20} {:<15}".format("Tag", "Expense Count"))
        print("-" * 35)
        for row in results:
            print("{:<20} {:<15}".format(
                row['tag_name'],
                row['expense_count'] or 0
            ))
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return False
# endregion