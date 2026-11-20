import sqlite3


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