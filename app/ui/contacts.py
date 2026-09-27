
import tkinter as tk
from tkinter import ttk, messagebox
from app.database import get_connection

class ContactsFrame(tk.Frame):
    def __init__(self, master, mode="customer", on_change=None):
        super().__init__(master,bg="#eef2f7")
        self.mode=mode
        self.on_change=on_change
        self.build()

    def build(self):
        title="Customers" if self.mode=="customer" else "Suppliers"
        table="customers" if self.mode=="customer" else "suppliers"
        tk.Label(self,text=title,bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,12))

        top=tk.Frame(self,bg="white",padx=18,pady=16);top.pack(fill="x")
        self.name=ttk.Entry(top,width=32);self.phone=ttk.Entry(top,width=20)
        self.address=ttk.Entry(top,width=38);self.limit=ttk.Entry(top,width=15)
        for i,(lab,w) in enumerate([("Name",self.name),("Phone",self.phone),("Address",self.address),("Credit Limit",self.limit)]):
            tk.Label(top,text=lab,bg="white",font=("Segoe UI",9,"bold")).grid(row=0,column=i,sticky="w",padx=5)
            w.grid(row=1,column=i,padx=5,pady=5)
        ttk.Button(top,text=f"ADD {title[:-1].upper()}",command=lambda:self.add(table)).grid(row=1,column=4,padx=10)

        box=tk.Frame(self,bg="white",padx=12,pady=12);box.pack(fill="both",expand=True,pady=12)
        cols=("ID","Name","Phone","Address","Credit Limit","Outstanding")
        self.tree=ttk.Treeview(box,columns=cols,show="headings")
        for c in cols:
            self.tree.heading(c,text=c);self.tree.column(c,width=160)
        self.tree.pack(fill="both",expand=True)
        self.refresh()

    def add(self,table):
        try:
            name=self.name.get().strip()
            if not name: raise ValueError("Name is required.")
            limit=float(self.limit.get().replace(",","") or 0)
            con=get_connection()
            con.execute(f"INSERT INTO {table}(name,phone,address,credit_limit) VALUES(?,?,?,?)",
                        (name,self.phone.get().strip(),self.address.get().strip(),limit))
            con.commit();con.close()
            for w in [self.name,self.phone,self.address,self.limit]: w.delete(0,"end")
            self.refresh()
            if self.on_change:self.on_change()
        except Exception as e: messagebox.showerror("Error",str(e))

    def refresh(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        table="customers" if self.mode=="customer" else "suppliers"
        con=get_connection()
        rows=con.execute(f"SELECT id,name,phone,address,credit_limit FROM {table} WHERE active=1 ORDER BY name").fetchall()
        for r in rows:
            if self.mode=="customer":
                b=con.execute("SELECT COALESCE(SUM(debit-credit),0) b FROM receivable_entries WHERE customer_id=?",(r["id"],)).fetchone()["b"]
            else:
                b=con.execute("SELECT COALESCE(SUM(credit-debit),0) b FROM payable_entries WHERE supplier_id=?",(r["id"],)).fetchone()["b"]
            self.tree.insert("","end",values=(r["id"],r["name"],r["phone"] or "",r["address"] or "",
                                               f"Rs. {r['credit_limit']:,.2f}",f"Rs. {b:,.2f}"))
        con.close()
