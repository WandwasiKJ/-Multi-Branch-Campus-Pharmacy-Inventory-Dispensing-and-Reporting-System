class Medicine:
    def __init__(self, code, name, unit_price, reorder_level):
        self.code = code
        self.name = name
        self.unit_price = unit_price
        self.reorder_level = reorder_level

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Medicine code cannot be empty.")
        self._code = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Medicine name cannot be empty.")
        self._name = value

    @property
    def unit_price(self):
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value):
        price = float(value)
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        self._unit_price = price

    @property
    def reorder_level(self):
        return self._reorder_level

    @reorder_level.setter
    def reorder_level(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("Reorder level must be an integer.")
        if value < 0:
            raise ValueError("Reorder level cannot be negative.")
        self._reorder_level = value

    def requires_authorisation(self):
        return False

    def category(self):
        return "Ordinary"


class OrdinaryMedicine(Medicine):
    pass


class ControlledMedicine(Medicine):
    def requires_authorisation(self):
        return True

    def category(self):
        return "Controlled"