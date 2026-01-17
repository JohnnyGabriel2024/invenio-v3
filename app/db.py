import sqlite3

DB_NAME = "base-de-datos.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # =========================
    # Tablas base
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        category_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        type TEXT,
        quantity INTEGER,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER
    )
    """)

    # =========================
    # Proveedores (NUEVO)
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # =========================
    # Agregar supplier_id a movements (idempotente)
    # =========================

    cur.execute("PRAGMA table_info(movements)")
    columns = [row[1] for row in cur.fetchall()]

    if "supplier_id" not in columns:
        cur.execute("""
        ALTER TABLE movements
        ADD COLUMN supplier_id INTEGER
        """)

    conn.commit()
    conn.close()


def query(sql, params=(), one=False):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows[0] if one and rows else rows
