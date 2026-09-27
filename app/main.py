
import tkinter as tk
from tkinter import ttk
from app.database import init_database,seed_accounts
from app.ui.dashboard import DashboardFrame
from app.ui.opening_balance import OpeningBalanceFrame
from app.ui.transactions import TransactionsFrame
from app.ui.ledger import LedgerFrame
from app.ui.reports import TrialBalanceFrame,PnLFrame,BalanceSheetFrame
from app.ui.contacts import ContactsFrame
from app.ui.credit import CreditFrame
from app.ui.aging import AgingFrame
from app.ui.inventory import InventoryFrame
from app.ui.trade import TradeFrame
from app.ui.bank import BankFrame,ReconciliationFrame,TransferFrame

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Business Accounting System")
        self.geometry("1380x840");self.minsize(1150,720);self.configure(bg="#eef2f7")
        h=tk.Frame(self,bg="#102f4f",height=72);h.pack(fill="x")
        tk.Label(h,text="BUSINESS ACCOUNTING SYSTEM",bg="#102f4f",fg="white",font=("Segoe UI",20,"bold")).pack(side="left",padx=24,pady=17)
        tk.Label(h,text="V5 + V6 • Inventory + Bank",bg="#102f4f",fg="#dce9f5",font=("Segoe UI",10)).pack(side="right",padx=24)
        nav=tk.Frame(self,bg="white");nav.pack(fill="x")
        buttons=[
          ("Dashboard",self.dashboard),("Opening",self.opening),("Transaction",self.transactions),
          ("Customers",self.customers),("Suppliers",self.suppliers),
          ("Customer Credit",self.customer_credit),("Supplier Credit",self.supplier_credit),
          ("Products",self.inventory),("Sale",self.sale),("Purchase",self.purchase),
          ("Banks",self.banks),("Transfer",self.transfer),("Reconcile",self.reconcile),
          ("Ledger",self.ledger),("Trial Balance",self.trial),("P&L",self.pnl),("Balance Sheet",self.bs)
        ]
        for label,cmd in buttons:ttk.Button(nav,text=label,command=cmd).pack(side="left",padx=2,pady=9)
        self.body=tk.Frame(self,bg="#eef2f7");self.body.pack(fill="both",expand=True,padx=22,pady=18)
        self.dashboard()
    def clear(self):
        for w in self.body.winfo_children():w.destroy()
    def show(self,cls,*args):
        self.clear();cls(self.body,*args).pack(fill="both",expand=True)
    def dashboard(self):self.show(DashboardFrame)
    def opening(self):self.show(OpeningBalanceFrame,self.dashboard)
    def transactions(self):self.show(TransactionsFrame,self.dashboard)
    def customers(self):self.show(ContactsFrame,"customer")
    def suppliers(self):self.show(ContactsFrame,"supplier")
    def customer_credit(self):self.show(CreditFrame,"customer",self.dashboard)
    def supplier_credit(self):self.show(CreditFrame,"supplier",self.dashboard)
    def inventory(self):self.show(InventoryFrame)
    def sale(self):self.show(TradeFrame,"sale",self.dashboard)
    def purchase(self):self.show(TradeFrame,"purchase",self.dashboard)
    def banks(self):self.show(BankFrame)
    def transfer(self):self.show(lambda p:TransferFrame(p,self.dashboard))
    def reconcile(self):self.show(ReconciliationFrame)
    def ledger(self):self.show(LedgerFrame)
    def trial(self):self.show(TrialBalanceFrame)
    def pnl(self):self.show(PnLFrame)
    def bs(self):self.show(BalanceSheetFrame)

if __name__=="__main__":
    init_database();seed_accounts();MainApp().mainloop()
