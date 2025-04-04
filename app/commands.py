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

# Replace current logout() with:
def logout():
    current_user.clear()
    current_user.update({'uid': None, 'username': None, 'role': None})
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
        print("Username already exists or the Role does not exist")
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
    try:
        if not current_user.get('uid'):
            print("Error: User not logged in.")
            return False
            
        if amount <= 0:
            print("Error: Amount must be greater than 0")
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
       
        cid = cid_result[0]
        
        # Get payment method ID
        pid_result = conn.execute("""
            SELECT pid FROM payment_methods 
            WHERE LOWER(method) = ?
        """, (payment_method,)).fetchone()

        if not pid_result:
            print(f"Error: Payment method '{payment_method}' not found.")
            return False
          
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
        # Remove the admin role check to allow all logged-in users to create tags
        if not current_user.get('uid'):
            print("Error: User not logged in.")
            return False
            
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
        if not current_user.get('uid'):
            print("Error: User not logged in.")
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create the group
        cursor.execute("INSERT INTO groups (group_name, description, date_created) VALUES (?, ?, date('now'))", 
                     (group_name, description))
        
        # Get the new group ID
        gid = cursor.lastrowid
        
        # Add the creator to the group
        cursor.execute("INSERT INTO user_group (uid, gid) VALUES (?, ?)", 
                     (current_user['uid'], gid))
        
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
        cursor = conn.cursor()

        # Check if the group exists
        gid = cursor.execute("SELECT gid FROM groups WHERE group_name = ?", (group_name,)).fetchone()
        if not gid:
            print(f"Error: Group '{group_name}' does not exist.")
            return False
        gid = gid[0]
        
        # Check if the user has permission to delete the group
        if not check_group_permissions(group_name):
            return False

        # Fetch all expense IDs associated with the group
        expense_ids = cursor.execute("SELECT geid FROM group_expenses WHERE gid = ?", (gid,)).fetchall()
        expense_ids = [row[0] for row in expense_ids]

        if expense_ids:
            # Handle the case where there's only one expense ID
            if len(expense_ids) == 1:
                cursor.execute("DELETE FROM split_users WHERE geid = ?", (expense_ids[0],))
                cursor.execute("DELETE FROM group_expense_tags WHERE geid = ?", (expense_ids[0],))
            else:
                # Convert list to a tuple for SQL queries
                expense_ids_tuple = tuple(expense_ids)

                # Delete related records in dependent tables
                cursor.execute("DELETE FROM split_users WHERE geid IN ({})".format(",".join("?" * len(expense_ids))), expense_ids_tuple)
                cursor.execute("DELETE FROM group_expense_tags WHERE geid IN ({})".format(",".join("?" * len(expense_ids))), expense_ids_tuple)
                
            cursor.execute("DELETE FROM group_expenses WHERE gid = ?", (gid,))

        # Delete user-group associations
        cursor.execute("DELETE FROM user_group WHERE gid = ?", (gid,))
        
        # Finally, delete the group
        cursor.execute("DELETE FROM groups WHERE gid = ?", (gid,))
        
        conn.commit()
        print(f"Group '{group_name}' and all related expenses deleted successfully.")
        return True

    except Exception as e:
        print(f"Error deleting group: {str(e)}")
        return False

    finally:
        conn.close()

