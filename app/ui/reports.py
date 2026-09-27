import tkinter as tk
from tkinter import ttk
from app.database import get_connection
from app.ui.theme import COLORS, FONT
from app.ui.widgets import Card, MiniBarChart, tree_with_scrollbars

def rows():
    con=get_connection(); r=con.execute("""SELECT a.code,a.name,a.account_type,COALESCE(SUM(l.debit),0) debit,COALESCE(SUM(l.credit),0) credit FROM accounts a LEFT JOIN journal_lines l ON a.id=l.account_id GROUP BY a.id ORDER BY a.code""").fetchall(); con.close(); return r

class TrialBalanceFrame(tk.Frame):
    def __init__(self,m):
        super().__init__(m,bg=COLORS['bg']); tk.Label(self,text='Trial Balance',bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,22,'bold')).pack(anchor='w')
        tk.Label(self,text='Account balances and visual debit/credit overview.',bg=COLORS['bg'],fg=COLORS['muted'],font=(FONT,9)).pack(anchor='w',pady=(2,10))
        rs=rows(); data=[]; td=tc=0
        for r in rs:
            x=r['debit']-r['credit']; d=max(x,0); c=max(-x,0)
            if d or c: td+=d; tc+=c; data.append({'label':r['code'],'debit':d,'credit':c})
        chart=MiniBarChart(self,'Debit vs Credit by Account',data,series=('debit','credit'),labels=[f"{x['label']}" for x in data],height=220); chart.pack(fill='x',pady=(0,10))
        box=Card(self,padx=10,pady=10); box.pack(fill='both',expand=True)
        frame,t=tree_with_scrollbars(box,('Code','Account','Debit','Credit'),{'Code':90,'Account':300,'Debit':180,'Credit':180},height=12); frame.pack(fill='both',expand=True)
        for r in rs:
            x=r['debit']-r['credit']; d=max(x,0); c=max(-x,0)
            if d or c:t.insert('','end',values=(r['code'],r['name'],f'Rs. {d:,.2f}',f'Rs. {c:,.2f}'))
        tk.Label(self,text=f'DEBIT  Rs. {td:,.2f}     CREDIT  Rs. {tc:,.2f}     CHECK  Rs. {td-tc:,.2f}',bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,10,'bold')).pack(anchor='e',pady=8)

class PnLFrame(tk.Frame):
    def __init__(self,m):
        super().__init__(m,bg=COLORS['bg']); rs=rows(); rev=sum(r['credit']-r['debit'] for r in rs if r['account_type']=='Revenue'); exp=sum(r['debit']-r['credit'] for r in rs if r['account_type']=='Expense'); profit=rev-exp
        tk.Label(self,text='Profit & Loss',bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,22,'bold')).pack(anchor='w')
        chart=MiniBarChart(self,'Revenue, Expenses & Net Profit',[{'label':'Revenue','value':rev},{'label':'Expenses','value':exp},{'label':'Net Profit','value':profit}],series=('value',),height=220); chart.pack(fill='x',pady=(10,12))
        b=Card(self,padx=25,pady=20); b.pack(fill='x')
        for x,v in [('Revenue',rev),('Expenses',exp),('NET PROFIT',profit)]: tk.Label(b,text=f'{x}: Rs. {v:,.2f}',bg='white',fg=COLORS['text'] if x!='NET PROFIT' else (COLORS['success'] if v>=0 else COLORS['danger']),font=(FONT,14,'bold')).pack(anchor='w',pady=7)

class BalanceSheetFrame(tk.Frame):
    def __init__(self,m):
        super().__init__(m,bg=COLORS['bg']); rs=rows(); assets=sum(r['debit']-r['credit'] for r in rs if r['account_type']=='Asset'); liab=sum(r['credit']-r['debit'] for r in rs if r['account_type']=='Liability'); eq=sum(r['credit']-r['debit'] for r in rs if r['account_type']=='Equity'); profit=sum(r['credit']-r['debit'] for r in rs if r['account_type']=='Revenue')-sum(r['debit']-r['credit'] for r in rs if r['account_type']=='Expense'); total_le=liab+eq+profit; check=assets-total_le
        tk.Label(self,text='Balance Sheet',bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,22,'bold')).pack(anchor='w')
        chart=MiniBarChart(self,'Assets vs Liabilities & Equity',[{'label':'Assets','value':assets},{'label':'Liabilities','value':liab},{'label':'Equity + Profit','value':eq+profit}],series=('value',),height=220); chart.pack(fill='x',pady=(10,12))
        b=Card(self,padx=25,pady=20); b.pack(fill='x')
        vals=[('TOTAL ASSETS',assets),('LIABILITIES',liab),('EQUITY',eq),('CURRENT PROFIT',profit),('LIABILITIES + EQUITY',total_le),('BALANCE CHECK',check)]
        for x,v in vals: tk.Label(b,text=f'{x}: Rs. {v:,.2f}',bg='white',fg=COLORS['danger'] if x=='BALANCE CHECK' and abs(v)>0.01 else COLORS['text'],font=(FONT,13,'bold')).pack(anchor='w',pady=6)
