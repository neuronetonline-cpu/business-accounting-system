
from datetime import date
from app.database import get_connection

def account_id(con, code):
    row = con.execute("SELECT id FROM accounts WHERE code=?", (code,)).fetchone()
    if not row:
        raise ValueError(f"Account not found: {code}")
    return row["id"]

def post_journal(entry_date, reference, description, lines, source_type="MANUAL"):
    """
    lines: list of (account_code, debit, credit)
    """
    debit_total = round(sum(x[1] for x in lines), 2)
    credit_total = round(sum(x[2] for x in lines), 2)
    if debit_total != credit_total:
        raise ValueError(f"Unbalanced journal: debit={debit_total}, credit={credit_total}")

    con = get_connection()
    try:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO journal_entries(entry_date,reference,description,source_type)
            VALUES(?,?,?,?)
        """, (entry_date, reference, description, source_type))
        jid = cur.lastrowid

        for code, debit, credit in lines:
            cur.execute("""
                INSERT INTO journal_lines(journal_id,account_id,debit,credit)
                VALUES(?,?,?,?)
            """, (jid, account_id(con, code), debit, credit))

        con.commit()
        return jid
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def create_opening_balance(entry_date, balances, reference="OPENING"):
    """
    balances: dict {account_code: signed_balance}
    Asset/Expense positive = debit.
    Liability/Equity/Revenue positive = credit.
    """
    con = get_connection()
    try:
        rows = {}
        for code in balances:
            row = con.execute(
                "SELECT account_type FROM accounts WHERE code=?", (code,)
            ).fetchone()
            if not row:
                raise ValueError(f"Account not found: {code}")
            rows[code] = row["account_type"]
    finally:
        con.close()

    debit_lines, credit_lines = [], []
    for code, value in balances.items():
        value = round(float(value), 2)
        if not value:
            continue
        typ = rows[code]
        normal_debit = typ in ("Asset", "Expense")
        if normal_debit:
            if value >= 0:
                debit_lines.append((code, value, 0))
            else:
                credit_lines.append((code, 0, abs(value)))
        else:
            if value >= 0:
                credit_lines.append((code, 0, value))
            else:
                debit_lines.append((code, abs(value), 0))

    total_d = sum(x[1] for x in debit_lines)
    total_c = sum(x[2] for x in credit_lines)

    # Automatically balance opening position through Owner Capital.
    difference = round(total_d - total_c, 2)
    if difference > 0:
        credit_lines.append(("3000", 0, difference))
    elif difference < 0:
        debit_lines.append(("3000", abs(difference), 0))

    return post_journal(
        entry_date, reference, "Opening balances", debit_lines + credit_lines,
        source_type="OPENING"
    )