def add_group_expense(amount, group_name, category, payment_method, date, description, tags, split_usernames):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the group exists
        gid = cursor.execute("SELECT gid FROM groups WHERE group_name = ?", (group_name,)).fetchone()
        if not gid:
            print(f"Error: Group '{group_name}' does not exist.")
            return False
        gid = gid[0]

        # Check if the current user is in the group
        is_user_in_group = cursor.execute(
            "SELECT 1 FROM user_group WHERE uid = ? AND gid = ?", (current_user['uid'], gid)
        ).fetchone()
        
        if not is_user_in_group and current_user.get('role') != 'Admin':
            print(f"Error: You must be a member of the group '{group_name}' to add expenses.")
            return False

        # Get category ID and payment method ID
        cid = cursor.execute("SELECT cid FROM categories WHERE LOWER(category_name) = ?", (category.lower(),)).fetchone()
        pid = cursor.execute("SELECT pid FROM payment_methods WHERE LOWER(method) = ?", (payment_method.lower(),)).fetchone()

        if not cid or not pid:
            print("Invalid category or payment method.")
            return False

        cid, pid = cid[0], pid[0]

        # Make a copy of split_usernames to avoid modifying the original list
        split_users = list(split_usernames)
        
        # Add current user if not already in the list
        if current_user.get('username') not in split_users:
            split_users.append(current_user.get('username'))

        unique_usernames = list(set(split_users))  # Remove duplicates

        # Fetch UIDs for all users and verify they're part of the group
        user_ids = []
        non_group_members = []
        
        for username in unique_usernames:
            # First check if user exists
            user_result = cursor.execute("SELECT uid FROM users WHERE username = ?", (username,)).fetchone()
            if not user_result:
                print(f"Warning: User '{username}' does not exist, skipping.")
                continue
                
            uid = user_result[0]
            
            # Then check if user is part of the group
            is_in_group = cursor.execute(
                "SELECT 1 FROM user_group WHERE uid = ? AND gid = ?", (uid, gid)
            ).fetchone()
            
            if is_in_group:
                user_ids.append(uid)
            else:
                non_group_members.append(username)
        
        # Handle case where some users aren't part of the group
        if non_group_members:
            print(f"Error: These users are not members of group '{group_name}': {', '.join(non_group_members)}")
            print("Only group members can be part of an expense split.")
            return False

        if len(user_ids) < 2:
            print("Error: The expense must be split between at least two group members.")
            return False

        # Add expense to group_expenses table
        cursor.execute(
            "INSERT INTO group_expenses (gid, uid, amount, cid, pid, date, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (gid, current_user['uid'], amount, cid, pid, date, description)
        )
        geid = cursor.lastrowid

        # Add tags to the expense
        for tag in tags:
            tag_result = cursor.execute("SELECT tid FROM tags WHERE tag_name = ?", (tag.strip().lower(),)).fetchone()
            if not tag_result:
                cursor.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag.strip().lower(),))
                tid = cursor.lastrowid
            else:
                tid = tag_result[0]
            cursor.execute("INSERT INTO group_expense_tags (geid, tid) VALUES (?, ?)", (geid, tid))

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

# Add this helper function at the top
def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# region Reports
def report_top_expenses(n, start_date, end_date):
    if not validate_date(start_date) or not validate_date(end_date):
        print("Invalid date format. Use YYYY-MM-DD")
        return False
    if start_date > end_date:
        print("Error: Start date must be before end date")
        return False
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
        if current_user.get('role') != 'Admin':
            print("Permission denied: Admin access required")
            return False
            
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
        # Get all categories with max count
        query = """
            WITH category_counts AS (
                SELECT c.category_name, COUNT(*) AS count,
                       MAX(COUNT(*)) OVER () AS max_count
                FROM expenses e
                JOIN categories c ON e.cid = c.cid
                WHERE e.uid = ?
                GROUP BY c.category_name
            )
            SELECT category_name, count
            FROM category_counts
            WHERE count = max_count
        """
        results = conn.execute(query, (current_user['uid'],)).fetchall()
        
        if not results:
            print("No expense data available")
            return

        print("\nMost Frequent Categories:")
        for row in results:
            print(f"{row['category_name']}: {row['count']} expenses")
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

        print("\nTag Expense (Users) Counts:")
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

