import unittest

from models.prescription import Prescription, PrescriptionLine


class TestPrescription(unittest.TestCase):

    def setUp(self):
        self.line1 = PrescriptionLine("MED001", 2)
        self.line2 = PrescriptionLine("MED002", 3)

        self.prescription = Prescription(
            "RX001",
            "PATIENT-DEMO-01",
            "BR001",
            "PRESC-DEMO-01",
            [self.line1, self.line2]
        )

    def test_prescription_starts_pending(self):
        self.assertEqual(self.prescription.status, "pending")

    def test_prescription_has_two_medicines(self):
        self.assertEqual(len(self.prescription.lines), 2)

    def test_mark_as_dispensed(self):
        self.prescription.mark_dispensed()
        self.assertEqual(self.prescription.status, "dispensed")

    def test_cancel_prescription(self):
        self.prescription.cancel()
        self.assertEqual(self.prescription.status, "cancelled")

    def test_cannot_dispense_cancelled_prescription(self):
        self.prescription.cancel()

        with self.assertRaises(ValueError):
            self.prescription.mark_dispensed()

    def test_quantity_must_be_positive(self):
        with self.assertRaises(ValueError):
            PrescriptionLine("MED001", 0)


if __name__ == "__main__":
    unittest.main()