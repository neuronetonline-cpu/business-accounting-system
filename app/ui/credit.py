
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.database import get_connection
from app.accounting.credit import (
    create_customer_credit, create_customer_payment,
    create_supplier_credit, create_supplier_payment
)

class CreditFrame(tk.Frame):
    def __init__(self,master,mode="customer",on_saved=None):
        super().__init__(master,bg="#eef2f7")
        self.mode=mode;self.on_saved=on_saved
        self.build()

    def build(self):
        customer=self.mode=="customer"
        title="Customer Credit" if customer else "Supplier Credit"
        tk.Label(self,text=title,bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,5))
        tk.Label(self,text="Post credit invoices and payments without entering debit/credit manually.",
                 bg="#eef2f7",fg="#647586").pack(anchor="w",pady=(0,14))

        box=tk.Frame(self,bg="white",padx=24,pady=20);box.pack(fill="x")
        labels=["Date","Reference","Type","Name","Amount","Due Date","Account"]
        self.f={}
        for i,l in enumerate(labels):
            tk.Label(box,text=l,bg="white",font=("Segoe UI",9,"bold")).grid(row=i,column=0,sticky="w",pady=7)
            if l=="Date":
                w=ttk.Entry(box,width=38);w.insert(0,date.today().isoformat())
            elif l=="Type":
                w=ttk.Combobox(box,values=["Credit Invoice","Payment"],state="readonly",width=36);w.current(0)
                w.bind("<<ComboboxSelected>>",lambda e:self.refresh_preview())
            elif l=="Name":
                w=ttk.Combobox(box,values=self.names(),state="readonly",width=36)
                if self.names():w.current(0)
                w.bind("<<ComboboxSelected>>",lambda e:self.refresh_preview())
            elif l=="Account":
                w=ttk.Combobox(box,values=["1010 - Bank - Main","1000 - Cash"],state="readonly",width=36);w.current(0)
            else:
                w=ttk.Entry(box,width=38)
            w.grid(row=i,column=1,padx=18,pady=7,sticky="w");self.f[l]=w

        self.preview=tk.Label(box,text="",bg="white",fg="#102f4f",justify="left",
                              font=("Consolas",10),anchor="nw")
        self.preview.grid(row=0,column=3,rowspan=7,padx=45,sticky="nsew")
        ttk.Button(box,text="SAVE",command=self.save).grid(row=8,column=1,sticky="w",pady=15)
        self.refresh_preview()

    def names(self):
        table="customers" if self.mode=="customer" else "suppliers"
        con=get_connection()
        rows=con.execute(f"SELECT id,name FROM {table} WHERE active=1 ORDER BY name").fetchall()
        con.close()
        return [f"{r['id']} - {r['name']}" for r in rows]

    def refresh_preview(self):
        typ=self.f.get("Type").get() if "Type" in self.f else "Credit Invoice"
        amt=self.f.get("Amount").get().strip() if "Amount" in self.f else ""
        try:a=float(amt.replace(",","")) if amt else 0
        except:a=0
        if self.mode=="customer":
            if typ=="Credit Invoice":
                txt=f"DEBIT  Accounts Receivable\n       Rs. {a:,.2f}\n\nCREDIT Sales Revenue\n       Rs. {a:,.2f}"
            else:
                txt=f"DEBIT  Bank / Cash\n       Rs. {a:,.2f}\n\nCREDIT Accounts Receivable\n       Rs. {a:,.2f}"
        else:
            if typ=="Credit Invoice":
                txt=f"DEBIT  Purchase / COGS\n       Rs. {a:,.2f}\n\nCREDIT Accounts Payable\n       Rs. {a:,.2f}"
            else:
                txt=f"DEBIT  Accounts Payable\n       Rs. {a:,.2f}\n\nCREDIT Bank / Cash\n       Rs. {a:,.2f}"
        self.preview.config(text=txt)

    def save(self):
        try:
            name=self.f["Name"].get()
            if not name:raise ValueError("Select a name.")
            entity_id=int(name.split(" - ")[0])
            dt=self.f["Date"].get().strip()
            ref=self.f["Reference"].get().strip()
            typ=self.f["Type"].get()
            amount=float(self.f["Amount"].get().replace(",",""))
            due=self.f["Due Date"].get().strip() or None
            account=self.f["Account"].get().split(" - ")[0]
            if amount<=0:raise ValueError("Amount must be greater than zero.")

            if self.mode=="customer":
                if typ=="Credit Invoice":
                    create_customer_credit(entity_id,dt,ref,amount,due)
                else:
                    create_customer_payment(entity_id,dt,ref,amount,account)
            else:
                if typ=="Credit Invoice":
                    create_supplier_credit(entity_id,dt,ref,amount,due)
                else:
                    create_supplier_payment(entity_id,dt,ref,amount,account)

            messagebox.showinfo("Saved","Credit transaction saved and posted to the accounting ledger.")
            if self.on_saved:self.on_saved()
        except Exception as e:messagebox.showerror("Error",str(e))
