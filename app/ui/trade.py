
import tkinter as tk
from tkinter import ttk,messagebox
from datetime import date
from app.database import get_connection
from app.accounting.inventory import create_purchase,create_sale

class TradeFrame(tk.Frame):
    def __init__(self,master,mode="sale",on_saved=None):
        super().__init__(master,bg="#eef2f7");self.mode=mode;self.on_saved=on_saved;self.build()
    def build(self):
        title="New Sale" if self.mode=="sale" else "New Purchase"
        tk.Label(self,text=title,bg="#eef2f7",fg="#102f4f",font=("Segoe UI",22,"bold")).pack(anchor="w")
        box=tk.Frame(self,bg="white",padx=25,pady=22);box.pack(fill="x",pady=15)
        self.f={}
        labels=["Date","Invoice / Bill No","Product","Qty","Unit Price / Cost","Payment Type","Customer / Supplier","Paid"]
        for i,l in enumerate(labels):
            tk.Label(box,text=l,bg="white",font=("Segoe UI",9,"bold")).grid(row=i,column=0,sticky="w",pady=7)
            if l=="Product":
                w=ttk.Combobox(box,values=self.products(),state="readonly",width=38)
                if self.products():w.current(0)
            elif l=="Payment Type":
                w=ttk.Combobox(box,values=["Cash","Bank","Credit"],state="readonly",width=38);w.current(0)
            elif l=="Customer / Supplier":
                w=ttk.Combobox(box,values=self.entities(),state="readonly",width=38)
                if self.entities():w.current(0)
            else:
                w=ttk.Entry(box,width=40)
                if l=="Date":w.insert(0,date.today().isoformat())
            w.grid(row=i,column=1,padx=18,sticky="w",pady=7);self.f[l]=w
        ttk.Button(box,text="SAVE",command=self.save).grid(row=8,column=1,sticky="w",pady=14)
    def products(self):
        con=get_connection();r=con.execute("SELECT id,name,cost_price,selling_price FROM products WHERE active=1 ORDER BY name").fetchall();con.close()
        return [f"{x['id']} - {x['name']} - {x['cost_price']:.2f}/{x['selling_price']:.2f}" for x in r]
    def entities(self):
        table="customers" if self.mode=="sale" else "suppliers"
        con=get_connection();r=con.execute(f"SELECT id,name FROM {table} WHERE active=1 ORDER BY name").fetchall();con.close()
        return ["0 - Walk-in / None"]+[f"{x['id']} - {x['name']}" for x in r]
    def save(self):
        try:
            p=self.f["Product"].get(); pid=int(p.split(" - ")[0])
            qty=float(self.f["Qty"].get()); unit=float(self.f["Unit Price / Cost"].get())
            pay=self.f["Payment Type"].get(); ent=self.f["Customer / Supplier"].get()
            eid=int(ent.split(" - ")[0]) if ent else 0
            paid=float(self.f["Paid"].get() or 0)
            con=get_connection();pr=con.execute("SELECT cost_price,selling_price FROM products WHERE id=?",(pid,)).fetchone();con.close()
            if self.mode=="sale":
                price=unit or pr["selling_price"]; cost=pr["cost_price"]
                create_sale(self.f["Date"].get(),self.f["Invoice / Bill No"].get(),eid or None,pay,[(pid,qty,price,cost)],paid)
            else:
                cost=unit; create_purchase(self.f["Date"].get(),self.f["Invoice / Bill No"].get(),eid or None,pay,[(pid,qty,cost)],paid)
            messagebox.showinfo("Saved","Transaction saved. Stock and accounting updated.")
            if self.on_saved:self.on_saved()
        except Exception as e:messagebox.showerror("Error",str(e))
