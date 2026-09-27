
from app.database import get_connection

def account_id(con, code):
    row = con.execute("SELECT id FROM accounts WHERE code=?", (code,)).fetchone()
    if not row:
        raise ValueError(f"Account not found: {code}")
    return row["id"]

def post_journal(entry_date, reference, description, lines, source_type="MANUAL"):
    debit_total = round(sum(float(x[1]) for x in lines), 2)
    credit_total = round(sum(float(x[2]) for x in lines), 2)
    if debit_total <= 0 or credit_total <= 0 or abs(debit_total-credit_total) > 0.005:
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
            """, (jid, account_id(con, code), float(debit), float(credit)))
        con.commit()
        return jid
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def post_simple_transaction(entry_date, reference, description,
                            debit_account, credit_account, amount,
                            source_type="TRANSACTION"):
    amount = float(amount)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return post_journal(
        entry_date, reference, description,
        [(debit_account, amount, 0), (credit_account, 0, amount)],
        source_type
    )

def create_opening_balance(entry_date, balances, reference="OPENING"):
    con = get_connection()
    try:
        types = {}
        for code in balances:
            row = con.execute(
                "SELECT account_type FROM accounts WHERE code=?", (code,)
            ).fetchone()
            if not row:
                raise ValueError(f"Account not found: {code}")
            types[code] = row["account_type"]
    finally:
        con.close()

    debit_lines, credit_lines = [], []
    for code, value in balances.items():
        value = round(float(value), 2)
        if not value:
            continue
        normal_debit = types[code] in ("Asset", "Expense")
        if normal_debit:
            if value > 0: debit_lines.append((code,value,0))
            else: credit_lines.append((code,0,abs(value)))
        else:
            if value > 0: credit_lines.append((code,0,value))
            else: debit_lines.append((code,abs(value),0))

    difference = round(sum(x[1] for x in debit_lines)-sum(x[2] for x in credit_lines),2)
    if difference > 0: credit_lines.append(("3000",0,difference))
    elif difference < 0: debit_lines.append(("3000",abs(difference),0))

    return post_journal(entry_date,reference,"Opening balances",
                        debit_lines+credit_lines,"OPENING")

def get_latest_opening(con=None):
    own = con is None
    con = con or get_connection()
    try:
        row = con.execute("SELECT id,entry_date,reference,description FROM journal_entries WHERE source_type='OPENING' ORDER BY entry_date DESC,id DESC LIMIT 1").fetchone()
        if not row: return None
        lines = con.execute("""SELECT l.id,a.code,a.name,l.debit,l.credit FROM journal_lines l JOIN accounts a ON a.id=l.account_id WHERE l.journal_id=? ORDER BY l.id""",(row['id'],)).fetchall()
        return {'id':row['id'],'entry_date':row['entry_date'],'reference':row['reference'] or 'OPENING','description':row['description'],'lines':lines}
    finally:
        if own: con.close()

def update_opening_balance(journal_id, entry_date, balances):
    con=get_connection()
    try:
        row=con.execute("SELECT id,source_type FROM journal_entries WHERE id=?",(journal_id,)).fetchone()
        if not row or row['source_type']!='OPENING': raise ValueError('Only an opening-balance journal can be edited here.')
        types={}
        for code in balances:
            a=con.execute('SELECT account_type FROM accounts WHERE code=?',(code,)).fetchone()
            if not a: raise ValueError(f'Account not found: {code}')
            types[code]=a['account_type']
        debit=[];credit=[]
        for code,value in balances.items():
            value=round(float(value),2)
            if not value: continue
            normal=types[code] in ('Asset','Expense')
            if normal:
                (debit if value>0 else credit).append((code,abs(value),0) if value>0 else (code,0,abs(value)))
            else:
                (credit if value>0 else debit).append((code,0,value) if value>0 else (code,abs(value),0))
        diff=round(sum(x[1] for x in debit)-sum(x[2] for x in credit),2)
        if diff>0: credit.append(('3000',0,diff))
        elif diff<0: debit.append(('3000',abs(diff),0))
        con.execute('UPDATE journal_entries SET entry_date=? WHERE id=?',(entry_date,journal_id))
        con.execute('DELETE FROM journal_lines WHERE journal_id=?',(journal_id,))
        for code,d,c in debit+credit:
            con.execute('INSERT INTO journal_lines(journal_id,account_id,debit,credit) VALUES(?,?,?,?)',(journal_id,account_id(con,code),d,c))
        con.commit()
    except Exception:
        con.rollback(); raise
    finally: con.close()

def update_manual_journal(journal_id, entry_date, reference, description, lines):
    debit_total=round(sum(float(x[1]) for x in lines),2); credit_total=round(sum(float(x[2]) for x in lines),2)
    if debit_total<=0 or abs(debit_total-credit_total)>0.005: raise ValueError('Journal must be balanced and have a debit amount.')
    con=get_connection()
    try:
        row=con.execute("SELECT source_type FROM journal_entries WHERE id=?",(journal_id,)).fetchone()
        if not row: raise ValueError('Journal entry not found.')
        if row['source_type'] not in ('MANUAL','TRANSACTION'):
            raise ValueError('System-generated sales, purchases, credit and opening entries cannot be edited here. Use the original transaction screen.')
        if row['source_type']=='TRANSACTION':
            # Transaction screen entries are safe to edit only when they have no linked operational record.
            linked=con.execute("""SELECT (SELECT COUNT(*) FROM sales WHERE journal_id=?)+(SELECT COUNT(*) FROM purchases WHERE journal_id=?)+
            (SELECT COUNT(*) FROM receivable_entries WHERE journal_id=?)+(SELECT COUNT(*) FROM payable_entries WHERE journal_id=?)+
            (SELECT COUNT(*) FROM stock_movements WHERE journal_id=?) n""",(journal_id,journal_id,journal_id,journal_id,journal_id)).fetchone()['n']
            if linked: raise ValueError('This journal is linked to a sale, purchase, credit or stock transaction. Edit it from the original transaction screen.')
        con.execute('UPDATE journal_entries SET entry_date=?,reference=?,description=? WHERE id=?',(entry_date,reference,description,journal_id))
        con.execute('DELETE FROM journal_lines WHERE journal_id=?',(journal_id,))
        for code,d,c in lines:
            con.execute('INSERT INTO journal_lines(journal_id,account_id,debit,credit) VALUES(?,?,?,?)',(journal_id,account_id(con,code),float(d),float(c)))
        con.commit()
    except Exception:
        con.rollback(); raise
    finally: con.close()
