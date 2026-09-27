
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.database import get_connection
from app.accounting.engine import create_opening_balance

class OpeningBalanceFrame(tk.Frame):
    def __init__(self,master,on_saved=None):
        super().__init__(master,bg="#eef2f7")
        self.on_saved=on_saved
        self.entries={}
        self.build()

    def build(self):
        tk.Label(self,text="Opening Balance",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,5))
        tk.Label(self,text="Enter opening balances for the start of the accounting period.",
                 bg="#eef2f7",fg="#647586",font=("Segoe UI",10)).pack(anchor="w",pady=(0,14))
        box=tk.Frame(self,bg="white",padx=24,pady=20);box.pack(fill="both",expand=True)

        top=tk.Frame(box,bg="white");top.pack(fill="x",pady=(0,12))
        tk.Label(top,text="Opening Date",bg="white",font=("Segoe UI",10,"bold")).pack(side="left")
        self.date_entry=ttk.Entry(top,width=18);self.date_entry.insert(0,date.today().isoformat())
        self.date_entry.pack(side="left",padx=12)

        body=tk.Frame(box,bg="white");body.pack(fill="both",expand=True)
        con=get_connection()
        accounts=con.execute("""
            SELECT code,name,account_type FROM accounts
            WHERE account_type IN ('Asset','Liability','Equity')
            ORDER BY code
        """).fetchall()
        con.close()

        for i,a in enumerate(accounts):
            tk.Label(body,text=f"{a['code']}  {a['name']}",bg="white",
                     fg="#243b53",font=("Segoe UI",10)).grid(row=i,column=0,sticky="w",pady=7)
            e=ttk.Entry(body,width=24);e.grid(row=i,column=1,padx=25,sticky="w",pady=7)
            self.entries[a["code"]]=e

        ttk.Button(box,text="SAVE OPENING BALANCE",command=self.save).pack(anchor="e",pady=(12,0))

    def save(self):
        try:
            balances={}
            for code,e in self.entries.items():
                s=e.get().strip().replace(",","")
                if s: balances[code]=float(s)
            if not balances: raise ValueError("Enter at least one balance.")
            create_opening_balance(self.date_entry.get().strip(),balances)
            messagebox.showinfo("Saved","Opening balance saved and posted to the accounting ledger.")
            if self.on_saved:self.on_saved()
        except Exception as e:
            messagebox.showerror("Error",str(e))
