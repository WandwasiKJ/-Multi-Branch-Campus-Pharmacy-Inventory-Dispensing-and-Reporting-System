from database.db_manager import DatabaseManager
from database.seed_data import seed_database

# Connect to the pharmacy database
db = DatabaseManager()
db.initialise()
seed_database(db)

# Tables we want to inspect
tables = [
    "medicines",
    "branches",
    "stock",
    "authorised_prescribers",
    "prescriptions",
    "prescription_lines"
]

with db.connect() as connection:

    for table in tables:
        table_exists = connection.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'table' AND name = ?",
            (table,)
        ).fetchone()

        if not table_exists:
            continue

        print("\n" + "=" * 60)
        print(f"TABLE: {table.upper()}")
        print("=" * 60)

        records = connection.execute(
            f"SELECT * FROM {table}"
        ).fetchall()

        if records:
            for record in records:
                print(dict(record))
        else:
            print("No records found in this table.")