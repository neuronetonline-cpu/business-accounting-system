"""Modern Tkinter theme for Business Accounting System."""

COLORS = {
    "navy": "#0b2f53",
    "navy_2": "#123f68",
    "blue": "#1976d2",
    "blue_2": "#2d8cff",
    "bg": "#eef3f8",
    "surface": "#ffffff",
    "surface_2": "#f7f9fc",
    "border": "#d8e1eb",
    "text": "#16324f",
    "muted": "#6f8296",
    "success": "#1aa36f",
    "warning": "#f59e0b",
    "danger": "#e64b4b",
}

FONT = "Segoe UI"


def configure_ttk(style):
    """Apply a consistent modern ttk baseline."""
    style.theme_use("clam")
    style.configure("TButton", font=(FONT, 9), padding=(10, 7), relief="flat")
    style.map("TButton", background=[("active", "#e8f2ff")], foreground=[("active", COLORS["navy"])])
    style.configure("Treeview", font=(FONT, 9), rowheight=28, background=COLORS["surface"], fieldbackground=COLORS["surface"], foreground=COLORS["text"])
    style.configure("Treeview.Heading", font=(FONT, 9, "bold"), background="#edf3f8", foreground=COLORS["text"], relief="flat", padding=7)
    style.map("Treeview", background=[("selected", "#dcecff")], foreground=[("selected", COLORS["navy"])])
    style.configure("TCombobox", padding=5)
    style.configure("TEntry", padding=5)
