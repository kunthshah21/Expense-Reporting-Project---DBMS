# app/commands.py

def login(username, password):
    print(f"[COMMAND] Login: username={username}, password={password}")

def logout():
    print("[COMMAND] Logout")

def list_users():
    print("[COMMAND] List users")

def add_user(username, password, role):
    print(f"[COMMAND] Add user: username={username}, password={password}, role={role}")

def add_category(category_name):
    print(f"[COMMAND] Add category: {category_name}")

def list_categories():
    print("[COMMAND] List categories")

def add_payment_method(method_name):
    print(f"[COMMAND] Add payment method: {method_name}")

def list_payment_methods():
    print("[COMMAND] List payment methods")

def add_expense(amount, category, payment_method, date, description, tag):
    print(f"[COMMAND] Add expense: amount={amount}, category={category}, payment_method={payment_method}, date={date}, description={description}, tag={tag}")

def update_expense(expense_id, field, new_value):
    print(f"[COMMAND] Update expense: id={expense_id}, field={field}, new_value={new_value}")

def delete_expense(expense_id):
    print(f"[COMMAND] Delete expense: {expense_id}")

def list_expenses(filters=None):
    print("[COMMAND] List expenses", filters)
