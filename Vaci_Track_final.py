import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from pathlib import Path


# =========================================================
# CITY VACCINATION MANAGEMENT SYSTEM - VACCITRACK
# DATABASE
# =========================================================

DB_PATH = Path(__file__).with_name("Vaci_Track.db")


def connect_database():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = connect_database()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS centres (
                centre_id INTEGER PRIMARY KEY AUTOINCREMENT,
                centre_name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                contact_email TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vaccination_drives (
                drive_id INTEGER PRIMARY KEY AUTOINCREMENT,
                centre_id INTEGER NOT NULL,
                vaccine_name TEXT NOT NULL,
                drive_date TEXT NOT NULL,
                FOREIGN KEY (centre_id)
                    REFERENCES centres(centre_id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dose_records (
                dose_id INTEGER PRIMARY KEY AUTOINCREMENT,
                drive_id INTEGER NOT NULL,
                dose_type TEXT NOT NULL,
                dose_quantity INTEGER NOT NULL CHECK (dose_quantity >= 0),
                FOREIGN KEY (drive_id)
                    REFERENCES vaccination_drives(drive_id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("Database and tables created successfully!")
    finally:
        conn.close()


def insert_sample_data():
    """Insert sample rows only when all three tables are empty."""
    conn = connect_database()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM centres")
        centre_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM vaccination_drives")
        drive_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM dose_records")
        dose_count = cursor.fetchone()[0]

        if centre_count == 0 and drive_count == 0 and dose_count == 0:
            with conn:
                centres_data = [
                    ("Ramaiah Health Centre", "ramaiah@health.com"),
                    ("Bangalore City Clinic", "bangalore@health.com"),
                    ("Green Valley Medical Centre", "greenvalley@health.com"),
                ]
                cursor.executemany("""
                    INSERT INTO centres (centre_name, contact_email)
                    VALUES (?, ?)
                """, centres_data)

                drives_data = [
                    (1, "Covishield", "2026-11-09"),
                    (1, "Pfizer", "2026-11-10"),
                    (2, "Covaxin", "2026-11-11"),
                    (3, "Covishield", "2026-11-12"),
                ]
                cursor.executemany("""
                    INSERT INTO vaccination_drives
                        (centre_id, vaccine_name, drive_date)
                    VALUES (?, ?, ?)
                """, drives_data)

                doses_data = [
                    (1, "First Dose", 100),
                    (1, "Second Dose", 75),
                    (2, "Booster", 50),
                    (3, "First Dose", 120),
                    (3, "Second Dose", 90),
                    (4, "Booster", 60),
                ]
                cursor.executemany("""
                    INSERT INTO dose_records
                        (drive_id, dose_type, dose_quantity)
                    VALUES (?, ?, ?)
                """, doses_data)

            print("Sample data inserted successfully!")
        else:
            print("Database already contains data. Sample data insertion skipped.")
    except sqlite3.Error as error:
        print("Database error while inserting sample data:", error)
    finally:
        conn.close()


def add_vaccination_record(centre_name, centre_email,
                           vaccine_name, dose_type, quantity):
    fields = [centre_name, centre_email, vaccine_name, dose_type]
    if not all(value.strip() for value in fields):
        return False, "Please complete all fields."

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return False, "Dose quantity must be a whole number."

    if quantity < 0:
        return False, "Dose quantity cannot be negative."

    conn = connect_database()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT centre_id
                FROM centres
                WHERE centre_name = ?
            """, (centre_name.strip(),))
            result = cursor.fetchone()

            if result:
                centre_id = result[0]
            else:
                cursor.execute("""
                    INSERT INTO centres (centre_name, contact_email)
                    VALUES (?, ?)
                """, (centre_name.strip(), centre_email.strip()))
                centre_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO vaccination_drives
                    (centre_id, vaccine_name, drive_date)
                VALUES (?, ?, ?)
            """, (centre_id, vaccine_name.strip(), date.today().isoformat()))
            drive_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO dose_records
                    (drive_id, dose_type, dose_quantity)
                VALUES (?, ?, ?)
            """, (drive_id, dose_type.strip(), quantity))

        return True, "Vaccination record added successfully!"
    except sqlite3.IntegrityError as error:
        return False, f"Database constraint error: {error}"
    except sqlite3.Error as error:
        return False, f"Database error: {error}"
    finally:
        conn.close()


# =========================================================
# TKINTER APPLICATION
# =========================================================

class VaccinationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VacciTrack - City Vaccination Management System")
        self.root.geometry("1250x780")
        self.root.minsize(1000, 650)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Title.TLabel",
            font=("Arial", 22, "bold"),
            foreground="white",
            background="#172B4D",
        )
        self.style.configure(
            "Subtitle.TLabel",
            font=("Arial", 10),
            foreground="#D6E3F5",
            background="#172B4D",
        )
        self.style.configure("TLabelframe.Label", font=("Arial", 11, "bold"))
        self.style.configure("TButton", font=("Arial", 10), padding=6)
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        self.create_header()
        self.create_main_layout()
        self.refresh_all_views()

    # ---------------- HEADER ----------------

    def create_header(self):
        header = tk.Frame(self.root, bg="#172B4D", height=85)
        header.pack(fill="x")
        header.pack_propagate(False)

        ttk.Label(
            header, text="VacciTrack", style="Title.TLabel"
        ).pack(anchor="w", padx=25, pady=(12, 0))

        ttk.Label(
            header,
            text="CITY VACCINATION MANAGEMENT SYSTEM",
            style="Subtitle.TLabel",
        ).pack(anchor="w", padx=27)

    # ---------------- MAIN LAYOUT ----------------

    def create_main_layout(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        self.left_frame = ttk.Frame(main_frame, width=300)
        self.left_frame.pack(side="left", fill="y", padx=(0, 15))
        self.left_frame.pack_propagate(False)

        self.insert_frame = ttk.LabelFrame(
            self.left_frame, text="Add Vaccination Record", padding=12
        )
        self.insert_frame.pack(fill="x", pady=(0, 12))
        self.create_insert_panel()

        self.delete_frame = ttk.LabelFrame(
            self.left_frame, text="Delete Records", padding=12
        )
        self.delete_frame.pack(fill="x")
        self.create_delete_panel()

        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side="left", fill="both", expand=True)
        self.create_database_tabs()

    # ---------------- INSERT PANEL ----------------

    def create_insert_panel(self):
        ttk.Label(self.insert_frame, text="Centre Name").pack(anchor="w", pady=(4, 2))
        self.centre_entry = ttk.Entry(self.insert_frame)
        self.centre_entry.pack(fill="x", pady=(0, 7))

        ttk.Label(self.insert_frame, text="Centre Email").pack(anchor="w", pady=(2, 2))
        self.email_entry = ttk.Entry(self.insert_frame)
        self.email_entry.pack(fill="x", pady=(0, 7))

        ttk.Label(self.insert_frame, text="Vaccine Name").pack(anchor="w", pady=(2, 2))
        self.vaccine_entry = ttk.Entry(self.insert_frame)
        self.vaccine_entry.pack(fill="x", pady=(0, 7))

        ttk.Label(self.insert_frame, text="Dose Type").pack(anchor="w", pady=(2, 2))
        self.dose_combo = ttk.Combobox(
            self.insert_frame,
            values=["First Dose", "Second Dose", "Booster"],
            state="readonly",
        )
        self.dose_combo.pack(fill="x", pady=(0, 7))

        ttk.Label(self.insert_frame, text="Dose Quantity").pack(anchor="w", pady=(2, 2))
        self.quantity_entry = ttk.Entry(self.insert_frame)
        self.quantity_entry.pack(fill="x", pady=(0, 10))

        ttk.Button(
            self.insert_frame,
            text="Add Record",
            command=self.add_record_from_gui,
        ).pack(fill="x", pady=4)

    def add_record_from_gui(self):
        success, message = add_vaccination_record(
            self.centre_entry.get(),
            self.email_entry.get(),
            self.vaccine_entry.get(),
            self.dose_combo.get(),
            self.quantity_entry.get(),
        )

        if success:
            messagebox.showinfo("Success", message)
            self.clear_insert_fields()
            self.refresh_all_views()
        else:
            messagebox.showerror("Cannot Add Record", message)

    def clear_insert_fields(self):
        self.centre_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.vaccine_entry.delete(0, tk.END)
        self.dose_combo.set("")
        self.quantity_entry.delete(0, tk.END)

    # ---------------- DELETE PANEL ----------------

    def create_delete_panel(self):
        ttk.Label(self.delete_frame, text="Select Centre:").pack(anchor="w", pady=(2, 2))
        self.delete_centre_combo = ttk.Combobox(
            self.delete_frame, state="readonly", width=30
        )
        self.delete_centre_combo.pack(fill="x", pady=(0, 3))
        ttk.Button(
            self.delete_frame,
            text="Delete Centre",
            command=self.delete_centre_from_gui,
        ).pack(fill="x", pady=(0, 9))

        ttk.Label(
            self.delete_frame, text="Select Vaccination Drive:"
        ).pack(anchor="w", pady=(2, 2))
        self.delete_drive_combo = ttk.Combobox(
            self.delete_frame, state="readonly", width=30
        )
        self.delete_drive_combo.pack(fill="x", pady=(0, 3))
        ttk.Button(
            self.delete_frame,
            text="Delete Vaccination Drive",
            command=self.delete_drive_from_gui,
        ).pack(fill="x", pady=(0, 9))

        ttk.Label(self.delete_frame, text="Select Dose Record:").pack(
            anchor="w", pady=(2, 2)
        )
        self.delete_dose_combo = ttk.Combobox(
            self.delete_frame, state="readonly", width=30
        )
        self.delete_dose_combo.pack(fill="x", pady=(0, 3))
        ttk.Button(
            self.delete_frame,
            text="Delete Dose Record",
            command=self.delete_dose_from_gui,
        ).pack(fill="x", pady=(0, 3))

    def refresh_delete_dropdowns(self):
        conn = connect_database()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT centre_id, centre_name
                FROM centres
                ORDER BY centre_id
            """)
            centres = cursor.fetchall()
            self.delete_centre_combo["values"] = [
                f"{row[0]} | {row[1]}" for row in centres
            ]

            cursor.execute("""
                SELECT drive_id, vaccine_name, drive_date
                FROM vaccination_drives
                ORDER BY drive_id
            """)
            drives = cursor.fetchall()
            self.delete_drive_combo["values"] = [
                f"{row[0]} | {row[1]} | {row[2]}" for row in drives
            ]

            cursor.execute("""
                SELECT dose_id, dose_type, dose_quantity
                FROM dose_records
                ORDER BY dose_id
            """)
            doses = cursor.fetchall()
            self.delete_dose_combo["values"] = [
                f"{row[0]} | {row[1]} | Quantity: {row[2]}" for row in doses
            ]
        finally:
            conn.close()

        self.delete_centre_combo.set("")
        self.delete_drive_combo.set("")
        self.delete_dose_combo.set("")

    def perform_delete(self, table, id_column, selected_value, description,
                       warning_text):
        if not selected_value:
            messagebox.showwarning("Selection Required", f"Please select a {description}.")
            return

        record_id = int(selected_value.split("|", 1)[0].strip())
        if not messagebox.askyesno("Confirm Deletion", warning_text):
            return

        conn = connect_database()
        try:
            cursor = conn.cursor()
            # Table and column names are fixed internally, never user-entered.
            cursor.execute(
                f"DELETE FROM {table} WHERE {id_column} = ?",
                (record_id,),
            )
            conn.commit()
            if cursor.rowcount == 0:
                messagebox.showwarning("Not Found", f"The selected {description} no longer exists.")
                return
        except sqlite3.Error as error:
            conn.rollback()
            messagebox.showerror("Database Error", str(error))
            return
        finally:
            conn.close()

        messagebox.showinfo("Deleted", f"{description.capitalize()} deleted successfully.")
        self.refresh_all_views()

    def delete_centre_from_gui(self):
        self.perform_delete(
            "centres", "centre_id", self.delete_centre_combo.get(), "centre",
            "Deleting this centre will also delete its vaccination drives "
            "and all associated dose records.\n\nContinue?"
        )

    def delete_drive_from_gui(self):
        self.perform_delete(
            "vaccination_drives", "drive_id", self.delete_drive_combo.get(),
            "vaccination drive",
            "Deleting this vaccination drive will also delete its dose records.\n\nContinue?"
        )

    def delete_dose_from_gui(self):
        self.perform_delete(
            "dose_records", "dose_id", self.delete_dose_combo.get(), "dose record",
            "Are you sure you want to delete this individual dose record?"
        )

    # ---------------- DATABASE TABS ----------------

    def create_database_tabs(self):
        tabs_frame = ttk.LabelFrame(
            self.right_frame, text="Database Management", padding=10
        )
        tabs_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(tabs_frame)
        self.notebook.pack(fill="both", expand=True)

        self.treeviews = {}

        tab_definitions = [
            ("combined", "Combined View", [
                ("drive_id", "Drive ID", 75),
                ("centre_name", "Centre Name", 170),
                ("vaccine_name", "Vaccine", 120),
                ("drive_date", "Drive Date", 105),
                ("dose_type", "Dose Type", 110),
                ("dose_quantity", "Quantity", 85),
            ]),
            ("centres", "Centres", [
                ("centre_id", "Centre ID", 80),
                ("centre_name", "Centre Name", 200),
                ("contact_email", "Contact Email", 220),
            ]),
            ("drives", "Vaccination Drives", [
                ("drive_id", "Drive ID", 80),
                ("centre_id", "Centre ID", 90),
                ("vaccine_name", "Vaccine", 150),
                ("drive_date", "Drive Date", 120),
            ]),
            ("doses", "Dose Records", [
                ("dose_id", "Dose ID", 80),
                ("drive_id", "Drive ID", 90),
                ("dose_type", "Dose Type", 140),
                ("dose_quantity", "Quantity", 100),
            ]),
        ]

        for key, title, columns in tab_definitions:
            tab = ttk.Frame(self.notebook, padding=8)
            self.notebook.add(tab, text=title)

            column_ids = [column[0] for column in columns]
            tree = ttk.Treeview(
                tab, columns=column_ids, show="headings", height=18
            )

            for column_id, heading, width in columns:
                tree.heading(column_id, text=heading)
                tree.column(column_id, width=width, minwidth=60, anchor="center")

            vertical_scroll = ttk.Scrollbar(
                tab, orient="vertical", command=tree.yview
            )
            horizontal_scroll = ttk.Scrollbar(
                tab, orient="horizontal", command=tree.xview
            )
            tree.configure(
                yscrollcommand=vertical_scroll.set,
                xscrollcommand=horizontal_scroll.set,
            )

            tree.grid(row=0, column=0, sticky="nsew")
            vertical_scroll.grid(row=0, column=1, sticky="ns")
            horizontal_scroll.grid(row=1, column=0, sticky="ew")
            tab.rowconfigure(0, weight=1)
            tab.columnconfigure(0, weight=1)

            self.treeviews[key] = tree

        ttk.Button(
            tabs_frame, text="Refresh All Views", command=self.refresh_all_views
        ).pack(anchor="e", pady=(8, 0))

    def fill_treeview(self, tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)

    def refresh_all_views(self):
        conn = connect_database()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    vaccination_drives.drive_id,
                    centres.centre_name,
                    vaccination_drives.vaccine_name,
                    vaccination_drives.drive_date,
                    dose_records.dose_type,
                    dose_records.dose_quantity
                FROM vaccination_drives
                INNER JOIN centres
                    ON vaccination_drives.centre_id = centres.centre_id
                INNER JOIN dose_records
                    ON vaccination_drives.drive_id = dose_records.drive_id
                ORDER BY vaccination_drives.drive_id, dose_records.dose_id
            """)
            combined_rows = cursor.fetchall()

            cursor.execute("""
                SELECT centre_id, centre_name, contact_email
                FROM centres ORDER BY centre_id
            """)
            centre_rows = cursor.fetchall()

            cursor.execute("""
                SELECT drive_id, centre_id, vaccine_name, drive_date
                FROM vaccination_drives ORDER BY drive_id
            """)
            drive_rows = cursor.fetchall()

            cursor.execute("""
                SELECT dose_id, drive_id, dose_type, dose_quantity
                FROM dose_records ORDER BY dose_id
            """)
            dose_rows = cursor.fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))
            return
        finally:
            conn.close()

        self.fill_treeview(self.treeviews["combined"], combined_rows)
        self.fill_treeview(self.treeviews["centres"], centre_rows)
        self.fill_treeview(self.treeviews["drives"], drive_rows)
        self.fill_treeview(self.treeviews["doses"], dose_rows)
        self.refresh_delete_dropdowns()


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":
    create_tables()
    insert_sample_data()

    root = tk.Tk()
    app = VaccinationApp(root)
    root.mainloop()
