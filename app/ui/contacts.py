import tkinter as tk
from tkinter import ttk,messagebox
from app.database import get_connection
from app.accounting.audit import audit
from app.ui.theme import COLORS, FONT
from app.ui.widgets import Card, tree_with_scrollbars

class ContactEditDialog(tk.Toplevel):
    def __init__(self,parent,row,mode):
        super().__init__(parent); self.mode=mode;self.row=row;self.title(('Customer' if mode=='customer' else 'Supplier')+' Edit');self.geometry('620x330');self.configure(bg=COLORS['bg'])
        box=Card(self,padx=18,pady=18);box.pack(fill='both',expand=True,padx=15,pady=15);self.e={}
        for i,(lab,key) in enumerate([('Name','name'),('Phone','phone'),('Address','address'),('Credit Limit','credit_limit')]):
            tk.Label(box,text=lab,bg='white',font=(FONT,9,'bold')).grid(row=i,column=0,sticky='w',pady=7);e=ttk.Entry(box,width=48);e.insert(0,str(row[key] or ''));e.grid(row=i,column=1,padx=12,pady=7);self.e[key]=e
        btn=tk.Frame(self,bg=COLORS['bg']);btn.pack(fill='x',padx=15,pady=(0,15));ttk.Button(btn,text='SAVE CHANGES',style='Accent.TButton',command=self.save).pack(side='right');ttk.Button(btn,text='CANCEL',command=self.destroy).pack(side='right',padx=8)
    def save(self):
        try:
            name=self.e['name'].get().strip();limit=float(self.e['credit_limit'].get().replace(',','') or 0)
            if not name:raise ValueError('Name is required.')
            table='customers' if self.mode=='customer' else 'suppliers';con=get_connection();con.execute(f'UPDATE {table} SET name=?,phone=?,address=?,credit_limit=? WHERE id=?',(name,self.e['phone'].get().strip(),self.e['address'].get().strip(),limit,self.row['id']));con.commit();con.close();audit(('CUSTOMER' if self.mode=='customer' else 'SUPPLIER')+'_EDIT',str(self.row['id']),f'{self.mode.title()} edited: {name}');messagebox.showinfo('Saved','Details updated successfully.');self.destroy()
        except Exception as e:messagebox.showerror('Edit Error',str(e))

