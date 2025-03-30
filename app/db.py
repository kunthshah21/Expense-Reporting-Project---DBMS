# app/db.py

import sqlite3
from config.config import DATABASE_CONFIG

def get_db_connection():
    db_path = DATABASE_CONFIG["sqlite"]["db_path"]
    print(f"Connecting to SQLite database at {db_path}")
    return sqlite3.connect(db_path)

def initialize_db(conn):
    cursor = conn.cursor()
    print("Creating tables...")
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT
        )
    """)
    
    # Create Payment Methods table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT NOT NULL UNIQUE
        )
    """)
    
    # Create Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            cid INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Create Tags table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tid INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Create User Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_expenses (
            eid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            date DATE NOT NULL,
            amount REAL NOT NULL,
            time TIME,
            cid INTEGER NOT NULL,
            description TEXT,
            pid INTEGER NOT NULL,
            FOREIGN KEY (uid) REFERENCES users(uid),
            FOREIGN KEY (cid) REFERENCES categories(cid),
            FOREIGN KEY (pid) REFERENCES payment_methods(pid)
        )
    """)
    
    # Create Groups table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            gid INTEGER PRIMARY KEY AUTOINCREMENT,
            date_created DATE NOT NULL,
            gname TEXT NOT NULL,
            description TEXT
        )
    """)
    
    # Create User Group (many-to-many relationship)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_group (
            gid INTEGER NOT NULL,
            uid INTEGER NOT NULL,
            PRIMARY KEY (gid, uid),
            FOREIGN KEY (gid) REFERENCES groups(gid),
            FOREIGN KEY (uid) REFERENCES users(uid)
        )
    """)
    
    # Create Group Expense table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_expense (
            geid INTEGER PRIMARY KEY AUTOINCREMENT,
            debtor_id INTEGER NOT NULL,
            date DATE NOT NULL,
            amount REAL NOT NULL,
            pid INTEGER NOT NULL,
            tag TEXT,
            FOREIGN KEY (debtor_id) REFERENCES users(uid),
            FOREIGN KEY (pid) REFERENCES payment_methods(pid)
        )
    """)
    
    # Create Split Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS split_users (
            geid INTEGER NOT NULL,
            uid INTEGER NOT NULL,
            status TEXT NOT NULL,
            split REAL NOT NULL,
            PRIMARY KEY (geid, uid),
            FOREIGN KEY (geid) REFERENCES group_expense(geid),
            FOREIGN KEY (uid) REFERENCES users(uid)
        )
    """)
    
    # Create Expense Tag (many-to-many relationship)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_tag (
            eid INTEGER NOT NULL,
            tid INTEGER NOT NULL,
            PRIMARY KEY (eid, tid),
            FOREIGN KEY (eid) REFERENCES user_expenses(eid),
            FOREIGN KEY (tid) REFERENCES tags(tid)
        )
    """)
    
    conn.commit()
