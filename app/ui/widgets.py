import tkinter as tk
from tkinter import ttk
from app.ui.theme import COLORS, FONT

class ScrollableFrame(tk.Frame):
    def __init__(self, master, bg=None):
        super().__init__(master, bg=bg or COLORS['bg'])
        self.canvas = tk.Canvas(self, bg=bg or COLORS['bg'], highlightthickness=0)
        self.vbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.hbar = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.inner = tk.Frame(self.canvas, bg=bg or COLORS['bg'])
        self.window_id = self.canvas.create_window((0,0), window=self.inner, anchor='nw')
        self.canvas.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.vbar.pack(side='right', fill='y')
        self.hbar.pack(side='bottom', fill='x')
        self.inner.bind('<Configure>', self._sync_region)
        self.canvas.bind('<Configure>', self._sync_width)
        self.canvas.bind_all('<MouseWheel>', self._wheel, add='+')
    def _sync_region(self, _=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    def _sync_width(self, event):
        self.canvas.itemconfigure(self.window_id, width=max(event.width, self.inner.winfo_reqwidth()))
    def _wheel(self, event):
        if self.winfo_exists():
            try: self.canvas.yview_scroll(int(-event.delta/120), 'units')
            except tk.TclError: pass

class Card(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=COLORS['surface'], highlightbackground=COLORS['border'], highlightthickness=1, **kwargs)

class StatCard(Card):
    def __init__(self, master, title, value, icon='◆', accent=None, subtitle=''):
        super().__init__(master, padx=16, pady=14)
        accent = accent or COLORS['blue']
        top=tk.Frame(self,bg='white');top.pack(fill='x')
        tk.Label(top,text=icon,bg=accent,fg='white',font=(FONT,12,'bold'),width=3,height=1).pack(side='left',padx=(0,10))
        tk.Label(top,text=title,bg='white',fg=COLORS['muted'],font=(FONT,9,'bold')).pack(side='left')
        tk.Label(self,text=value,bg='white',fg=COLORS['text'],font=(FONT,18,'bold')).pack(anchor='w',pady=(8,0))
        if subtitle: tk.Label(self,text=subtitle,bg='white',fg=COLORS['muted'],font=(FONT,8)).pack(anchor='w',pady=(2,0))

class MiniBarChart(Card):
    def __init__(self, master, title, data, series=('value',), labels=None, height=220, colors=None):
        super().__init__(master, padx=14, pady=12)
        tk.Label(self,text=title,bg='white',fg=COLORS['text'],font=(FONT,12,'bold')).pack(anchor='w')
        self.canvas=tk.Canvas(self,bg='white',height=height,highlightthickness=0)
        self.canvas.pack(fill='both',expand=True,pady=(8,0))
        self.data=data; self.series=series; self.labels=labels or [x.get('label','') for x in data]
        self.colors=colors or [COLORS['blue'], COLORS['danger'], COLORS['success'], '#7c5cff']
        self.canvas.bind('<Configure>',lambda e:self.draw())
        self.after(20,self.draw)
    def draw(self):
        c=self.canvas; c.delete('all'); w=max(c.winfo_width(),300); h=max(c.winfo_height(),180)
        if not self.data:return
        maxv=max([max([float(d.get(s,0)) for s in self.series]) for d in self.data] or [1]) or 1
        left,bottom,top=50,h-30,20; plot_h=bottom-top; plot_w=w-left-20
        for i in range(5):
            y=top+plot_h*i/4
            c.create_line(left,y,w-20,y,fill='#e9eef4')
            c.create_text(left-8,y,text=f'{maxv*(4-i)/4:,.0f}',anchor='e',fill=COLORS['muted'],font=(FONT,7))
        groups=len(self.data); gap=plot_w/max(groups,1); group_width=min(60,gap*0.72); barw=max(8,(group_width-6*len(self.series))/len(self.series))
        for i,d in enumerate(self.data):
            gx=left+i*gap+gap/2-group_width/2
            for j,s in enumerate(self.series):
                val=float(d.get(s,0)); bh=plot_h*val/maxv
                x1=gx+j*(barw+4); x2=x1+barw; y1=bottom-bh
                c.create_rectangle(x1,y1,x2,bottom,fill=self.colors[j%len(self.colors)],outline='')
            c.create_text(left+i*gap+gap/2,bottom+12,text=self.labels[i][:12],fill=COLORS['muted'],font=(FONT,7))

def tree_with_scrollbars(parent, columns, widths=None, height=15):
    frame=tk.Frame(parent,bg='white')
    tree=ttk.Treeview(frame,columns=columns,show='headings',height=height)
    widths=widths or {}
    for c in columns:
        tree.heading(c,text=c)
        tree.column(c,width=widths.get(c,140),anchor='w')
    y=ttk.Scrollbar(frame,orient='vertical',command=tree.yview)
    x=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview)
    tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
    tree.grid(row=0,column=0,sticky='nsew'); y.grid(row=0,column=1,sticky='ns'); x.grid(row=1,column=0,sticky='ew')
    frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
    return frame,tree
