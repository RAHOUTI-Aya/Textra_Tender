import sqlite3
import hashlib
from datetime import datetime
import streamlit as st

# Database path
DB_PATH = "textra_tender.db"

def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    return conn

def initialize_database():
    """Create tables if they don't exist and add default admin user"""
    conn = create_connection()
    if conn is not None:
        try:
            # Create users table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            ''')
            
            # Create tenders table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS tenders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            ''')
            
            # Create bids table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS bids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tender_id INTEGER NOT NULL,
                bidder_username TEXT NOT NULL,
                amount REAL NOT NULL,
                proposal TEXT NOT NULL,
                status TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                FOREIGN KEY (tender_id) REFERENCES tenders (id),
                FOREIGN KEY (bidder_username) REFERENCES users (username)
            )
            ''')
            
            # Check if admin exists, create if not
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                admin_password = hash_password("admin123")
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(
                    "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                    ("admin", admin_password, "admin", created_at)
                )
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    else:
        st.error("Error: Cannot create the database connection.")

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()