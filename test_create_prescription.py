from database.db_manager import DatabaseManager
from database.seed_data import seed_database
from services.pharmacy_service import PharmacyService
from models.prescription import Prescription, PrescriptionLine

# Connect to the existing database
db = DatabaseManager()
db.initialise()
seed_database(db)
service = PharmacyService(db)

# Make this standalone script repeatable.
with db.connect() as connection:
    connection.execute(
        "DELETE FROM prescriptions WHERE prescription_id = ?",
        ("RX-TEST-001",)
    )

# Create medicine lines
line1 = PrescriptionLine("MED001", 2)
line2 = PrescriptionLine("MED002", 3)

# Create a prescription
prescription = Prescription(
    prescription_id="RX-TEST-001",
    patient_id="PATIENT-DEMO-02",
    branch_code="BR001",
    prescriber_code="PRESC-DEMO-01",
    lines=[line1, line2]
)

# Save the prescription
try:
    service.create_prescription(prescription)
    print("Prescription successfully saved!")

except (ValueError, TypeError) as error:
    print("Error:", error)

# Retrieve and display the saved prescription
saved = service.get_prescription("RX-TEST-001")

if saved:
    print("\nSAVED PRESCRIPTION")
    print("------------------")
    print("Prescription ID:", saved["prescription_id"])
    print("Patient ID:", saved["patient_id"])
    print("Branch:", saved["branch_code"])
    print("Status:", saved["status"])

    print("\nMEDICINES")
    for line in saved["lines"]:
        print(
            line["medicine_code"],
            "- Quantity:",
            line["quantity"]
        )
else:
    print("Prescription was not found.")