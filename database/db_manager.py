import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "digisave.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.initialize_db()

    def get_connection(self):
        """Creates a database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enables accessing columns by name
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_db(self):
        """Executes the schema script if the database is newly created."""
        if os.path.exists(SCHEMA_PATH):
            with self.get_connection() as conn:
                with open(SCHEMA_PATH, "r") as f:
                    conn.executescript(f.read())
                conn.commit()
        else:
            raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    def execute_query(self, query, params=()):
        """Executes INSERT, UPDATE, or DELETE queries and returns last row ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def fetch_all(self, query, params=()):
        """Fetches all rows for a SELECT query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query, params=()):
        """Fetches a single row for a SELECT query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None