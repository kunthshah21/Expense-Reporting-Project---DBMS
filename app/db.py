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
    # Example: Create a table for users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    # Create table for expense categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    """)
    # Create table for payment methods
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method_name TEXT NOT NULL UNIQUE
        )
    """)
    # Create table for expenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category_id INTEGER,
            payment_method_id INTEGER,
            date TEXT,
            description TEXT,
            tag TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
        )
    """)
    conn.commit()
