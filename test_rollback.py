from database.db_manager import DatabaseManager
from services.dispensing_service import DispensingService
from services.pharmacy_service import PharmacyService
from models.prescription import Prescription, PrescriptionLine

# Connect to the database and services
db = DatabaseManager()
pharmacy = PharmacyService(db)
dispensing = DispensingService(db)


def show_stock(medicine_code, branch_code):
    with db.connect() as connection:
        record = connection.execute(
            """
            SELECT quantity
            FROM stock
            WHERE medicine_code = ?
            AND branch_code = ?
            """,
            (medicine_code, branch_code)
        ).fetchone()

        return record["quantity"] if record else 0


# Record stock quantities before testing
med001_before = show_stock("MED001", "BR001")
med002_before = show_stock("MED002", "BR001")

print("STOCK BEFORE TEST")
print("MED001:", med001_before)
print("MED002:", med002_before)


# Create a prescription with insufficient stock required
test_prescription = Prescription(
    "RX-ROLLBACK-001",
    "PATIENT-DEMO-04",
    "BR001",
    "PRESC-DEMO-01",
    [
        PrescriptionLine("MED001", 5),
        PrescriptionLine("MED002", 1000)
    ]
)

try:
    pharmacy.create_prescription(test_prescription)
    print("\nPrescription created successfully.")

    dispensing.dispense("RX-ROLLBACK-001")

    print("Unexpected result: dispensing succeeded.")

except ValueError as error:
    print("\nEXPECTED FAILURE:")
    print(error)


# Check stock after the failed dispensing attempt
med001_after = show_stock("MED001", "BR001")
med002_after = show_stock("MED002", "BR001")

print("\nSTOCK AFTER TEST")
print("MED001:", med001_after)
print("MED002:", med002_after)

# Check prescription status
saved = pharmacy.get_prescription("RX-ROLLBACK-001")

print("\nPRESCRIPTION STATUS:", saved["status"])


# Verify that rollback worked
if (
    med001_before == med001_after
    and med002_before == med002_after
    and saved["status"] == "pending"
):
    print("\nSUCCESS: ATOMIC ROLLBACK WORKS!")
else:
    print("\nFAILURE: CHECK YOUR DISPENSING IMPLEMENTATION.")