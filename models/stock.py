class Stock:

    def __init__(self, medicine_code, branch_code, quantity):

        self.medicine_code = medicine_code
        self.branch_code = branch_code
        self.quantity = quantity

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("Stock quantity must be a whole number.")

        if value < 0:
            raise ValueError("Stock quantity cannot be negative.")

        self._quantity = value

    def receive_stock(self, quantity):

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Received quantity must be a whole number.")

        if quantity <= 0:
            raise ValueError("Received quantity must be positive.")

        self.quantity += quantity

    def remove_stock(self, quantity):

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Quantity must be a whole number.")

        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        if quantity > self.quantity:
            raise ValueError("Insufficient stock available.")

        self.quantity -= quantity

    def is_low_stock(self, reorder_level):

        return self.quantity <= reorder_level

    def display_stock(self):

        return (
            f"Medicine: {self.medicine_code} | "
            f"Branch: {self.branch_code} | "
            f"Quantity: {self.quantity}"
        )

    