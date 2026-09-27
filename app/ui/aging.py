
import tkinter as tk
from tkinter import ttk
from datetime import date, datetime

from app.database import get_connection

def days_old(d):
    try:
        return max(0,(date.today()-datetime.strptime(d,"%Y-%m-%d").date()).days)
    except:
        return 0

class AgingFrame(tk.Frame):
    def __init__(self,master,mode="customer"):
        super().__init__(master,bg="#eef2f7")
        self.mode=mode;self.build()

    def build(self):
        title="Customer Receivable Aging" if self.mode=="customer" else "Supplier Payable Aging"
        tk.Label(self,text=title,bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,12))
        box=tk.Frame(self,bg="white",padx=12,pady=12);box.pack(fill="both",expand=True)
        cols=("Name","Reference","Date","Due Date","Outstanding","Age","Bucket")
        tree=ttk.Treeview(box,columns=cols,show="headings")
        for c in cols:tree.heading(c,text=c);tree.column(c,width=145)
        tree.pack(fill="both",expand=True)

        con=get_connection()
        if self.mode=="customer":
            rows=con.execute("""
            SELECT c.name,r.reference,r.entry_date,r.due_date,
                   SUM(r.debit-r.credit) outstanding
            FROM receivable_entries r JOIN customers c ON c.id=r.customer_id
            GROUP BY r.customer_id,r.reference,r.entry_date,r.due_date
            HAVING outstanding > 0.005
            ORDER BY r.due_date
            """).fetchall()
        else:
            rows=con.execute("""
            SELECT s.name,p.reference,p.entry_date,p.due_date,
                   SUM(p.credit-p.debit) outstanding
            FROM payable_entries p JOIN suppliers s ON s.id=p.supplier_id
            GROUP BY p.supplier_id,p.reference,p.entry_date,p.due_date
            HAVING outstanding > 0.005
            ORDER BY p.due_date
            """).fetchall()

        for r in rows:
            d=days_old(r["due_date"] or r["entry_date"])
            bucket="0-30" if d<=30 else "31-60" if d<=60 else "61-90" if d<=90 else "90+"
            tree.insert("","end",values=(r["name"],r["reference"] or "",r["entry_date"],
                                         r["due_date"] or "",f"Rs. {r['outstanding']:,.2f}",d,bucket))
        con.close()
