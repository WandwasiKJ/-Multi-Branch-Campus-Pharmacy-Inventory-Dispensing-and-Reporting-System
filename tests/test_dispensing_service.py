import tempfile
import unittest
from pathlib import Path

from database.db_manager import DatabaseManager
from database.seed_data import seed_database
from models.prescription import Prescription, PrescriptionLine
from services.dispensing_service import DispensingService
from services.pharmacy_service import PharmacyService


class DispensingServiceTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "pharmacy.db"

        self.db = DatabaseManager(db_path)
        self.db.initialise()
        seed_database(self.db)
        self.pharmacy = PharmacyService(self.db)
        self.dispensing = DispensingService(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_prescription(
        self,
        prescription_id,
        medicine_code="MED001",
        quantity=1,
        prescriber_code="PRESC-DEMO-01",
    ):
        prescription = Prescription(
            prescription_id,
            "PATIENT-TEST-01",
            "BR001",
            prescriber_code,
            [PrescriptionLine(medicine_code, quantity)],
        )
        self.pharmacy.create_prescription(prescription)

    def get_stock(self, medicine_code):
        with self.db.connect() as connection:
            row = connection.execute(
                """
                SELECT quantity
                FROM stock
                WHERE medicine_code = ? AND branch_code = 'BR001'
                """,
                (medicine_code,),
            ).fetchone()
        return row["quantity"]

    def test_dispensing_updates_status_and_deducts_stock(self):
        self.create_prescription("RX-SUCCESS", quantity=2)
        stock_before = self.get_stock("MED001")

        self.dispensing.dispense("RX-SUCCESS")

        saved = self.pharmacy.get_prescription("RX-SUCCESS")
        self.assertEqual(saved["status"], "dispensed")
        self.assertEqual(self.get_stock("MED001"), stock_before - 2)

    def test_insufficient_stock_returns_clear_error_without_partial_changes(self):
        self.create_prescription(
            "RX-INSUFFICIENT",
            medicine_code="MED002",
            quantity=1000,
        )
        stock_before = self.get_stock("MED002")

        with self.assertRaisesRegex(
            ValueError, "Insufficient stock for MED002"
        ):
            self.dispensing.dispense("RX-INSUFFICIENT")

        saved = self.pharmacy.get_prescription("RX-INSUFFICIENT")
        self.assertEqual(saved["status"], "pending")
        self.assertEqual(self.get_stock("MED002"), stock_before)

    def test_unauthorized_controlled_medicine_returns_clear_error(self):
        self.create_prescription(
            "RX-UNAUTHORIZED",
            medicine_code="MED003",
            prescriber_code="PRESC-UNAUTHORISED",
        )
        stock_before = self.get_stock("MED003")

        with self.assertRaisesRegex(
            ValueError, "not authorised to dispense controlled medicine MED003"
        ):
            self.dispensing.dispense("RX-UNAUTHORIZED")

        saved = self.pharmacy.get_prescription("RX-UNAUTHORIZED")
        self.assertEqual(saved["status"], "pending")
        self.assertEqual(self.get_stock("MED003"), stock_before)

    def test_prescription_cannot_be_dispensed_twice(self):
        self.create_prescription("RX-DOUBLE")
        stock_before = self.get_stock("MED001")

        self.dispensing.dispense("RX-DOUBLE")
        with self.assertRaisesRegex(
            ValueError, "Only pending prescriptions can be dispensed"
        ):
            self.dispensing.dispense("RX-DOUBLE")

        saved = self.pharmacy.get_prescription("RX-DOUBLE")
        self.assertEqual(saved["status"], "dispensed")
        self.assertEqual(self.get_stock("MED001"), stock_before - 1)


if __name__ == "__main__":
    unittest.main()
