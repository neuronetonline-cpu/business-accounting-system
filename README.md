# Business Accounting System

## V7 + V8 — Management Dashboard + Production Preparation

This is the combined V7/V8 development build with audit, reconciliation persistence, stock validation, and partial-payment accounting fixes.

### V7 Management Decision Dashboard
- Sales
- Net profit
- Receivables
- Payables
- Inventory value
- Total assets
- Low-stock alerts
- Receivable/payable attention
- Monthly sales / COGS / gross profit table

### V8 Production Preparation
- Backup
- Restore
- Audit log
- Production checklist
- Windows EXE build script
- PyInstaller spec

### Run from source
```bash
python -m app.main
```

### Build EXE on Windows
Run:
```text
build_exe.bat
```

The final EXE is created at:
```text
dist\BusinessAccounting.exe
```

### Database
The application stores its SQLite database under the Windows user profile:
```text
%USERPROFILE%\BusinessAccountingSystem\business.db
```

Backups are stored under:
```text
%USERPROFILE%\BusinessAccountingSystem\backups\
```

### Important
This is a production-preparation build, not a substitute for a final accounting-system acceptance test. Before entering real business records, validate opening balances, inventory valuation, bank reconciliation, credit balances and month-end reports against known figures.
