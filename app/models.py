import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "inventory.db"
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables from db/schema.sql (idempotent)."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


# ---------- PRODUCTS / BINS HELPERS ----------

def create_product(name: str, sku: str | None = None, notes: str | None = None) -> int:
    """Insert a product and return its id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO products (name, sku, notes)
        VALUES (?, ?, ?)
        """,
        (name, sku, notes),
    )
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    return product_id


def create_bin(
    label: str,
    product_id: int | None,
    max_qty: int,
    low_threshold: int,
    roi_x: int,
    roi_y: int,
    roi_w: int,
    roi_h: int,
) -> int:
    """Insert a bin and return its id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO bins (label, product_id, max_qty, low_threshold, roi_x, roi_y, roi_w, roi_h)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (label, product_id, max_qty, low_threshold, roi_x, roi_y, roi_w, roi_h),
    )
    conn.commit()
    bin_id = cur.lastrowid
    conn.close()
    return bin_id


def insert_demo_bin() -> None:
    """Create one demo product + bin so /bins has something to show."""
    product_id = create_product("Demo product", "DEMO-001", "Test product for shelf MVP")
    create_bin(
        label="Bin 1",
        product_id=product_id,
        max_qty=10,
        low_threshold=3,
        roi_x=0,
        roi_y=0,
        roi_w=100,
        roi_h=100,
    )


def get_all_bins() -> list[dict]:
    """Return all bins with attached product info (if any)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            b.id          AS bin_id,
            b.label       AS bin_label,
            b.max_qty,
            b.low_threshold,
            b.roi_x,
            b.roi_y,
            b.roi_w,
            b.roi_h,
            p.id          AS product_id,
            p.name        AS product_name,
            p.sku         AS product_sku
        FROM bins b
        LEFT JOIN products p ON b.product_id = p.id
        ORDER BY b.id
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ---------- READINGS HELPERS ----------

def insert_reading(bin_id: int, qty: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO readings (bin_id, qty, created_at)
        VALUES (?, ?, ?)
        """,
        (bin_id, qty, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_latest_readings() -> list[dict]:
    """Latest reading per bin."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.bin_id, r.qty, r.created_at
        FROM readings r
        JOIN (
            SELECT bin_id, MAX(created_at) AS max_ts
            FROM readings
            GROUP BY bin_id
        ) latest
        ON r.bin_id = latest.bin_id AND r.created_at = latest.max_ts
        ORDER BY r.bin_id
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
