import unittest
from models.medicine import OrdinaryMedicine, ControlledMedicine


class MedicineTests(unittest.TestCase):

    def test_ordinary_medicine(self):
        medicine = OrdinaryMedicine(
            "MED001", "Paracetamol", 500, 20
        )
        self.assertEqual(medicine.category(), "Ordinary")
        self.assertFalse(medicine.requires_authorisation())

    def test_controlled_medicine(self):
        medicine = ControlledMedicine(
            "MED002", "Sample Controlled Medicine", 1500, 5
        )
        self.assertEqual(medicine.category(), "Controlled")
        self.assertTrue(medicine.requires_authorisation())

    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            OrdinaryMedicine("MED003", "Test Medicine", 0, 5)

    def test_negative_reorder_level(self):
        with self.assertRaises(ValueError):
            OrdinaryMedicine("MED004", "Test Medicine", 500, -2)


if __name__ == "__main__":
    unittest.main()