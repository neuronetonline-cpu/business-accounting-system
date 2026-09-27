
import sqlite3
from pathlib import Path

APP_DIR = Path.home() / "BusinessAccountingSystem"
APP_DIR.mkdir(exist_ok=True)
DB_PATH = APP_DIR / "business.db"

def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_database():
    con = get_connection()
    cur = con.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        account_type TEXT NOT NULL,
        parent_code TEXT,
        active INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date TEXT NOT NULL,
        reference TEXT,
        description TEXT NOT NULL,
        source_type TEXT NOT NULL DEFAULT 'MANUAL',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS journal_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journal_id INTEGER NOT NULL,
        account_id INTEGER NOT NULL,
        debit REAL NOT NULL DEFAULT 0,
        credit REAL NOT NULL DEFAULT 0,
        FOREIGN KEY(journal_id) REFERENCES journal_entries(id) ON DELETE CASCADE,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    );

    CREATE TABLE IF NOT EXISTS accounting_periods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_name TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OPEN',
        UNIQUE(start_date, end_date)
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    con.commit()
    con.close()

def seed_accounts():
    accounts = [
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
    con = get_connection()
    con.executemany(
        "INSERT OR IGNORE INTO accounts(code,name,account_type,parent_code) VALUES(?,?,?,?)",
        accounts
    )
    con.commit()
    con.close()
