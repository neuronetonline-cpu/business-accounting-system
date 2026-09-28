import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from app.database import get_connection
from app.accounting.inventory import create_purchase, create_sale, add_product
from app.accounting.purchase_import import import_purchase_excel, commit_purchase_import, create_purchase_template
from app.accounting.audit import audit
from app.ui.theme import COLORS, FONT
from app.ui.widgets import Card, SearchableCombobox

class TradeFrame(tk.Frame):
    def __init__(self,master,mode='sale',on_saved=None):
        super().__init__(master,bg=COLORS['bg']); self.mode=mode; self.on_saved=on_saved; self.build()
    def build(self):
        title='New Sale' if self.mode=='sale' else 'New Purchase'
        tk.Label(self,text=title,bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,22,'bold')).pack(anchor='w')
        box=Card(self,padx=25,pady=22);box.pack(fill='x',pady=15)
        self.f={}
        labels=['Date','Invoice / Bill No','Product','Qty','Unit Price / Cost','Payment Type','Customer / Supplier','Paid']
        for i,l in enumerate(labels):
            tk.Label(box,text=l,bg='white',font=(FONT,9,'bold')).grid(row=i,column=0,sticky='w',pady=7)
            if l=='Product':
                holder=tk.Frame(box,bg='white');holder.grid(row=i,column=1,padx=18,sticky='w',pady=7)
                w=SearchableCombobox(holder,values=self.products(),width=34)
                if self.products():w.current(0)
                w.pack(side='left'); self.product_combo=w
                if self.mode=='purchase':
                    ttk.Button(holder,text='+ NEW PRODUCT',command=self.add_product_dialog).pack(side='left',padx=(8,0))
            elif l=='Payment Type':
                w=ttk.Combobox(box,values=['Cash','Bank','Credit'],state='readonly',width=38);w.current(0);w.grid(row=i,column=1,padx=18,sticky='w',pady=7)
            elif l=='Customer / Supplier':
                w=SearchableCombobox(box,values=self.entities(),width=38)
                if self.entities():w.current(0)
                w.grid(row=i,column=1,padx=18,sticky='w',pady=7)
            else:
                w=ttk.Entry(box,width=40)
                if l=='Date':w.insert(0,date.today().isoformat())
                w.grid(row=i,column=1,padx=18,sticky='w',pady=7)
            self.f[l]=w
        actions=tk.Frame(box,bg='white');actions.grid(row=8,column=1,sticky='w',padx=18,pady=14)
        ttk.Button(actions,text='SAVE',style='Accent.TButton',command=self.save).pack(side='left')
        if self.mode=='purchase':
            ttk.Button(actions,text='IMPORT PURCHASE EXCEL',command=self.import_purchase).pack(side='left',padx=8)
            ttk.Button(actions,text='PURCHASE TEMPLATE',command=self.purchase_template).pack(side='left',padx=8)
    def products(self):
        con=get_connection();r=con.execute('SELECT id,name,cost_price,selling_price FROM products WHERE active=1 ORDER BY name').fetchall();con.close()
        return [f"{x['id']} - {x['name']} - {x['cost_price']:.2f}/{x['selling_price']:.2f}" for x in r]
    def entities(self):
        table='customers' if self.mode=='sale' else 'suppliers';con=get_connection();r=con.execute(f'SELECT id,name FROM {table} WHERE active=1 ORDER BY name').fetchall();con.close()
        return ['0 - Walk-in / None']+[f"{x['id']} - {x['name']}" for x in r]
    def refresh_products(self,select_id=None):
        values=self.products();self.product_combo.set_values(values)
        if select_id is not None:
            for i,v in enumerate(values):
                if int(v.split(' - ')[0])==select_id:self.product_combo.current(i);break
        elif values and self.product_combo.get() not in values:self.product_combo.current(0)
    def add_product_dialog(self):
        win=tk.Toplevel(self);win.title('Add New Product');win.geometry('620x560');win.configure(bg=COLORS['bg']);win.transient(self.winfo_toplevel());win.grab_set()
        box=Card(win,padx=20,pady=20);box.pack(fill='both',expand=True,padx=15,pady=15);fields={}
        specs=[('SKU / Barcode','sku',''),('Product Name','name',''),('Category','category',''),('Brand','brand',''),('Unit','unit','pcs'),('Cost Price','cost',''),('Selling Price','selling',''),('Reorder Level','reorder','0')]
        for i,(lab,key,default) in enumerate(specs):
            tk.Label(box,text=lab,bg='white',font=(FONT,9,'bold')).grid(row=i,column=0,sticky='w',pady=7);e=ttk.Entry(box,width=42);e.insert(0,default);e.grid(row=i,column=1,padx=15,pady=7);fields[key]=e
        def save():
            try:
                name=fields['name'].get().strip()
                if not name:raise ValueError('Product Name is required.')
                sku=fields['sku'].get().strip();cost=float(fields['cost'].get().replace(',','') or 0);selling=float(fields['selling'].get().replace(',','') or 0);reorder=float(fields['reorder'].get().replace(',','') or 0)
                con=get_connection()
                if sku and con.execute('SELECT id FROM products WHERE sku=?',(sku,)).fetchone():con.close();raise ValueError('This SKU / Barcode already exists.')
                con.close()
                add_product(sku,name,fields['category'].get().strip(),fields['brand'].get().strip(),fields['unit'].get().strip() or 'pcs',cost,selling,reorder)
                con=get_connection();row=con.execute('SELECT id FROM products WHERE sku=?',(sku,)).fetchone() if sku else con.execute('SELECT id FROM products WHERE lower(name)=lower(?) ORDER BY id DESC LIMIT 1',(name,)).fetchone();con.close();pid=row['id']
                self.refresh_products(pid);win.destroy();messagebox.showinfo('Saved','Product added. It is now available in the purchase list.')
            except Exception as e:messagebox.showerror('Product Error',str(e),parent=win)
        btn=tk.Frame(win,bg=COLORS['bg']);btn.pack(fill='x',padx=15,pady=(0,15));ttk.Button(btn,text='SAVE PRODUCT',style='Accent.TButton',command=save).pack(side='right');ttk.Button(btn,text='CANCEL',command=win.destroy).pack(side='right',padx=8)
    def save(self):
        try:
            p=self.f['Product'].get();
            if not p:raise ValueError('Select a product.')
            pid=int(p.split(' - ')[0]);qty=float(self.f['Qty'].get());unit=float(self.f['Unit Price / Cost'].get());pay=self.f['Payment Type'].get();ent=self.f['Customer / Supplier'].get();eid=int(ent.split(' - ')[0]) if ent else 0;paid=float(self.f['Paid'].get() or 0)
            con=get_connection();pr=con.execute('SELECT cost_price,selling_price FROM products WHERE id=?',(pid,)).fetchone();con.close()
            if self.mode=='sale':
                price=unit or pr['selling_price'];cost=pr['cost_price'];create_sale(self.f['Date'].get(),self.f['Invoice / Bill No'].get(),eid or None,pay,[(pid,qty,price,cost)],paid)
            else:
                cost=unit;create_purchase(self.f['Date'].get(),self.f['Invoice / Bill No'].get(),eid or None,pay,[(pid,qty,cost)],paid)
            messagebox.showinfo('Saved','Transaction saved. Stock and accounting updated.')
            if self.on_saved:self.on_saved()
        except Exception as e:messagebox.showerror('Error',str(e))
    def import_purchase(self):
        path=filedialog.askopenfilename(title='Select Purchase Excel',filetypes=[('Excel Workbook','*.xlsx'),('All Files','*.*')])
        if not path:return
        try:
            records,grouped,preview=import_purchase_excel(path)
            total=sum(x[5] for x in preview);bills=len(preview);lines=len(records)
            text=f'Purchase Excel detected.\n\nBills: {bills}\nProduct lines: {lines}\nTotal purchase value: Rs. {total:,.2f}\n\nExisting products are matched by SKU/Barcode or Product Name. Missing products are created from the Excel data.\n\nImport these purchases?'
            if not messagebox.askyesno('Purchase Import Preview',text):return
            imported,created=commit_purchase_import(records,grouped)
            messagebox.showinfo('Purchase Import',f'Imported successfully.\n\nPurchase bills: {imported}\nNew products created: {created}')
            if self.on_saved:self.on_saved()
        except Exception as e:messagebox.showerror('Purchase Import Error',str(e))
    def purchase_template(self):
        try:
            path=filedialog.asksaveasfilename(title='Save Purchase Excel Template',defaultextension='.xlsx',filetypes=[('Excel Workbook','*.xlsx')],initialfile='purchase_import_template.xlsx')
            if not path:return
            create_purchase_template(path);messagebox.showinfo('Template','Purchase Excel template created.')
        except Exception as e:messagebox.showerror('Template Error',str(e))
