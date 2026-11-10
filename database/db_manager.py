import sqlite3
from config import DATABASE_PATH


def get_db_connection():
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    schema_file = __import__("pathlib").Path(__file__).parent / "schema.sql"
    with get_db_connection() as conn:
        with open(schema_file, "r", encoding="utf-8") as f:
            conn.executescript(f.read())


def execute_insert(query, params=()):
    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        return cursor.lastrowid


def execute_query(query, params=()):
    with get_db_connection() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def execute_scalar(query, params=()):
    with get_db_connection() as conn:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None


def execute_update(query, params=()):
    with get_db_connection() as conn:
        conn.execute(query, params)
