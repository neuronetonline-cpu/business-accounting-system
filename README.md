# Business Accounting System

## V5 + V6 — Inventory, Sales, Purchases, Bank & Reports

Combined build.

### Inventory
- Product master
- SKU
- Category / brand
- Cost and selling price
- Reorder level
- Stock movements
- Current quantity
- Stock cost value
- Low-stock status

### Sales & Purchases
- Simple sale entry
- Simple purchase entry
- Cash / Bank / Credit
- COGS posting
- Inventory movement
- Customer / Supplier linkage

### Bank
- Multiple bank accounts
- Bank account master
- Book balance
- Statement balance check
- Reconciliation difference

### Accounting
Transactions post to:
Journal -> General Ledger -> Trial Balance -> P&L -> Balance Sheet

### Run
```bash
python -m app.main
```

### Build Windows EXE
```bash
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name BusinessAccounting app/main.py
```

### Important
This is a development/test build. Before production use, V7/V8 should add transaction editing/reversal, stronger validation, backups, period closing, detailed invoice lines, stock valuation policy, and audit controls.
