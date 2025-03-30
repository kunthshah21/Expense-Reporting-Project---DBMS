# app/db.py
import sqlite3
from config.config import DATABASE_CONFIG

def get_db_connection():
    db_path = DATABASE_CONFIG["sqlite"]["db_path"]
    return sqlite3.connect(db_path)

def initialize_db(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Users table with username and password
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    # Other tables (payment_methods, categories, tags) remain the same
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT NOT NULL UNIQUE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            cid INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tid INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT NOT NULL UNIQUE
        )
    """)
    
    # User_expenses without 'time' column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_expenses (
            eid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            date DATE NOT NULL,
            amount REAL NOT NULL,
            cid INTEGER NOT NULL,
            description TEXT,
            pid INTEGER NOT NULL,
            FOREIGN KEY (uid) REFERENCES users(uid),
            FOREIGN KEY (cid) REFERENCES categories(cid),
            FOREIGN KEY (pid) REFERENCES payment_methods(pid)
        )
    """)
    
    # Expense_tag for many-to-many relationship
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