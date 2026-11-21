from models.medicine import OrdinaryMedicine, ControlledMedicine
from models.branch import Branch
from services.pharmacy_service import PharmacyService
import tkinter as tk
from tkinter import ttk, messagebox


class PharmacyApp:
    def __init__(self, db):
        self.db = db
        
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
        """Retrieve summary figures from the database."""

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

            low_stock = connection.execute(
                """
                SELECT COUNT(*)
                FROM stock s
                JOIN medicines m
                    ON s.medicine_code = m.medicine_code
                WHERE s.quantity <= m.reorder_level
                """
            ).fetchone()[0]

        return medicines, branches, prescriptions, low_stock

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
                "Low Stock Items"
            ]

            colours = [
                "#2874A6",
                "#239B56",
                "#8E44AD",
                "#D35400"
            ]

            cards_frame = tk.Frame(
                self.content,
                bg=self.background
            )
            cards_frame.pack(fill="x")

            for i, (label, value, colour) in enumerate(
                zip(labels, values, colours)
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
        self.show_placeholder(
            "Prescription Management",
            "Create prescriptions containing one or more medicines."
        )

    def show_dispensing(self):
        self.show_placeholder(
            "Prescription Dispensing",
            "Review prescriptions and dispense medicines."
        )

    def show_reports(self):
        self.show_placeholder(
            "Low Stock Reports",
            "View medicines that have reached or fallen below reorder levels."
        )

    def run(self):
        self.root.mainloop()
