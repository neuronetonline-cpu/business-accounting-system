# Business Accounting System

## V3 — Daily Transactions

This build adds user-friendly daily transaction entry while keeping double-entry accounting automatic.

### Included
- Dashboard
- Opening Balance
- Daily Transaction screen
- Automatic debit/credit posting
- General Ledger
- Trial Balance
- Profit & Loss
- Balance Sheet
- SQLite local database

### Transaction types
- Cash Sale
- Bank Sale
- Credit Sale
- Customer Payment
- Cash Customer Payment
- Cash/Bank Purchase
- Supplier Payment
- Expense payments
- Other Income
- Owner Investment
- Owner Drawing

### Run
```bash
python -m app.main
```

### Build EXE
```bash
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name BusinessAccounting app/main.py
```

The EXE will be created under `dist`.

## Next
V4 will add:
- Customer master
- Supplier master
- Multiple bank accounts
- Receivable/payable aging
- Inventory
- Purchase and sales invoices
- Bank reconciliation
- Period closing
- Backup/restore
- Management decision dashboard
