import tkinter as tk
from tkinter import ttk
from datetime import date

from app.database import init_database, seed_accounts
from app.ui.dashboard import DashboardFrame
from app.ui.opening_balance import OpeningBalanceFrame
from app.ui.transactions import TransactionsFrame
from app.ui.ledger import LedgerFrame
from app.ui.reports import TrialBalanceFrame, PnLFrame, BalanceSheetFrame
from app.ui.contacts import ContactsFrame
from app.ui.credit import CreditFrame
from app.ui.inventory import InventoryFrame
from app.ui.trade import TradeFrame
from app.ui.bank import BankFrame, ReconciliationFrame, TransferFrame
from app.ui.decision_dashboard import DecisionDashboardFrame
from app.ui.admin import AdminFrame
from app.ui.pos_import import POSImportFrame
from app.ui.theme import COLORS, FONT, configure_ttk
from app.ui.widgets import ScrollableFrame


class NavButton(tk.Button):
    def __init__(self, master, text, command, icon="", active=False):
        self.base = COLORS["navy"]
        self.active_bg = COLORS["blue"]
        self.hover_bg = "#174a77"
        label = f"  {icon}  {text}" if icon else f"  {text}"
        super().__init__(
            master,
            text=label,
            command=command,
            anchor="w",
            bd=0,
            relief="flat",
            cursor="hand2",
            font=(FONT, 9, "bold" if active else "normal"),
            bg=self.active_bg if active else self.base,
            fg="white",
            activebackground=self.hover_bg,
            activeforeground="white",
            padx=10,
            pady=9,
            highlightthickness=0,
        )
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_bg if self.cget("bg") != self.active_bg else self.active_bg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.active_bg if self.cget("font").find("bold") >= 0 else self.base))


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Business Accounting System")
        self.geometry("1500x900")
        self.minsize(1180, 720)
        self.configure(bg=COLORS["bg"])

        self.style = ttk.Style(self)
        configure_ttk(self.style)
        self.current_label = "Dashboard"
        self.nav_buttons = {}

        self._build_header()
        self._build_main_area()
        self._build_footer()
        self.decision_dashboard()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["navy"], height=82)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=COLORS["navy"])
        brand.pack(side="left", fill="y", padx=22)
        tk.Label(brand, text="▮▮▮", bg=COLORS["navy"], fg="#24a6ff", font=(FONT, 18, "bold")).pack(side="left", padx=(0, 12))
        text = tk.Frame(brand, bg=COLORS["navy"])
        text.pack(side="left", pady=12)
        tk.Label(text, text="BUSINESS ACCOUNTING SYSTEM", bg=COLORS["navy"], fg="white", font=(FONT, 18, "bold")).pack(anchor="w")
        tk.Label(text, text="Manage your business easily", bg=COLORS["navy"], fg="#b9cee2", font=(FONT, 9)).pack(anchor="w")

        right = tk.Frame(header, bg=COLORS["navy"])
        right.pack(side="right", padx=18, fill="y")
        date_box = tk.Frame(right, bg=COLORS["navy_2"], padx=14, pady=7)
        date_box.pack(side="left", pady=14, padx=6)
        tk.Label(date_box, text="TODAY", bg=COLORS["navy_2"], fg="#a9c2d9", font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(date_box, text=date.today().isoformat(), bg=COLORS["navy_2"], fg="white", font=(FONT, 10, "bold")).pack(anchor="w")
        user_box = tk.Frame(right, bg=COLORS["navy_2"], padx=14, pady=7)
        user_box.pack(side="left", pady=14, padx=6)
        tk.Label(user_box, text="ADMIN", bg=COLORS["navy_2"], fg="white", font=(FONT, 10, "bold")).pack(anchor="w")
        tk.Label(user_box, text="Administrator", bg=COLORS["navy_2"], fg="#a9c2d9", font=(FONT, 8)).pack(anchor="w")
        tk.Button(right, text="⚙", command=self.admin, bg=COLORS["navy_2"], fg="white", activebackground="#1a4e7a", activeforeground="white", bd=0, font=(FONT, 15), width=3, cursor="hand2").pack(side="left", pady=14, padx=6)

    def _build_main_area(self):
        shell = tk.Frame(self, bg=COLORS["bg"])
        shell.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(shell, bg=COLORS["navy"], width=225)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Navigation groups
        groups = [
            ("MAIN", [
                ("Dashboard", "▦", self.dashboard),
                ("Transactions", "▤", self.transactions),
                ("Sales", "▣", self.sale),
                ("Purchases", "▣", self.purchase),
            ]),
            ("CONTACTS", [
                ("Customers", "●", self.customers),
                ("Suppliers", "●", self.suppliers),
                ("Customer Credit", "◉", self.customer_credit),
                ("Supplier Credit", "◉", self.supplier_credit),
            ]),
            ("INVENTORY", [
                ("Products & Stock", "□", self.inventory),
            ]),
            ("BANKING", [
                ("Banks & Cash", "▤", self.banks),
                ("Transfers", "↔", self.transfer),
                ("Reconciliation", "✓", self.reconcile),
            ]),
            ("REPORTS", [
                ("General Ledger", "≡", self.ledger),
                ("Trial Balance", "≡", self.trial),
                ("P&L (Profit & Loss)", "⌁", self.pnl),
                ("Balance Sheet", "▥", self.bs),
            ]),
            ("SYSTEM", [
                ("Opening Balances", "◌", self.opening),
                ("POS Import Center", "⇅", self.pos_import),
                ("Administration", "⚙", self.admin),
                ("Decision Dashboard", "◈", self.decision_dashboard),
            ]),
        ]

        for title, items in groups:
            tk.Label(self.sidebar, text=title, bg=COLORS["navy"], fg="#8fb0cc", font=(FONT, 8, "bold"), anchor="w").pack(fill="x", padx=18, pady=(12, 4))
            for label, icon, cmd in items:
                btn = NavButton(self.sidebar, label, lambda c=cmd, l=label: self._navigate(c, l), icon=icon)
                btn.pack(fill="x", padx=9, pady=1)
                self.nav_buttons[label] = btn

        content = tk.Frame(shell, bg=COLORS["bg"])
        content.pack(side="left", fill="both", expand=True)

        self.content_header = tk.Frame(content, bg=COLORS["bg"], height=58)
        self.content_header.pack(fill="x", padx=24, pady=(16, 0))
        self.content_header.pack_propagate(False)
        self.page_title = tk.Label(self.content_header, text="Management Decision Dashboard", bg=COLORS["bg"], fg=COLORS["text"], font=(FONT, 20, "bold"))
        self.page_title.pack(side="left", anchor="center")
        self.page_hint = tk.Label(self.content_header, text="", bg=COLORS["bg"], fg=COLORS["muted"], font=(FONT, 9))
        self.page_hint.pack(side="right", anchor="center")

        self.body = ScrollableFrame(content, bg=COLORS["bg"])
        self.body.pack(fill="both", expand=True, padx=22, pady=(0, 16))

    def _build_footer(self):
        footer = tk.Frame(self, bg="white", height=30, highlightbackground=COLORS["border"], highlightthickness=1)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(footer, text="●  Database Connected", bg="white", fg=COLORS["success"], font=(FONT, 8, "bold")).pack(side="left", padx=14)
        tk.Label(footer, text="User: Admin  |  Version: V7 + V8  |  Environment: Production", bg="white", fg=COLORS["muted"], font=(FONT, 8)).pack(side="left")
        tk.Label(footer, text="Business Accounting System", bg="white", fg=COLORS["muted"], font=(FONT, 8)).pack(side="right", padx=14)

    def _navigate(self, command, label):
        self.current_label = label
        self._update_nav()
        command()

    def _update_nav(self):
        for label, btn in self.nav_buttons.items():
            active = label == self.current_label
            btn.configure(bg=COLORS["blue"] if active else COLORS["navy"], font=(FONT, 9, "bold" if active else "normal"))

    def clear(self):
        for w in self.body.winfo_children():
            w.destroy()

    def show(self, cls, *args, title=None):
        self.clear()
        frame = cls(self.body.inner, *args)
        frame.pack(fill="both", expand=True)
        if title:
            self.page_title.configure(text=title)
        self._update_nav()

    def decision_dashboard(self):
        self.current_label = "Decision Dashboard"
        self.show(DecisionDashboardFrame, title="Management Decision Dashboard")

    def dashboard(self):
        self.current_label = "Dashboard"
        self.show(DashboardFrame, title="Dashboard")

    def opening(self):
        self.current_label = "Opening Balances"
        self.show(OpeningBalanceFrame, self.dashboard, title="Opening Balances")

    def transactions(self):
        self.current_label = "Transactions"
        self.show(TransactionsFrame, self.dashboard, title="Transactions")

    def customers(self):
        self.current_label = "Customers"
        self.show(ContactsFrame, "customer", title="Customers")

    def suppliers(self):
        self.current_label = "Suppliers"
        self.show(ContactsFrame, "supplier", title="Suppliers")

    def customer_credit(self):
        self.current_label = "Customer Credit"
        self.show(CreditFrame, "customer", self.dashboard, title="Customer Credit")

    def supplier_credit(self):
        self.current_label = "Supplier Credit"
        self.show(CreditFrame, "supplier", self.dashboard, title="Supplier Credit")

    def inventory(self):
        self.current_label = "Products & Stock"
        self.show(InventoryFrame, title="Products & Stock")

    def sale(self):
        self.current_label = "Sales"
        self.show(TradeFrame, "sale", self.dashboard, title="New Sale")

    def purchase(self):
        self.current_label = "Purchases"
        self.show(TradeFrame, "purchase", self.dashboard, title="New Purchase")

    def banks(self):
        self.current_label = "Banks & Cash"
        self.show(BankFrame, title="Banks & Cash Accounts")

    def transfer(self):
        self.current_label = "Transfers"
        self.show(lambda p: TransferFrame(p, self.dashboard), title="Bank & Cash Transfer")

    def reconcile(self):
        self.current_label = "Reconciliation"
        self.show(ReconciliationFrame, title="Bank Reconciliation")

    def pos_import(self):
        self.current_label = "POS Import Center"
        self.show(POSImportFrame, self.dashboard, title="POS Import Center")

    def admin(self):
        self.current_label = "Administration"
        self.show(AdminFrame, title="System Administration")

    def ledger(self):
        self.current_label = "General Ledger"
        self.show(LedgerFrame, title="General Ledger")

    def trial(self):
        self.current_label = "Trial Balance"
        self.show(TrialBalanceFrame, title="Trial Balance")

    def pnl(self):
        self.current_label = "P&L (Profit & Loss)"
        self.show(PnLFrame, title="Profit & Loss")

    def bs(self):
        self.current_label = "Balance Sheet"
        self.show(BalanceSheetFrame, title="Balance Sheet")


if __name__ == "__main__":
    init_database()
    seed_accounts()
    MainApp().mainloop()
