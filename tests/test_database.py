import tempfile
import unittest

from database.db_manager import DatabaseManager
from models.medicine import OrdinaryMedicine
from models.branch import Branch
from services.pharmacy_service import PharmacyService


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        db_path = f"{self.temp_dir.name}/test_pharmacy.db"

        self.db = DatabaseManager(db_path)
        self.db.initialise()

        self.service = PharmacyService(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register_medicine(self):
        medicine = OrdinaryMedicine(
            "MED001", "Paracetamol", 500, 20
        )

        self.service.register_medicine(medicine)

        with self.db.connect() as connection:
            result = connection.execute(
                "SELECT * FROM medicines WHERE medicine_code = ?",
                ("MED001",)
            ).fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Paracetamol")

    def test_duplicate_medicine_code(self):
        medicine = OrdinaryMedicine(
            "MED001", "Paracetamol", 500, 20
        )

        self.service.register_medicine(medicine)

        with self.assertRaises(ValueError):
            self.service.register_medicine(medicine)

    def test_stock_receipt(self):
        medicine = OrdinaryMedicine(
            "MED001", "Paracetamol", 500, 20
        )

        branch = Branch("BR001", "Main Campus")

        self.service.register_medicine(medicine)
        self.service.register_branch(branch)

        self.service.receive_stock("MED001", "BR001", 50)
        self.service.receive_stock("MED001", "BR001", 20)

        with self.db.connect() as connection:
            result = connection.execute(
                "SELECT quantity FROM stock WHERE medicine_code = ?",
                ("MED001",)
            ).fetchone()

        self.assertEqual(result["quantity"], 70)


if __name__ == "__main__":
    unittest.main()