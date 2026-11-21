"""Application entry point."""
import argparse
from database.db_manager import DatabaseManager
from database.seed_data import seed_database
from ui.app import PharmacyApp

def main():
    parser = argparse.ArgumentParser(description="Campus Pharmacy System")
    parser.add_argument("--init-db", action="store_true", help="Create database tables")
    parser.add_argument("--seed", action="store_true", help="Insert fictional sample records")
    args = parser.parse_args()

    db = DatabaseManager()
    if args.init_db:
        db.initialise()
        print("Database tables created.")
        return
    if args.seed:
        db.initialise()
        seed_database(db)
        print("Fictional sample data loaded.")
        return

    db.initialise()
    PharmacyApp(db).run()

if __name__ == "__main__":
    main()
