
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.accounting.engine import post_simple_transaction

TYPES={
"Cash Sale":("1000","4000","Cash sale"),
"Bank Sale":("1010","4000","Bank sale"),
"Credit Sale":("1100","4000","Credit sale"),
"Other Income - Bank":("1010","4100","Other income"),
"Other Income - Cash":("1000","4100","Other income"),
"Rent Payment":("5100","1010","Rent expense"),
"Salary Payment":("5200","1010","Salary expense"),
"Utilities Payment":("5300","1010","Utilities expense"),
"Advertising Payment":("5400","1010","Advertising expense"),
"Delivery Payment":("5500","1010","Delivery expense"),
"Other Expense":("5600","1010","Other expense"),
"Owner Investment - Bank":("1010","3000","Owner investment"),
"Owner Investment - Cash":("1000","3000","Owner investment"),
"Owner Drawing - Bank":("3100","1010","Owner drawing"),
"Owner Drawing - Cash":("3100","1000","Owner drawing"),
}
class TransactionsFrame(tk.Frame):
    def __init__(self,master,on_saved=None):
        super().__init__(master,bg="#eef2f7");self.on_saved=on_saved;self.build()
    def build(self):
        tk.Label(self,text="Daily Transaction",bg="#eef2f7",fg="#102f4f",font=("Segoe UI",22,"bold")).pack(anchor="w")
        box=tk.Frame(self,bg="white",padx=25,pady=22);box.pack(fill="x",pady=15)
        self.f={}
        fields=["Date","Transaction Type","Reference","Description","Amount"]
        for i,l in enumerate(fields):
            tk.Label(box,text=l,bg="white",font=("Segoe UI",10,"bold")).grid(row=i,column=0,sticky="w",pady=8)
            if l=="Transaction Type":
                w=ttk.Combobox(box,values=list(TYPES),state="readonly",width=42);w.current(0)
            else:
                w=ttk.Entry(box,width=45)
                if l=="Date":w.insert(0,date.today().isoformat())
            w.grid(row=i,column=1,padx=18,sticky="w",pady=8);self.f[l]=w
        ttk.Button(box,text="SAVE TRANSACTION",command=self.save).grid(row=5,column=1,sticky="w",pady=15)
    def save(self):
        try:
            typ=self.f["Transaction Type"].get();a=float(self.f["Amount"].get().replace(",",""))
            if a<=0:raise ValueError("Amount must be greater than zero.")
            d,c,default=TYPES[typ]
            post_simple_transaction(self.f["Date"].get(),self.f["Reference"].get(),self.f["Description"].get() or default,d,c,a)
            messagebox.showinfo("Saved","Transaction saved and posted to the ledger.")
            if self.on_saved:self.on_saved()
        except Exception as e:messagebox.showerror("Error",str(e))
