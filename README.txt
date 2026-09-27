
BUSINESS ACCOUNTING SYSTEM V1
=============================

This is the first accounting-core prototype.

Included:
- Clean Windows desktop UI
- SQLite local database
- Chart of Accounts
- Double-entry journal engine
- Simple transaction entry
- Automatic General Ledger
- Automatic Trial Balance
- Automatic Profit & Loss
- Automatic Balance Sheet
- Dashboard

Run:
    python business_accounting.py

Build EXE on Windows:
    py -m pip install pyinstaller
    py -m PyInstaller --noconfirm --onefile --windowed --name BusinessAccounting business_accounting.py

EXE:
    dist\BusinessAccounting.exe

IMPORTANT:
This V1 is a prototype accounting engine, not yet a complete production accounting package.
Next build should add:
- Opening Balance Wizard
- Multiple bank accounts
- Customer/Supplier master data
- Sales invoice and purchase forms
- Customer receipts
- Supplier payments
- Expense forms
- Inventory opening and movement
- Date/month closing
- Reports with filters
- Backup/restore
- Edit/delete/reverse transaction controls
