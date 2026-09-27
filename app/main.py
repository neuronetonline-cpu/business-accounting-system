
import tkinter as tk
from tkinter import ttk
from app.database import init_database, seed_accounts
from app.ui.dashboard import DashboardFrame
from app.ui.opening_balance import OpeningBalanceFrame

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Business Accounting System")
        self.geometry("1250x780")
        self.minsize(1050,680)
        self.configure(bg="#eef2f7")

        header=tk.Frame(self,bg="#102f4f",height=72)
        header.pack(fill="x")
        tk.Label(header,text="BUSINESS ACCOUNTING SYSTEM",
                 bg="#102f4f",fg="white",font=("Segoe UI",20,"bold")).pack(
                     side="left",padx=24,pady=17)
        tk.Label(header,text="V2 • Accounting Core",
                 bg="#102f4f",fg="#dce9f5",font=("Segoe UI",10)).pack(
                     side="right",padx=24)

        self.nav=tk.Frame(self,bg="white")
        self.nav.pack(fill="x")
        for label,cmd in [
            ("Dashboard",self.show_dashboard),
            ("Opening Balance",self.show_opening),
        ]:
            ttk.Button(self.nav,text=label,command=cmd).pack(side="left",padx=5,pady=9)

        self.body=tk.Frame(self,bg="#eef2f7")
        self.body.pack(fill="both",expand=True,padx=22,pady=18)
        self.show_dashboard()

    def clear(self):
        for w in self.body.winfo_children(): w.destroy()

    def show_dashboard(self):
        self.clear()
        DashboardFrame(self.body).pack(fill="both",expand=True)

    def show_opening(self):
        self.clear()
        OpeningBalanceFrame(self.body,on_saved=self.show_dashboard).pack(fill="both",expand=True)

if __name__=="__main__":
    init_database()
    seed_accounts()
    MainApp().mainloop()
