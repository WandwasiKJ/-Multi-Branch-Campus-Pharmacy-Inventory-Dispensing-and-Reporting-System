from models.medicine import OrdinaryMedicine, ControlledMedicine
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
        self.show_placeholder(
            "Branches and Stock Management",
            "Manage pharmacy branches and receive stock."
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
