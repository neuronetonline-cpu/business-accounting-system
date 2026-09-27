
import tkinter as tk
from app.database import get_connection

class DashboardFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7");self.build()

    def build(self):
        tk.Label(self,text="Business Dashboard",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,16))
        con=get_connection()
        rows=con.execute("""
        SELECT a.account_type,COALESCE(SUM(l.debit),0) debit,COALESCE(SUM(l.credit),0) credit
        FROM accounts a LEFT JOIN journal_lines l ON a.id=l.account_id GROUP BY a.id
        """).fetchall()
        receivable=con.execute("SELECT COALESCE(SUM(debit-credit),0) b FROM receivable_entries").fetchone()["b"]
        payable=con.execute("SELECT COALESCE(SUM(credit-debit),0) b FROM payable_entries").fetchone()["b"]
        customers=con.execute("SELECT COUNT(*) n FROM customers WHERE active=1").fetchone()["n"]
        suppliers=con.execute("SELECT COUNT(*) n FROM suppliers WHERE active=1").fetchone()["n"]
        con.close()

        asset=liab=rev=exp=0
        for r in rows:
            bal=r["debit"]-r["credit"]
            if r["account_type"]=="Asset":asset+=bal
            elif r["account_type"]=="Liability":liab-=bal
            elif r["account_type"]=="Revenue":rev-=bal
            elif r["account_type"]=="Expense":exp+=bal
        cards=[
            ("SALES",rev),("EXPENSES",exp),("NET PROFIT",rev-exp),
            ("RECEIVABLES",receivable),("PAYABLES",payable),("TOTAL ASSETS",asset)
        ]
        grid=tk.Frame(self,bg="#eef2f7");grid.pack(fill="x")
        for i,(title,v) in enumerate(cards):
            c=tk.Frame(grid,bg="white",highlightbackground="#d4dde6",highlightthickness=1)
            c.grid(row=i//3,column=i%3,sticky="nsew",padx=6,pady=6,ipadx=14,ipady=12)
            tk.Label(c,text=title,bg="white",fg="#6b7b8c",font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(c,text=f"Rs. {v:,.2f}",bg="white",fg="#102f4f",font=("Segoe UI",16,"bold")).pack(anchor="w",pady=(4,0))
        for i in range(3):grid.columnconfigure(i,weight=1)

        info=tk.Frame(self,bg="white",padx=20,pady=18);info.pack(fill="both",expand=True,pady=18)
        tk.Label(info,text=f"Active Customers: {customers}     Active Suppliers: {suppliers}",
                 bg="white",fg="#102f4f",font=("Segoe UI",12,"bold")).pack(anchor="w")
        tk.Label(info,text="Receivables and Payables are linked to the accounting ledger automatically.",
                 bg="white",fg="#5b6f82",font=("Segoe UI",10)).pack(anchor="w",pady=8)
