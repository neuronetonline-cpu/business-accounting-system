import os
import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from app.accounting.backup import create_backup,restore_backup,get_backup_dir,set_backup_dir
from app.database import get_connection
from app.ui.theme import COLORS, FONT
from app.ui.widgets import Card, tree_with_scrollbars

class AdminFrame(tk.Frame):
    def __init__(self,master):
        super().__init__(master,bg=COLORS["bg"]); self.build()

    def build(self):
        tk.Label(self,text="System Administration",bg=COLORS["bg"],fg=COLORS["text"],font=(FONT,22,"bold")).pack(anchor="w")
        box=Card(self,padx=22,pady=18);box.pack(fill="x",pady=15)
        ttk.Button(box,text="CREATE BACKUP",style='Accent.TButton',command=self.backup).grid(row=0,column=0,padx=6,pady=5)
        ttk.Button(box,text="RESTORE BACKUP",command=self.restore).grid(row=0,column=1,padx=6,pady=5)
        ttk.Button(box,text="OPEN BACKUP FOLDER",command=self.open_backup_folder).grid(row=0,column=2,padx=6,pady=5)
        ttk.Button(box,text="REFRESH AUDIT LOG",command=self.refresh).grid(row=0,column=3,padx=6,pady=5)
        tk.Label(box,text="Backup Location",bg="white",fg=COLORS["text"],font=(FONT,9,"bold")).grid(row=1,column=0,sticky='w',padx=6,pady=(14,3))
        self.backup_path=ttk.Entry(box,width=78); self.backup_path.grid(row=2,column=0,columnspan=3,sticky='we',padx=6,pady=4)
        self.backup_path.insert(0,str(get_backup_dir()))
        ttk.Button(box,text="CHANGE LOCATION",command=self.change_backup_location).grid(row=2,column=3,padx=6,pady=4)
        box.columnconfigure(0,weight=1); box.columnconfigure(1,weight=1); box.columnconfigure(2,weight=1)
        self.status=tk.Label(box,text="",bg="white",fg="#425466",wraplength=1000,justify='left');self.status.grid(row=3,column=0,columnspan=4,sticky='w',padx=6,pady=(12,0))

        logbox=Card(self,padx=12,pady=12);logbox.pack(fill="both",expand=True)
        cols=("Time","Type","Reference","Description")
        frame,self.tree=tree_with_scrollbars(logbox,cols,{"Time":170,"Type":170,"Reference":220,"Description":600},height=18)
        frame.pack(fill="both",expand=True); self.refresh()

    def backup(self):
        try:
            p=create_backup(); self.status.config(text=f"Backup created successfully:\n{p}")
        except Exception as e:messagebox.showerror("Backup Error",str(e))

    def restore(self):
        p=filedialog.askopenfilename(title="Select database backup",filetypes=[("SQLite Database","*.db"),("All files","*.*")])
        if not p:return
        if not messagebox.askyesno("Confirm Restore","Restore this backup and replace the current database?\n\nThe application should be restarted immediately after restore."):return
        try:
            restore_backup(p); self.status.config(text="Backup restored successfully. Restart the application before continuing.")
            messagebox.showinfo("Restore Complete","Backup restored successfully. Please close and reopen the application.")
        except Exception as e:messagebox.showerror("Restore Error",str(e))

    def change_backup_location(self):
        path=filedialog.askdirectory(title="Select Backup Folder",initialdir=str(get_backup_dir()))
        if not path:return
        try:
            new=set_backup_dir(path); self.backup_path.delete(0,'end'); self.backup_path.insert(0,str(new)); self.status.config(text=f"Backup location saved:\n{new}")
        except Exception as e:messagebox.showerror("Backup Location Error",str(e))

    def open_backup_folder(self):
        try:
            p=get_backup_dir(); os.startfile(str(p))
        except Exception as e:messagebox.showerror("Folder Error",str(e))

    def refresh(self):
        for x in self.tree.get_children():self.tree.delete(x)
        con=get_connection(); rows=con.execute("SELECT event_time,event_type,reference,description FROM audit_log ORDER BY id DESC LIMIT 200").fetchall(); con.close()
        for r in rows:self.tree.insert("","end",values=(r["event_time"],r["event_type"],r["reference"] or "",r["description"] or ""))
