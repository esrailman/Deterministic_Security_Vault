import sqlite3
from pathlib import Path

# Veritabanı dosya yolu (backend klasörü içinde vault.db oluşacak)
DB_PATH = Path(__file__).resolve().parent / "vault.db"


def get_connection():
    """SQLite veritabanına bağlanır ve connection nesnesi döner."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """records tablosu yoksa oluşturur."""
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
    """Yeni bir kayıt ekler (timestamp DIŞARIDAN gelir)."""
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
    """En son eklenen kaydı döndürür."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()

    conn.close()
    return row


def get_records():
    """Tüm kayıtları döndürür."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records ORDER BY id ASC")
    rows = cur.fetchall()

    conn.close()
    return rows


def verify_chain():
    """
    Hash chain tutarlılığını kontrol eder.
    """
    records = get_records()

    if not records or len(records) == 1:
        return True, []

    broken_records = []

    for i in range(1, len(records)):
        prev_record = records[i - 1]
        current_record = records[i]

        if current_record["prev_hash"] != prev_record["file_hash"]:
            broken_records.append(current_record["id"])

    return len(broken_records) == 0, broken_records


def get_record_by_hash(file_hash: str):
    """
    Belirtilen file_hash değerine sahip kaydı döndürür.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records WHERE file_hash = ?", (file_hash,))
    row = cur.fetchone()

    conn.close()
    return row
