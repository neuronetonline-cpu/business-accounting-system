
import tkinter as tk
from tkinter import ttk
from app.database import init_database, seed_accounts
from app.ui.dashboard import DashboardFrame
from app.ui.opening_balance import OpeningBalanceFrame
from app.ui.transactions import TransactionsFrame
from app.ui.ledger import LedgerFrame
from app.ui.reports import TrialBalanceFrame, PnLFrame, BalanceSheetFrame

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Business Accounting System")
        self.geometry("1280x800")
        self.minsize(1080,700)
        self.configure(bg="#eef2f7")

        header=tk.Frame(self,bg="#102f4f",height=72);header.pack(fill="x")
        tk.Label(header,text="BUSINESS ACCOUNTING SYSTEM",bg="#102f4f",fg="white",
                 font=("Segoe UI",20,"bold")).pack(side="left",padx=24,pady=17)
        tk.Label(header,text="V3 • Daily Transactions",bg="#102f4f",fg="#dce9f5",
                 font=("Segoe UI",10)).pack(side="right",padx=24)

        nav=tk.Frame(self,bg="white");nav.pack(fill="x")
        buttons=[
            ("Dashboard",self.dashboard),("Opening Balance",self.opening),
            ("New Transaction",self.transactions),("General Ledger",self.ledger),
            ("Trial Balance",self.trial),("Profit & Loss",self.pnl),
            ("Balance Sheet",self.bs)
        ]
        for label,cmd in buttons:
            ttk.Button(nav,text=label,command=cmd).pack(side="left",padx=4,pady=9)

        self.body=tk.Frame(self,bg="#eef2f7");self.body.pack(fill="both",expand=True,padx=22,pady=18)
        self.dashboard()

    def clear(self):
        for w in self.body.winfo_children():w.destroy()

    def show(self,frame):
        self.clear();frame(self.body).pack(fill="both",expand=True)

    def dashboard(self): self.show(DashboardFrame)
    def opening(self): self.show(lambda p: OpeningBalanceFrame(p,on_saved=self.dashboard))
    def transactions(self): self.show(lambda p: TransactionsFrame(p,on_saved=self.dashboard))
    def ledger(self): self.show(LedgerFrame)
    def trial(self): self.show(TrialBalanceFrame)
    def pnl(self): self.show(PnLFrame)
    def bs(self): self.show(BalanceSheetFrame)

if __name__=="__main__":
    init_database()
    seed_accounts()
    MainApp().mainloop()
