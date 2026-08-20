import os
import sqlite3

# On Render's free tier the filesystem is ephemeral, but SQLite still works
# fine for a demo/portfolio deployment - no external database service needed.
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "homeservice.db"))


def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    """Create all tables if they don't already exist. Safe to call every startup."""
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            mobile TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            mobile TEXT NOT NULL,
            city TEXT,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS booking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            contact TEXT NOT NULL,
            service TEXT NOT NULL,
            address TEXT NOT NULL,
            landmark TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migration for older DBs created before the status column existed.
    cur.execute("PRAGMA table_info(booking)")
    columns = [row[1] for row in cur.fetchall()]
    if "status" not in columns:
        cur.execute("ALTER TABLE booking ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'")

    con.commit()
    cur.close()
    con.close()
