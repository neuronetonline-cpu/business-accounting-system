COLORS = {
    'navy':'#082846','navy_2':'#0e3b61','blue':'#1976d2','blue_2':'#2d8cff',
    'bg':'#eef3f8','surface':'#ffffff','surface_2':'#f7f9fc','border':'#d8e1eb',
    'text':'#16324f','muted':'#6f8296','success':'#159a68','warning':'#f59e0b','danger':'#dc4545',
}
FONT='Segoe UI'

def configure_ttk(style):
    style.theme_use('clam')
    style.configure('TButton',font=(FONT,9,'bold'),padding=(11,7),background='#ffffff',foreground=COLORS['text'],bordercolor=COLORS['border'],relief='flat')
    style.map('TButton',background=[('active','#e8f2ff'),('pressed','#dbeaff')],foreground=[('active',COLORS['blue'])])
    style.configure('Accent.TButton',font=(FONT,9,'bold'),padding=(13,8),background=COLORS['blue'],foreground='white',borderwidth=0)
    style.map('Accent.TButton',background=[('active',COLORS['blue_2'])],foreground=[('active','white')])
    style.configure('Treeview',font=(FONT,9),rowheight=30,background='white',fieldbackground='white',foreground=COLORS['text'],bordercolor=COLORS['border'],borderwidth=1)
    style.configure('Treeview.Heading',font=(FONT,9,'bold'),background='#edf3f8',foreground=COLORS['text'],relief='flat',padding=8)
    style.map('Treeview',background=[('selected','#dcecff')],foreground=[('selected',COLORS['navy'])])
    style.configure('TCombobox',padding=6)
    style.configure('TEntry',padding=6)
