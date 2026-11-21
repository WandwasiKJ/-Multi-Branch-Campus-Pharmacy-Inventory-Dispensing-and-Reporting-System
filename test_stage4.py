from database.db_manager import DatabaseManager
from database.seed_data import seed_database
from services.pharmacy_service import PharmacyService
from services.dispensing_service import DispensingService
from models.prescription import Prescription, PrescriptionLine


db = DatabaseManager()
db.initialise()
seed_database(db)
pharmacy = PharmacyService(db)
dispensing = DispensingService(db)

# Make this standalone script repeatable.
with db.connect() as connection:
    connection.executemany(
        "DELETE FROM prescriptions WHERE prescription_id = ?",
        [
            ("RX-TEST-CONTROLLED",),
            ("RX-TEST-DOUBLE",),
            ("RX-TEST-CANCELLED",),
        ]
    )


def get_status(prescription_id):
    saved = pharmacy.get_prescription(prescription_id)
    return saved["status"] if saved else None


def add_prescription(prescription_id, prescriber, medicine, quantity):
    prescription = Prescription(
        prescription_id,
        "PATIENT-TEST-01",
        "BR001",
        prescriber,
        [PrescriptionLine(medicine, quantity)]
    )
    pharmacy.create_prescription(prescription)


# ------------------------------------------------
# TEST 1: UNAUTHORISED CONTROLLED MEDICINE
# ------------------------------------------------

print("\nTEST 1: UNAUTHORISED CONTROLLED MEDICINE")

add_prescription(
    "RX-TEST-CONTROLLED",
    "PRESC-UNAUTHORISED",
    "MED003",
    1
)

try:
    dispensing.dispense("RX-TEST-CONTROLLED")
    print("FAILED: Unauthorised prescriber was accepted.")

except ValueError as error:
    print("PASSED:", error)

print("Prescription status:",
      get_status("RX-TEST-CONTROLLED"))


# ------------------------------------------------
# TEST 2: PREVENT DOUBLE DISPENSING
# ------------------------------------------------

print("\nTEST 2: PREVENT DOUBLE DISPENSING")

add_prescription(
    "RX-TEST-DOUBLE",
    "PRESC-DEMO-01",
    "MED001",
    1
)

try:
    dispensing.dispense("RX-TEST-DOUBLE")
    print("First dispensing successful.")

    try:
        dispensing.dispense("RX-TEST-DOUBLE")
        print("FAILED: Prescription was dispensed twice.")

    except ValueError as error:
        print("PASSED:", error)

except ValueError as error:
    print("Could not complete double-dispensing test:", error)

print("Prescription status:",
      get_status("RX-TEST-DOUBLE"))


# ------------------------------------------------
# TEST 3: PREVENT DISPENSING CANCELLED PRESCRIPTION
# ------------------------------------------------

print("\nTEST 3: CANCELLED PRESCRIPTION")

add_prescription(
    "RX-TEST-CANCELLED",
    "PRESC-DEMO-01",
    "MED001",
    1
)

# Cancel the prescription directly in the database.
with db.connect() as connection:
    connection.execute(
        """
        UPDATE prescriptions
        SET status = 'cancelled'
        WHERE prescription_id = ?
        """,
        ("RX-TEST-CANCELLED",)
    )

try:
    dispensing.dispense("RX-TEST-CANCELLED")
    print("FAILED: Cancelled prescription was dispensed.")

except ValueError as error:
    print("PASSED:", error)

print("Prescription status:",
      get_status("RX-TEST-CANCELLED"))


print("\n================================")
print("STAGE 4 TESTING COMPLETED")
print("================================")