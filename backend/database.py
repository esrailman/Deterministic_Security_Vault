import sqlite3
from datetime import datetime
from pathlib import Path

# Veritabanı dosya yolu (backend klasörü içinde vault.db oluşacak)
DB_PATH = Path(__file__).resolve().parent / "vault.db"

# ------------------------------
# 1) Veritabanı bağlantısı
# ------------------------------
def get_connection():
    """SQLite veritabanına bağlanır ve connection nesnesi döner."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Verileri dictionary gibi okumamızı sağlar
    return conn

# ------------------------------
# 2) Veritabanı kurulum fonksiyonu (TABLO OLUŞTURMA)
# ------------------------------
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

# ------------------------------
# 3) Yeni kayıt ekleme fonksiyonu
# ------------------------------
def insert_record(file_name: str, file_hash: str, prev_hash: str, user_key: str, merkle_root: str):
    """Yeni bir kayıt ekler."""
    conn = get_connection()
    cur = conn.cursor()

    ts = datetime.utcnow().isoformat()

    cur.execute(
        """
        INSERT INTO records (file_name, file_hash, prev_hash, timestamp, user_key, merkle_root)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (file_name, file_hash, prev_hash, ts, user_key, merkle_root)
    )

    conn.commit()
    conn.close()

# ------------------------------
# 4) Son kaydı getir (hash chain için gerekli)
# ------------------------------
def get_last_record():
    """En son eklenen kaydı döndürür."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()

    conn.close()
    return row

# ------------------------------
# 5) Tüm kayıtları getir (audit için)
# ------------------------------
def get_records():
    """Tüm kayıtları döndürür."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records ORDER BY id ASC")
    rows = cur.fetchall()

    conn.close()
    return rows
