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
        category_name TEXT UNIQUE NOT NULL
    )""")

    # Payment methods table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment_methods (
        pid INTEGER PRIMARY KEY AUTOINCREMENT,
        method TEXT UNIQUE NOT NULL
    )""")

    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        eid INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER NOT NULL,
        amount REAL NOT NULL,
        cid INTEGER NOT NULL,
        pid INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        tag TEXT,
        FOREIGN KEY(uid) REFERENCES users(uid),
        FOREIGN KEY(cid) REFERENCES categories(cid),
        FOREIGN KEY(pid) REFERENCES payment_methods(pid)
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