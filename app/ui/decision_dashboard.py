import tkinter as tk
from app.accounting.analytics import kpis, monthly_sales
from app.ui.theme import COLORS, FONT
from app.ui.widgets import Card, StatCard, MiniBarChart, tree_with_scrollbars

class DecisionDashboardFrame(tk.Frame):
    def __init__(self,master): super().__init__(master,bg=COLORS['bg']); self.build()
    def build(self):
        tk.Label(self,text='Management Decision Dashboard',bg=COLORS['bg'],fg=COLORS['text'],font=(FONT,24,'bold')).pack(anchor='w')
        tk.Label(self,text='A visual overview of sales, profit, working capital, stock and business attention points.',bg=COLORS['bg'],fg=COLORS['muted'],font=(FONT,9)).pack(anchor='w',pady=(2,14))
        k=kpis(); cards=[('Sales',k['sales'],'▣',COLORS['success']),('Net Profit',k['profit'],'▥',COLORS['blue']),('Receivables',k['receivables'],'●',COLORS['warning']),('Payables',k['payables'],'●',COLORS['danger']),('Inventory',k['inventory'],'□','#159a9a'),('Total Assets',k['assets'],'◉','#7c5cff')]
        grid=tk.Frame(self,bg=COLORS['bg']); grid.pack(fill='x');
        for i,(t,v,ic,ac) in enumerate(cards):
            c=StatCard(grid,t,f"Rs. {v:,.2f}",ic,ac); c.grid(row=i//3,column=i%3,sticky='nsew',padx=5,pady=5)
        for i in range(3):grid.columnconfigure(i,weight=1)
        monthly=monthly_sales(); data=[{'label':r['month'],'sales':r['sales'],'cogs':r['cogs'],'profit':r['sales']-r['cogs']} for r in monthly]
        row=tk.Frame(self,bg=COLORS['bg']); row.pack(fill='both',expand=True,pady=10)
        chart=MiniBarChart(row,'Monthly Sales / COGS / Gross Profit',data,series=('sales','cogs','profit'),labels=[d['label'] for d in data],height=250); chart.pack(side='left',fill='both',expand=True,padx=(0,6))
        alerts=Card(row,padx=16,pady=14); alerts.pack(side='right',fill='both',expand=True,padx=(6,0))
        tk.Label(alerts,text='Alerts & Attention',bg='white',fg=COLORS['text'],font=(FONT,13,'bold')).pack(anchor='w')
        alert_lines=[]
        if k['low_stock']: alert_lines.append((COLORS['warning'],f"{k['low_stock']} product(s) are at or below reorder level."))
        if k['receivables']>0: alert_lines.append((COLORS['warning'],f"Receivables outstanding: Rs. {k['receivables']:,.2f}"))
        if k['payables']>0: alert_lines.append((COLORS['danger'],f"Payables outstanding: Rs. {k['payables']:,.2f}"))
        if k['profit']<0: alert_lines.append((COLORS['danger'],'Current result is a loss.'))
        if not alert_lines: alert_lines=[(COLORS['success'],'No current alerts from the available accounting data.')]
        for color,text in alert_lines:
            f=tk.Frame(alerts,bg='white'); f.pack(fill='x',pady=7); tk.Label(f,text='●',bg='white',fg=color,font=(FONT,10,'bold')).pack(side='left',padx=(0,8)); tk.Label(f,text=text,bg='white',fg=COLORS['text'],font=(FONT,9),wraplength=420,justify='left').pack(side='left',anchor='w')
        recent=Card(self,padx=12,pady=12); recent.pack(fill='both',expand=True,pady=(4,0)); tk.Label(recent,text='Recent Transactions',bg='white',fg=COLORS['text'],font=(FONT,13,'bold')).pack(anchor='w',pady=(0,8))
        from app.database import get_connection
        con=get_connection(); rows=con.execute('SELECT event_time,event_type,reference,description FROM audit_log ORDER BY id DESC LIMIT 10').fetchall(); con.close()
        frame,tree=tree_with_scrollbars(recent,('Time','Type','Reference','Description'),{'Time':150,'Type':150,'Reference':180,'Description':500},height=7); frame.pack(fill='both',expand=True)
        for r in rows:tree.insert('','end',values=(r['event_time'],r['event_type'],r['reference'] or '',r['description'] or ''))
