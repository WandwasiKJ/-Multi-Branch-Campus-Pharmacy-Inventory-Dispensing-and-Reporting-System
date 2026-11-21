class Branch:

    def __init__(self, branch_code, branch_name):

        self.branch_code = branch_code
        self.branch_name = branch_name

    @property
    def branch_code(self):
        return self._branch_code

    @branch_code.setter
    def branch_code(self, value):

        value = str(value).strip()

        if not value:
            raise ValueError("Branch code cannot be empty.")

        self._branch_code = value

    @property
    def branch_name(self):
        return self._branch_name

    @branch_name.setter
    def branch_name(self, value):

        value = str(value).strip()

        if not value:
            raise ValueError("Branch name cannot be empty.")

        self._branch_name = value

    def display_branch(self):

        return f"{self.branch_code} - {self.branch_name}"