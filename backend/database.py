import sqlite3
from pathlib import Path

# Database file path (vault.db will be created inside the backend folder)
DB_PATH = Path(__file__).resolve().parent / "vault.db"


def get_connection():
    """Connects to the SQLite database and returns the connection object."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the records table if it does not exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            file_hash TEXT,
            prev_hash TEXT,
            timestamp TEXT,
            user_key TEXT,
            merkle_root TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def insert_record(
    file_name: str,
    file_hash: str,
    prev_hash: str,
    user_key: str,
    merkle_root: str,
    timestamp: str
):
    """Inserts a new record (timestamp comes from OUTSIDE)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO records (file_name, file_hash, prev_hash, timestamp, user_key, merkle_root)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (file_name, file_hash, prev_hash, timestamp, user_key, merkle_root)
    )

    conn.commit()
    conn.close()


def get_last_record():
    """Returns the last added record."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()

    conn.close()
    return row


def get_records():
    """Returns all records."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records ORDER BY id ASC")
    rows = cur.fetchall()

    conn.close()
    return rows


def get_record_by_hash(file_hash: str):
    """
    Returns the record with the specified file_hash.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records WHERE file_hash = ?", (file_hash,))
    row = cur.fetchone()

    conn.close()
    return row

