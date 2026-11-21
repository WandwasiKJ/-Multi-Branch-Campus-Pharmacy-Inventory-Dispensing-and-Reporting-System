from database.db_manager import DatabaseManager
from services.dispensing_service import DispensingService
from services.pharmacy_service import PharmacyService
from models.prescription import Prescription, PrescriptionLine


db = DatabaseManager()
db.initialise()
pharmacy = PharmacyService(db)
dispensing = DispensingService(db)

# Make this standalone script repeatable.
with db.connect() as connection:
    connection.execute(
        "DELETE FROM prescriptions WHERE prescription_id = ?",
        ("RX-DISPENSE-001",)
    )


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


# Create a fresh prescription for this test.
prescription = Prescription(
    "RX-DISPENSE-001",
    "PATIENT-DEMO-03",
    "BR001",
    "PRESC-DEMO-01",
    [
        PrescriptionLine("MED001", 2),
        PrescriptionLine("MED002", 3)
    ]
)

try:
    pharmacy.create_prescription(prescription)

    print("Prescription created successfully.")

    print("\nSTOCK BEFORE DISPENSING")
    print("Paracetamol:", show_stock("MED001", "BR001"))
    print("Amoxicillin:", show_stock("MED002", "BR001"))

    dispensing.dispense("RX-DISPENSE-001")

    print("\nPrescription successfully dispensed!")

    print("\nSTOCK AFTER DISPENSING")
    print("Paracetamol:", show_stock("MED001", "BR001"))
    print("Amoxicillin:", show_stock("MED002", "BR001"))

    saved = pharmacy.get_prescription("RX-DISPENSE-001")
    print("\nPrescription status:", saved["status"])

except (ValueError, TypeError) as error:
    print("\nDISPENSING FAILED:", error)