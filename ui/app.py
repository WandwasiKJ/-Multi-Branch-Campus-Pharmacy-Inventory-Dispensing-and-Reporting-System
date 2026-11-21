from models.medicine import OrdinaryMedicine, ControlledMedicine
from models.branch import Branch
from services.pharmacy_service import PharmacyService
import tkinter as tk
from tkinter import ttk, messagebox
from models.prescription import Prescription, PrescriptionLine
from services.dispensing_service import DispensingService 

class PharmacyApp:
    def __init__(self, db):
        self.db = db
        self.dispensing_service = DispensingService(db)

        self.pharmacy_service = PharmacyService(db)

        # Main application window
        self.root = tk.Tk()
        self.root.title("Campus Pharmacy Management System")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.configure(bg="#F4F6F9")

        # Application colours
        self.primary = "#17365D"
        self.secondary = "#2874A6"
        self.background = "#F4F6F9"
        self.white = "#FFFFFF"

        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            font=("Arial", 10),
            rowheight=30,
            background=self.white,
            fieldbackground=self.white
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            background="#DCE6F1",
            foreground=self.primary
        )

    def create_layout(self):

        # Header
        header = tk.Frame(
            self.root,
            bg=self.primary,
            height=75
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="CAMPUS PHARMACY MANAGEMENT SYSTEM",
            bg=self.primary,
            fg=self.white,
            font=("Arial", 17, "bold")
        ).pack(side="left", padx=25, pady=20)

        # Main body
        body = tk.Frame(self.root, bg=self.background)
        body.pack(fill="both", expand=True)

        # Navigation sidebar
        self.sidebar = tk.Frame(
            body,
            bg=self.primary,
            width=220
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="MAIN MENU",
            bg=self.primary,
            fg="#AFC6DD",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=20, pady=(25, 15))

        menu_items = [
            ("Dashboard", self.show_dashboard),
            ("Medicines", self.show_medicines),
            ("Branches & Stock", self.show_stock),
            ("Prescriptions", self.show_prescriptions),
            ("Dispensing", self.show_dispensing),
            ("Low Stock Reports", self.show_reports)
        ]

        for label, command in menu_items:
            button = tk.Button(
                self.sidebar,
                text=label,
                command=command,
                bg=self.primary,
                fg=self.white,
                activebackground=self.secondary,
                activeforeground=self.white,
                font=("Arial", 11),
                anchor="w",
                relief="flat",
                padx=20,
                pady=13,
                cursor="hand2"
            )
            button.pack(fill="x", padx=5, pady=2)

        # Main content area
        self.content = tk.Frame(
            body,
            bg=self.background
        )
        self.content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    
    def get_dashboard_counts(self):
        """Retrieve current summary figures from SQLite."""

        with self.db.connect() as connection:

            medicines = connection.execute(
                "SELECT COUNT(*) FROM medicines"
            ).fetchone()[0]

            branches = connection.execute(
                "SELECT COUNT(*) FROM branches"
            ).fetchone()[0]

            prescriptions = connection.execute(
                "SELECT COUNT(*) FROM prescriptions"
            ).fetchone()[0]

            pending = connection.execute("""
                SELECT COUNT(*)
                FROM prescriptions
                WHERE status = 'pending'
            """).fetchone()[0]

            low_stock = connection.execute("""
                SELECT COUNT(*)
                FROM stock s
                JOIN medicines m
                    ON s.medicine_code = m.medicine_code
                WHERE s.quantity <= m.reorder_level
            """).fetchone()[0]

        return {
            "medicines": medicines,
            "branches": branches,
            "prescriptions": prescriptions,
            "pending": pending,
            "low_stock": low_stock
        }

    def create_summary_card(self, parent, title, value, colour):

        card = tk.Frame(
            parent,
            bg=self.white,
            highlightbackground="#D9E0E8",
            highlightthickness=1,
            padx=20,
            pady=20
        )

        tk.Label(
            card,
            text=title,
            bg=self.white,
            fg="#667085",
            font=("Arial", 11)
        ).pack(anchor="w")

        tk.Label(
            card,
            text=str(value),
            bg=self.white,
            fg=colour,
            font=("Arial", 25, "bold")
        ).pack(anchor="w", pady=(10, 0))

        return card

    def show_dashboard(self):
        self.clear_content()

        tk.Label(
            self.content,
            text="Dashboard",
            bg=self.background,
            fg=self.primary,
            font=("Arial", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            self.content,
            text="Overview of pharmacy operations",
            bg=self.background,
            fg="#667085",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(5, 25))

        try:
            values = self.get_dashboard_counts()

            labels = [
                "Registered Medicines",
                "Pharmacy Branches",
                "Prescriptions",
                "Pending Prescriptions",
                "Low Stock Items"
            ]

            colours = [
                "#2874A6",
                "#239B56",
                "#8E44AD",
                "#F39C12",
                "#D35400"
            ]

            value_keys = [
                "medicines",
                "branches",
                "prescriptions",
                "pending",
                "low_stock"
            ]

            cards_frame = tk.Frame(
                self.content,
                bg=self.background
            )
            cards_frame.pack(fill="x")

            for i, (label, value, colour) in enumerate(
                zip(labels, [values[key] for key in value_keys], colours)
            ):
                card = self.create_summary_card(
                    cards_frame, label, value, colour
                )
                card.grid(
                    row=0,
                    column=i,
                    padx=7,
                    sticky="nsew"
                )
                cards_frame.columnconfigure(i, weight=1)

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load dashboard information:\n{error}"
            )

        # Welcome section
        welcome = tk.Frame(
            self.content,
            bg=self.white,
            padx=25,
            pady=25
        )
        welcome.pack(fill="x", pady=30)

        tk.Label(
            welcome,
            text="Welcome to the Pharmacy System",
            bg=self.white,
            fg=self.primary,
            font=("Arial", 16, "bold")
        ).pack(anchor="w")

        tk.Label(
            welcome,
            text=(
                "Use the navigation menu to manage medicines, "
                "branch stock, prescriptions and dispensing."
            ),
            bg=self.white,
            fg="#667085",
            font=("Arial", 11),
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=12)

    def show_placeholder(self, title, description):
        self.clear_content()

        tk.Label(
            self.content,
            text=title,
            bg=self.background,
            fg=self.primary,
            font=("Arial", 22, "bold")
        ).pack(anchor="w", pady=(0, 15))

        tk.Label(
            self.content,
            text=description,
            bg=self.background,
            fg="#667085",
            font=("Arial", 12),
            wraplength=650,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            self.content,
            text="This section will be implemented in the next stages.",
            bg=self.background,
            fg=self.secondary,
            font=("Arial", 11, "italic")
        ).pack(anchor="w", pady=20)

    def show_medicines(self):
        self.clear_content()

        # Page heading
        tk.Label(
            self.content,
            text="Medicine Management",
            bg=self.background,
            fg=self.primary,
            font=("Arial", 22, "bold")
        ).pack(anchor="w")
    
        tk.Label(
            self.content,
            text="Register and view pharmacy medicines",
            bg=self.background,
            fg="#667085",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(5, 20))

        # Registration form
        form = tk.LabelFrame(
            self.content,
            text="Register New Medicine",
            bg=self.white,
            fg=self.primary,
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        form.pack(fill="x", pady=(0, 20))

        self.medicine_code = tk.StringVar()
        self.medicine_name = tk.StringVar()
        self.medicine_price = tk.StringVar()
        self.medicine_reorder = tk.StringVar()
        self.medicine_type = tk.StringVar(value="Ordinary")

        fields = [
            ("Medicine Code", self.medicine_code),
            ("Medicine Name", self.medicine_name),
            ("Unit Price", self.medicine_price),
            ("Reorder Level", self.medicine_reorder)
        ]

        for index, (label, variable) in enumerate(fields):
            row = index // 2
            column = (index % 2) * 2

            tk.Label(
                form,
                text=label,
                bg=self.white,
                fg=self.primary,
                font=("Arial", 10)
            ).grid(
                row=row,
                column=column,
                sticky="w",
                padx=8,
                pady=8
            )

            tk.Entry(
                form,
                textvariable=variable,
                font=("Arial", 10),
                width=25
            ).grid(
                row=row,
                column=column + 1,
                sticky="ew",
                padx=8,
                pady=8
            )

        # Medicine category
        tk.Label(
            form,
            text="Medicine Type",
            bg=self.white,
            fg=self.primary,
            font=("Arial", 10)
        ).grid(row=2, column=0, sticky="w", padx=8, pady=8)
    
        medicine_type_box = ttk.Combobox(
            form,
            textvariable=self.medicine_type,
            values=["Ordinary", "Controlled"],
            state="readonly",
            width=22
        )
        medicine_type_box.grid(
            row=2,
            column=1,
            sticky="w",
            padx=8,
            pady=8
        )

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # Save button
        tk.Button(
            form,
            text="Register Medicine",
            command=self.register_medicine,
            bg=self.secondary,
            fg=self.white,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=9,
            cursor="hand2"
        ).grid(
            row=3,
            column=0,
            columnspan=4,
            pady=15
        )

        # Registered medicines table
        tk.Label(
            self.content,
            text="Registered Medicines",
            bg=self.background,
            fg=self.primary,
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))
    
        table_frame = tk.Frame(
            self.content,
            bg=self.white
        )
        table_frame.pack(fill="both", expand=True)

        columns = (
            "code",
            "name",
            "price",
            "reorder",
            "type"
        )

        self.medicine_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "code": "Medicine Code",
            "name": "Medicine Name",
            "price": "Unit Price",
            "reorder": "Reorder Level",
            "type": "Medicine Type"
        }

        for column, heading in headings.items():
            self.medicine_table.heading(column, text=heading)
            self.medicine_table.column(column, width=120)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.medicine_table.yview
        )

        self.medicine_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.medicine_table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(side="right", fill="y")

        self.refresh_medicines()

    def register_medicine(self):
        """Validate and save a medicine using the existing service."""

        code = self.medicine_code.get().strip()
        name = self.medicine_name.get().strip()
        medicine_type = self.medicine_type.get()

        try:
            price = float(self.medicine_price.get())
            reorder_level = int(self.medicine_reorder.get())

            if not code or not name:
                raise ValueError("Medicine code and name are required.")

            if medicine_type == "Ordinary":
                medicine = OrdinaryMedicine(
                    code, name, price, reorder_level
                )
            else:
                medicine = ControlledMedicine(
                    code, name, price, reorder_level
                )

            self.pharmacy_service.register_medicine(medicine)

            messagebox.showinfo(
                "Success",
                "Medicine registered successfully."
            )

            self.medicine_code.set("")
            self.medicine_name.set("")
            self.medicine_price.set("")
            self.medicine_reorder.set("")
            self.medicine_type.set("Ordinary")

            self.refresh_medicines()

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))

        except Exception as error:
            messagebox.showerror(
                "Registration Error",
                f"Could not register medicine:\n{error}"
            )

    def refresh_medicines(self):
        """Load registered medicines from SQLite into the table."""

        for item in self.medicine_table.get_children():
            self.medicine_table.delete(item)

        try:
            with self.db.connect() as connection:
                records = connection.execute(
                    """
                    SELECT medicine_code, name, unit_price,
                        reorder_level, medicine_type
                    FROM medicines
                    ORDER BY medicine_code
                    """
                ).fetchall()

                for record in records:
                    self.medicine_table.insert(
                        "",
                        "end",
                        values=(
                            record["medicine_code"],
                            record["name"],
                            record["unit_price"],
                            record["reorder_level"],
                            record["medicine_type"]
                        )
                    )

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load medicines:\n{error}"
            )

    def show_stock(self):
        self.clear_content()

        tk.Label(
            self.content,
            text="Branches and Stock Management",
            bg=self.background,
            fg=self.primary,
            font=("Arial", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            self.content,
            text="Register branches and receive stock.",
            bg=self.background,
            fg="#667085",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(5, 15))

        forms = tk.Frame(self.content, bg=self.background)
        forms.pack(fill="x")
        forms.columnconfigure(0, weight=1)
        forms.columnconfigure(1, weight=1)

        branch_form = tk.LabelFrame(
            forms,
            text="Register Branch",
            bg=self.white,
            fg=self.primary,
            font=("Arial", 11, "bold"),
            padx=12,
            pady=12
        )
        branch_form.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.branch_code = tk.StringVar()
        self.branch_name = tk.StringVar()

        tk.Label(
            branch_form, text="Branch Code",
            bg=self.white, fg=self.primary
        ).grid(row=0, column=0, sticky="w", padx=6, pady=6)
        tk.Entry(
            branch_form, textvariable=self.branch_code, width=22
        ).grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        tk.Label(
            branch_form, text="Branch Name",
            bg=self.white, fg=self.primary
        ).grid(row=1, column=0, sticky="w", padx=6, pady=6)
        tk.Entry(
            branch_form, textvariable=self.branch_name, width=22
        ).grid(row=1, column=1, sticky="ew", padx=6, pady=6)

        tk.Button(
            branch_form,
            text="Register Branch",
            command=self.register_branch,
            bg=self.secondary,
            fg=self.white,
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2"
        ).grid(row=2, column=0, columnspan=2, pady=(8, 2))
        branch_form.columnconfigure(1, weight=1)

        stock_form = tk.LabelFrame(
            forms,
            text="Receive Stock",
            bg=self.white,
            fg=self.primary,
            font=("Arial", 11, "bold"),
            padx=12,
            pady=12
        )
        stock_form.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.receive_branch_var = tk.StringVar()
        self.receive_medicine_var = tk.StringVar()
        self.receive_quantity_var = tk.StringVar()

        tk.Label(
            stock_form, text="Branch",
            bg=self.white, fg=self.primary
        ).grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.receive_branch_box = ttk.Combobox(
            stock_form,
            textvariable=self.receive_branch_var,
            state="readonly",
            width=30
        )
        self.receive_branch_box.grid(
            row=0, column=1, sticky="ew", padx=6, pady=6
        )

        tk.Label(
            stock_form, text="Medicine",
            bg=self.white, fg=self.primary
        ).grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.receive_medicine_box = ttk.Combobox(
            stock_form,
            textvariable=self.receive_medicine_var,
            state="readonly",
            width=30
        )
        self.receive_medicine_box.grid(
            row=1, column=1, sticky="ew", padx=6, pady=6
        )

        tk.Label(
            stock_form, text="Quantity",
            bg=self.white, fg=self.primary
        ).grid(row=2, column=0, sticky="w", padx=6, pady=6)
        tk.Entry(
            stock_form,
            textvariable=self.receive_quantity_var,
            width=33
        ).grid(row=2, column=1, sticky="ew", padx=6, pady=6)

        tk.Button(
            stock_form,
            text="Receive Stock",
            command=self.receive_stock_gui,
            bg=self.secondary,
            fg=self.white,
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2"
        ).grid(row=3, column=0, columnspan=2, pady=(8, 2))
        stock_form.columnconfigure(1, weight=1)

        table_frame = tk.Frame(self.content, bg=self.background)
        table_frame.pack(fill="both", expand=True, pady=(15, 0))
        table_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(1, weight=2)

        branch_table_frame = tk.Frame(table_frame, bg=self.white)
        branch_table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(
            branch_table_frame,
            text="Registered Branches",
            bg=self.white,
            fg=self.primary,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=8, pady=8)

        self.branch_table = ttk.Treeview(
            branch_table_frame,
            columns=("code", "name"),
            show="headings",
            height=10
        )
        self.branch_table.heading("code", text="Branch Code")
        self.branch_table.heading("name", text="Branch Name")
        self.branch_table.column("code", width=100)
        self.branch_table.column("name", width=180)
        self.branch_table.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        stock_table_frame = tk.Frame(table_frame, bg=self.white)
        stock_table_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(
            stock_table_frame,
            text="Stock by Branch",
            bg=self.white,
            fg=self.primary,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=8, pady=8)

        filter_frame = tk.Frame(stock_table_frame, bg=self.white)
        filter_frame.pack(fill="x", padx=8)

        self.stock_filter_var = tk.StringVar(value="All branches")
        self.stock_filter_box = ttk.Combobox(
            filter_frame,
            textvariable=self.stock_filter_var,
            state="readonly",
            width=28
        )
        self.stock_filter_box.pack(side="left")
        self.stock_filter_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_stock()
        )

        tk.Button(
            filter_frame,
            text="Refresh",
            command=self.refresh_stock,
            bg=self.primary,
            fg=self.white,
            relief="flat",
            padx=10
        ).pack(side="left", padx=8)

        self.stock_table = ttk.Treeview(
            stock_table_frame,
            columns=("medicine", "name", "branch", "quantity", "reorder", "status"),
            show="headings",
            height=10
        )
        stock_headings = {
            "medicine": "Medicine Code",
            "name": "Medicine",
            "branch": "Branch",
            "quantity": "Quantity",
            "reorder": "Reorder",
            "status": "Status"
        }
        for column, heading in stock_headings.items():
            self.stock_table.heading(column, text=heading)
            self.stock_table.column(column, width=95)

        self.stock_table.tag_configure(
            "low", background="#FCE4D6", foreground="#9C0006"
        )
        self.stock_table.tag_configure(
            "normal", background="#E2F0D9", foreground="#375623"
        )

        stock_scroll = ttk.Scrollbar(
            stock_table_frame,
            orient="vertical",
            command=self.stock_table.yview
        )
        self.stock_table.configure(yscrollcommand=stock_scroll.set)
        self.stock_table.pack(
            side="left", fill="both", expand=True, padx=(8, 0), pady=(8, 8)
        )
        stock_scroll.pack(side="right", fill="y", pady=(8, 8), padx=(0, 8))

        self.load_stock_options()
        self.refresh_branches()
        self.refresh_stock()

    def register_branch(self):
        code = self.branch_code.get().strip()
        name = self.branch_name.get().strip()

        try:
            if not code or not name:
                raise ValueError("Branch code and name are required.")

            branch = Branch(code, name)
            self.pharmacy_service.register_branch(branch)

            messagebox.showinfo(
                "Success", "Branch registered successfully."
            )
            self.branch_code.set("")
            self.branch_name.set("")
            self.load_stock_options()
            self.refresh_branches()
            self.refresh_stock()

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))
        except Exception as error:
            messagebox.showerror(
                "Registration Error",
                f"Could not register branch:\n{error}"
            )

    def load_stock_options(self):
        try:
            with self.db.connect() as connection:
                branches = connection.execute(
                    """
                    SELECT branch_code, branch_name
                    FROM branches
                    ORDER BY branch_name
                    """
                ).fetchall()
                medicines = connection.execute(
                    """
                    SELECT medicine_code, name
                    FROM medicines
                    ORDER BY name
                    """
                ).fetchall()

            self.branch_lookup = {
                f'{record["branch_code"]} - {record["branch_name"]}':
                record["branch_code"]
                for record in branches
            }
            self.medicine_lookup = {
                f'{record["medicine_code"]} - {record["name"]}':
                record["medicine_code"]
                for record in medicines
            }

            branch_values = list(self.branch_lookup.keys())
            medicine_values = list(self.medicine_lookup.keys())
            self.receive_branch_box.configure(values=branch_values)
            self.receive_medicine_box.configure(values=medicine_values)
            self.stock_filter_box.configure(
                values=["All branches"] + branch_values
            )

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load branches and medicines:\n{error}"
            )

    def receive_stock_gui(self):
        branch_selection = self.receive_branch_var.get()
        medicine_selection = self.receive_medicine_var.get()
        quantity_text = self.receive_quantity_var.get().strip()

        if not branch_selection or not medicine_selection:
            messagebox.showwarning(
                "Missing Information",
                "Please select a branch and medicine."
            )
            return

        try:
            quantity = int(quantity_text)
            branch_code = self.branch_lookup[branch_selection]
            medicine_code = self.medicine_lookup[medicine_selection]

            self.pharmacy_service.receive_stock(
                medicine_code, branch_code, quantity
            )

            messagebox.showinfo(
                "Success",
                f"{quantity} units of {medicine_code} received at {branch_code}."
            )
            self.receive_quantity_var.set("")
            self.refresh_stock()

        except (ValueError, KeyError) as error:
            messagebox.showerror("Invalid Input", str(error))
        except Exception as error:
            messagebox.showerror(
                "Stock Error",
                f"Could not receive stock:\n{error}"
            )

    def refresh_branches(self):
        for item in self.branch_table.get_children():
            self.branch_table.delete(item)

        try:
            with self.db.connect() as connection:
                records = connection.execute(
                    """
                    SELECT branch_code, branch_name
                    FROM branches
                    ORDER BY branch_code
                    """
                ).fetchall()

            for record in records:
                self.branch_table.insert(
                    "",
                    "end",
                    values=(record["branch_code"], record["branch_name"])
                )
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load branches:\n{error}"
            )

    def refresh_stock(self):
        for item in self.stock_table.get_children():
            self.stock_table.delete(item)

        selected_branch = self.stock_filter_var.get()
        branch_code = None
        if selected_branch != "All branches":
            branch_code = getattr(self, "branch_lookup", {}).get(
                selected_branch
            )

        try:
            with self.db.connect() as connection:
                query = """
                    SELECT
                        m.medicine_code,
                        m.name,
                        b.branch_code,
                        s.quantity,
                        m.reorder_level
                    FROM stock s
                    JOIN medicines m
                        ON s.medicine_code = m.medicine_code
                    JOIN branches b
                        ON s.branch_code = b.branch_code
                """
                parameters = ()
                if branch_code:
                    query += " WHERE b.branch_code = ?"
                    parameters = (branch_code,)
                query += " ORDER BY b.branch_code, m.medicine_code"

                records = connection.execute(query, parameters).fetchall()

            for record in records:
                if record["quantity"] <= record["reorder_level"]:
                    status = "LOW STOCK"
                    tag = "low"
                else:
                    status = "Available"
                    tag = "normal"

                self.stock_table.insert(
                    "",
                    "end",
                    values=(
                        record["medicine_code"],
                        record["name"],
                        record["branch_code"],
                        record["quantity"],
                        record["reorder_level"],
                        status
                    ),
                    tags=(tag,)
                )
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load stock records:\n{error}"
            )

    def show_prescriptions(self):
        """Display the prescription creation form and saved prescriptions."""

        for widget in self.content.winfo_children():
            widget.destroy()

        self.prescription_draft_lines = []

        tk.Label(
            self.content,
            text="Prescription Management",
            font=("Arial", 20, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 15))

        # Main form
        form = tk.LabelFrame(
            self.content,
            text="Create New Prescription",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=12,
            pady=10
        )
        form.pack(fill="x", pady=5)

        # Prescription details
        tk.Label(form, text="Prescription ID:", bg="white").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.prescription_id_entry = tk.Entry(form, width=25)
        self.prescription_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Patient ID:", bg="white").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        self.patient_id_entry = tk.Entry(form, width=25)
        self.patient_id_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form, text="Prescriber Code:", bg="white").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.prescriber_entry = tk.Entry(form, width=25)
        self.prescriber_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Branch:", bg="white").grid(
            row=1, column=2, sticky="w", padx=5, pady=5
        )

        with self.db.connect() as connection:
            branches = connection.execute(
                "SELECT branch_code, branch_name FROM branches "
                "ORDER BY branch_name"
            ).fetchall()

            medicines = connection.execute(
                "SELECT medicine_code, name FROM medicines ORDER BY name"
            ).fetchall()

        self.prescription_branch_lookup = {
            f"{row['branch_code']} - {row['branch_name']}": row["branch_code"]
            for row in branches
        }

        self.prescription_medicine_lookup = {
            f"{row['medicine_code']} - {row['name']}": row["medicine_code"]
            for row in medicines
        }

        self.prescription_branch_combo = ttk.Combobox(
            form,
            width=23,
            values=list(self.prescription_branch_lookup.keys())
        )
        self.prescription_branch_combo.grid(
            row=1, column=3, padx=5, pady=5
        )

        # Medicine selection
        medicine_frame = tk.LabelFrame(
            self.content,
            text="Add Medicines to Prescription",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=12,
            pady=10
        )
        medicine_frame.pack(fill="x", pady=10)

        tk.Label(medicine_frame, text="Medicine:", bg="white").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        self.prescription_medicine_combo = ttk.Combobox(
            medicine_frame,
            width=35,
            state="readonly",
            values=list(self.prescription_medicine_lookup.keys())
        )
        self.prescription_medicine_combo.grid(
            row=0, column=1, padx=5, pady=5
        )

        tk.Label(medicine_frame, text="Quantity:", bg="white").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )

        self.prescription_quantity_entry = tk.Entry(
            medicine_frame, width=12
        )
        self.prescription_quantity_entry.grid(
            row=0, column=3, padx=5, pady=5
        )

        tk.Button(
            medicine_frame,
            text="Add Medicine",
            command=self.add_prescription_line,
            bg="#1976D2",
            fg="white",
            padx=10
        ).grid(row=0, column=4, padx=10, pady=5)

        # Draft prescription lines
        self.prescription_line_tree = ttk.Treeview(
            self.content,
            columns=("medicine_code", "medicine_name", "quantity"),
            show="headings",
            height=5
        )

        self.prescription_line_tree.heading(
            "medicine_code", text="Medicine Code"
        )
        self.prescription_line_tree.heading(
            "medicine_name", text="Medicine Name"
        )
        self.prescription_line_tree.heading(
            "quantity", text="Quantity"
        )

        self.prescription_line_tree.column(
            "medicine_code", width=150
        )
        self.prescription_line_tree.column(
            "medicine_name", width=250
        )
        self.prescription_line_tree.column(
            "quantity", width=100
        )

        self.prescription_line_tree.pack(fill="x", pady=5)

        tk.Button(
            self.content,
            text="Save Prescription",
            command=self.save_prescription_gui,
            bg="#2E7D32",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=7
        ).pack(anchor="e", pady=8)

        # Previously saved prescriptions
        tk.Label(
            self.content,
            text="Saved Prescriptions",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(12, 5))

        self.prescription_table = ttk.Treeview(
            self.content,
            columns=(
                "prescription_id",
                "patient_id",
                "branch_code",
                "prescriber_code",
                "status"
            ),
            show="headings",
            height=7
        )

        headings = {
            "prescription_id": "Prescription ID",
            "patient_id": "Patient ID",
            "branch_code": "Branch",
            "prescriber_code": "Prescriber",
            "status": "Status"
        }

        for column, heading in headings.items():
            self.prescription_table.heading(column, text=heading)
            self.prescription_table.column(column, width=130)

        self.prescription_table.pack(fill="both", expand=True)

        self.refresh_prescriptions()

    def add_prescription_line(self):
        """Add a medicine and quantity to the current prescription."""

        selected_medicine = self.prescription_medicine_combo.get()
        quantity_text = self.prescription_quantity_entry.get().strip()

        if not selected_medicine:
            messagebox.showerror(
                "Missing Medicine",
                "Please select a medicine."
            )
            return

        try:
            quantity = int(quantity_text)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Enter a whole number greater than zero."
            )
            return

        medicine_code = self.prescription_medicine_lookup[
            selected_medicine
        ]
        medicine_name = selected_medicine.split(" - ", 1)[1]

        # Combine duplicate medicine entries in the draft.
        existing_line = next(
            (
                line for line in self.prescription_draft_lines
                if line["medicine_code"] == medicine_code
            ),
            None
        )

        if existing_line:
            existing_line["quantity"] += quantity
        else:
            self.prescription_draft_lines.append({
                "medicine_code": medicine_code,
                "medicine_name": medicine_name,
                "quantity": quantity
            })

        # Refresh the draft table.
        for item in self.prescription_line_tree.get_children():
            self.prescription_line_tree.delete(item)

        for line in self.prescription_draft_lines:
            self.prescription_line_tree.insert(
                "",
                "end",
                values=(
                    line["medicine_code"],
                    line["medicine_name"],
                    line["quantity"]
                )
            )

        self.prescription_quantity_entry.delete(0, tk.END)
        self.prescription_medicine_combo.set("")

    def save_prescription_gui(self):
        """Validate and save the prescription in the database."""

        prescription_id = self.prescription_id_entry.get().strip()
        patient_id = self.patient_id_entry.get().strip()
        prescriber_code = self.prescriber_entry.get().strip()
        selected_branch = self.prescription_branch_combo.get()

        if not all([
            prescription_id,
            patient_id,
            prescriber_code,
            selected_branch
        ]):
            messagebox.showerror(
                "Missing Information",
                "Please complete all prescription details."
            )
            return

        if not self.prescription_draft_lines:
            messagebox.showerror(
                "No Medicines",
                "Add at least one medicine before saving."
            )
            return

        branch_code = self.prescription_branch_lookup.get(selected_branch)

        if branch_code is None:
            entered_branch = selected_branch.strip()
            with self.db.connect() as connection:
                branch = connection.execute(
                    """
                    SELECT branch_code
                    FROM branches
                    WHERE branch_code = ? OR branch_name = ?
                    """,
                    (entered_branch, entered_branch)
                ).fetchone()

            if branch is None:
                messagebox.showerror(
                    "Invalid Branch",
                    "Enter or select a registered branch."
                )
                return

            branch_code = branch["branch_code"]

        try:
            lines = [
                PrescriptionLine(
                    medicine_code=line["medicine_code"],
                    quantity=line["quantity"]
                )
                for line in self.prescription_draft_lines
            ]

            prescription = Prescription(
                prescription_id=prescription_id,
                patient_id=patient_id,
                branch_code=branch_code,
                prescriber_code=prescriber_code,
                lines=lines
            )

            self.pharmacy_service.create_prescription(prescription)

            messagebox.showinfo(
                "Success",
                "Prescription created successfully."
            )

            self.prescription_id_entry.delete(0, tk.END)
            self.patient_id_entry.delete(0, tk.END)
            self.prescriber_entry.delete(0, tk.END)
            self.prescription_branch_combo.set("")

            self.prescription_draft_lines.clear()

            for item in self.prescription_line_tree.get_children():
                self.prescription_line_tree.delete(item)

            self.refresh_prescriptions()

        except Exception as error:
            messagebox.showerror(
                "Prescription Error",
                str(error)
            )

    def refresh_prescriptions(self):
        """Load saved prescriptions into the table."""

        for item in self.prescription_table.get_children():
            self.prescription_table.delete(item)

        with self.db.connect() as connection:
            prescriptions = connection.execute("""
                SELECT
                    prescription_id,
                    patient_id,
                    branch_code,
                    prescriber_code,
                    status
                FROM prescriptions
                ORDER BY rowid DESC
            """).fetchall()

        for prescription in prescriptions:
            self.prescription_table.insert(
                "",
                "end",
                values=(
                    prescription["prescription_id"],
                    prescription["patient_id"],
                    prescription["branch_code"],
                    prescription["prescriber_code"],
                    prescription["status"]
                )
            )
        

    def show_dispensing(self):
        """Display prescriptions, their statuses, and dispensing details."""

        for widget in self.content.winfo_children():
            widget.destroy()

        tk.Label(
            self.content,
            text="Medicine Dispensing",
            font=("Arial", 20, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 15))

        tk.Label(
            self.content,
            text="Select a prescription to view its medicines and status.",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor="w", pady=5)

        # Prescription table
        pending_frame = tk.LabelFrame(
            self.content,
            text="Prescriptions",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        pending_frame.pack(fill="x", pady=5)

        self.pending_prescription_table = ttk.Treeview(
            pending_frame,
            columns=(
                "prescription_id",
                "patient_id",
                "branch_code",
                "prescriber_code",
                "status"
            ),
            show="headings",
            height=6
        )

        columns = {
            "prescription_id": "Prescription ID",
            "patient_id": "Patient ID",
            "branch_code": "Branch",
            "prescriber_code": "Prescriber",
            "status": "Status"
        }

        for column, heading in columns.items():
            self.pending_prescription_table.heading(
                column, text=heading
            )
            self.pending_prescription_table.column(
                column, width=130
            )

        self.pending_prescription_table.pack(
            fill="x", expand=True
        )

        self.pending_prescription_table.bind(
            "<<TreeviewSelect>>",
            self.show_selected_prescription
        )

        # Selected prescription details
        details_frame = tk.LabelFrame(
            self.content,
            text="Prescription Medicines",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        details_frame.pack(fill="both", expand=True, pady=10)

        self.selected_prescription_label = tk.Label(
            details_frame,
            text="No prescription selected.",
            font=("Arial", 10, "bold"),
            bg="white"
        )
        self.selected_prescription_label.pack(
            anchor="w", pady=5
        )

        self.dispensing_lines_table = ttk.Treeview(
            details_frame,
            columns=(
                "medicine_code",
                "medicine_name",
                "quantity"
            ),
            show="headings",
            height=6
        )

        self.dispensing_lines_table.heading(
            "medicine_code", text="Medicine Code"
        )
        self.dispensing_lines_table.heading(
            "medicine_name", text="Medicine Name"
        )
        self.dispensing_lines_table.heading(
            "quantity", text="Quantity Required"
        )

        self.dispensing_lines_table.column(
            "medicine_code", width=150
        )
        self.dispensing_lines_table.column(
            "medicine_name", width=250
        )
        self.dispensing_lines_table.column(
            "quantity", width=150
        )

        self.dispensing_lines_table.pack(
            fill="both", expand=True, pady=5
        )

        # Dispense button
        tk.Button(
            self.content,
            text="Dispense Selected Prescription",
            command=self.dispense_selected_prescription,
            bg="#2E7D32",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8
        ).pack(anchor="e", pady=5)

        self.refresh_pending_prescriptions()

    def refresh_pending_prescriptions(self):
        """Refresh all prescriptions and their current statuses."""

        for item in self.pending_prescription_table.get_children():
            self.pending_prescription_table.delete(item)

        for item in self.dispensing_lines_table.get_children():
            self.dispensing_lines_table.delete(item)

        self.selected_prescription_label.config(
            text="No prescription selected."
        )

        with self.db.connect() as connection:
            prescriptions = connection.execute("""
                SELECT
                    prescription_id,
                    patient_id,
                    branch_code,
                    prescriber_code,
                    status
                FROM prescriptions
                ORDER BY rowid DESC
            """).fetchall()

        for prescription in prescriptions:
            self.pending_prescription_table.insert(
                "",
                "end",
                values=(
                    prescription["prescription_id"],
                    prescription["patient_id"],
                    prescription["branch_code"],
                    prescription["prescriber_code"],
                    prescription["status"]
                )
            )

    def show_selected_prescription(self, event=None):
        """Display the medicines belonging to the selected prescription."""

        selected = self.pending_prescription_table.selection()

        if not selected:
            return

        values = self.pending_prescription_table.item(
            selected[0], "values"
        )

        prescription_id = values[0]

        self.selected_prescription_label.config(
            text=f"Selected Prescription: {prescription_id}"
        )

        for item in self.dispensing_lines_table.get_children():
            self.dispensing_lines_table.delete(item)

        with self.db.connect() as connection:
            lines = connection.execute("""
                SELECT
                    pl.medicine_code,
                    m.name AS medicine_name,
                    SUM(pl.quantity) AS quantity
                FROM prescription_lines pl
                JOIN medicines m
                    ON pl.medicine_code = m.medicine_code
                WHERE pl.prescription_id = ?
                GROUP BY pl.medicine_code, m.name
                ORDER BY m.name
            """, (prescription_id,)).fetchall()

        for line in lines:
            self.dispensing_lines_table.insert(
                "",
                "end",
                values=(
                    line["medicine_code"],
                    line["medicine_name"],
                    line["quantity"]
                )
            )

    def dispense_selected_prescription(self):
        """Send the selected prescription to the dispensing service."""

        selected = self.pending_prescription_table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a pending prescription first."
            )
            return

        values = self.pending_prescription_table.item(
            selected[0], "values"
        )

        prescription_id = values[0]

        if values[4] != "pending":
            messagebox.showwarning(
                "Prescription Not Pending",
                "Only pending prescriptions can be dispensed."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Dispensing",
            f"Are you sure you want to dispense prescription "
            f"{prescription_id}?"
        )

        if not confirm:
            return

        try:
            self.dispensing_service.dispense(prescription_id)

            messagebox.showinfo(
                "Dispensing Successful",
                f"Prescription {prescription_id} has been "
                "successfully dispensed."
            )

            self.refresh_pending_prescriptions()

        except Exception as error:
            messagebox.showerror(
                "Dispensing Failed",
                str(error)
            )

            self.refresh_pending_prescriptions()

    
    def show_low_stock(self):
        """Display medicines whose stock is at or below reorder level."""

        for widget in self.content.winfo_children():
            widget.destroy()

        tk.Label(
            self.content,
            text="Low Stock Reports",
            font=("Arial", 20, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            self.content,
            text="Medicines requiring restocking are highlighted below.",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor="w", pady=5)

        # Branch filter
        filter_frame = tk.Frame(self.content, bg="white")
        filter_frame.pack(fill="x", pady=10)

        tk.Label(
            filter_frame,
            text="Filter by Branch:",
            bg="white",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=5)

        with self.db.connect() as connection:
            branches = connection.execute("""
                SELECT branch_code, branch_name
                FROM branches
                ORDER BY branch_name
            """).fetchall()

        self.report_branch_lookup = {
            f"{row['branch_code']} - {row['branch_name']}": row['branch_code']
            for row in branches
        }

        self.report_branch_combo = ttk.Combobox(
            filter_frame,
            state="readonly",
            width=30,
            values=["All Branches"] +
                   list(self.report_branch_lookup.keys())
        )
        self.report_branch_combo.pack(side="left", padx=5)
        self.report_branch_combo.set("All Branches")

        tk.Button(
            filter_frame,
            text="Apply Filter",
            command=self.refresh_low_stock_report,
            bg="#1976D2",
            fg="white"
        ).pack(side="left", padx=5)

        tk.Button(
            filter_frame,
            text="Refresh",
            command=self.refresh_low_stock_report,
            bg="#2E7D32",
            fg="white"
        ).pack(side="left", padx=5)

        # Report summary
        self.low_stock_summary = tk.Label(
            self.content,
            text="",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        self.low_stock_summary.pack(anchor="w", pady=10)

        # Report table
        self.low_stock_table = ttk.Treeview(
            self.content,
            columns=(
                "medicine_code",
                "medicine_name",
                "branch",
                "quantity",
                "reorder_level",
                "status"
            ),
            show="headings",
            height=15
        )

        headings = {
            "medicine_code": "Medicine Code",
            "medicine_name": "Medicine Name",
            "branch": "Branch",
            "quantity": "Current Quantity",
            "reorder_level": "Reorder Level",
            "status": "Stock Status"
        }

        for column, heading in headings.items():
            self.low_stock_table.heading(column, text=heading)
            self.low_stock_table.column(column, width=145)

        self.low_stock_table.tag_configure(
            "low",
            background="#FFCDD2",
            foreground="#B71C1C"
        )

        self.low_stock_table.tag_configure(
            "normal",
            background="#E8F5E9",
            foreground="#1B5E20"
        )

        self.low_stock_table.pack(
            fill="both",
            expand=True,
            pady=10
        )

        self.refresh_low_stock_report()

    def refresh_low_stock_report(self):
        """Refresh the low-stock report using current database values."""

        for item in self.low_stock_table.get_children():
            self.low_stock_table.delete(item)

        selected_branch = self.report_branch_combo.get()

        query = """
            SELECT
                m.medicine_code,
                m.name AS medicine_name,
                b.branch_name,
                s.quantity,
                m.reorder_level
            FROM stock s
            JOIN medicines m
                ON s.medicine_code = m.medicine_code
            JOIN branches b
                ON s.branch_code = b.branch_code
        """

        parameters = []

        if selected_branch and selected_branch != "All Branches":
            branch_code = self.report_branch_lookup[selected_branch]
            query += " WHERE s.branch_code = ?"
            parameters.append(branch_code)

        query += """
            ORDER BY
                CASE WHEN s.quantity <= m.reorder_level
                     THEN 0 ELSE 1 END,
                m.name
        """

        with self.db.connect() as connection:
            records = connection.execute(
                query, parameters
            ).fetchall()

        low_count = 0

        for record in records:
            is_low = record["quantity"] <= record["reorder_level"]

            if is_low:
                low_count += 1
                status = "LOW STOCK"
                tag = "low"
            else:
                status = "NORMAL"
                tag = "normal"

            self.low_stock_table.insert(
                "",
                "end",
                values=(
                    record["medicine_code"],
                    record["medicine_name"],
                    record["branch_name"],
                    record["quantity"],
                    record["reorder_level"],
                    status
                ),
                tags=(tag,)
            )

        self.low_stock_summary.config(
            text=(
                f"Total stock records: {len(records)}   |   "
                f"Medicines requiring restocking: {low_count}"
            )
        )

    def show_reports(self):
        """Compatibility entry point for the low-stock report menu."""
        self.show_low_stock()

    def run(self):
        self.root.mainloop()
