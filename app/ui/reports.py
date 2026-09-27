
import tkinter as tk
from tkinter import ttk
from app.database import get_connection

def account_balances():
    con=get_connection()
    rows=con.execute("""
    SELECT a.code,a.name,a.account_type,
           COALESCE(SUM(l.debit),0) debit,
           COALESCE(SUM(l.credit),0) credit
    FROM accounts a
    LEFT JOIN journal_lines l ON a.id=l.account_id
    GROUP BY a.id
    ORDER BY a.code
    """).fetchall()
    con.close()
    return rows

class TrialBalanceFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7")
        tk.Label(self,text="Trial Balance",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,12))
        box=tk.Frame(self,bg="white",padx=15,pady=15);box.pack(fill="both",expand=True)
        cols=("Code","Account","Debit","Credit")
        tree=ttk.Treeview(box,columns=cols,show="headings")
        for c in cols: tree.heading(c,text=c);tree.column(c,width=190)
        tree.pack(fill="both",expand=True)
        td=tc=0
        for r in account_balances():
            balance=r["debit"]-r["credit"]
            debit=max(balance,0);credit=max(-balance,0)
            if debit or credit:
                td+=debit;tc+=credit
                tree.insert("", "end", values=(r["code"],r["name"],f"Rs. {debit:,.2f}",f"Rs. {credit:,.2f}"))
        tk.Label(self,text=f"TOTAL DEBIT: Rs. {td:,.2f}     TOTAL CREDIT: Rs. {tc:,.2f}",
                 bg="#eef2f7",fg="#102f4f",font=("Segoe UI",12,"bold")).pack(anchor="e",pady=10)

class PnLFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7")
        tk.Label(self,text="Profit & Loss",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,12))
        box=tk.Frame(self,bg="white",padx=20,pady=20);box.pack(fill="x")
        revenue=expenses=0
        for r in account_balances():
            if r["account_type"]=="Revenue": revenue += r["credit"]-r["debit"]
            if r["account_type"]=="Expense": expenses += r["debit"]-r["credit"]
        profit=revenue-expenses
        for label,value in [("Revenue",revenue),("Expenses",expenses),("NET PROFIT",profit)]:
            tk.Label(box,text=f"{label}:  Rs. {value:,.2f}",bg="white",
                     fg="#102f4f",font=("Segoe UI",14,"bold" if label=="NET PROFIT" else "normal")).pack(anchor="w",pady=8)

class BalanceSheetFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7")
        tk.Label(self,text="Balance Sheet",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,12))
        box=tk.Frame(self,bg="white",padx=20,pady=20);box.pack(fill="both",expand=True)
        assets=liabilities=equity=0
        for r in account_balances():
            bal=r["debit"]-r["credit"]
            if r["account_type"]=="Asset": assets += bal
            elif r["account_type"]=="Liability": liabilities -= bal
            elif r["account_type"]=="Equity": equity -= bal
        revenue=sum(r["credit"]-r["debit"] for r in account_balances() if r["account_type"]=="Revenue")
        expenses=sum(r["debit"]-r["credit"] for r in account_balances() if r["account_type"]=="Expense")
        profit=revenue-expenses
        equity_total=equity+profit

        for label,value in [
            ("TOTAL ASSETS",assets),
            ("TOTAL LIABILITIES",liabilities),
            ("OWNER EQUITY",equity),
            ("CURRENT PERIOD PROFIT",profit),
            ("LIABILITIES + EQUITY",liabilities+equity_total),
            ("BALANCE CHECK",assets-(liabilities+equity_total))
        ]:
            tk.Label(box,text=f"{label}:  Rs. {value:,.2f}",bg="white",
                     fg="#102f4f",font=("Segoe UI",13,"bold")).pack(anchor="w",pady=7)
