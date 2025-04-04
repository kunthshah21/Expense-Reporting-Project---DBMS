# Expense Reporting Project - DBMS
 This is a DBMS project which deals with building a Expense reporting tool with a logic overview built in python and SQL as the backend

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [ER](#Entity-Relationship-Diagrams)
- [Queries](#queries)
- [Contributers](#contributers)


## Overview

This project is a CLI tool designed to manage expense reporting with user authentication, expense management, and various reporting features. It uses SQLite as its database engine to keep things simple and self-contained.

## Project Structure

Below is an overview of the project structure along with a description of what each file/folder does:


- **README.md:**  
  Provides an overview, setup instructions, and documentation for the project.

- **requirements.txt:**  
  Lists Python dependencies. Since we use SQLite from the standard library, no external packages are needed at the moment. Future dependencies can be added here.

- **.gitignore:**  
  Ensures that unnecessary or sensitive files (e.g., compiled Python files, SQLite database file) are not committed to the repository.

- **config/config.py:**  
  Contains configuration settings (e.g., database type and SQLite file path). This centralizes configuration for easier modifications and environment-specific setups.

- **db/init_db.py:**  
  A script to initialize the database. It connects to SQLite, creates the necessary tables, and is used during the initial setup of the project.

- **db/schema.sql:**  
  An optional SQL script that can be used to set up database schemas manually or as part of a migration process.

- **app/__init__.py:**  
  Marks the `app` directory as a Python package, allowing for modular import and organization of code.

- **app/cli.py:**  
  Implements the command-line interface (CLI) loop. It reads user input and will eventually parse and delegate commands to appropriate functions.

- **app/commands.py:**  
  Contains stub implementations for various CLI commands (like login, add expense, etc.). These are the starting points for your business logic.

- **app/db.py:**  
  Provides functions to connect to the SQLite database and initialize it (e.g., create tables). This module abstracts the database operations.

- **main.py:**  
  The main entry point for the application. It starts the CLI and ties together the initialization and application logic.

## Setup and Installation

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the CLI**:
   ```bash
   python main.py
   ```
4. **Optional GUI Interface**:
   ```bash
   streamlit run app/streamlit_app.py
   ```

## Usage

### Expense Management System - Available Commands
```
[Authentication]
login <username> <password>    - Authenticate user
logout                         - End current session

[User Management (Admin only)]
add_user <username> <password> <role>  - Create new user (Admin/User)
update_user <username> <field> <value> - Update user (fields: password, role)
delete_user <username>         - Remove user
list_users                     - List all users (Admin only)

[Category Management (Admin only)]
add_category <name>            - Create new expense category
list_categories                - Show available categories

[Payment Methods (Admin only)]
add_payment_method <name>      - Add new payment method
list_payment_methods           - Show available payment methods

[Expense Management]
add_expense <amount> <category> <payment_method> <YYYY-MM-DD> <description> [tags]
                               - Record new expense
update_expense <id> <field> <value>
                               - Modify expense
delete_expense <id>           - Remove expense
list_expenses [filters]       - View expenses with optional filters

[Group Management]
add_group <name> <description> - Create new group
add_group_expense <amount> <group> <category> <payment> <date> <desc> <tags>|<users>
                               - Add group expense
add_user_to_group <user> <group> - Add member to group
list_groups
report_group_expenses <group_name> [filters]
report_group_tag_usage
report_group_category_spending
report_group_user_expenses
export_group_csv
import_group_csv

[Import/Export]
import_expenses <file.csv>    - Bulk import from CSV
export_csv <file.csv> sort-on <field>
                               - Export sorted data

[Reports]
report top_expenses <N> date-range <start> to <end>
report category_spending <category>
report above_average_expenses
report monthly_category_spending
report highest_spender_per_month
report frequent_category
report payment_method_usage
report tag_expenses

[System]
help                          - Show help
exit                          - Exit program

[Filter Examples]
list_expenses --category=food --min-amount=100
list_expenses --date=2024-03-15 --tag=urgent
list_expenses --amount=50-200 --payment-method=credit_card

[Notes]
- Dates must be in YYYY-MM-DD format
- Admin privileges required for user/category/payment management
- Tags are comma-separated
- Amount ranges use '-'
```


## Entity Relationship Diagrams
<img width="4768" alt="Untitled (14)" src="https://github.com/user-attachments/assets/9b0e9f25-ec38-4b5b-aabe-50376c78ba62" />
<img width="2560" alt="Untitled (15)" src="https://github.com/user-attachments/assets/dfd68226-bef9-42f1-81df-e93c1ad2d596" />



## Queries

The following SQL queries are used by the application to interact with the database:

### Authentication
```sql
-- Login
SELECT * FROM users 
WHERE username = ? AND password = ?
```

### User Management
```sql
-- Add User
INSERT INTO users (username, password, role)
VALUES (?, ?, ?)

-- List Users
SELECT uid, username, role FROM users

-- Update User
UPDATE users SET {field} = ? WHERE username = ?

-- Delete User
DELETE FROM users WHERE username = ?
```

### Category Management
```sql
-- Add Category
INSERT INTO categories (category_name) VALUES (?)

-- List Categories
SELECT category_name FROM categories
```

### Payment Methods
```sql
-- Add Payment Method
INSERT INTO payment_methods (method) VALUES (?)

-- List Payment Methods
SELECT method FROM payment_methods
```

### Expense Management
```sql
-- Add Expense
-- Get category ID
SELECT cid FROM categories WHERE LOWER(category_name) = ?
-- Get payment method ID
SELECT pid FROM payment_methods WHERE LOWER(method) = ?
-- Insert expense
INSERT INTO expenses (uid, amount, cid, pid, date, description)
VALUES (?, ?, ?, ?, ?, ?)
-- Handle tags
SELECT tid FROM tags WHERE tag_name = ?
INSERT INTO tags (tag_name) VALUES (?)
SELECT last_insert_rowid()
INSERT INTO expenses_tags (eid, tid) VALUES (?, ?)

-- Update Expense
SELECT uid FROM expenses WHERE eid = ?
-- For category updates
SELECT cid FROM categories WHERE category_name = ?
UPDATE expenses SET cid = ? WHERE eid = ?
-- For payment method updates
SELECT pid FROM payment_methods WHERE method = ?
UPDATE expenses SET pid = ? WHERE eid = ?
-- For tag updates
DELETE FROM expenses_tags WHERE eid = ?
SELECT tid FROM tags WHERE tag_name = ?
INSERT INTO tags (tag_name) VALUES (?)
INSERT INTO expenses_tags (eid, tid) VALUES (?, ?)
UPDATE expenses SET {field} = ? WHERE eid = ?

-- Delete Expense
SELECT uid FROM expenses WHERE eid = ?
DELETE FROM expenses_tags WHERE eid = ?
DELETE FROM expenses WHERE eid = ?

-- List Expenses
SELECT e.eid, e.amount, c.category_name, p.method, e.date, e.description,
GROUP_CONCAT(t.tag_name, ', ') AS tags
FROM expenses e
JOIN categories c ON e.cid = c.cid
JOIN payment_methods p ON e.pid = p.pid
LEFT JOIN expenses_tags et ON e.eid = et.eid
LEFT JOIN tags t ON et.tid = t.tid
WHERE e.uid = ?
GROUP BY e.eid ORDER BY e.date DESC
```

### Group Management
```sql
-- Create Group
INSERT INTO groups (group_name, description, date_created) 
VALUES (?, ?, date('now'))

-- Add User to Group
SELECT uid FROM users WHERE username = ?
SELECT gid FROM groups WHERE group_name = ?
SELECT COUNT(*) FROM user_group WHERE gid = ?
SELECT 1 FROM user_group WHERE uid = ? AND gid = ?
INSERT INTO user_group (uid, gid) VALUES (?, ?)

-- Delete Group
DELETE FROM groups WHERE group_name = ?

-- Add Group Expense
SELECT gid FROM groups WHERE group_name = ?
SELECT cid FROM categories WHERE category_name = ?
SELECT pid FROM payment_methods WHERE method = ?
INSERT INTO group_expenses (gid, d_uid, amount, cid, pid, date, description) 
VALUES (?, ?, ?, ?, ?, date('now'), ?)
SELECT tid FROM tags WHERE tag_name = ?
INSERT INTO tags (tag_name) VALUES (?)
INSERT INTO group_expense_tags (geid, tid) VALUES (?, ?)
SELECT uid FROM users WHERE username = ?
INSERT INTO split_users (geid, uid, split_amount) VALUES (?, ?, ?)
```

### Reports
```sql
-- Top Expenses
SELECT e.eid, e.amount, c.category_name, p.method, e.date, e.description,
GROUP_CONCAT(t.tag_name, ', ') AS tags
FROM expenses e
JOIN categories c ON e.cid = c.cid
JOIN payment_methods p ON e.pid = p.pid
LEFT JOIN expenses_tags et ON e.eid = et.eid
LEFT JOIN tags t ON et.tid = t.tid
WHERE e.uid = ? AND e.date BETWEEN ? AND ?
GROUP BY e.eid
ORDER BY e.amount DESC
LIMIT ?

-- Category Spending
SELECT SUM(e.amount) AS total, c.category_name
FROM expenses e
JOIN categories c ON e.cid = c.cid
WHERE e.uid = ? AND LOWER(c.category_name) = ?

-- Above Average Expenses
SELECT e.*, c.category_name, p.method, 
    (SELECT AVG(amount) FROM expenses e2 WHERE e2.cid = e.cid) AS category_avg
FROM expenses e
JOIN categories c ON e.cid = c.cid
JOIN payment_methods p ON e.pid = p.pid
WHERE e.uid = ? AND e.amount > category_avg
ORDER BY c.category_name, e.amount DESC

-- Monthly Category Spending
SELECT strftime('%Y-%m', e.date) AS month,
    c.category_name,
    SUM(e.amount) AS total,
    COUNT(e.eid) AS count
FROM expenses e
JOIN categories c ON e.cid = c.cid
WHERE e.uid = ?
GROUP BY month, c.category_name
ORDER BY month DESC, total DESC

-- Highest Spender Per Month
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

-- Frequent Category
SELECT c.category_name, COUNT(*) AS count
FROM expenses e
JOIN categories c ON e.cid = c.cid
WHERE e.uid = ?
GROUP BY c.category_name
ORDER BY count DESC
LIMIT 1

-- Payment Method Usage
SELECT p.method, SUM(e.amount) AS total_spent,
COUNT(e.eid) AS expense_count
FROM expenses e
JOIN payment_methods p ON e.pid = p.pid
WHERE e.uid = ?
GROUP BY p.method
ORDER BY total_spent DESC

-- Tag Expenses
SELECT t.tag_name, COUNT(et.eid) AS expense_count
FROM tags t
LEFT JOIN expenses_tags et ON t.tid = et.tid
WHERE EXISTS (
    SELECT 1 FROM expenses e
    WHERE e.eid = et.eid AND e.uid = ?
)
GROUP BY t.tag_name
ORDER BY expense_count DESC
```

### Import/Export
```sql
-- Import Expenses
SELECT cid FROM categories WHERE category_name = ?
SELECT pid FROM payment_methods WHERE method = ?

-- Export CSV
SELECT e.eid, e.amount, c.category_name, p.method, e.date, e.description,
GROUP_CONCAT(t.tag_name, ', ') AS tags
FROM expenses e
JOIN categories c ON e.cid = c.cid
JOIN payment_methods p ON e.pid = p.pid
LEFT JOIN expenses_tags et ON e.eid = et.eid
LEFT JOIN tags t ON et.tid = t.tid
WHERE e.uid = ?
GROUP BY e.eid
```

## Contributers
Aadit Shah,
Kalash Shah,
Maanya DN,
Nidhi,
Kunth Shah
