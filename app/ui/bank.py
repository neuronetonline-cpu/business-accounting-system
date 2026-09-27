
import tkinter as tk
from tkinter import ttk,messagebox
from app.database import get_connection

class BankFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7");self.build()
    def build(self):
        tk.Label(self,text="Bank & Cash Accounts",bg="#eef2f7",fg="#102f4f",font=("Segoe UI",22,"bold")).pack(anchor="w")
        top=tk.Frame(self,bg="white",padx=18,pady=14);top.pack(fill="x",pady=12)
        self.name=ttk.Entry(top,width=25);self.bank=ttk.Entry(top,width=20);self.number=ttk.Entry(top,width=22);self.code=ttk.Entry(top,width=12)
        for i,(lab,e) in enumerate([("Account Name",self.name),("Bank",self.bank),("Account No.",self.number),("Ledger Code",self.code)]):
            tk.Label(top,text=lab,bg="white",font=("Segoe UI",9,"bold")).grid(row=0,column=i)
            e.grid(row=1,column=i,padx=5,pady=5)
        ttk.Button(top,text="ADD BANK",command=self.add).grid(row=1,column=4,padx=8)
        box=tk.Frame(self,bg="white",padx=12,pady=12);box.pack(fill="both",expand=True)
        cols=("ID","Name","Bank","Account No.","Ledger Code","Book Balance")
        self.tree=ttk.Treeview(box,columns=cols,show="headings")
        for c in cols:self.tree.heading(c,text=c);self.tree.column(c,width=170)
        self.tree.pack(fill="both",expand=True);self.refresh()
    def add(self):
        try:
            code=self.code.get().strip()
            name=self.name.get().strip()
            if not code or not name: raise ValueError("Account code and name are required.")
            con=get_connection()
            exists=con.execute("SELECT 1 FROM accounts WHERE code=?",(code,)).fetchone()
            if not exists:
                con.execute("INSERT INTO accounts(code,name,account_type,parent_code) VALUES(?,?,?,?)",
                            (code,name,"Asset","1010"))
            con.execute("INSERT INTO bank_accounts(account_code,name,bank_name,account_number,ledger_code) VALUES(?,?,?,?,?)",
                        (code,name,self.bank.get(),self.number.get(),code))
            con.commit();con.close();self.refresh()
        except Exception as e:messagebox.showerror("Error",str(e))
    def refresh(self):
        for x in self.tree.get_children():self.tree.delete(x)
        con=get_connection();rows=con.execute("SELECT * FROM bank_accounts WHERE active=1").fetchall()
        for r in rows:
            code=r["ledger_code"]
            ar=con.execute("""SELECT COALESCE(SUM(l.debit-l.credit),0) b FROM journal_lines l
                              JOIN accounts a ON a.id=l.account_id WHERE a.code=?""",(code,)).fetchone()["b"]
            self.tree.insert("","end",values=(r["id"],r["name"],r["bank_name"] or "",r["account_number"] or "",code,f"Rs. {ar:,.2f}"))
        con.close()

class ReconciliationFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7");self.build()
    def build(self):
        tk.Label(self,text="Bank Reconciliation",bg="#eef2f7",fg="#102f4f",font=("Segoe UI",22,"bold")).pack(anchor="w")
        box=tk.Frame(self,bg="white",padx=24,pady=20);box.pack(fill="x",pady=15)
        self.bank=ttk.Combobox(box,values=self.banks(),state="readonly",width=40)
        if self.banks():self.bank.current(0)
        self.date=ttk.Entry(box,width=20);self.statement=ttk.Entry(box,width=20)
        for i,(lab,w) in enumerate([("Bank",self.bank),("Statement Date",self.date),("Statement Balance",self.statement)]):
            tk.Label(box,text=lab,bg="white",font=("Segoe UI",9,"bold")).grid(row=0,column=i)
            w.grid(row=1,column=i,padx=6,pady=5)
        ttk.Button(box,text="CHECK",command=self.check).grid(row=1,column=3,padx=10)
        self.result=tk.Label(box,text="",bg="white",fg="#102f4f",font=("Segoe UI",12,"bold"))
        self.result.grid(row=2,column=0,columnspan=4,sticky="w",pady=14)
    def banks(self):
        con=get_connection();r=con.execute("SELECT id,name FROM bank_accounts WHERE active=1").fetchall();con.close()
        return [f"{x['id']} - {x['name']}" for x in r]
    def check(self):
        try:
            bid=int(self.bank.get().split(" - ")[0]); stmt=float(self.statement.get().replace(",",""))
            con=get_connection();r=con.execute("SELECT ledger_code FROM bank_accounts WHERE id=?",(bid,)).fetchone()
            book=con.execute("""SELECT COALESCE(SUM(l.debit-l.credit),0) b FROM journal_lines l
                                JOIN accounts a ON a.id=l.account_id WHERE a.code=?""",(r["ledger_code"],)).fetchone()["b"]
            diff=stmt-book
            self.result.config(text=f"Book Balance: Rs. {book:,.2f}    Difference: Rs. {diff:,.2f}")
            con.close()
        except Exception as e:messagebox.showerror("Error",str(e))


class TransferFrame(tk.Frame):
    def __init__(self,master,on_saved=None):
        super().__init__(master,bg="#eef2f7");self.on_saved=on_saved;self.build()
    def accounts(self):
        con=get_connection()
        rows=con.execute("""SELECT code,name FROM accounts
                           WHERE account_type='Asset' AND code LIKE '10%' ORDER BY code""").fetchall()
        con.close()
        return [f"{r['code']} - {r['name']}" for r in rows]
    def build(self):
        from app.accounting.engine import post_simple_transaction
        tk.Label(self,text="Bank / Cash Transfer",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w")
        box=tk.Frame(self,bg="white",padx=24,pady=20);box.pack(fill="x",pady=15)
        self.f={}
        fields=["Date","Reference","From Account","To Account","Amount","Description"]
        vals=self.accounts()
        for i,l in enumerate(fields):
            tk.Label(box,text=l,bg="white",font=("Segoe UI",9,"bold")).grid(row=i,column=0,sticky="w",pady=7)
            if l in ("From Account","To Account"):
                w=ttk.Combobox(box,values=vals,state="readonly",width=40)
                if vals:w.current(0)
            else:
                w=ttk.Entry(box,width=42)
                if l=="Date":
                    from datetime import date
                    w.insert(0,date.today().isoformat())
            w.grid(row=i,column=1,padx=18,sticky="w",pady=7);self.f[l]=w
        ttk.Button(box,text="SAVE TRANSFER",command=self.save).grid(row=6,column=1,sticky="w",pady=15)
    def save(self):
        try:
            from app.accounting.engine import post_simple_transaction
            fr=self.f["From Account"].get().split(" - ")[0]
            to=self.f["To Account"].get().split(" - ")[0]
            if fr==to: raise ValueError("From and To accounts must be different.")
            amount=float(self.f["Amount"].get().replace(",",""))
            if amount<=0: raise ValueError("Amount must be greater than zero.")
            post_simple_transaction(self.f["Date"].get(),self.f["Reference"].get(),
                                    self.f["Description"].get() or "Bank/Cash transfer",
                                    to,fr,amount,"TRANSFER")
            messagebox.showinfo("Saved","Transfer posted successfully.")
            if self.on_saved:self.on_saved()
        except Exception as e:messagebox.showerror("Error",str(e))
