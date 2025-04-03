import sqlite3
import os
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('db/expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    PRAGMA foreign_keys = ON;
    """)
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        uid INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('Admin', 'User')) NOT NULL
    )""")

    # Categories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        cid INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL CHECK(category_name =LOWER(category_name))
    )""")

    # Payment methods table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment_methods (
        pid INTEGER PRIMARY KEY AUTOINCREMENT,
        method TEXT NOT NULL
    )""")

    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        eid INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER NOT NULL,
        amount REAL NOT NULL CHECK(amount >= 0),
        cid INTEGER NOT NULL,
        pid INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY(uid) REFERENCES users(uid),
        FOREIGN KEY(cid) REFERENCES categories(cid) ON DELETE RESTRICT,
        FOREIGN KEY(pid) REFERENCES payment_methods(pid) ON DELETE RESTRICT
    )""")

    # TAG table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags(
        tid INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_name TEXT UNIQUE NOT NULL CHECK(tag_name = LOWER(tag_name))
    )""")

    # Expense_TAG relationship table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses_tags
    (
        tid INTEGER NOT NULL,
        eid INTEGER NOT NULL,
        PRIMARY KEY (eid, tid),
        FOREIGN KEY(tid) REFERENCES tags(tid) ON DELETE RESTRICT,
        FOREIGN KEY(eid) REFERENCES expenses(eid) ON DELETE RESTRICT
    )
    """)

    # Expenses group
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups(
        gid INTEGER PRIMARY KEY AUTOINCREMENT,
        date_created TEXT NOT NULL,
        group_name TEXT UNIQUE NOT NULL,
        description TEXT
    )""")

    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_group (
        uid INTEGER NOT NULL,
        gid INTEGER NOT NULL,
        PRIMARY KEY (uid, gid),
        FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE RESTRICT,
        FOREIGN KEY(gid) REFERENCES groups(gid) ON DELETE RESTRICT
    )""")
    
    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_expenses (
        geid INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER NOT NULL,
        gid INTEGER NOT NULL,
        amount REAL NOT NULL CHECK(amount >= 0),
        cid INTEGER NOT NULL,
        pid INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE RESTRICT,
        FOREIGN KEY(gid) REFERENCES groups(gid) ON DELETE RESTRICT,
        FOREIGN KEY(cid) REFERENCES categories(cid) ON DELETE RESTRICT,
        FOREIGN KEY(pid) REFERENCES payment_methods(pid) ON DELETE RESTRICT
    )""")

        # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS split_users (
            geid INTEGER NOT NULL,
            uid INTEGER NOT NULL,
            split_amount REAL NOT NULL CHECK(split_amount >= 0),
            PRIMARY KEY (uid, geid),
            FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE RESTRICT,
            FOREIGN KEY(geid) REFERENCES group_expenses(geid) ON DELETE RESTRICT
        );
    """)

    # GROUP_TAG table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_expense_tags(
        tid INTEGER NOT NULL,
        geid INTEGER NOT NULL,
        PRIMARY KEY (geid, tid),
        FOREIGN KEY(tid) REFERENCES tags(tid) ON DELETE RESTRICT,
        FOREIGN KEY(geid) REFERENCES group_expenses(geid) ON DELETE RESTRICT
    )""")

    # Create default admin
    try:
        cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES ('admin', 'admin123', 'Admin')
        """)
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()