#region group queries
def list_groups():
    try:
        conn = get_db_connection()

        # If the user is not an admin, only show the groups they belong to
        if current_user['role'] != 'Admin':
            print(f"Only admins can view all the groups. \n Showing {current_user['username']}'s groups")

            # Simplified query to fetch the groups that the current user is part of
            query = """
                SELECT group_name, date_created, description
                FROM groups
                JOIN user_group ON groups.gid = user_group.gid
                WHERE user_group.uid = ?
            """
            groups = conn.execute(query, (current_user['uid'],)).fetchall()

        else:
            # Admins can view all groups
            print("Admin is viewing all groups.")
            query = "SELECT group_name, date_created, description FROM groups"
            groups = conn.execute(query).fetchall()

        if not groups:
            print("No groups found.")
            return False
        
        print("\nGroups:")
        print("{:<20} {:<20} {:<50}".format("Group Name", "Date Created", "Description"))
        print("-" * 80)
        for group in groups:
            print("{:<20} {:<20} {:<50}".format(group['group_name'], group['date_created'], group['description'] or "-"))

        return True

    except Exception as e:
        print(f"Error retrieving groups: {str(e)}")
        return False


def report_group_expenses(group_name, filters=None):
    try:
        conn = get_db_connection()

        # Check if user has permission to view the group
        if not check_group_permissions(group_name):
            return False

        base_query = """
            SELECT ge.geid, ge.amount, c.category_name, p.method, ge.date, ge.description,
                   (SELECT GROUP_CONCAT(DISTINCT t.tag_name) 
                    FROM group_expense_tags getag 
                    JOIN tags t ON getag.tid = t.tid 
                    WHERE getag.geid = ge.geid) AS tags,
                   (SELECT GROUP_CONCAT(DISTINCT u.username) 
                    FROM split_users su 
                    JOIN users u ON su.uid = u.uid 
                    WHERE su.geid = ge.geid) AS usernames
            FROM group_expenses ge
            JOIN categories c ON ge.cid = c.cid
            JOIN payment_methods p ON ge.pid = p.pid
            WHERE ge.gid = (SELECT gid FROM groups WHERE group_name = ?)
        """
        params = [group_name]

        # Apply filters
        if filters:
            for key, value in filters.items():
                if key == 'category':
                    base_query += " AND LOWER(c.category_name) = ?"
                    params.append(value.lower())
                elif key == 'date':
                    base_query += " AND ge.date = ?"
                    params.append(value)
                elif key == 'min_amount':
                    base_query += " AND ge.amount >= ?"
                    params.append(float(value))
                elif key == 'max_amount':
                    base_query += " AND ge.amount <= ?"
                    params.append(float(value))
                elif key == 'tag':
                    base_query += " AND EXISTS (SELECT 1 FROM group_expense_tags getag JOIN tags t ON getag.tid = t.tid WHERE getag.geid = ge.geid AND t.tag_name = ?)"
                    params.append(value.lower())

        base_query += " ORDER BY ge.amount DESC"

        expenses = conn.execute(base_query, params).fetchall()

        if not expenses:
            print(f"No expenses found for group {group_name}")
            return False

        print(f"\nGroup {group_name} Expenses:")
        print("{:<5} {:<10} {:<15} {:<12} {:<15} {:<30} {:<20} {:<30}".format(
            "ID", "Amount", "Category", "Payment", "Date", "Description", "Tags", "Users"))
        print("-" * 120)

        for exp in expenses:
            print("{:<5} ₹{:<9.2f} {:<15} {:<12} {:<15} {:<30} {:<20} {:<30}".format(
                exp['geid'],
                exp['amount'],
                exp['category_name'],
                exp['method'],
                exp['date'],
                exp['description'] or "-",
                exp['tags'] or "-",
                exp['usernames'] or "-"
            ))
        return True

    except Exception as e:
        print(f"Error generating group expenses report: {str(e)}")
        return False


