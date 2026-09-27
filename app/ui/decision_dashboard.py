
import tkinter as tk
from tkinter import ttk
from app.accounting.analytics import kpis,monthly_sales

class DecisionDashboardFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7"); self.build()

    def build(self):
        tk.Label(self,text="Management Decision Dashboard",bg="#eef2f7",
                 fg="#102f4f",font=("Segoe UI",24,"bold")).pack(anchor="w")
        tk.Label(self,text="Use the figures below to review cash, working capital, stock and profitability.",
                 bg="#eef2f7",fg="#647586").pack(anchor="w",pady=(4,15))

        k=kpis()
        grid=tk.Frame(self,bg="#eef2f7");grid.pack(fill="x")
        cards=[
          ("SALES",k["sales"]),("NET PROFIT",k["profit"]),
          ("RECEIVABLES",k["receivables"]),("PAYABLES",k["payables"]),
          ("INVENTORY",k["inventory"]),("TOTAL ASSETS",k["assets"])
        ]
        for i,(title,val) in enumerate(cards):
            c=tk.Frame(grid,bg="white",highlightbackground="#d4dde6",highlightthickness=1)
            c.grid(row=i//3,column=i%3,sticky="nsew",padx=5,pady=5,ipadx=15,ipady=13)
            tk.Label(c,text=title,bg="white",fg="#718096",font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(c,text=f"Rs. {val:,.2f}",bg="white",fg="#102f4f",
                     font=("Segoe UI",17,"bold")).pack(anchor="w",pady=(4,0))
        for i in range(3):grid.columnconfigure(i,weight=1)

        lower=tk.Frame(self,bg="#eef2f7");lower.pack(fill="both",expand=True,pady=15)

        alerts=tk.Frame(lower,bg="white",padx=18,pady=18);alerts.pack(side="left",fill="both",expand=True,padx=(0,8))
        tk.Label(alerts,text="Alerts / Attention",bg="white",fg="#102f4f",
                 font=("Segoe UI",13,"bold")).pack(anchor="w")
        alert_lines=[]
        if k["low_stock"]>0: alert_lines.append(f"{k['low_stock']} product(s) at or below reorder level.")
        if k["receivables"]>0: alert_lines.append(f"Customer receivables outstanding: Rs. {k['receivables']:,.2f}")
        if k["payables"]>0: alert_lines.append(f"Supplier payables outstanding: Rs. {k['payables']:,.2f}")
        if k["profit"]<0: alert_lines.append("Current accounting result is a loss.")
        if not alert_lines: alert_lines.append("No current alerts from the available accounting data.")
        for line in alert_lines:
            tk.Label(alerts,text="• "+line,bg="white",fg="#425466",
                     font=("Segoe UI",10),wraplength=430,justify="left").pack(anchor="w",pady=7)

        trend=tk.Frame(lower,bg="white",padx=18,pady=18);trend.pack(side="right",fill="both",expand=True,padx=(8,0))
        tk.Label(trend,text="Monthly Sales / COGS",bg="white",fg="#102f4f",
                 font=("Segoe UI",13,"bold")).pack(anchor="w")
        cols=("Month","Sales","COGS","Gross Profit")
        tree=ttk.Treeview(trend,columns=cols,show="headings",height=8)
        for c in cols:tree.heading(c,text=c);tree.column(c,width=120)
        tree.pack(fill="both",expand=True,pady=8)
        for r in monthly_sales():
            gp=r["sales"]-r["cogs"]
            tree.insert("","end",values=(r["month"],f"{r['sales']:,.2f}",f"{r['cogs']:,.2f}",f"{gp:,.2f}"))
