import sqlite3


class DispensingService:
    """Handles safe and atomic prescription dispensing."""

    def __init__(self, db):
        self.db = db

    def dispense(self, prescription_id):
        """
        Dispense a prescription using one atomic transaction.

        If any validation fails, all database changes are rolled back.
        """

        with self.db.connect() as connection:

            # Start a transaction and reserve the database for writing.
            connection.execute("BEGIN IMMEDIATE")

            # 1. Retrieve the prescription.
            prescription = connection.execute(
                """
                SELECT *
                FROM prescriptions
                WHERE prescription_id = ?
                """,
                (prescription_id,)
            ).fetchone()

            if prescription is None:
                raise ValueError("Prescription does not exist.")

            # 2. Only pending prescriptions can be dispensed.
            if prescription["status"] != "pending":
                raise ValueError(
                    "Only pending prescriptions can be dispensed."
                )

            branch_code = prescription["branch_code"]
            prescriber_code = prescription["prescriber_code"]

            # 3. Retrieve all medicine lines.
            # GROUP BY also handles repeated medicine codes correctly.
            medicine_lines = connection.execute(
                """
                SELECT
                    pl.medicine_code,
                    SUM(pl.quantity) AS required_quantity,
                    m.medicine_type
                FROM prescription_lines pl
                JOIN medicines m
                    ON pl.medicine_code = m.medicine_code
                WHERE pl.prescription_id = ?
                GROUP BY pl.medicine_code, m.medicine_type
                """,
                (prescription_id,)
            ).fetchall()

            if not medicine_lines:
                raise ValueError(
                    "Prescription has no valid medicine lines."
                )

            # 4. Check the branch exists.
            branch = connection.execute(
                """
                SELECT branch_code
                FROM branches
                WHERE branch_code = ?
                """,
                (branch_code,)
            ).fetchone()

            if branch is None:
                raise ValueError("Branch does not exist.")

            # 5. Validate every medicine before deducting any stock.
            for line in medicine_lines:

                medicine_code = line["medicine_code"]
                required_quantity = line["required_quantity"]
                medicine_type = line["medicine_type"]

                # Check controlled medicine authorisation.
                if medicine_type.lower() == "controlled":

                    authorised = connection.execute(
                        """
                        SELECT prescriber_code
                        FROM authorised_prescribers
                        WHERE prescriber_code = ?
                        AND active = 1
                        """,
                        (prescriber_code,)
                    ).fetchone()

                    if authorised is None:
                        raise ValueError(
                            f"Prescriber is not authorised to dispense "
                            f"controlled medicine {medicine_code}."
                        )

                # Check available branch stock.
                stock = connection.execute(
                    """
                    SELECT quantity
                    FROM stock
                    WHERE medicine_code = ?
                    AND branch_code = ?
                    """,
                    (medicine_code, branch_code)
                ).fetchone()

                if stock is None:
                    raise ValueError(
                        f"No stock record for {medicine_code} "
                        f"at branch {branch_code}."
                    )

                if stock["quantity"] < required_quantity:
                    raise ValueError(
                        f"Insufficient stock for {medicine_code}. "
                        f"Required: {required_quantity}, "
                        f"Available: {stock['quantity']}."
                    )

            # 6. All checks have passed. Deduct the stock.
            for line in medicine_lines:

                connection.execute(
                    """
                    UPDATE stock
                    SET quantity = quantity - ?
                    WHERE medicine_code = ?
                    AND branch_code = ?
                    AND quantity >= ?
                    """,
                    (
                        line["required_quantity"],
                        line["medicine_code"],
                        branch_code,
                        line["required_quantity"]
                    )
                )

            # 7. Update the prescription status.
            result = connection.execute(
                """
                UPDATE prescriptions
                SET status = 'dispensed'
                WHERE prescription_id = ?
                AND status = 'pending'
                """,
                (prescription_id,)
            )

            if result.rowcount != 1:
                raise ValueError(
                    "Prescription status could not be updated."
                )

            # The connection context commits when everything succeeds.
            # Any exception above causes the transaction to roll back.

        return True