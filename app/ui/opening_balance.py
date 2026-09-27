import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.database import get_connection
from app.accounting.engine import create_opening_balance, get_latest_opening, update_opening_balance
from app.accounting.audit import audit
from app.ui.theme import COLORS, FONT
from app.ui.widgets import Card, tree_with_scrollbars

class OpeningBalanceFrame(tk.Frame):
    def __init__(self,master,on_saved=None):
        super().__init__(master,bg=COLORS['bg']); self.on_saved=on_saved; self.entries={}; self.build()
    def build(self):
        tk.Label(self,text='Opening Balances',bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,22,'bold')).pack(anchor='w')
        tk.Label(self,text='Start a new period or correct the latest opening balance without creating a duplicate entry.',bg=COLORS['bg'],fg=COLORS['muted'],font=(FONT,9)).pack(anchor='w',pady=(2,10))
        top=Card(self,padx=18,pady=14); top.pack(fill='x',pady=(0,12))
        tk.Label(top,text='Opening Date',bg='white',font=(FONT,9,'bold')).pack(side='left')
        self.date_entry=ttk.Entry(top,width=18); self.date_entry.insert(0,date.today().isoformat()); self.date_entry.pack(side='left',padx=10)
        ttk.Button(top,text='LOAD LAST OPENING',command=self.load_last).pack(side='left',padx=5)
        ttk.Button(top,text='SAVE NEW OPENING',style='Accent.TButton',command=self.save_new).pack(side='left',padx=5)
        ttk.Button(top,text='UPDATE LAST OPENING',command=self.update_last).pack(side='left',padx=5)
        self.last_label=tk.Label(top,text='Latest opening: None',bg='white',fg=COLORS['muted'],font=(FONT,9,'bold')); self.last_label.pack(side='right')
        body=Card(self,padx=18,pady=16); body.pack(fill='both',expand=True)
        cols=('Code','Account','Last Opening','Correction / New Value')
        frame,self.summary=tree_with_scrollbars(body,cols,{'Code':90,'Account':260,'Last Opening':180,'Correction / New Value':200},height=7); frame.pack(fill='x',pady=(0,14))
        form=tk.Frame(body,bg='white'); form.pack(fill='both',expand=True)
        con=get_connection(); accounts=con.execute("SELECT code,name FROM accounts WHERE account_type IN ('Asset','Liability','Equity') ORDER BY code").fetchall(); con.close()
        for i,a in enumerate(accounts):
            tk.Label(form,text=f"{a['code']}  {a['name']}",bg='white',fg=COLORS['text'],font=(FONT,9,'bold')).grid(row=i,column=0,sticky='w',pady=5)
            e=ttk.Entry(form,width=24); e.grid(row=i,column=1,padx=20,sticky='w',pady=5); self.entries[a['code']]=e
        self.latest=None; self.load_last()
    def load_last(self):
        self.latest=get_latest_opening();
        for e in self.entries.values(): e.delete(0,'end')
        for x in self.summary.get_children(): self.summary.delete(x)
        if not self.latest:
            self.last_label.config(text='Latest opening: None'); return
        self.last_label.config(text=f"Latest opening: {self.latest['entry_date']}  •  #{self.latest['id']}")
        con=get_connection(); types={r['code']:r['account_type'] for r in con.execute('SELECT code,account_type FROM accounts').fetchall()}; con.close()
        vals={}
        for l in self.latest['lines']:
            v=l['debit']-l['credit'] if types.get(l['code']) in ('Asset','Expense') else l['credit']-l['debit']; vals[l['code']]=v
        con=get_connection(); accounts=con.execute("SELECT code,name FROM accounts WHERE account_type IN ('Asset','Liability','Equity') ORDER BY code").fetchall(); con.close()
        for a in accounts:
            v=vals.get(a['code'],0); self.summary.insert('','end',values=(a['code'],a['name'],f'Rs. {v:,.2f}',f'Rs. {v:,.2f}'))
            if abs(v)>0.0001:self.entries[a['code']].insert(0,str(v))
    def _values(self):
        balances={c:float(e.get().replace(',','') or 0) for c,e in self.entries.items() if e.get().strip()}
        if not balances: raise ValueError('Enter at least one opening balance.')
        return balances
    def save_new(self):
        try:
            balances=self._values(); create_opening_balance(self.date_entry.get().strip(),balances); audit('OPENING_ADD',self.date_entry.get().strip(),'New opening balance posted'); messagebox.showinfo('Saved','New opening balance posted successfully.'); self.load_last();
            if self.on_saved:self.on_saved()
        except Exception as e:messagebox.showerror('Opening Balance Error',str(e))
    def update_last(self):
        try:
            if not self.latest: raise ValueError('There is no previous opening balance to update.')
            balances=self._values(); update_opening_balance(self.latest['id'],self.date_entry.get().strip(),balances); audit('OPENING_EDIT',str(self.latest['id']),'Latest opening balance corrected'); messagebox.showinfo('Updated','Latest opening balance corrected successfully.'); self.load_last();
            if self.on_saved:self.on_saved()
        except Exception as e:messagebox.showerror('Opening Balance Error',str(e))
