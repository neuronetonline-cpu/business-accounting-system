
import tkinter as tk
from app.database import get_connection

class DashboardFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#eef2f7")
        self.build()

    def build(self):
        tk.Label(self,text="Business Dashboard",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,18))

        con=get_connection()
        rows=con.execute("""
        SELECT a.account_type,
               COALESCE(SUM(l.debit),0) debit,
               COALESCE(SUM(l.credit),0) credit
        FROM accounts a
        LEFT JOIN journal_lines l ON l.account_id=a.id
        GROUP BY a.id
        """).fetchall()
        con.close()

        vals={"Asset":0,"Liability":0,"Equity":0,"Revenue":0,"Expense":0}
        for r in rows:
            if r["account_type"] in vals:
                vals[r["account_type"]] += r["debit"]-r["credit"]

        sales = -vals["Revenue"]
        expenses = vals["Expense"]
        profit = sales-expenses

        cards=[
            ("SALES",sales),("EXPENSES",expenses),("NET PROFIT",profit),
            ("ASSETS",vals["Asset"]),("LIABILITIES",-vals["Liability"]),
            ("EQUITY",-vals["Equity"]+profit)
        ]

        grid=tk.Frame(self,bg="#eef2f7"); grid.pack(fill="x")
        for i,(title,value) in enumerate(cards):
            card=tk.Frame(grid,bg="white",highlightbackground="#d4dde6",highlightthickness=1)
            card.grid(row=i//3,column=i%3,sticky="nsew",padx=6,pady=6,ipadx=14,ipady=12)
            tk.Label(card,text=title,bg="white",fg="#6b7b8c",
                     font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(card,text=f"Rs. {value:,.2f}",bg="white",fg="#102f4f",
                     font=("Segoe UI",16,"bold")).pack(anchor="w",pady=(4,0))
        for i in range(3): grid.columnconfigure(i,weight=1)
