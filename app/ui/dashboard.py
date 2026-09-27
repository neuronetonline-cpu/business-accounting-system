
import tkinter as tk
from app.database import get_connection

class DashboardFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7")
        self.build()

    def build(self):
        tk.Label(self,text="Business Dashboard",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,16))
        con=get_connection()
        rows=con.execute("""
        SELECT a.account_type,COALESCE(SUM(l.debit),0) debit,COALESCE(SUM(l.credit),0) credit
        FROM accounts a LEFT JOIN journal_lines l ON a.id=l.account_id
        GROUP BY a.id
        """).fetchall();con.close()

        asset=liab=rev=exp=0
        for r in rows:
            bal=r["debit"]-r["credit"]
            if r["account_type"]=="Asset": asset+=bal
            elif r["account_type"]=="Liability": liab-=bal
            elif r["account_type"]=="Revenue": rev-=bal
            elif r["account_type"]=="Expense": exp+=bal

        cards=[
            ("SALES",rev),("EXPENSES",exp),("NET PROFIT",rev-exp),
            ("ASSETS",asset),("LIABILITIES",liab),("EQUITY",asset-liab)
        ]
        grid=tk.Frame(self,bg="#eef2f7");grid.pack(fill="x")
        for i,(title,v) in enumerate(cards):
            c=tk.Frame(grid,bg="white",highlightbackground="#d4dde6",highlightthickness=1)
            c.grid(row=i//3,column=i%3,sticky="nsew",padx=6,pady=6,ipadx=14,ipady=12)
            tk.Label(c,text=title,bg="white",fg="#6b7b8c",font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(c,text=f"Rs. {v:,.2f}",bg="white",fg="#102f4f",font=("Segoe UI",16,"bold")).pack(anchor="w",pady=(4,0))
        for i in range(3):grid.columnconfigure(i,weight=1)

        note=tk.Frame(self,bg="white",padx=20,pady=18);note.pack(fill="both",expand=True,pady=18)
        tk.Label(note,text="Accounting engine status",bg="white",fg="#102f4f",
                 font=("Segoe UI",12,"bold")).pack(anchor="w")
        tk.Label(note,text="Daily transactions automatically post to the journal and update accounting reports.",
                 bg="white",fg="#5b6f82",font=("Segoe UI",10)).pack(anchor="w",pady=8)
