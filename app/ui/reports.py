
import tkinter as tk
from tkinter import ttk
from app.database import get_connection
def rows():
    con=get_connection()
    r=con.execute("""SELECT a.code,a.name,a.account_type,COALESCE(SUM(l.debit),0) debit,COALESCE(SUM(l.credit),0) credit
    FROM accounts a LEFT JOIN journal_lines l ON a.id=l.account_id GROUP BY a.id ORDER BY a.code""").fetchall()
    con.close();return r
class TrialBalanceFrame(tk.Frame):
    def __init__(self,m):
        super().__init__(m,bg="#eef2f7");tk.Label(self,text="Trial Balance",bg="#eef2f7",fg="#102f4f",font=("Segoe UI",22,"bold")).pack(anchor="w")
        b=tk.Frame(self,bg="white",padx=12,pady=12);b.pack(fill="both",expand=True,pady=12)
        t=ttk.Treeview(b,columns=("Code","Account","Debit","Credit"),show="headings")
        for c in ("Code","Account","Debit","Credit"):t.heading(c,text=c);t.column(c,width=200)
        t.pack(fill="both",expand=True);td=tc=0
        for r in rows():
            x=r["debit"]-r["credit"];d=max(x,0);c=max(-x,0)
            if d or c:td+=d;tc+=c;t.insert("","end",values=(r["code"],r["name"],f"Rs. {d:,.2f}",f"Rs. {c:,.2f}"))
        tk.Label(self,text=f"DEBIT {td:,.2f}    CREDIT {tc:,.2f}",bg="#eef2f7",font=("Segoe UI",12,"bold")).pack(anchor="e")
class PnLFrame(tk.Frame):
    def __init__(self,m):
        super().__init__(m,bg="#eef2f7");tk.Label(self,text="Profit & Loss",bg="#eef2f7",fg="#102f4f",font=("Segoe UI",22,"bold")).pack(anchor="w")
        rev=sum(r["credit"]-r["debit"] for r in rows() if r["account_type"]=="Revenue")
        exp=sum(r["debit"]-r["credit"] for r in rows() if r["account_type"]=="Expense")
        b=tk.Frame(self,bg="white",padx=25,pady=25);b.pack(fill="x",pady=15)
        for x,v in [("Revenue",rev),("Expenses",exp),("NET PROFIT",rev-exp)]:tk.Label(b,text=f"{x}: Rs. {v:,.2f}",bg="white",font=("Segoe UI",14,"bold")).pack(anchor="w",pady=7)
class BalanceSheetFrame(tk.Frame):
    def __init__(self,m):
        super().__init__(m,bg="#eef2f7");tk.Label(self,text="Balance Sheet",bg="#eef2f7",fg="#102f4f",font=("Segoe UI",22,"bold")).pack(anchor="w")
        rs=rows();assets=sum(r["debit"]-r["credit"] for r in rs if r["account_type"]=="Asset")
        liab=sum(r["credit"]-r["debit"] for r in rs if r["account_type"]=="Liability")
        eq=sum(r["credit"]-r["debit"] for r in rs if r["account_type"]=="Equity")
        profit=sum(r["credit"]-r["debit"] for r in rs if r["account_type"]=="Revenue")-sum(r["debit"]-r["credit"] for r in rs if r["account_type"]=="Expense")
        b=tk.Frame(self,bg="white",padx=25,pady=25);b.pack(fill="x",pady=15)
        for x,v in [("TOTAL ASSETS",assets),("LIABILITIES",liab),("EQUITY",eq),("CURRENT PROFIT",profit),("LIABILITIES + EQUITY",liab+eq+profit),("BALANCE CHECK",assets-(liab+eq+profit))]:
            tk.Label(b,text=f"{x}: Rs. {v:,.2f}",bg="white",font=("Segoe UI",13,"bold")).pack(anchor="w",pady=6)
