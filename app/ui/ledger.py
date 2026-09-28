import tkinter as tk
from tkinter import ttk, messagebox
from app.database import get_connection
from app.accounting.engine import update_manual_journal
from app.accounting.audit import audit
from app.ui.theme import COLORS, FONT
from app.ui.widgets import Card, tree_with_scrollbars, SearchableCombobox

class LedgerEditDialog(tk.Toplevel):
    def __init__(self, parent, journal_id):
        super().__init__(parent); self.title('Edit Journal Entry'); self.geometry('760x520'); self.configure(bg=COLORS['bg']); self.journal_id=journal_id; self.rows=[]
        con=get_connection(); entry=con.execute('SELECT * FROM journal_entries WHERE id=?',(journal_id,)).fetchone(); lines=con.execute('SELECT a.code,a.name,l.debit,l.credit FROM journal_lines l JOIN accounts a ON a.id=l.account_id WHERE l.journal_id=? ORDER BY l.id',(journal_id,)).fetchall(); accounts=con.execute('SELECT code,name FROM accounts WHERE active=1 ORDER BY code').fetchall(); con.close()
        if not entry: self.destroy(); return
        self.accounts=[f"{a['code']} - {a['name']}" for a in accounts]; self.map={f"{a['code']} - {a['name']}":a['code'] for a in accounts}
        top=Card(self,padx=18,pady=14); top.pack(fill='x',padx=14,pady=14)
        self.date=ttk.Entry(top,width=18); self.date.insert(0,entry['entry_date']); self.ref=ttk.Entry(top,width=25); self.ref.insert(0,entry['reference'] or ''); self.desc=ttk.Entry(top,width=45); self.desc.insert(0,entry['description'] or '')
        for i,(lab,w) in enumerate([('Date',self.date),('Reference',self.ref),('Description',self.desc)]): tk.Label(top,text=lab,bg='white',font=(FONT,9,'bold')).grid(row=0,column=i,sticky='w',padx=5); w.grid(row=1,column=i,padx=5,pady=5)
        box=Card(self,padx=12,pady=12); box.pack(fill='both',expand=True,padx=14)
        tk.Label(box,text='Account',bg='white',font=(FONT,9,'bold')).grid(row=0,column=0,sticky='w'); tk.Label(box,text='Debit',bg='white',font=(FONT,9,'bold')).grid(row=0,column=1); tk.Label(box,text='Credit',bg='white',font=(FONT,9,'bold')).grid(row=0,column=2)
        self.lines_frame=tk.Frame(box,bg='white'); self.lines_frame.grid(row=1,column=0,columnspan=3,sticky='nsew'); box.rowconfigure(1,weight=1); box.columnconfigure(0,weight=1)
        for l in lines:self.add_line(l['code'],l['debit'],l['credit'])
        btns=tk.Frame(self,bg=COLORS['bg']); btns.pack(fill='x',padx=14,pady=12)
        ttk.Button(btns,text='+ ADD LINE',command=lambda:self.add_line()).pack(side='left'); ttk.Button(btns,text='SAVE CHANGES',style='Accent.TButton',command=self.save).pack(side='right'); ttk.Button(btns,text='CANCEL',command=self.destroy).pack(side='right',padx=8)
    def add_line(self,code='',debit=0,credit=0):
        row=tk.Frame(self.lines_frame,bg='white'); row.pack(fill='x',pady=3)
        account=SearchableCombobox(row,values=self.accounts,width=38);
        if code:
            match=[x for x in self.accounts if x.startswith(code+' - ')];
            if match: account.set(match[0])
        d=ttk.Entry(row,width=18); c=ttk.Entry(row,width=18); d.insert(0,str(debit or '')); c.insert(0,str(credit or ''))
        account.pack(side='left',padx=4); d.pack(side='left',padx=4); c.pack(side='left',padx=4)
        ttk.Button(row,text='REMOVE',command=lambda:r.destroy()).pack(side='left',padx=4)
        r={'frame':row,'account':account,'debit':d,'credit':c}; self.rows.append(r)
    def save(self):
        try:
            lines=[]
            for r in self.rows:
                if not r['frame'].winfo_exists(): continue
                label=r['account'].get().strip();
                if not label: continue
                d=float(r['debit'].get().replace(',','') or 0); c=float(r['credit'].get().replace(',','') or 0)
                if d<0 or c<0: raise ValueError('Debit/Credit cannot be negative.')
                if d and c: raise ValueError('A line cannot contain both Debit and Credit.')
                lines.append((self.map[label],d,c))
            if len(lines)<2: raise ValueError('At least two journal lines are required.')
            update_manual_journal(self.journal_id,self.date.get().strip(),self.ref.get().strip(),self.desc.get().strip(),lines)
            audit('JOURNAL_EDIT',self.ref.get().strip(),f'Journal entry {self.journal_id} edited')
            messagebox.showinfo('Saved','Journal entry updated successfully.'); self.destroy()
        except Exception as e: messagebox.showerror('Edit Error',str(e))

class LedgerFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg=COLORS['bg']); self.build()
    def build(self):
        tk.Label(self,text='General Ledger',bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,22,'bold')).pack(anchor='w')
        tk.Label(self,text='Double-click an entry to inspect it. Use Edit for eligible manual entries.',bg=COLORS['bg'],fg=COLORS['muted'],font=(FONT,9)).pack(anchor='w',pady=(2,10))
        box=Card(self,padx=12,pady=12); box.pack(fill='both',expand=True)
        cols=('ID','Date','Reference','Description','Account','Debit','Credit','Source')
        frame,self.tree=tree_with_scrollbars(box,cols,{'ID':55,'Date':105,'Reference':140,'Description':210,'Account':220,'Debit':120,'Credit':120,'Source':120},height=18); frame.pack(fill='both',expand=True)
        actions=tk.Frame(self,bg='white'); actions.pack(fill='x',pady=(10,0))
        ttk.Button(actions,text='✎ EDIT SELECTED',style='Accent.TButton',command=self.edit_selected).pack(side='right'); ttk.Button(actions,text='↻ REFRESH',command=self.refresh).pack(side='right',padx=8)
        self.tree.bind('<Double-1>',lambda e:self.edit_selected()); self.refresh()
    def refresh(self):
        for x in self.tree.get_children():self.tree.delete(x)
        con=get_connection(); rows=con.execute("""SELECT j.id,j.entry_date,j.reference,j.description,j.source_type,a.code||' - '||a.name account,l.debit,l.credit
        FROM journal_entries j JOIN journal_lines l ON j.id=l.journal_id JOIN accounts a ON a.id=l.account_id ORDER BY j.entry_date,j.id,l.id""").fetchall(); con.close()
        for r in rows:self.tree.insert('','end',values=(r['id'],r['entry_date'],r['reference'] or '',r['description'],r['account'],f"Rs. {r['debit']:,.2f}" if r['debit'] else '',f"Rs. {r['credit']:,.2f}" if r['credit'] else '',r['source_type']))
    def edit_selected(self):
        sel=self.tree.selection()
        if not sel:return
        jid=int(self.tree.item(sel[0])['values'][0]); src=self.tree.item(sel[0])['values'][7]
        if src=='OPENING': messagebox.showinfo('Opening Balance','Opening balances should be corrected from the Opening Balances screen.'); return
        dlg=LedgerEditDialog(self,jid); self.wait_window(dlg); self.refresh()
