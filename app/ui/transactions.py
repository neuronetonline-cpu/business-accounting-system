
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.accounting.engine import post_simple_transaction
from app.database import get_connection

TRANSACTION_TYPES = {
    "Cash Sale": ("1000", "4000", "Cash sale"),
    "Bank Sale": ("1010", "4000", "Bank sale"),
    "Credit Sale": ("1100", "4000", "Credit sale"),
    "Customer Payment": ("1010", "1100", "Customer payment"),
    "Cash Customer Payment": ("1000", "1100", "Customer cash payment"),
    "Cash Purchase": ("5000", "1000", "Cash purchase / COGS"),
    "Bank Purchase": ("5000", "1010", "Bank purchase / COGS"),
    "Supplier Payment": ("2000", "1010", "Supplier payment"),
    "Cash Supplier Payment": ("2000", "1000", "Supplier cash payment"),
    "Rent Payment": ("5100", "1010", "Rent expense"),
    "Salary Payment": ("5200", "1010", "Salary expense"),
    "Utilities Payment": ("5300", "1010", "Utilities expense"),
    "Advertising Payment": ("5400", "1010", "Advertising expense"),
    "Delivery Payment": ("5500", "1010", "Delivery expense"),
    "Other Expense": ("5600", "1010", "Other expense"),
    "Other Income - Bank": ("1010", "4100", "Other income"),
    "Other Income - Cash": ("1000", "4100", "Other income"),
    "Owner Investment - Bank": ("1010", "3000", "Owner investment"),
    "Owner Investment - Cash": ("1000", "3000", "Owner investment"),
    "Owner Drawing - Bank": ("3100", "1010", "Owner drawing"),
    "Owner Drawing - Cash": ("3100", "1000", "Owner drawing"),
}

class TransactionsFrame(tk.Frame):
    def __init__(self, master, on_saved=None):
        super().__init__(master, bg="#eef2f7")
        self.on_saved = on_saved
        self.build()

    def build(self):
        tk.Label(self, text="Daily Transactions", bg="#eef2f7", fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w", pady=(0,6))
        tk.Label(self, text="Enter the business event. The accounting entry is created automatically.",
                 bg="#eef2f7", fg="#647586", font=("Segoe UI",10)).pack(anchor="w", pady=(0,16))

        box = tk.Frame(self, bg="white", padx=26, pady=24)
        box.pack(fill="x")

        self.fields = {}
        labels = [
            ("Date", "date"),
            ("Transaction Type", "type"),
            ("Reference / Invoice", "reference"),
            ("Description", "description"),
            ("Amount", "amount"),
        ]

        for row, (label, key) in enumerate(labels):
            tk.Label(box, text=label, bg="white", fg="#26384a",
                     font=("Segoe UI",10,"bold")).grid(
                         row=row, column=0, sticky="w", pady=9)

            if key == "type":
                widget = ttk.Combobox(
                    box, values=list(TRANSACTION_TYPES.keys()),
                    state="readonly", width=46
                )
                widget.current(0)
            else:
                widget = ttk.Entry(box, width=50)
                if key == "date":
                    widget.insert(0, date.today().isoformat())

            widget.grid(row=row, column=1, sticky="w", padx=20, pady=9)
            self.fields[key] = widget

        preview = tk.LabelFrame(
            box, text="Automatic Accounting Entry",
            bg="white", fg="#102f4f",
            font=("Segoe UI",10,"bold"), padx=15, pady=12
        )
        preview.grid(row=0, column=3, rowspan=5, padx=40, sticky="nsew")

        self.preview = tk.Label(
            preview, text="", bg="white", justify="left",
            font=("Consolas",11), width=35, anchor="nw"
        )
        self.preview.pack(fill="both", expand=True)

        self.fields["type"].bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        self.fields["amount"].bind("<KeyRelease>", lambda e: self.update_preview())
        self.update_preview()

        ttk.Button(
            box, text="SAVE TRANSACTION",
            command=self.save
        ).grid(row=6, column=1, sticky="w", pady=20)

        ttk.Button(
            box, text="CLEAR",
            command=self.clear
        ).grid(row=6, column=1, sticky="w", padx=170, pady=20)

    def account_name(self, code):
        con = get_connection()
        row = con.execute("SELECT name FROM accounts WHERE code=?", (code,)).fetchone()
        con.close()
        return row["name"] if row else code

    def update_preview(self):
        typ = self.fields["type"].get()
        debit, credit, desc = TRANSACTION_TYPES[typ]
        amount = self.fields["amount"].get().strip()
        try:
            a = float(amount.replace(",", "")) if amount else 0
        except ValueError:
            a = 0

        self.preview.config(
            text=(
                f"DEBIT\n"
                f"  {debit}  {self.account_name(debit)}\n"
                f"  Rs. {a:,.2f}\n\n"
                f"CREDIT\n"
                f"  {credit}  {self.account_name(credit)}\n"
                f"  Rs. {a:,.2f}\n\n"
                f"{desc}"
            )
        )

    def save(self):
        try:
            dt = self.fields["date"].get().strip()
            typ = self.fields["type"].get()
            ref = self.fields["reference"].get().strip()
            desc = self.fields["description"].get().strip()
            amount = float(self.fields["amount"].get().replace(",", ""))

            if not dt:
                raise ValueError("Date is required.")
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            debit, credit, default_desc = TRANSACTION_TYPES[typ]
            final_desc = desc or default_desc

            post_simple_transaction(
                dt, ref, final_desc, debit, credit, amount, "TRANSACTION"
            )

            messagebox.showinfo(
                "Transaction Saved",
                "Transaction saved successfully.\n\n"
                "Journal, General Ledger, Trial Balance and reports are updated."
            )
            self.clear()
            if self.on_saved:
                self.on_saved()

        except Exception as exc:
            messagebox.showerror("Transaction Error", str(exc))

    def clear(self):
        self.fields["date"].delete(0, "end")
        self.fields["date"].insert(0, date.today().isoformat())
        self.fields["reference"].delete(0, "end")
        self.fields["description"].delete(0, "end")
        self.fields["amount"].delete(0, "end")
        self.fields["type"].current(0)
        self.update_preview()
