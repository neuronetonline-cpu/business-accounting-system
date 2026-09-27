from app.database import get_connection
from app.accounting.engine import post_journal
from app.accounting.audit import audit

def product_balance(product_id):
    con=get_connection()
    r=con.execute("""SELECT COALESCE(SUM(CASE WHEN movement_type IN
    ('PURCHASE','OPENING','ADJUST_IN') THEN qty ELSE -qty END),0) q,
    COALESCE(SUM(CASE WHEN movement_type IN ('PURCHASE','OPENING','ADJUST_IN')
    THEN total_cost ELSE -total_cost END),0) c FROM stock_movements WHERE product_id=?""",(product_id,)).fetchone()
    con.close()
    return r["q"],r["c"]

def add_product(sku,name,category,brand,unit,cost,selling,reorder):
    con=get_connection()
    try:
        con.execute("""INSERT INTO products(sku,name,category,brand,unit,cost_price,selling_price,reorder_level)
                       VALUES(?,?,?,?,?,?,?,?)""",(sku or None,name,category,brand,unit,cost,selling,reorder))
        con.commit()
    finally:
        con.close()
    audit("PRODUCT_ADD", sku or "", f"Product added: {name}")

def create_purchase(purchase_date,bill_no,supplier_id,payment_type,items,paid=0):
    if not items: raise ValueError("At least one purchase item is required.")
    subtotal=round(sum(q*c for _,q,c in items),2)
    paid=float(paid or 0)
    if paid<0 or paid>subtotal: raise ValueError("Paid amount must be between 0 and the purchase total.")
    if payment_type=="Credit" and not supplier_id:
        raise ValueError("Select a supplier for a credit purchase.")
    due=round(subtotal-paid,2)
    if due>0 and not supplier_id:
        raise ValueError("Select a supplier when the purchase has an unpaid balance.")
    for product_id,qty,cost in items:
        if qty<=0 or cost<0:
            raise ValueError("Purchase quantity must be greater than zero and cost cannot be negative.")
    lines=[]
    if paid>0:
        account="1010" if payment_type=="Bank" else "1000"
        lines.append((account,paid,0))
    if due>0:
        lines.append(("2000",due,0))
    lines.append(("1200",0,subtotal))
    # Purchase should debit Inventory and credit cash/bank/payable.
    lines=[("1200",subtotal,0)] + ([("1010" if payment_type=="Bank" else "1000",0,paid)] if paid else []) + ([("2000",0,due)] if due else [])
    jid=post_journal(purchase_date,bill_no,"Purchase",lines,"PURCHASE")
    con=get_connection()
    try:
        cur=con.cursor()
        cur.execute("""INSERT INTO purchases(purchase_date,bill_no,supplier_id,payment_type,subtotal,paid,due,journal_id)
                       VALUES(?,?,?,?,?,?,?,?)""",(purchase_date,bill_no,supplier_id,payment_type,subtotal,paid,due,jid))
        pid=cur.lastrowid
        for product_id,qty,cost in items:
            total=qty*cost
            cur.execute("""INSERT INTO purchase_items(purchase_id,product_id,qty,unit_cost,total)
                           VALUES(?,?,?,?,?)""",(pid,product_id,qty,cost,total))
            cur.execute("""INSERT INTO stock_movements(product_id,movement_date,reference,movement_type,qty,unit_cost,total_cost,journal_id)
                           VALUES(?,?,?,?,?,?,?,?)""",(product_id,purchase_date,bill_no,"PURCHASE",qty,cost,total,jid))
        if supplier_id and due>0:
            cur.execute("""INSERT INTO payable_entries(supplier_id,entry_date,reference,entry_type,debit,credit,journal_id)
                           VALUES(?,?,?,?,?,?,?)""",(supplier_id,purchase_date,bill_no,"BILL",0,due,jid))
        con.commit()
    except:
        con.rollback(); raise
    finally: con.close()
    audit("PURCHASE", bill_no, f"Purchase posted / Rs. {subtotal:,.2f}")
    return pid

def create_sale(sale_date,invoice_no,customer_id,payment_type,items,paid=0):
    if not items: raise ValueError("At least one sale item is required.")
    subtotal=round(sum(q*p for _,q,p,_ in items),2)
    cost_total=round(sum(q*c for _,q,p,c in items),2)
    paid=float(paid or 0)
    if paid<0 or paid>subtotal: raise ValueError("Paid amount must be between 0 and the sale total.")
    if payment_type=="Credit" and not customer_id:
        raise ValueError("Select a customer for a credit sale.")
    due=round(subtotal-paid,2)
    if due>0 and not customer_id:
        raise ValueError("Select a customer when the sale has an unpaid balance.")
    con=get_connection()
    try:
        for product_id,qty,price,cost in items:
            if qty<=0 or price<0 or cost<0: raise ValueError("Sale quantity must be greater than zero and prices cannot be negative.")
            q,_=product_balance(product_id)
            if q < qty:
                raise ValueError(f"Insufficient stock. Available: {q:g}, requested: {qty:g}.")
    finally:
        con.close()
    lines=[]
    if paid>0:
        account="1010" if payment_type=="Bank" else "1000"
        lines.append((account,paid,0))
    if due>0:
        lines.append(("1100",due,0))
    lines.append(("4000",0,subtotal))
    lines.append(("5000",cost_total,0))
    lines.append(("1200",0,cost_total))
    jid=post_journal(sale_date,invoice_no,"Sale",lines,"SALE")
    con=get_connection()
    try:
        cur=con.cursor()
        cur.execute("""INSERT INTO sales(sale_date,invoice_no,customer_id,payment_type,subtotal,cost_total,paid,due,journal_id)
                       VALUES(?,?,?,?,?,?,?,?,?)""",(sale_date,invoice_no,customer_id,payment_type,subtotal,cost_total,paid,due,jid))
        sid=cur.lastrowid
        for product_id,qty,price,cost in items:
            cur.execute("""INSERT INTO sale_items(sale_id,product_id,qty,unit_price,unit_cost,total,cost_total)
                           VALUES(?,?,?,?,?,?,?)""",(sid,product_id,qty,price,cost,qty*price,qty*cost))
            cur.execute("""INSERT INTO stock_movements(product_id,movement_date,reference,movement_type,qty,unit_cost,total_cost,journal_id)
                           VALUES(?,?,?,?,?,?,?,?)""",(product_id,sale_date,invoice_no,"SALE",qty,cost,qty*cost,jid))
        if customer_id and due>0:
            cur.execute("""INSERT INTO receivable_entries(customer_id,entry_date,reference,entry_type,debit,credit,journal_id)
                           VALUES(?,?,?,?,?,?,?)""",(customer_id,sale_date,invoice_no,"INVOICE",due,0,jid))
        con.commit()
    except:
        con.rollback(); raise
    finally: con.close()
    audit("SALE", invoice_no, f"Sale posted / Rs. {subtotal:,.2f}")
    return sid
