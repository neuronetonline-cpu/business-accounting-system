import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date
from app.ui.theme import COLORS, FONT
from app.ui.widgets import Card, tree_with_scrollbars
from app.database import get_connection
from app.accounting.pos_import import parse_sales_pdf, import_sales, import_opening_stock_xlsx, opening_stock_value
from app.accounting.engine import create_opening_balance, get_latest_opening, update_opening_balance
from app.accounting.audit import audit

class POSImportFrame(tk.Frame):
    def __init__(self, master, on_saved=None):
        super().__init__(master,bg=COLORS['bg']); self.on_saved=on_saved; self.parsed=[]; self.build()
    def build(self):
        tk.Label(self,text='POS Import Center',bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,24,'bold')).pack(anchor='w')
        tk.Label(self,text='Prepare the opening position and import POS sales without entering bills one by one.',bg=COLORS['bg'],fg=COLORS['muted'],font=(FONT,9)).pack(anchor='w',pady=(2,12))
        nb=ttk.Notebook(self); nb.pack(fill='both',expand=True)
        self.opening_tab=tk.Frame(nb,bg=COLORS['bg']); self.sales_tab=tk.Frame(nb,bg=COLORS['bg']); nb.add(self.opening_tab,text='  Opening Position  '); nb.add(self.sales_tab,text='  POS Sales Import  ')
        self.build_opening(); self.build_sales()

    def build_opening(self):
        top=Card(self.opening_tab,padx=16,pady=14); top.pack(fill='x',pady=(0,10))
        tk.Label(top,text='Opening Date',bg='white',font=(FONT,9,'bold')).grid(row=0,column=0,sticky='w')
        self.odate=ttk.Entry(top,width=16); self.odate.insert(0,'2026-08-31'); self.odate.grid(row=1,column=0,padx=(0,10),pady=5)
        ttk.Button(top,text='IMPORT OPENING STOCK EXCEL',style='Accent.TButton',command=self.import_stock).grid(row=1,column=1,padx=6)
        ttk.Button(top,text='REFRESH',command=self.refresh_opening).grid(row=1,column=2,padx=6)
        self.stock_label=tk.Label(top,text='Opening stock: Rs. 0.00',bg='white',fg=COLORS['blue'],font=(FONT,10,'bold')); self.stock_label.grid(row=1,column=3,padx=18)

        body=Card(self.opening_tab,padx=16,pady=14); body.pack(fill='both',expand=True)
        tk.Label(body,text='Opening Position',bg='white',fg=COLORS['text'],font=(FONT,13,'bold')).pack(anchor='w')
        tk.Label(body,text='Cash, active bank accounts and other opening balances. Inventory is imported from the POS stock Excel.',bg='white',fg=COLORS['muted'],font=(FONT,9)).pack(anchor='w',pady=(2,8))
        self.balance_frame=tk.Frame(body,bg='white'); self.balance_frame.pack(fill='both',expand=True,pady=(4,4)); self.balance_entries={}
        self.refresh_opening()

        bottom=Card(self.opening_tab,padx=16,pady=14); bottom.pack(fill='x',pady=(10,0))
        tk.Label(bottom,text='Opening Balance Notes',bg='white',fg=COLORS['text'],font=(FONT,10,'bold')).grid(row=0,column=0,sticky='w')
        tk.Label(bottom,text='You can leave unknown balances blank and add/correct them later from Opening Balances.',bg='white',fg=COLORS['muted'],font=(FONT,9)).grid(row=1,column=0,sticky='w',pady=(2,6))
        self.save_btn=ttk.Button(bottom,text='SAVE / UPDATE OPENING POSITION',style='Accent.TButton',command=self.save_opening); self.save_btn.grid(row=2,column=0,sticky='w',pady=8)
        self.opening_status=tk.Label(bottom,text='',bg='white',fg=COLORS['muted'],font=(FONT,9)); self.opening_status.grid(row=2,column=1,padx=15,sticky='w')

    def refresh_opening(self):
        for w in self.balance_frame.winfo_children(): w.destroy()
        self.balance_entries={}
        con=get_connection()
        banks=con.execute("SELECT ledger_code,name FROM bank_accounts WHERE active=1 ORDER BY name").fetchall()
        # Show the same accounting accounts used by the main Opening Balances screen,
        # while replacing generic Bank-Main/Bank-Other with real bank accounts.
        base=con.execute("SELECT code,name FROM accounts WHERE account_type IN ('Asset','Liability','Equity') ORDER BY CAST(code AS INTEGER), code").fetchall()
        con.close()

        rows=[]
        for r in base:
            code=r['code']; name=r['name']
            if code == '1000':
                rows.append((code,name,'editable'))
            elif code in ('1010','1020'):
                # Real bank accounts are shown below instead of generic bank buckets.
                if not banks and code == '1010': rows.append((code,name,'editable'))
            elif code == '1200':
                rows.append((code,name,'stock'))
            else:
                rows.append((code,name,'editable'))
        # Add all actual bank accounts from Banks & Cash.
        bank_rows=[(r['ledger_code'],f"Bank - {r['name']}",'editable') for r in banks]
        # Put Cash first, then actual banks, then other accounting balances.
        cash=[r for r in rows if r[0]=='1000']
        others=[r for r in rows if r[0] not in ('1000','1010','1020')]
        rows=cash+bank_rows+others

        for i,(code,label,kind) in enumerate(rows):
            col=i%3; rr=(i//3)*2
            tk.Label(self.balance_frame,text=f'{code}  {label}',bg='white',fg=COLORS['text'],font=(FONT,9,'bold')).grid(row=rr,column=col*2,sticky='w',padx=6,pady=(4,0))
            if kind=='stock':
                value=opening_stock_value(self.odate.get().strip())
                e=ttk.Entry(self.balance_frame,width=20); e.insert(0,f'{value:.2f}' if value else ''); e.configure(state='readonly')
                e.grid(row=rr+1,column=col*2,padx=6,pady=(3,6),sticky='w')
            else:
                e=ttk.Entry(self.balance_frame,width=20); e.grid(row=rr+1,column=col*2,padx=6,pady=(3,6),sticky='w')
            self.balance_entries[code]=e
        self.stock_label.config(text=f'Opening stock: Rs. {opening_stock_value(self.odate.get().strip()):,.2f}')
    def import_stock(self):
        path=filedialog.askopenfilename(title='Select August 31 Opening Stock',filetypes=[('Excel','*.xlsx'),('All files','*.*')])
        if not path:return
        try:
            r=import_opening_stock_xlsx(path,self.odate.get().strip()); self.stock_label.config(text=f"Opening stock: Rs. {r['value']:,.2f}"); messagebox.showinfo('Opening Stock',f"Imported {r['count']} product rows.\nNew products: {r['created']}\nExisting products updated: {r['updated']}\nStock value: Rs. {r['value']:,.2f}")
        except Exception as e: messagebox.showerror('Opening Stock Import',str(e))

    def save_opening(self):
        try:
            balances={}
            for code,e in self.balance_entries.items():
                v=e.get().replace(',','').strip()
                if v: balances[code]=float(v)
            sv=opening_stock_value(self.odate.get().strip())
            if sv: balances['1200']=sv
            if not balances: raise ValueError('Enter at least one opening balance or import opening stock.')
            latest=get_latest_opening()
            if latest and latest['entry_date']==self.odate.get().strip():
                update_opening_balance(latest['id'],self.odate.get().strip(),balances); audit('OPENING_POSITION_EDIT',str(latest['id']),'Opening position corrected')
                msg='Opening position updated.'
            else:
                create_opening_balance(self.odate.get().strip(),balances); audit('OPENING_POSITION_ADD',self.odate.get().strip(),'Opening position created'); msg='Opening position saved.'
            self.opening_status.config(text=msg); messagebox.showinfo('Opening Position',msg)
            if self.on_saved:self.on_saved()
        except Exception as e: messagebox.showerror('Opening Position',str(e))

    def build_sales(self):
        top=Card(self.sales_tab,padx=16,pady=14); top.pack(fill='x',pady=(0,10))
        ttk.Button(top,text='SELECT POS SALES PDF',style='Accent.TButton',command=self.select_pdf).pack(side='left')
        tk.Label(top,text='Bank account for POS Bank Transfer/Deposit:',bg='white',font=(FONT,9,'bold')).pack(side='left',padx=(20,6))
        self.bank_combo=ttk.Combobox(top,state='readonly',width=32); self.bank_combo.pack(side='left'); self.refresh_bank_choices()
        ttk.Button(top,text='IMPORT SELECTED',command=self.do_import).pack(side='left',padx=8)
        self.file_label=tk.Label(top,text='No PDF selected',bg='white',fg=COLORS['muted'],font=(FONT,8)); self.file_label.pack(side='right')
        box=Card(self.sales_tab,padx=10,pady=10); box.pack(fill='both',expand=True)
        cols=('Bill No','Date','Payment','Customer','Gross','Final Adj.','Net Total','Items','Status'); frame,self.tree=tree_with_scrollbars(box,cols,{'Bill No':100,'Date':90,'Payment':100,'Customer':190,'Gross':110,'Discount':100,'Net Total':110,'Items':70,'Status':260},height=18); frame.pack(fill='both',expand=True)
        self.summary=tk.Label(self.sales_tab,text='Select a PDF to preview transactions.',bg=COLORS['bg'],fg=COLORS['muted'],font=(FONT,9,'bold')); self.summary.pack(anchor='w',pady=8)

    def refresh_bank_choices(self):
        con=get_connection(); rows=con.execute("SELECT ledger_code,name FROM bank_accounts WHERE active=1 ORDER BY name").fetchall(); con.close()
        vals=[f"{r['ledger_code']} - {r['name']}" for r in rows]
        if not vals: vals=['1010 - Bank - Main']
        self.bank_combo['values']=vals; self.bank_combo.current(0)

    def select_pdf(self):
        path=filedialog.askopenfilename(title='Select POS Sales Report PDF',filetypes=[('PDF','*.pdf'),('All files','*.*')])
        if not path:return
        try:
            self.parsed=parse_sales_pdf(path); self.file_label.config(text=path.split('/')[-1])
            for x in self.tree.get_children(): self.tree.delete(x)
            unresolved=0
            for s in self.parsed:
                status='READY' if not s['unresolved'] else 'UNMATCHED: '+', '.join(s['unresolved'][:1])
                if s['unresolved']: unresolved+=1
                self.tree.insert('','end',values=(s['bill_no'],s['transaction_id'][:6],s['payment_type'],s.get('customer_name',''),f"{s['gross_total']:,.2f}",f"{s['final_discount']:,.2f}",f"{s['total']:,.2f}",len(s['items']),status))
            total=sum(s['total'] for s in self.parsed); self.summary.config(text=f"{len(self.parsed)} bills | Net total Rs. {total:,.2f} | Unmatched bills: {unresolved}")
        except Exception as e: messagebox.showerror('POS PDF',str(e))

    def do_import(self):
        if not self.parsed: messagebox.showwarning('POS Import','Select and preview a POS Sales PDF first.'); return
        bank=self.bank_combo.get().split(' - ')[0]
        bad=[s for s in self.parsed if s['unresolved']]
        if bad:
            messagebox.showwarning('POS Import',f"{len(bad)} bill(s) have unmatched products. Import was stopped. Import opening stock/products first, then preview the PDF again."); return
        if not messagebox.askyesno('Confirm POS Import',f'Import {len(self.parsed)} POS bills? Existing bill numbers will be skipped.'): return
        try:
            n,skipped,errors=import_sales(self.parsed,bank_code=bank)
            msg=f'Imported: {n}\nSkipped duplicates: {skipped}\nErrors: {len(errors)}'
            if errors: msg+='\n\n'+"\n".join(errors[:8])
            messagebox.showinfo('POS Import Result',msg)
            if self.on_saved:self.on_saved()
        except Exception as e: messagebox.showerror('POS Import',str(e))
