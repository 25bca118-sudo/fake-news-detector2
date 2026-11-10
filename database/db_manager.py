import sqlite3
import json
from pathlib import Path
from truthlens_ai.config import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    schema_file = Path(__file__).parent / 'schema.sql'
    with open(schema_file, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def execute_insert(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def execute_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def execute_scalar(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def execute_update(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()
