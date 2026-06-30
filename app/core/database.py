import sqlite3
from contextlib import contextmanager
import bcrypt

DB_PATH = "./data/database.db"

update_timestamp_trigger = """
CREATE TRIGGER update_timestamp
AFTER UPDATE ON test
FOR EACH ROW
BEGIN
    UPDATE test
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
"""


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              description TEXT,
              status TEXT NOT NULL CHECK(status IN ('new', 'in_progress', 'done')),
              priority TEXT NOT NULL CHECK(priority IN ('low', 'normal', 'high')),
              created_at TEXT DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL
            )
            """)
        conn.execute(
            "INSERT OR IGNORE INTO users (username, hashed_password) VALUES (?, ?)",
            (
                "admin",
                bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt()).decode(
                    "utf-8"
                ),
            ),
        )
        conn.execute("DROP TRIGGER IF EXISTS update_timestamp;")
        conn.execute(update_timestamp_trigger)
        conn.commit()
