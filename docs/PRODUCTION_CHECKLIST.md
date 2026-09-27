# Production Checklist

## Accounting
- [x] Double-entry journal
- [x] General Ledger
- [x] Trial Balance
- [x] P&L
- [x] Balance Sheet
- [x] Customers / Suppliers
- [x] Inventory
- [x] Sales / Purchases
- [x] Bank accounts
- [x] Reconciliation check

## Management
- [x] KPI dashboard
- [x] Receivables / Payables visibility
- [x] Inventory value
- [x] Low-stock alert
- [x] Monthly sales / COGS view

## Data safety
- [x] Local SQLite database
- [x] Manual backup
- [x] Restore
- [x] Audit log

## Final testing still recommended
- Test backup/restore before real data entry.
- Test a complete month with known figures.
- Reconcile bank balances against statements.
- Verify inventory quantities and valuation.
- Verify Trial Balance debit = credit.
- Keep regular database backups.

## Windows EXE
Run `build_exe.bat` on a Windows machine with Python installed.
