
import sqlite3
from pathlib import Path

APP_DIR = Path.home() / "BusinessAccountingSystem"
APP_DIR.mkdir(exist_ok=True)
DB_PATH = APP_DIR / "business.db"

def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA busy_timeout = 5000")
    con.execute("PRAGMA journal_mode = WAL")
    return con

def init_database():
    con=get_connection(); cur=con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS accounts(
      id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL, account_type TEXT NOT NULL, parent_code TEXT,
      active INTEGER NOT NULL DEFAULT 1);

    CREATE TABLE IF NOT EXISTS journal_entries(
      id INTEGER PRIMARY KEY AUTOINCREMENT, entry_date TEXT NOT NULL,
      reference TEXT, description TEXT NOT NULL,
      source_type TEXT NOT NULL DEFAULT 'MANUAL',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);

    CREATE TABLE IF NOT EXISTS journal_lines(
      id INTEGER PRIMARY KEY AUTOINCREMENT, journal_id INTEGER NOT NULL,
      account_id INTEGER NOT NULL, debit REAL NOT NULL DEFAULT 0,
      credit REAL NOT NULL DEFAULT 0,
      FOREIGN KEY(journal_id) REFERENCES journal_entries(id) ON DELETE CASCADE,
      FOREIGN KEY(account_id) REFERENCES accounts(id));

    CREATE TABLE IF NOT EXISTS customers(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT,
      address TEXT, credit_limit REAL DEFAULT 0, active INTEGER DEFAULT 1);

    CREATE TABLE IF NOT EXISTS suppliers(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT,
      address TEXT, credit_limit REAL DEFAULT 0, active INTEGER DEFAULT 1);

    CREATE TABLE IF NOT EXISTS receivable_entries(
      id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL,
      entry_date TEXT NOT NULL, reference TEXT, entry_type TEXT NOT NULL,
      debit REAL DEFAULT 0, credit REAL DEFAULT 0, due_date TEXT,
      journal_id INTEGER, FOREIGN KEY(customer_id) REFERENCES customers(id));

    CREATE TABLE IF NOT EXISTS payable_entries(
      id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_id INTEGER NOT NULL,
      entry_date TEXT NOT NULL, reference TEXT, entry_type TEXT NOT NULL,
      debit REAL DEFAULT 0, credit REAL DEFAULT 0, due_date TEXT,
      journal_id INTEGER, FOREIGN KEY(supplier_id) REFERENCES suppliers(id));

    CREATE TABLE IF NOT EXISTS products(
      id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT UNIQUE, name TEXT NOT NULL,
      category TEXT, brand TEXT, unit TEXT DEFAULT 'pcs',
      cost_price REAL DEFAULT 0, selling_price REAL DEFAULT 0,
      reorder_level REAL DEFAULT 0, active INTEGER DEFAULT 1);

    CREATE TABLE IF NOT EXISTS stock_movements(
      id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL,
      movement_date TEXT NOT NULL, reference TEXT, movement_type TEXT NOT NULL,
      qty REAL NOT NULL, unit_cost REAL DEFAULT 0, total_cost REAL DEFAULT 0,
      journal_id INTEGER, FOREIGN KEY(product_id) REFERENCES products(id));

    CREATE TABLE IF NOT EXISTS sales(
      id INTEGER PRIMARY KEY AUTOINCREMENT, sale_date TEXT NOT NULL,
      invoice_no TEXT, customer_id INTEGER, payment_type TEXT NOT NULL,
      subtotal REAL DEFAULT 0, cost_total REAL DEFAULT 0,
      paid REAL DEFAULT 0, due REAL DEFAULT 0,
      journal_id INTEGER, FOREIGN KEY(customer_id) REFERENCES customers(id));

    CREATE TABLE IF NOT EXISTS sale_items(
      id INTEGER PRIMARY KEY AUTOINCREMENT, sale_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL, qty REAL NOT NULL,
      unit_price REAL NOT NULL, unit_cost REAL DEFAULT 0,
      total REAL DEFAULT 0, cost_total REAL DEFAULT 0,
      FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
      FOREIGN KEY(product_id) REFERENCES products(id));

    CREATE TABLE IF NOT EXISTS purchases(
      id INTEGER PRIMARY KEY AUTOINCREMENT, purchase_date TEXT NOT NULL,
      bill_no TEXT, supplier_id INTEGER, payment_type TEXT NOT NULL,
      subtotal REAL DEFAULT 0, paid REAL DEFAULT 0, due REAL DEFAULT 0,
      journal_id INTEGER, FOREIGN KEY(supplier_id) REFERENCES suppliers(id));

    CREATE TABLE IF NOT EXISTS purchase_items(
      id INTEGER PRIMARY KEY AUTOINCREMENT, purchase_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL, qty REAL NOT NULL,
      unit_cost REAL NOT NULL, total REAL DEFAULT 0,
      FOREIGN KEY(purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
      FOREIGN KEY(product_id) REFERENCES products(id));

    CREATE TABLE IF NOT EXISTS bank_accounts(
      id INTEGER PRIMARY KEY AUTOINCREMENT, account_code TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL, bank_name TEXT, account_number TEXT,
      ledger_code TEXT UNIQUE, active INTEGER DEFAULT 1);

    CREATE TABLE IF NOT EXISTS cash_accounts(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL,
      ledger_code TEXT UNIQUE, active INTEGER DEFAULT 1);

    CREATE TABLE IF NOT EXISTS bank_reconciliations(
      id INTEGER PRIMARY KEY AUTOINCREMENT, bank_account_id INTEGER NOT NULL,
      statement_date TEXT NOT NULL, statement_balance REAL NOT NULL,
      book_balance REAL NOT NULL, difference REAL NOT NULL,
      status TEXT NOT NULL DEFAULT 'OPEN',
      FOREIGN KEY(bank_account_id) REFERENCES bank_accounts(id));

    CREATE TABLE IF NOT EXISTS accounting_periods(
      id INTEGER PRIMARY KEY AUTOINCREMENT, period_name TEXT NOT NULL,
      start_date TEXT NOT NULL, end_date TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'OPEN', UNIQUE(start_date,end_date));

    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);

    CREATE TABLE IF NOT EXISTS audit_log(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      event_type TEXT NOT NULL,
      reference TEXT,
      description TEXT
    );
    """)
    con.commit(); con.close()

def seed_accounts():
    accounts=[
      ("1000","Cash","Asset",None),
      ("1010","Bank - Main","Asset",None),
      ("1020","Bank - Other","Asset",None),
      ("1100","Accounts Receivable","Asset",None),
      ("1200","Inventory","Asset",None),
      ("1300","Other Current Assets","Asset",None),
      ("2000","Accounts Payable","Liability",None),
      ("2100","Other Payables","Liability",None),
      ("3000","Owner Capital","Equity",None),
      ("3100","Owner Drawings","Equity",None),
      ("4000","Sales Revenue","Revenue",None),
      ("4100","Other Income","Revenue",None),
      ("5000","Cost of Goods Sold","Expense",None),
      ("5100","Rent Expense","Expense",None),
      ("5200","Salary Expense","Expense",None),
      ("5300","Utilities Expense","Expense",None),
      ("5400","Advertising Expense","Expense",None),
      ("5500","Delivery Expense","Expense",None),
      ("5600","Other Expenses","Expense",None),
    ]
    con=get_connection()
    con.executemany("INSERT OR IGNORE INTO accounts(code,name,account_type,parent_code) VALUES(?,?,?,?)",accounts)
    con.commit(); con.close()
