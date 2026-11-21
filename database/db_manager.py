"""SQLite connection and schema initialisation."""
from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "pharmacy.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


class ManagedConnection(sqlite3.Connection):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
        return False


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        connection = sqlite3.connect(
            self.db_path,
            factory=ManagedConnection
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialise(self):
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        with self.connect() as connection:
            connection.executescript(schema)