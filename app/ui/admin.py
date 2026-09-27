
import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from app.accounting.backup import create_backup,restore_backup
from app.database import get_connection

class AdminFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg="#eef2f7");self.build()

    def build(self):
        tk.Label(self,text="System Administration",bg="#eef2f7",fg="#102f4f",
                 font=("Segoe UI",22,"bold")).pack(anchor="w")
        box=tk.Frame(self,bg="white",padx=22,pady=22);box.pack(fill="x",pady=15)

        ttk.Button(box,text="CREATE BACKUP",command=self.backup).pack(side="left",padx=6)
        ttk.Button(box,text="RESTORE BACKUP",command=self.restore).pack(side="left",padx=6)
        ttk.Button(box,text="REFRESH AUDIT LOG",command=self.refresh).pack(side="left",padx=6)

        self.status=tk.Label(box,text="",bg="white",fg="#425466")
        self.status.pack(anchor="w",pady=(18,0))

        logbox=tk.Frame(self,bg="white",padx=12,pady=12);logbox.pack(fill="both",expand=True)
        cols=("Time","Type","Reference","Description")
        self.tree=ttk.Treeview(logbox,columns=cols,show="headings")
        for c in cols:self.tree.heading(c,text=c);self.tree.column(c,width=190)
        self.tree.column("Description",width=400)
        self.tree.pack(fill="both",expand=True)
        self.refresh()

    def backup(self):
        try:
            p=create_backup()
            self.status.config(text=f"Backup created: {p}")
        except Exception as e:messagebox.showerror("Backup Error",str(e))

    def restore(self):
        p=filedialog.askopenfilename(title="Select database backup",
                                     filetypes=[("SQLite Database","*.db"),("All files","*.*")])
        if not p:return
        if not messagebox.askyesno("Confirm Restore","Restore this backup and replace the current database?"):
            return
        try:
            restore_backup(p)
            self.status.config(text="Backup restored. Restart the application to refresh all screens.")
        except Exception as e:messagebox.showerror("Restore Error",str(e))

    def refresh(self):
        for x in self.tree.get_children():self.tree.delete(x)
        con=get_connection()
        rows=con.execute("SELECT event_time,event_type,reference,description FROM audit_log ORDER BY id DESC LIMIT 200").fetchall()
        con.close()
        for r in rows:self.tree.insert("","end",values=(r["event_time"],r["event_type"],r["reference"] or "",r["description"] or ""))
