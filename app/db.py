# app/db.py
import sqlite3
from config.config import DATABASE_CONFIG
import datetime

def get_db_connection():
    db_path = DATABASE_CONFIG["sqlite"]["db_path"]
    return sqlite3.connect(db_path)

def initialize_db(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Users table with new fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Payment methods table remains largely the same
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT NOT NULL UNIQUE
        )
    """)
    
    # Categories table with renamed field
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            cid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Tags table with renamed field
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # User_expenses with timestamp and created_at
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_expenses (
            eid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            amount REAL NOT NULL,
            cid INTEGER NOT NULL,
            description TEXT,
            pid INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uid) REFERENCES users(uid),
            FOREIGN KEY (cid) REFERENCES categories(cid),
            FOREIGN KEY (pid) REFERENCES payment_methods(pid)
        )
    """)
    
    # Group table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            gid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # User_group for many-to-many relationship
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_group (
            gid INTEGER NOT NULL,
            uid INTEGER NOT NULL,
            PRIMARY KEY (gid, uid),
            FOREIGN KEY (gid) REFERENCES groups(gid),
            FOREIGN KEY (uid) REFERENCES users(uid)
        )
    """)
    
    # Group expense table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_expense (
            geid INTEGER PRIMARY KEY AUTOINCREMENT,
            gid INTEGER NOT NULL,
            debtor_uid INTEGER NOT NULL,
            tid INTEGER,
            timestamp DATETIME NOT NULL,
            amount REAL NOT NULL,
            pid INTEGER NOT NULL,
            cid INTEGER NOT NULL,
            description TEXT,
            FOREIGN KEY (gid) REFERENCES groups(gid),
            FOREIGN KEY (debtor_uid) REFERENCES users(uid),
            FOREIGN KEY (tid) REFERENCES tags(tid),
            FOREIGN KEY (pid) REFERENCES payment_methods(pid),
            FOREIGN KEY (cid) REFERENCES categories(cid)
        )
    """)
    
    # Split users table for expense splitting
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS split_users (
            geid INTEGER NOT NULL,
            uid INTEGER NOT NULL,
            split REAL NOT NULL,
            PRIMARY KEY (geid, uid),
            FOREIGN KEY (geid) REFERENCES group_expense(geid),
            FOREIGN KEY (uid) REFERENCES users(uid)
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