def report_group_category_spending(group_name, category):
    try:
        # Check if the current user is an admin or a member of the group
        conn = get_db_connection()
        if (check_group_permissions(group_name)):
            pass
        else:
            return False

        # Proceed with generating the group category report
        query = """
            SELECT SUM(ge.amount) AS total, c.category_name
            FROM group_expenses ge
            JOIN categories c ON ge.cid = c.cid
            WHERE ge.gid = (SELECT gid FROM groups WHERE group_name = ?) 
            AND LOWER(c.category_name) = ?
        """
        
        result = conn.execute(query, (group_name, category.lower())).fetchone()
        
        if not result or not result['total']:
            print(f"No spending found in category '{category}' for group {group_name}")
            return False
            
        print(f"\nTotal spending in {category} for group {group_name}: ₹{result['total']:.2f}")
        return True

    except Exception as e:
        print(f"Error generating group category report: {str(e)}")
        return False
    
def report_group_tag_usage(group_name):
    try:
        conn = get_db_connection()
        
        if not check_group_permissions(group_name):
            return False

        # Get group ID
        gid_result = conn.execute("SELECT gid FROM groups WHERE group_name = ?", (group_name,)).fetchone()
        if not gid_result:
            print(f"Error: Group '{group_name}' not found.")
            return False
        
        gid = gid_result[0]

        # Modified query to properly handle tags with 0 counts
        query = """
            SELECT t.tag_name, 
                   COUNT(CASE WHEN ge.gid = ? THEN getag.geid ELSE NULL END) AS expense_count
            FROM tags t
            LEFT JOIN group_expense_tags getag ON t.tid = getag.tid
            LEFT JOIN group_expenses ge ON getag.geid = ge.geid AND ge.gid = ?
            GROUP BY t.tag_name
            ORDER BY expense_count DESC, t.tag_name
        """
        
        results = conn.execute(query, (gid, gid)).fetchall()
        
        if not results:
            print(f"No tags found in the system")
            return False

        # Filter to only show tags with counts > 0
        results_with_counts = [row for row in results if row['expense_count'] > 0]
        
        if not results_with_counts:
            print(f"No tag usage data found for group {group_name}")
            return False

        print(f"\nTag Usage for Group {group_name}:")
        print("{:<20} {:<15}".format("Tag", "Expense Count"))
        print("-" * 35)
        for row in results_with_counts:
            print("{:<20} {:<15}".format(row['tag_name'], row['expense_count']))
        return True

    except Exception as e:
        print(f"Error generating group tag report: {str(e)}")
        return False
    finally:
        conn.close()    

def report_group_user_expenses(group_name):
    try:
        conn = get_db_connection()
        if (check_group_permissions(group_name)):
            pass
        else:
            return False
        query = """
            SELECT u.username, SUM(su.split_amount) AS total_spent
            FROM users u
            JOIN split_users su ON u.uid = su.uid
            JOIN group_expenses ge ON su.geid = ge.geid
            JOIN groups g ON ge.gid = g.gid
            WHERE g.group_name = ?
            GROUP BY u.uid
            ORDER BY total_spent ASC
        """
        results = conn.execute(query, (group_name,)).fetchall()

        if not results:
            print(f"No users found in group {group_name} or no spending recorded.")
            return

        print(f"\nUsers and Their Spending in Group {group_name}:")
        print("{:<20} {:<15}".format("Username", "Total Spent"))
        print("-" * 40)
        for row in results:
            print("{:<20} ₹{:<13.2f}".format(row['username'], row['total_spent'] or 0))

        return True
    except Exception as e:
        print(f"Error retrieving group user spending data: {str(e)}")
        return False


def check_group_permissions(group_name):
    try:
        conn = get_db_connection()
        
        # Check if the current user is an admin
        if current_user['role'] == 'Admin':
            # Admins can access any group, so no further check needed
            return True
        else:
            # Check if the current user is part of the group
            query = """
                SELECT 1 
                FROM user_group ug
                JOIN groups g ON ug.gid = g.gid
                WHERE g.group_name = ? AND ug.uid = ?
            """
            user_part_of_group = conn.execute(query, (group_name, current_user['uid'])).fetchone()
            
            if not user_part_of_group:
                print(f"Error: {current_user['username']} is not a member of group '{group_name}'.")
                return False
            
        return True
    
    except Exception as e:
        print(f"Error checking permissions for group '{group_name}': {str(e)}")
        return False

