import sqlite3
from models.prescription import Prescription


class PharmacyService:

    def __init__(self, db):
        self.db = db

    def register_medicine(self, medicine):

        medicine_type = medicine.category().lower()

        try:
            with self.db.connect() as connection:

                connection.execute("""
                    INSERT INTO medicines
                    (medicine_code, name, unit_price,
                     reorder_level, medicine_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    medicine.code,
                    medicine.name,
                    medicine.unit_price,
                    medicine.reorder_level,
                    medicine_type
                ))

            return "Medicine registered successfully."

        except sqlite3.IntegrityError as error:
            raise ValueError(
                f"Medicine could not be registered: {error}"
            )

    def register_branch(self, branch):

        try:
            with self.db.connect() as connection:

                connection.execute("""
                    INSERT INTO branches
                    (branch_code, branch_name)
                    VALUES (?, ?)
                """, (
                    branch.branch_code,
                    branch.branch_name
                ))

            return "Branch registered successfully."

        except sqlite3.IntegrityError as error:
            raise ValueError(
                f"Branch could not be registered: {error}"
            )

    def receive_stock(self, medicine_code, branch_code, quantity):

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Quantity must be a whole number.")

        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        with self.db.connect() as connection:

            connection.execute("""
                INSERT INTO stock
                (medicine_code, branch_code, quantity)
                VALUES (?, ?, ?)

                ON CONFLICT(medicine_code, branch_code)
                DO UPDATE SET
                    quantity = stock.quantity + excluded.quantity
            """, (
                medicine_code,
                branch_code,
                quantity
            ))

        return "Stock received successfully."

    def get_low_stock(self, branch_code=None):

        query = """
            SELECT
                medicines.medicine_code,
                medicines.name,
                branches.branch_name,
                stock.quantity,
                medicines.reorder_level

            FROM stock

            JOIN medicines
                ON stock.medicine_code = medicines.medicine_code

            JOIN branches
                ON stock.branch_code = branches.branch_code

            WHERE stock.quantity <= medicines.reorder_level
        """

        parameters = ()

        if branch_code:
            query += " AND stock.branch_code = ?"
            parameters = (branch_code,)

        with self.db.connect() as connection:
            results = connection.execute(
                query, parameters
            ).fetchall()

        return results

    def create_prescription(self, prescription):
        """Save a prescription and all its medicine lines."""

        if not isinstance(prescription, Prescription):
            raise TypeError("Expected a Prescription object.")

        try:
            # The connection context commits on success
            # and rolls back if an exception occurs.
            with self.db.connect() as connection:

                connection.execute(
                    """
                    INSERT INTO prescriptions (
                        prescription_id,
                        patient_id,
                        branch_code,
                        prescriber_code,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        prescription.prescription_id,
                        prescription.patient_id,
                        prescription.branch_code,
                        prescription.prescriber_code,
                        prescription.status
                    )
                )

                # Save every medicine line.
                for line in prescription.lines:
                    connection.execute(
                        """
                        INSERT INTO prescription_lines (
                            prescription_id,
                            medicine_code,
                            quantity
                        )
                        VALUES (?, ?, ?)
                        """,
                        (
                            prescription.prescription_id,
                            line.medicine_code,
                            line.quantity
                        )
                    )

            return True

        except sqlite3.IntegrityError as error:
            raise ValueError(
                f"Could not save prescription. "
                f"Check duplicate IDs and referenced records: {error}"
            ) from error

    def get_prescription(self, prescription_id):
        """Retrieve a prescription together with its medicine lines."""

        with self.db.connect() as connection:

            prescription = connection.execute(
                """
                SELECT *
                FROM prescriptions
                WHERE prescription_id = ?
                """,
                (prescription_id,)
            ).fetchone()

            if prescription is None:
                return None

            lines = connection.execute(
                """
                SELECT *
                FROM prescription_lines
                WHERE prescription_id = ?
                """,
                (prescription_id,)
            ).fetchall()

            result = dict(prescription)
            result["lines"] = [dict(line) for line in lines]

            return result