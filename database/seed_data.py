"""Fictional sample data only."""
def seed_database(db):
    medicines = [
        ("MED001", "Sample Paracetamol", 500.0, 20, "ordinary"),
        ("MED002", "Sample Amoxicillin", 1200.0, 10, "ordinary"),
        ("MED003", "Sample Controlled Item", 2500.0, 5, "controlled"),
    ]
    branches = [("BR001", "Main Campus Pharmacy"), ("BR002", "Satellite Clinic")]
    stock = [
        ("MED001", "BR001", 100), ("MED002", "BR001", 40),
        ("MED003", "BR001", 12), ("MED001", "BR002", 8),
    ]
    prescribers = [
        ("PRESC-DEMO-01", "Fictional Prescriber One", 1),
        ("PRESC-UNAUTHORISED", "Fictional Unauthorised Prescriber", 0),
    ]

    with db.connect() as con:
        con.executemany("INSERT OR IGNORE INTO medicines VALUES (?, ?, ?, ?, ?)", medicines)
        con.executemany("INSERT OR IGNORE INTO branches VALUES (?, ?)", branches)
        con.executemany("INSERT OR IGNORE INTO stock VALUES (?, ?, ?)", stock)
        con.executemany(
            "INSERT OR IGNORE INTO authorised_prescribers VALUES (?, ?, ?)", prescribers
        )
        