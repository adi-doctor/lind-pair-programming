import os
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL REFERENCES patients(id),
    filename TEXT NOT NULL,
    visit_date TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id TEXT NOT NULL REFERENCES notes(id),
    patient_id TEXT NOT NULL REFERENCES patients(id),
    event_type TEXT NOT NULL,
    name TEXT NOT NULL,
    event_date TEXT NOT NULL
);
"""


def get_conn() -> sqlite3.Connection:
    path = os.environ.get("CHRONICLE_DB", "chronicle.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
