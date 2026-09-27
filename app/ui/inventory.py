
import tkinter as tk
from tkinter import ttk,messagebox
from app.database import get_connection
from app.accounting.inventory import add_product,product_balance

class InventoryFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7"); self.build()
    def build(self):
        tk.Label(self,text="Inventory & Products",bg="#eef2f7",fg="#102f4f",font=("Segoe UI",22,"bold")).pack(anchor="w")
        top=tk.Frame(self,bg="white",padx=18,pady=14);top.pack(fill="x",pady=12)
        self.f={}
        labels=["SKU","Product Name","Category","Brand","Unit","Cost Price","Selling Price","Reorder Level"]
        for i,l in enumerate(labels):
            tk.Label(top,text=l,bg="white",font=("Segoe UI",8,"bold")).grid(row=0,column=i,padx=3)
            e=ttk.Entry(top,width=14);e.grid(row=1,column=i,padx=3,pady=4);self.f[l]=e
        ttk.Button(top,text="ADD PRODUCT",command=self.add).grid(row=1,column=8,padx=8)
        box=tk.Frame(self,bg="white",padx=10,pady=10);box.pack(fill="both",expand=True)
        cols=("ID","SKU","Product","Category","Brand","Cost","Selling","Qty","Stock Value","Reorder","Status")
        self.tree=ttk.Treeview(box,columns=cols,show="headings")
        for c in cols:self.tree.heading(c,text=c);self.tree.column(c,width=105)
        self.tree.column("Product",width=190);self.tree.pack(fill="both",expand=True)
        self.refresh()
    def add(self):
        try:
            add_product(self.f["SKU"].get().strip(),self.f["Product Name"].get().strip(),
                        self.f["Category"].get().strip(),self.f["Brand"].get().strip(),
                        self.f["Unit"].get().strip() or "pcs",
                        float(self.f["Cost Price"].get() or 0),
                        float(self.f["Selling Price"].get() or 0),
                        float(self.f["Reorder Level"].get() or 0))
            messagebox.showinfo("Saved","Product added.")
            for e in self.f.values():e.delete(0,"end")
            self.refresh()
        except Exception as e:messagebox.showerror("Error",str(e))
    def refresh(self):
        for x in self.tree.get_children():self.tree.delete(x)
        con=get_connection(); rows=con.execute("SELECT * FROM products WHERE active=1 ORDER BY name").fetchall()
        for r in rows:
            q,c=product_balance(r["id"]); status="LOW" if q<=r["reorder_level"] else "OK"
            self.tree.insert("","end",values=(r["id"],r["sku"] or "",r["name"],r["category"] or "",r["brand"] or "",
                f"{r['cost_price']:,.2f}",f"{r['selling_price']:,.2f}",f"{q:,.2f}",f"{c:,.2f}",f"{r['reorder_level']:,.2f}",status))
        con.close()
