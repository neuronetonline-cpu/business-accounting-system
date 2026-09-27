
import tkinter as tk
from tkinter import ttk, messagebox
from app.database import get_connection
from app.accounting.engine import create_opening_balance

class OpeningBalanceFrame(tk.Frame):
    def __init__(self, master, on_saved=None):
        super().__init__(master, bg="#eef2f7")
        self.on_saved = on_saved
        self.entries = {}
        self.build()

    def build(self):
        tk.Label(self, text="Opening Balance",
                 bg="#eef2f7", fg="#102f4f",
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0,6))
        tk.Label(self,
                 text="Enter the balances at the beginning of the accounting period.",
                 bg="#eef2f7", fg="#647586",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0,16))

        box = tk.Frame(self, bg="white", padx=24, pady=22)
        box.pack(fill="both", expand=True)

        top = tk.Frame(box, bg="white")
        top.pack(fill="x", pady=(0,18))

        tk.Label(top, text="Opening Date", bg="white",
                 font=("Segoe UI",10,"bold")).pack(side="left")
        self.date_entry = ttk.Entry(top, width=18)
        self.date_entry.insert(0, __import__("datetime").date.today().isoformat())
        self.date_entry.pack(side="left", padx=12)

        canvas = tk.Canvas(box, bg="white", highlightthickness=0)
        scroll = ttk.Scrollbar(box, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg="white")
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        con = get_connection()
        accounts = con.execute("""
            SELECT code,name,account_type FROM accounts
            WHERE account_type IN ('Asset','Liability','Equity')
            ORDER BY code
        """).fetchall()
        con.close()

        for r, a in enumerate(accounts):
            tk.Label(body, text=f"{a['code']}  {a['name']}",
                     bg="white", fg="#243b53",
                     font=("Segoe UI",10)).grid(row=r,column=0,sticky="w",padx=10,pady=8)
            e = ttk.Entry(body, width=24)
            e.grid(row=r,column=1,sticky="w",padx=30,pady=8)
            self.entries[a["code"]] = e

        ttk.Button(box, text="SAVE OPENING BALANCE",
                   command=self.save).pack(anchor="e", pady=(16,0))

    def save(self):
        try:
            balances = {}
            for code, entry in self.entries.items():
                text = entry.get().strip().replace(",","")
                if text:
                    balances[code] = float(text)
            if not balances:
                raise ValueError("Enter at least one opening balance.")

            create_opening_balance(self.date_entry.get().strip(), balances)
            messagebox.showinfo(
                "Saved",
                "Opening balances saved successfully.\n\n"
                "The opening journal entry and ledger balances have been created automatically."
            )
            if self.on_saved:
                self.on_saved()
        except Exception as exc:
            messagebox.showerror("Opening Balance Error", str(exc))
