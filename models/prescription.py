class PrescriptionLine:
    """Represents one medicine item on a prescription."""

    def __init__(self, medicine_code, quantity):
        if not isinstance(medicine_code, str) or not medicine_code.strip():
            raise ValueError("Medicine code cannot be empty.")

        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        self.medicine_code = medicine_code.strip()
        self.quantity = quantity

    def __str__(self):
        return f"{self.medicine_code}: {self.quantity} units"


class Prescription:
    """Represents a prescription containing one or more medicines."""

    VALID_STATUSES = ("pending", "dispensed", "cancelled")

    def __init__(
        self,
        prescription_id,
        patient_id,
        branch_code,
        prescriber_code,
        lines
    ):
        if not prescription_id or not prescription_id.strip():
            raise ValueError("Prescription ID cannot be empty.")

        if not patient_id or not patient_id.strip():
            raise ValueError("Patient ID cannot be empty.")

        if not branch_code or not branch_code.strip():
            raise ValueError("Branch code cannot be empty.")

        if not prescriber_code or not prescriber_code.strip():
            raise ValueError("Prescriber code cannot be empty.")

        if not isinstance(lines, list) or len(lines) == 0:
            raise ValueError("A prescription must contain at least one medicine.")

        for line in lines:
            if not isinstance(line, PrescriptionLine):
                raise ValueError("Every item must be a PrescriptionLine.")

        self.prescription_id = prescription_id.strip()
        self.patient_id = patient_id.strip()
        self.branch_code = branch_code.strip()
        self.prescriber_code = prescriber_code.strip()
        self.lines = lines
        self.status = "pending"

    def mark_dispensed(self):
        """Change status only when the prescription is pending."""
        if self.status != "pending":
            raise ValueError(
                "Only pending prescriptions can be dispensed."
            )

        self.status = "dispensed"

    def cancel(self):
        """Cancel a pending prescription."""
        if self.status != "pending":
            raise ValueError(
                "Only pending prescriptions can be cancelled."
            )

        self.status = "cancelled"

    def display_prescription(self):
        print(f"Prescription ID: {self.prescription_id}")
        print(f"Patient ID: {self.patient_id}")
        print(f"Branch: {self.branch_code}")
        print(f"Prescriber: {self.prescriber_code}")
        print(f"Status: {self.status}")

        print("Medicines:")
        for line in self.lines:
            print(f"  {line}")