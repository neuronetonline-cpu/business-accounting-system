
from app.database import get_connection
from app.accounting.engine import post_journal

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
    con.execute("""INSERT INTO products(sku,name,category,brand,unit,cost_price,selling_price,reorder_level)
                   VALUES(?,?,?,?,?,?,?,?)""",(sku or None,name,category,brand,unit,cost,selling,reorder))
    con.commit(); con.close()

def create_purchase(purchase_date,bill_no,supplier_id,payment_type,items,paid=0):
    # items = [(product_id, qty, unit_cost)]
    subtotal=sum(q*c for _,q,c in items)
    due=max(0,subtotal-paid)
    debit_account="1200"  # inventory asset
    credit_account="1010" if payment_type=="Bank" else "1000" if payment_type=="Cash" else "2000"
    lines=[(debit_account,subtotal,0),(credit_account,0,subtotal)]
    jid=post_journal(purchase_date,bill_no,"Purchase","{}".format(""),"") if False else None
    # Use engine directly
    from app.accounting.engine import post_journal
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
        if supplier_id and payment_type=="Credit":
            cur.execute("""INSERT INTO payable_entries(supplier_id,entry_date,reference,entry_type,debit,credit,journal_id)
                           VALUES(?,?,?,?,?,?,?)""",(supplier_id,purchase_date,bill_no,"BILL",0,subtotal,jid))
        con.commit()
    except:
        con.rollback(); raise
    finally: con.close()
    return pid

def create_sale(sale_date,invoice_no,customer_id,payment_type,items,paid=0):
    subtotal=sum(q*p for _,q,p,_ in items)
    cost_total=sum(q*c for _,q,p,c in items)
    due=max(0,subtotal-paid)
    receipt_account="1010" if payment_type=="Bank" else "1000" if payment_type=="Cash" else "1100"
    from app.accounting.engine import post_journal
    # Revenue + COGS entry: Dr cash/AR, Cr sales; Dr COGS, Cr inventory
    jid=post_journal(sale_date,invoice_no,"Sale",
                     [(receipt_account,subtotal,0),(4000,0,subtotal),
                      (5000,cost_total,0),(1200,0,cost_total)],"SALE")
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
        if customer_id and payment_type=="Credit":
            cur.execute("""INSERT INTO receivable_entries(customer_id,entry_date,reference,entry_type,debit,credit,journal_id)
                           VALUES(?,?,?,?,?,?,?)""",(customer_id,sale_date,invoice_no,"INVOICE",subtotal,0,jid))
        con.commit()
    except:
        con.rollback(); raise
    finally: con.close()
    return sid
