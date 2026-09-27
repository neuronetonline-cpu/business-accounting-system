
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date

APP_DIR = Path.home() / "BusinessAccountingSystem"
APP_DIR.mkdir(exist_ok=True)
DB = APP_DIR / "business.db"

ACCOUNTS = [
    ("1000","Cash","Asset"),("1010","Bank - Main","Asset"),
    ("1100","Accounts Receivable","Asset"),("1200","Inventory","Asset"),
    ("1300","Other Current Assets","Asset"),
    ("2000","Accounts Payable","Liability"),("2100","Other Payables","Liability"),
    ("3000","Owner Capital","Equity"),("3100","Owner Drawings","Equity"),
    ("4000","Sales Revenue","Revenue"),("4100","Other Income","Revenue"),
    ("5000","Cost of Goods Sold","Expense"),("5100","Rent Expense","Expense"),
    ("5200","Salary Expense","Expense"),("5300","Utilities Expense","Expense"),
    ("5400","Advertising Expense","Expense"),("5500","Delivery Expense","Expense"),
    ("5600","Other Expenses","Expense"),
]

def conn():
    return sqlite3.connect(DB)

def init_db():
    c=conn(); cur=c.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS accounts(
      id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, name TEXT, type TEXT, active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS journal(
      id INTEGER PRIMARY KEY AUTOINCREMENT, entry_date TEXT, ref TEXT, description TEXT);
    CREATE TABLE IF NOT EXISTS journal_lines(
      id INTEGER PRIMARY KEY AUTOINCREMENT, journal_id INTEGER, account_id INTEGER,
      debit REAL DEFAULT 0, credit REAL DEFAULT 0);
    """)
    for code,name,typ in ACCOUNTS:
        cur.execute("INSERT OR IGNORE INTO accounts(code,name,type) VALUES(?,?,?)",(code,name,typ))
    c.commit(); c.close()

def money(x): return f"Rs. {x:,.2f}"

def balances():
    c=conn(); cur=c.cursor()
    cur.execute("""SELECT a.code,a.name,a.type,
      COALESCE(SUM(l.debit),0),COALESCE(SUM(l.credit),0)
      FROM accounts a LEFT JOIN journal_lines l ON a.id=l.account_id
      GROUP BY a.id ORDER BY a.code""")
    rows=cur.fetchall(); c.close()
    return [(r[0],r[1],r[2],r[3],r[4],r[3]-r[4]) for r in rows]

def add_entry(dt,ref,desc,lines):
    # lines = [(account_code,debit,credit), ...]
    if abs(sum(x[1] for x in lines)-sum(x[2] for x in lines)) > 0.005:
        raise ValueError("Debit and Credit totals must be equal.")
    c=conn(); cur=c.cursor()
    cur.execute("INSERT INTO journal(entry_date,ref,description) VALUES(?,?,?)",(dt,ref,desc))
    jid=cur.lastrowid
    for code,debit,credit in lines:
        cur.execute("SELECT id FROM accounts WHERE code=?",(code,))
        r=cur.fetchone()
        if not r: raise ValueError(f"Account {code} not found")
        cur.execute("INSERT INTO journal_lines(journal_id,account_id,debit,credit) VALUES(?,?,?,?)",
                    (jid,r[0],debit,credit))
    c.commit(); c.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Business Accounting System - V1")
        self.geometry("1220x760"); self.minsize(1050,680)
        self.configure(bg="#eef2f7")
        s=ttk.Style(self)
        try:s.theme_use("clam")
        except:pass
        s.configure("TButton",font=("Segoe UI",10),padding=7)
        self.make_ui(); self.refresh()

    def make_ui(self):
        h=tk.Frame(self,bg="#102f4f",height=72); h.pack(fill="x")
        tk.Label(h,text="BUSINESS ACCOUNTING",bg="#102f4f",fg="white",
                 font=("Segoe UI",20,"bold")).pack(side="left",padx=24,pady=17)
        tk.Label(h,text="V1 • Double Entry Core",bg="#102f4f",fg="#dce9f5",
                 font=("Segoe UI",10)).pack(side="right",padx=24)
        nav=tk.Frame(self,bg="white"); nav.pack(fill="x")
        for n,cmd in [("Dashboard",self.dashboard),("New Transaction",self.transaction),
                      ("Chart of Accounts",self.accounts),("General Ledger",self.ledger),
                      ("Trial Balance",self.trial),("Profit & Loss",self.pnl),
                      ("Balance Sheet",self.bs)]:
            ttk.Button(nav,text=n,command=cmd).pack(side="left",padx=4,pady=9)
        self.body=tk.Frame(self,bg="#eef2f7"); self.body.pack(fill="both",expand=True,padx=22,pady=18)

    def clear(self):
        for w in self.body.winfo_children(): w.destroy()

    def dashboard(self):
        self.clear()
        tk.Label(self.body,text="Dashboard",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w")
        rows=balances()
        def val(typ, mode):
            total=0
            for _,_,t,d,c,b in rows:
                if t==typ:
                    total += (d-c) if mode=="bal" else (c-d)
            return total
        cards=[
            ("CASH",val("Asset","bal")),("BANK",0),("RECEIVABLE",0),
            ("PAYABLE",val("Liability","bal")),("SALES",val("Revenue","rev")),
            ("EXPENSES",val("Expense","rev"))
        ]
        grid=tk.Frame(self.body,bg="#eef2f7"); grid.pack(fill="x",pady=18)
        for i,(title,v) in enumerate(cards):
            card=tk.Frame(grid,bg="white",highlightbackground="#d4dde6",highlightthickness=1)
            card.grid(row=i//3,column=i%3,sticky="nsew",padx=6,pady=6,ipadx=12,ipady=10)
            tk.Label(card,text=title,bg="white",fg="#6b7b8c",font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(card,text=money(v),bg="white",fg="#102f4f",font=("Segoe UI",17,"bold")).pack(anchor="w",pady=4)
        for i in range(3): grid.columnconfigure(i,weight=1)
        box=tk.LabelFrame(self.body,text="Accounting Status",bg="white",fg="#102f4f",
                          font=("Segoe UI",11,"bold"),padx=15,pady=15)
        box.pack(fill="both",expand=True,pady=12)
        tb=self.tb_totals()
        tk.Label(box,text=f"Trial Balance — Debit: {money(tb[0])}     Credit: {money(tb[1])}",
                 bg="white",font=("Segoe UI",12,"bold")).pack(anchor="w",pady=8)
        tk.Label(box,text="All reports are generated automatically from journal entries.",
                 bg="white",fg="#536779",font=("Segoe UI",10)).pack(anchor="w")

    def transaction(self):
        self.clear()
        tk.Label(self.body,text="New Transaction",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(0,15))
        f=tk.Frame(self.body,bg="white",padx=20,pady=20); f.pack(fill="x")
        labels=["Date","Reference","Description","Debit Account","Credit Account","Amount"]
        entries={}
        for i,l in enumerate(labels):
            tk.Label(f,text=l,bg="white",font=("Segoe UI",10,"bold")).grid(row=i,column=0,sticky="w",pady=7)
            if l in ("Debit Account","Credit Account"):
                vals=[f"{a[0]} - {a[1]}" for a in ACCOUNTS]
                cb=ttk.Combobox(f,values=vals,width=48,state="readonly")
                cb.grid(row=i,column=1,sticky="w",padx=15)
                entries[l]=cb
            else:
                e=ttk.Entry(f,width=52); e.grid(row=i,column=1,sticky="w",padx=15)
                entries[l]=e
        entries["Date"].insert(0,date.today().isoformat())
        ttk.Button(f,text="SAVE TRANSACTION",command=lambda:self.save_tx(entries)).grid(row=6,column=1,sticky="w",pady=18)

    def save_tx(self,e):
        try:
            dt=e["Date"].get().strip(); ref=e["Reference"].get().strip()
            desc=e["Description"].get().strip()
            dc=e["Debit Account"].get().split(" - ")[0]; cc=e["Credit Account"].get().split(" - ")[0]
            amt=float(e["Amount"].get().replace(",",""))
            if not dc or not cc or amt<=0: raise ValueError()
            add_entry(dt,ref,desc,[(dc,amt,0),(cc,0,amt)])
            messagebox.showinfo("Saved","Transaction saved. Ledger and reports updated automatically.")
            self.dashboard()
        except Exception as ex:
            messagebox.showerror("Error",f"Please check the entry.\n\n{ex}")

    def accounts(self):
        self.clear(); self.title_label("Chart of Accounts")
        tree=self.tree(["Code","Account","Type"]); tree.pack(fill="both",expand=True,pady=12)
        for a in ACCOUNTS: tree.insert("","end",values=a)

    def ledger(self):
        self.clear(); self.title_label("General Ledger")
        tree=self.tree(["Date","Ref","Description","Account","Debit","Credit"]); tree.pack(fill="both",expand=True,pady=12)
        c=conn(); cur=c.cursor()
        cur.execute("""SELECT j.entry_date,j.ref,j.description,a.name,l.debit,l.credit
                       FROM journal j JOIN journal_lines l ON j.id=l.journal_id
                       JOIN accounts a ON a.id=l.account_id ORDER BY j.entry_date,j.id,l.id""")
        for r in cur.fetchall(): tree.insert("","end",values=(r[0],r[1],r[2],r[3],money(r[4]),money(r[5])))
        c.close()

    def trial(self):
        self.clear(); self.title_label("Trial Balance")
        tree=self.tree(["Code","Account","Debit","Credit"]); tree.pack(fill="both",expand=True,pady=12)
        td=tc=0
        for code,name,typ,d,c,b in balances():
            debit=max(b,0); credit=max(-b,0)
            if debit or credit:
                td+=debit;tc+=credit;tree.insert("","end",values=(code,name,money(debit),money(credit)))
        tk.Label(self.body,text=f"TOTAL   Debit {money(td)}     Credit {money(tc)}",
                 bg="#eef2f7",fg="#102f4f",font=("Segoe UI",12,"bold")).pack(anchor="e")

    def pnl(self):
        self.clear(); self.title_label("Profit & Loss")
        rev=exp=0
        tree=self.tree(["Type","Account","Amount"]); tree.pack(fill="both",expand=True,pady=12)
        for code,name,typ,d,c,b in balances():
            if typ=="Revenue":
                x=c-d; rev+=x; tree.insert("","end",values=("Revenue",name,money(x)))
            elif typ=="Expense":
                x=d-c; exp+=x; tree.insert("","end",values=("Expense",name,money(x)))
        tk.Label(self.body,text=f"Revenue: {money(rev)}    Expenses: {money(exp)}    NET PROFIT: {money(rev-exp)}",
                 bg="#eef2f7",fg="#102f4f",font=("Segoe UI",12,"bold")).pack(anchor="e")

    def bs(self):
        self.clear(); self.title_label("Balance Sheet")
        assets=liab=equity=0
        tree=self.tree(["Section","Account","Balance"]); tree.pack(fill="both",expand=True,pady=12)
        for code,name,typ,d,c,b in balances():
            if typ=="Asset":
                x=b; assets+=x
                if x: tree.insert("","end",values=("Assets",name,money(x)))
            elif typ=="Liability":
                x=-b; liab+=x
                if x: tree.insert("","end",values=("Liabilities",name,money(x)))
            elif typ=="Equity":
                x=-b; equity+=x
                if x: tree.insert("","end",values=("Equity",name,money(x)))
        # Current profit is part of equity for reporting
        rev=sum(c-d for _,_,t,d,c,b in balances() if t=="Revenue")
        exp=sum(d-c for _,_,t,d,c,b in balances() if t=="Expense")
        profit=rev-exp; equity+=profit
        tree.insert("","end",values=("Equity","Current Period Profit",money(profit)))
        tk.Label(self.body,text=f"Assets: {money(assets)}    Liabilities + Equity: {money(liab+equity)}",
                 bg="#eef2f7",fg="#102f4f",font=("Segoe UI",12,"bold")).pack(anchor="e")

    def title_label(self,text):
        tk.Label(self.body,text=text,bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w")

    def tree(self,cols):
        t=ttk.Treeview(self.body,columns=cols,show="headings")
        for c in cols: t.heading(c,text=c); t.column(c,width=170,anchor="w")
        return t

    def tb_totals(self):
        td=tc=0
        for _,_,_,d,c,b in balances():
            td+=max(b,0);tc+=max(-b,0)
        return td,tc

    def refresh(self): self.dashboard()

if __name__=="__main__":
    init_db()
    App().mainloop()