def export_group_csv(group_name, file_path, sort_field=None):
    try:
        conn = get_db_connection()

        # Check if the current user has permission to access this group
        if not check_group_permissions(group_name):
            return False

        # Fetch group details
        query_group = """
            SELECT g.gid, g.group_name, g.date_created, g.description
            FROM groups g
            WHERE g.group_name = ?
        """
        group = conn.execute(query_group, (group_name,)).fetchone()

        if not group:
            print(f"Group {group_name} does not exist.")
            return False
        
        # Fetch group expenses
        query_expenses = """
            SELECT ge.geid, ge.uid, ge.amount, c.category_name, p.method, ge.date, ge.description,
                   u.username as creator_username
            FROM group_expenses ge
            JOIN categories c ON ge.cid = c.cid
            JOIN payment_methods p ON ge.pid = p.pid
            JOIN users u ON ge.uid = u.uid
            WHERE ge.gid = ?
        """
        if sort_field:
            query_expenses += f" ORDER BY {sort_field}"
            
        expenses = conn.execute(query_expenses, (group['gid'],)).fetchall()

        # Prepare data for export
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['group_name', 'date_created', 'description', 
                         'expense_id', 'creator_username', 'amount', 'category_name', 
                         'payment_method', 'expense_date', 'expense_description', 
                         'tags', 'split_usernames', 'split_amounts']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for expense in expenses:
                # Get tags for this expense
                tags_query = """
                    SELECT t.tag_name
                    FROM group_expense_tags get
                    JOIN tags t ON get.tid = t.tid
                    WHERE get.geid = ?
                """
                tags_result = conn.execute(tags_query, (expense['geid'],)).fetchall()
                tags_str = ', '.join([tag['tag_name'] for tag in tags_result])
                
                # Get split users for this expense
                split_query = """
                    SELECT u.username, su.split_amount
                    FROM split_users su
                    JOIN users u ON su.uid = u.uid
                    WHERE su.geid = ?
                """
                splits = conn.execute(split_query, (expense['geid'],)).fetchall()
                
                split_usernames = ', '.join([split['username'] for split in splits])
                split_amounts = ', '.join([str(split['split_amount']) for split in splits])
                
                writer.writerow({
                    'group_name': group['group_name'],
                    'date_created': group['date_created'],
                    'description': group['description'],
                    'expense_id': expense['geid'],
                    'creator_username': expense['creator_username'],
                    'amount': expense['amount'],
                    'category_name': expense['category_name'],
                    'payment_method': expense['method'],
                    'expense_date': expense['date'],
                    'expense_description': expense['description'],
                    'tags': tags_str,
                    'split_usernames': split_usernames,
                    'split_amounts': split_amounts
                })

        print(f"Group data successfully exported to {file_path}")
        return True

    except Exception as e:
        print(f"Error exporting group data: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def import_group_csv(group_name, file_path):
    conn = None
    try:
        # Check if user is logged in
        if not current_user.get('uid'):
            print("Error: User not logged in.")
            return False
            
        conn = get_db_connection()
        conn.execute("BEGIN TRANSACTION")

        # Check if the group exists 
        group_query = "SELECT gid FROM groups WHERE group_name = ?"
        group_result = conn.execute(group_query, (group_name,)).fetchone()
        
        if group_result:
            # If group exists, check permissions
            if not check_group_permissions(group_name):
                return False
            group_id = group_result['gid']
        else:
            # Create new group
            print(f"Creating new group '{group_name}'")
            try:
                conn.execute("""
                    INSERT INTO groups (group_name, description, date_created) 
                    VALUES (?, ?, date('now'))
                """, (group_name, f"Imported group from {file_path}"))
                
                group_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                
                # Add current user to the group
                conn.execute("""
                    INSERT INTO user_group (uid, gid) VALUES (?, ?)
                """, (current_user['uid'], group_id))
                
            except sqlite3.IntegrityError:
                print(f"Error creating group '{group_name}'")
                raise

        # Open and read the CSV file
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            if not rows:
                print("CSV file is empty")
                return False
            
            # Process each expense row
            imported_count = 0
            for i, row in enumerate(rows, 1):
                try:
                    # Check required fields
                    required_fields = ['amount', 'category_name', 'payment_method', 'expense_date']
                    if not all(field in row and row[field] for field in required_fields):
                        print(f"Row {i}: Missing required fields. Skipping.")
                        continue
                    
                    # Get creator ID (default to current user if not specified)
                    creator_id = current_user['uid']
                    if 'creator_username' in row and row['creator_username']:
                        creator_query = "SELECT uid FROM users WHERE username = ?"
                        creator_result = conn.execute(creator_query, (row['creator_username'],)).fetchone()
                        if creator_result:
                            creator_id = creator_result['uid']
                    
                    # Get category ID
                    category_query = "SELECT cid FROM categories WHERE LOWER(category_name) = ?"
                    category_result = conn.execute(category_query, (row['category_name'].lower(),)).fetchone()
                    if not category_result:
                        # Create category if it doesn't exist
                        conn.execute("INSERT INTO categories (category_name) VALUES (?)", (row['category_name'].lower(),))
                        category_result = conn.execute(category_query, (row['category_name'].lower(),)).fetchone()
                    category_id = category_result['cid']
                    
                    # Get payment method ID
                    payment_query = "SELECT pid FROM payment_methods WHERE LOWER(method) = ?"
                    payment_result = conn.execute(payment_query, (row['payment_method'].lower(),)).fetchone()
                    if not payment_result:
                        # Create payment method if it doesn't exist and user is admin
                        if current_user.get('role') == 'Admin':
                            conn.execute("INSERT INTO payment_methods (method) VALUES (?)", (row['payment_method'].lower(),))
                            payment_result = conn.execute(payment_query, (row['payment_method'].lower(),)).fetchone()
                        else:
                            print(f"Row {i}: Payment method '{row['payment_method']}' not found. Skipping.")
                            continue
                    payment_id = payment_result['pid']
                    
                    # Parse amount
                    try:
                        amount = float(row['amount'])
                        if amount <= 0:
                            print(f"Row {i}: Amount must be positive. Skipping.")
                            continue
                    except ValueError:
                        print(f"Row {i}: Invalid amount '{row['amount']}'. Skipping.")
                        continue
                    
                    # Validate date
                    try:
                        expense_date = row['expense_date']
                        datetime.strptime(expense_date, '%Y-%m-%d')
                    except ValueError:
                        print(f"Row {i}: Invalid date format. Use YYYY-MM-DD. Skipping.")
                        continue
                    
                    description = row.get('expense_description', '')
                    
                    # Insert expense
                    expense_insert = """
                        INSERT INTO group_expenses (gid, uid, amount, cid, pid, date, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    expense_result = conn.execute(expense_insert, (
                        group_id, 
                        creator_id, 
                        amount, 
                        category_id, 
                        payment_id, 
                        expense_date, 
                        description
                    ))
                    expense_id = expense_result.lastrowid
                    
                    # Process tags if present
                    if 'tags' in row and row['tags']:
                        tags = [tag.strip() for tag in row['tags'].split(',') if tag.strip()]
                        for tag in tags:
                            tag_query = "SELECT tid FROM tags WHERE tag_name = ?"
                            tag_result = conn.execute(tag_query, (tag.lower(),)).fetchone()
                            
                            if not tag_result:
                                # Create tag if it doesn't exist
                                conn.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag.lower(),))
                                tag_result = conn.execute(tag_query, (tag.lower(),)).fetchone()
                                
                            tag_id = tag_result['tid']
                            tag_insert = """
                                INSERT INTO group_expense_tags (geid, tid)
                                VALUES (?, ?)
                            """
                            conn.execute(tag_insert, (expense_id, tag_id))
                    
                    # Process split users
                    split_usernames = []
                    split_amounts = []
                    
                    if 'split_usernames' in row and row['split_usernames']:
                        split_usernames = [u.strip() for u in row['split_usernames'].split(',') if u.strip()]
                        
                        if 'split_amounts' in row and row['split_amounts']:
                            split_amounts = [a.strip() for a in row['split_amounts'].split(',') if a.strip()]
                    
                    # Add current user if not in split list
                    if current_user['username'] not in split_usernames:
                        split_usernames.append(current_user['username'])
                    
                    # If no split amounts specified, split evenly
                    if not split_amounts or len(split_amounts) != len(split_usernames):
                        split_amount = amount / len(split_usernames)
                        split_amounts = [split_amount] * len(split_usernames)
                    else:
                        try:
                            split_amounts = [float(amt) for amt in split_amounts]
                            # Validate that split amounts sum to total
                            if abs(sum(split_amounts) - amount) > 0.01:  # Allow for small rounding errors
                                print(f"Row {i}: Split amounts do not sum to total amount. Adjusting.")
                                adjustment = amount - sum(split_amounts)
                                split_amounts[0] += adjustment
                        except ValueError:
                            print(f"Row {i}: Invalid split amounts. Splitting evenly.")
                            split_amount = amount / len(split_usernames)
                            split_amounts = [split_amount] * len(split_usernames)
                    
                    # Add users and their split amounts
                    for j, username in enumerate(split_usernames):
                        user_query = "SELECT uid FROM users WHERE username = ?"
                        user_result = conn.execute(user_query, (username,)).fetchone()
                        
                        if user_result:
                            user_id = user_result['uid']
                            conn.execute("""
                                INSERT INTO split_users (geid, uid, split_amount)
                                VALUES (?, ?, ?)
                            """, (expense_id, user_id, split_amounts[min(j, len(split_amounts)-1)]))
                        else:
                            print(f"Row {i}: User '{username}' not found. Skipping this split.")
                    
                    imported_count += 1
                    
                except Exception as row_error:
                    print(f"Row {i}: Error processing row: {str(row_error)}")
            
            print(f"Successfully imported {imported_count} group expenses")
        
        conn.execute("COMMIT")
        return True

    except Exception as e:
        if conn:
            conn.execute("ROLLBACK")
        print(f"Error importing group data: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def update_group(group_name, field, new_value):
    try:
        conn = get_db_connection()

        # Check if the group exists
        group = conn.execute("SELECT gid FROM groups WHERE group_name = ?", (group_name,)).fetchone()
        if not group:
            print(f"Error: Group '{group_name}' does not exist.")
            return False
        
        # Check if the user has permission to update this group
        if not check_group_permissions(group_name):
            return False
        
        # Validate the field to update
        valid_fields = ['group_name', 'description']
        if field not in valid_fields:
            print(f"Error: Invalid field '{field}'. Valid fields are: {', '.join(valid_fields)}")
            return False
        
        # If updating the group name, check if the new name already exists
        if field == 'group_name' and group_name != new_value:
            existing = conn.execute("SELECT 1 FROM groups WHERE group_name = ?", (new_value,)).fetchone()
            if existing:
                print(f"Error: A group with name '{new_value}' already exists.")
                return False
        
        # Update the group
        conn.execute(f"UPDATE groups SET {field} = ? WHERE group_name = ?", (new_value, group_name))
        conn.commit()
        
        print(f"Group '{group_name}' updated successfully.")
        return True
        
    except Exception as e:
        print(f"Error updating group: {str(e)}")
        return False
    finally:
        conn.close()