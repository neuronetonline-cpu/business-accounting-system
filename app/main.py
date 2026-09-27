
import tkinter as tk
from tkinter import ttk
from app.database import init_database, seed_accounts
from app.ui.dashboard import DashboardFrame
from app.ui.opening_balance import OpeningBalanceFrame
from app.ui.transactions import TransactionsFrame
from app.ui.ledger import LedgerFrame
from app.ui.reports import TrialBalanceFrame, PnLFrame, BalanceSheetFrame
from app.ui.contacts import ContactsFrame
from app.ui.credit import CreditFrame
from app.ui.aging import AgingFrame

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Business Accounting System")
        self.geometry("1320x820")
        self.minsize(1100,700)
        self.configure(bg="#eef2f7")

        header=tk.Frame(self,bg="#102f4f",height=72);header.pack(fill="x")
        tk.Label(header,text="BUSINESS ACCOUNTING SYSTEM",bg="#102f4f",fg="white",
                 font=("Segoe UI",20,"bold")).pack(side="left",padx=24,pady=17)
        tk.Label(header,text="V4 • Credit Management",bg="#102f4f",fg="#dce9f5",
                 font=("Segoe UI",10)).pack(side="right",padx=24)

        nav=tk.Frame(self,bg="white");nav.pack(fill="x")
        buttons=[
            ("Dashboard",self.dashboard),("Opening Balance",self.opening),
            ("Transaction",self.transactions),("Customers",self.customers),
            ("Suppliers",self.suppliers),("Customer Credit",self.customer_credit),
            ("Supplier Credit",self.supplier_credit),("Receivable Aging",self.receivable_aging),
            ("Payable Aging",self.payable_aging),("Ledger",self.ledger),
            ("Trial Balance",self.trial),("P&L",self.pnl),("Balance Sheet",self.bs)
        ]
        for label,cmd in buttons:
            ttk.Button(nav,text=label,command=cmd).pack(side="left",padx=2,pady=9)

        self.body=tk.Frame(self,bg="#eef2f7");self.body.pack(fill="both",expand=True,padx=22,pady=18)
        self.dashboard()

    def clear(self):
        for w in self.body.winfo_children():w.destroy()
    def show(self, frame):
        self.clear();frame(self.body).pack(fill="both",expand=True)
    def dashboard(self):self.show(DashboardFrame)
    def opening(self):self.show(lambda p:OpeningBalanceFrame(p,on_saved=self.dashboard))
    def transactions(self):self.show(lambda p:TransactionsFrame(p,on_saved=self.dashboard))
    def customers(self):self.show(lambda p:ContactsFrame(p,"customer"))
    def suppliers(self):self.show(lambda p:ContactsFrame(p,"supplier"))
    def customer_credit(self):self.show(lambda p:CreditFrame(p,"customer",self.dashboard))
    def supplier_credit(self):self.show(lambda p:CreditFrame(p,"supplier",self.dashboard))
    def receivable_aging(self):self.show(lambda p:AgingFrame(p,"customer"))
    def payable_aging(self):self.show(lambda p:AgingFrame(p,"supplier"))
    def ledger(self):self.show(LedgerFrame)
    def trial(self):self.show(TrialBalanceFrame)
    def pnl(self):self.show(PnLFrame)
    def bs(self):self.show(BalanceSheetFrame)

if __name__=="__main__":
    init_database();seed_accounts();MainApp().mainloop()
