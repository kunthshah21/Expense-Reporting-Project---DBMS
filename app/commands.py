from app.db import get_db_connection

def login(email, password):
    print(f"[COMMAND] Login: email={email}, password={password}")

def logout():
    print("[COMMAND] Logout")

def list_users():
    print("[COMMAND] List users")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uid, email, role, phone FROM users")
    users = cursor.fetchall()
    conn.close()
    for user in users:
        print(f"User ID: {user[0]}, Email: {user[1]}, Role: {user[2]}, Phone: {user[3]}")
    return users

def add_user(email, role, phone):
    print(f"[COMMAND] Add user: email={email}, role={role}, phone={phone}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, role, phone) VALUES (?, ?, ?)", 
                  (email, role, phone))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    print(f"User added with ID: {user_id}")
    return user_id

def add_category(category_name):
    print(f"[COMMAND] Add category: {category_name}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (category_name) VALUES (?)", (category_name,))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    print(f"Category added with ID: {category_id}")
    return category_id

def list_categories():
    print("[COMMAND] List categories")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cid, category_name FROM categories")
    categories = cursor.fetchall()
    conn.close()
    for category in categories:
        print(f"Category ID: {category[0]}, Name: {category[1]}")
    return categories

def add_payment_method(method_name):
    print(f"[COMMAND] Add payment method: {method_name}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payment_methods (method) VALUES (?)", (method_name,))
    conn.commit()
    method_id = cursor.lastrowid
    conn.close()
    print(f"Payment method added with ID: {method_id}")
    return method_id

def list_payment_methods():
    print("[COMMAND] List payment methods")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pid, method FROM payment_methods")
    methods = cursor.fetchall()
    conn.close()
    for method in methods:
        print(f"Method ID: {method[0]}, Name: {method[1]}")
    return methods

def add_tag(tag_name):
    print(f"[COMMAND] Add tag: {tag_name}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag_name,))
    conn.commit()
    tag_id = cursor.lastrowid
    conn.close()
    print(f"Tag added with ID: {tag_id}")
    return tag_id

def list_tags():
    print("[COMMAND] List tags")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tid, tag_name FROM tags")
    tags = cursor.fetchall()
    conn.close()
    for tag in tags:
        print(f"Tag ID: {tag[0]}, Name: {tag[1]}")
    return tags

def add_expense(uid, amount, category_id, payment_method_id, date, time, description, tags=[]):
    print(f"[COMMAND] Add expense: user={uid}, amount={amount}, category={category_id}, payment_method={payment_method_id}, date={date}, time={time}, description={description}")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Add expense
    cursor.execute("""
        INSERT INTO user_expenses (uid, date, amount, time, cid, description, pid) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (uid, date, amount, time, category_id, description, payment_method_id))
    
    expense_id = cursor.lastrowid
    
    # Add tags if provided
    for tag_id in tags:
        cursor.execute("INSERT INTO expense_tag (eid, tid) VALUES (?, ?)", (expense_id, tag_id))
    
    conn.commit()
    conn.close()
    print(f"Expense added with ID: {expense_id}")
    return expense_id

def update_expense(expense_id, field, new_value):
    print(f"[COMMAND] Update expense: id={expense_id}, field={field}, new_value={new_value}")
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"UPDATE user_expenses SET {field} = ? WHERE eid = ?"
    cursor.execute(query, (new_value, expense_id))
    conn.commit()
    conn.close()

def delete_expense(expense_id):
    print(f"[COMMAND] Delete expense: {expense_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    # First delete any tag associations
    cursor.execute("DELETE FROM expense_tag WHERE eid = ?", (expense_id,))
    # Then delete the expense
    cursor.execute("DELETE FROM user_expenses WHERE eid = ?", (expense_id,))
    conn.commit()
    conn.close()

def list_expenses(filters=None):
    print("[COMMAND] List expenses", filters)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if not filters:
        query = """
            SELECT e.eid, e.uid, u.email, e.date, e.amount, e.time, 
                   c.category_name, e.description, p.method 
            FROM user_expenses e
            JOIN users u ON e.uid = u.uid
            JOIN categories c ON e.cid = c.cid
            JOIN payment_methods p ON e.pid = p.pid
        """
        cursor.execute(query)
    else:
        # Handle filters here
        pass
        
    expenses = cursor.fetchall()
    conn.close()
    
    for expense in expenses:
        print(f"Expense ID: {expense[0]}, User: {expense[2]}, Date: {expense[3]}, Amount: {expense[4]}")
    
    return expenses
