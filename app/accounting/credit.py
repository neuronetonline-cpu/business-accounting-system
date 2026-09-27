
from app.database import get_connection
from app.accounting.engine import post_journal
from app.accounting.audit import audit

def create_customer_credit(customer_id, entry_date, reference, amount, due_date=None, description="Credit sale"):
    amount=float(amount)
    if amount<=0: raise ValueError("Amount must be greater than zero.")
    con=get_connection()
    try:
        row=con.execute("SELECT name FROM customers WHERE id=?",(customer_id,)).fetchone()
        if not row: raise ValueError("Customer not found.")
        jid=post_journal(entry_date,reference,description,
                         [("1100",amount,0),("4000",0,amount)],"CUSTOMER_CREDIT")
        con.execute("""INSERT INTO receivable_entries
            (customer_id,entry_date,reference,entry_type,debit,credit,due_date,journal_id)
            VALUES(?,?,?,?,?,?,?,?)""",
            (customer_id,entry_date,reference,"INVOICE",amount,0,due_date,jid))
        con.commit()
        audit("CUSTOMER_CREDIT", reference, f"Customer credit invoice posted: {row['name']} / Rs. {amount:,.2f}")
        return jid
    except:
        con.rollback()
        raise
    finally:
        con.close()

def create_customer_payment(customer_id, entry_date, reference, amount, account_code="1010", description="Customer payment"):
    amount=float(amount)
    if amount<=0: raise ValueError("Amount must be greater than zero.")
    con=get_connection()
    try:
        row=con.execute("SELECT name FROM customers WHERE id=?",(customer_id,)).fetchone()
        if not row: raise ValueError("Customer not found.")
        jid=post_journal(entry_date,reference,description,
                         [(account_code,amount,0),("1100",0,amount)],"CUSTOMER_PAYMENT")
        con.execute("""INSERT INTO receivable_entries
            (customer_id,entry_date,reference,entry_type,debit,credit,due_date,journal_id)
            VALUES(?,?,?,?,?,?,?,?)""",
            (customer_id,entry_date,reference,"PAYMENT",0,amount,None,jid))
        con.commit()
        audit("CUSTOMER_PAYMENT", reference, f"Customer payment posted: {row['name']} / Rs. {amount:,.2f}")
        return jid
    except:
        con.rollback()
        raise
    finally:
        con.close()

def create_supplier_credit(supplier_id, entry_date, reference, amount, due_date=None, description="Credit purchase"):
    amount=float(amount)
    if amount<=0: raise ValueError("Amount must be greater than zero.")
    con=get_connection()
    try:
        row=con.execute("SELECT name FROM suppliers WHERE id=?",(supplier_id,)).fetchone()
        if not row: raise ValueError("Supplier not found.")
        jid=post_journal(entry_date,reference,description,
                         [("1200",amount,0),("2000",0,amount)],"SUPPLIER_CREDIT")
        con.execute("""INSERT INTO payable_entries
            (supplier_id,entry_date,reference,entry_type,debit,credit,due_date,journal_id)
            VALUES(?,?,?,?,?,?,?,?)""",
            (supplier_id,entry_date,reference,"BILL",0,amount,due_date,jid))
        con.commit()
        audit("SUPPLIER_CREDIT", reference, f"Supplier credit invoice posted: {row['name']} / Rs. {amount:,.2f}")
        return jid
    except:
        con.rollback()
        raise
    finally:
        con.close()

def create_supplier_payment(supplier_id, entry_date, reference, amount, account_code="1010", description="Supplier payment"):
    amount=float(amount)
    if amount<=0: raise ValueError("Amount must be greater than zero.")
    con=get_connection()
    try:
        row=con.execute("SELECT name FROM suppliers WHERE id=?",(supplier_id,)).fetchone()
        if not row: raise ValueError("Supplier not found.")
        jid=post_journal(entry_date,reference,description,
                         [("2000",amount,0),(account_code,0,amount)],"SUPPLIER_PAYMENT")
        con.execute("""INSERT INTO payable_entries
            (supplier_id,entry_date,reference,entry_type,debit,credit,due_date,journal_id)
            VALUES(?,?,?,?,?,?,?,?)""",
            (supplier_id,entry_date,reference,"PAYMENT",amount,0,None,jid))
        con.commit()
        audit("SUPPLIER_PAYMENT", reference, f"Supplier payment posted: {row['name']} / Rs. {amount:,.2f}")
        return jid
    except:
        con.rollback()
        raise
    finally:
        con.close()

def customer_balance(customer_id):
    con=get_connection()
    r=con.execute("""SELECT COALESCE(SUM(debit-credit),0) balance
                     FROM receivable_entries WHERE customer_id=?""",(customer_id,)).fetchone()
    con.close()
    return r["balance"]

def supplier_balance(supplier_id):
    con=get_connection()
    r=con.execute("""SELECT COALESCE(SUM(credit-debit),0) balance
                     FROM payable_entries WHERE supplier_id=?""",(supplier_id,)).fetchone()
    con.close()
    return r["balance"]
