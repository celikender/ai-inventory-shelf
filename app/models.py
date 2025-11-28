import sqlite3
from datetime import datetime
from .config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    with conn:
        with open("db/schema.sql", "r") as f:
            conn.executescript(f.read())
    conn.close()


def get_all_bins():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM bins")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_reading(bin_id: int, qty: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO readings (bin_id, qty, created_at) VALUES (?, ?, ?)",
        (bin_id, qty, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_latest_readings():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r1.*
        FROM readings r1
        JOIN (
          SELECT bin_id, MAX(created_at) AS max_time
          FROM readings
          GROUP BY bin_id
        ) latest
        ON r1.bin_id = latest.bin_id AND r1.created_at = latest.max_time
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
