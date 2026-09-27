# Business Accounting System

## V4 — Customers, Suppliers & Credit

Added:
- Customer master
- Supplier master
- Customer credit invoices
- Customer payments
- Supplier credit bills
- Supplier payments
- Customer outstanding balances
- Supplier outstanding balances
- Receivable aging
- Payable aging
- Credit limits
- Automatic accounting journal posting
- Dashboard receivable/payable cards

Run:
```bash
python -m app.main
```

Build EXE:
```bash
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name BusinessAccounting app/main.py
```

Next:
- Inventory module
- Product master
- Purchases and sales invoices
- Stock movement and COGS
- Bank reconciliation
- Advanced reports
- Management decision dashboard
