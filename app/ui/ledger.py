
import tkinter as tk
from tkinter import ttk
from app.database import get_connection

class LedgerFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#eef2f7")
        self.build()

    def build(self):
        tk.Label(self,text="General Ledger",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,12))
        box=tk.Frame(self,bg="white",padx=15,pady=15)
        box.pack(fill="both",expand=True)
        cols=("Date","Reference","Description","Account","Debit","Credit")
        tree=ttk.Treeview(box,columns=cols,show="headings")
        for c in cols:
            tree.heading(c,text=c)
            tree.column(c,width=160,anchor="w")
        tree.column("Description",width=260)
        tree.pack(fill="both",expand=True)

        con=get_connection()
        rows=con.execute("""
        SELECT j.entry_date,j.reference,j.description,a.code||' - '||a.name account,
               l.debit,l.credit
        FROM journal_entries j
        JOIN journal_lines l ON j.id=l.journal_id
        JOIN accounts a ON a.id=l.account_id
        ORDER BY j.entry_date,j.id,l.id
        """).fetchall()
        con.close()

        for r in rows:
            tree.insert("", "end", values=(
                r["entry_date"],r["reference"] or "",
                r["description"],r["account"],
                f"Rs. {r['debit']:,.2f}" if r["debit"] else "",
                f"Rs. {r['credit']:,.2f}" if r["credit"] else ""
            ))