class ContactsFrame(tk.Frame):
    def __init__(self, master, mode='customer', on_change=None):super().__init__(master,bg=COLORS['bg']);self.mode=mode;self.on_change=on_change;self.build()
    def build(self):
        title='Customers' if self.mode=='customer' else 'Suppliers';table='customers' if self.mode=='customer' else 'suppliers'
        tk.Label(self,text=title,bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,22,'bold')).pack(anchor='w',pady=(0,12))
        top=Card(self,padx=18,pady=16);top.pack(fill='x');self.name=ttk.Entry(top,width=32);self.phone=ttk.Entry(top,width=20);self.address=ttk.Entry(top,width=38);self.limit=ttk.Entry(top,width=15)
        for i,(lab,w) in enumerate([('Name',self.name),('Phone',self.phone),('Address',self.address),('Credit Limit',self.limit)]):tk.Label(top,text=lab,bg='white',font=('Segoe UI',9,'bold')).grid(row=0,column=i,sticky='w',padx=5);w.grid(row=1,column=i,padx=5,pady=5)
        ttk.Button(top,text=f'ADD {title[:-1].upper()}',command=lambda:self.add(table)).grid(row=1,column=4,padx=10)
        box=Card(self,padx=12,pady=12);box.pack(fill='both',expand=True,pady=12);cols=('ID','Name','Phone','Address','Credit Limit','Outstanding','Status');frame,self.tree=tree_with_scrollbars(box,cols,{'ID':60,'Name':220,'Phone':140,'Address':260,'Credit Limit':160,'Outstanding':160,'Status':90},height=15);frame.pack(fill='both',expand=True)
        actions=tk.Frame(self,bg=COLORS['bg']);actions.pack(fill='x',pady=(0,10));ttk.Button(actions,text='EDIT SELECTED',command=self.edit_selected).pack(side='right');ttk.Button(actions,text='DEACTIVATE SELECTED',command=self.deactivate).pack(side='right',padx=8);ttk.Button(actions,text='DELETE SELECTED',command=self.delete_selected).pack(side='right',padx=8);ttk.Button(actions,text='REFRESH',command=self.refresh).pack(side='right')
        self.refresh()
    def add(self,table):
        try:
            name=self.name.get().strip()
            if not name:raise ValueError('Name is required.')
            limit=float(self.limit.get().replace(',','') or 0);con=get_connection();con.execute(f'INSERT INTO {table}(name,phone,address,credit_limit) VALUES(?,?,?,?)',(name,self.phone.get().strip(),self.address.get().strip(),limit));con.commit();con.close();audit(('CUSTOMER' if self.mode=='customer' else 'SUPPLIER')+'_ADD',name,f'{self.mode.title()} added: {name}')
            for w in [self.name,self.phone,self.address,self.limit]:w.delete(0,'end')
            self.refresh()
            if self.on_change:self.on_change()
        except Exception as e:messagebox.showerror('Error',str(e))
    def refresh(self):
        for x in self.tree.get_children():self.tree.delete(x)
        table='customers' if self.mode=='customer' else 'suppliers';con=get_connection();rows=con.execute(f'SELECT * FROM {table} ORDER BY active DESC,name').fetchall()
        for r in rows:
            if self.mode=='customer':b=con.execute('SELECT COALESCE(SUM(debit-credit),0) b FROM receivable_entries WHERE customer_id=?',(r['id'],)).fetchone()['b']
            else:b=con.execute('SELECT COALESCE(SUM(credit-debit),0) b FROM payable_entries WHERE supplier_id=?',(r['id'],)).fetchone()['b']
            self.tree.insert('','end',values=(r['id'],r['name'],r['phone'] or '',r['address'] or '',f"Rs. {r['credit_limit']:,.2f}",f"Rs. {b:,.2f}",'ACTIVE' if r['active'] else 'INACTIVE'))
        con.close()
    def selected(self):
        sel=self.tree.selection()
        if not sel:return None
        rid=int(self.tree.item(sel[0])['values'][0]);table='customers' if self.mode=='customer' else 'suppliers';con=get_connection();r=con.execute(f'SELECT * FROM {table} WHERE id=?',(rid,)).fetchone();con.close();return r
    def edit_selected(self):
        r=self.selected()
        if not r:return
        if not r['active']:messagebox.showinfo('Inactive','This record is inactive.');return
        dlg=ContactEditDialog(self,r,self.mode);self.wait_window(dlg);self.refresh()
    def delete_selected(self):
        r=self.selected()
        if not r:return
        table='customers' if self.mode=='customer' else 'suppliers'
        try:
            con=get_connection()
            linked_table='receivable_entries' if self.mode=='customer' else 'payable_entries'
            linked=con.execute(f'SELECT COUNT(*) n FROM {linked_table} WHERE {"customer_id" if self.mode=="customer" else "supplier_id"}=?',(r['id'],)).fetchone()['n']
            trade='sales' if self.mode=='customer' else 'purchases'; key='customer_id' if self.mode=='customer' else 'supplier_id'
            linked += con.execute(f'SELECT COUNT(*) n FROM {trade} WHERE {key}=?',(r['id'],)).fetchone()['n'];con.close()
            if linked:
                messagebox.showinfo('Cannot Delete','This record has transaction history. Use DEACTIVATE instead so history is preserved.');return
            if not messagebox.askyesno('Delete',f'Delete {r["name"]}? This cannot be undone.'):return
            con=get_connection();con.execute(f'DELETE FROM {table} WHERE id=?',(r['id'],));con.commit();con.close();audit(('CUSTOMER' if self.mode=='customer' else 'SUPPLIER')+'_DELETE',str(r['id']),f'{self.mode.title()} deleted: {r["name"]}');self.refresh()
        except Exception as e:messagebox.showerror('Delete Error',str(e))
    def deactivate(self):
        r=self.selected()
        if not r:return
        if not messagebox.askyesno('Deactivate',f'Deactivate {r["name"]}?\n\nExisting transactions will be preserved.'):return
        table='customers' if self.mode=='customer' else 'suppliers';con=get_connection();con.execute(f'UPDATE {table} SET active=0 WHERE id=?',(r['id'],));con.commit();con.close();audit(('CUSTOMER' if self.mode=='customer' else 'SUPPLIER')+'_DEACTIVATE',str(r['id']),f'{self.mode.title()} deactivated: {r["name"]}');self.refresh()
