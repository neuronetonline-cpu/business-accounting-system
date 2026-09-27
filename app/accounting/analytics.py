
from app.database import get_connection

def kpis():
    con=get_connection()
    rows=con.execute("""SELECT a.account_type,
        COALESCE(SUM(l.debit),0) debit,COALESCE(SUM(l.credit),0) credit
        FROM accounts a LEFT JOIN journal_lines l ON a.id=l.account_id
        GROUP BY a.id""").fetchall()

    sales=sum(r["credit"]-r["debit"] for r in rows if r["account_type"]=="Revenue")
    expenses=sum(r["debit"]-r["credit"] for r in rows if r["account_type"]=="Expense")
    assets=sum(r["debit"]-r["credit"] for r in rows if r["account_type"]=="Asset")
    liabilities=sum(r["credit"]-r["debit"] for r in rows if r["account_type"]=="Liability")
    equity=sum(r["credit"]-r["debit"] for r in rows if r["account_type"]=="Equity")
    receivable=con.execute("SELECT COALESCE(SUM(debit-credit),0) b FROM receivable_entries").fetchone()["b"]
    payable=con.execute("SELECT COALESCE(SUM(credit-debit),0) b FROM payable_entries").fetchone()["b"]
    stock=con.execute("""SELECT COALESCE(SUM(CASE WHEN movement_type IN
      ('PURCHASE','OPENING','ADJUST_IN') THEN total_cost ELSE -total_cost END),0) v
      FROM stock_movements""").fetchone()["v"]
    low=con.execute("""SELECT COUNT(*) n FROM products p WHERE p.active=1 AND
      (SELECT COALESCE(SUM(CASE WHEN movement_type IN
      ('PURCHASE','OPENING','ADJUST_IN') THEN qty ELSE -qty END),0)
       FROM stock_movements m WHERE m.product_id=p.id) <= p.reorder_level""").fetchone()["n"]
    con.close()
    return {
      "sales":sales,"expenses":expenses,"profit":sales-expenses,
      "assets":assets,"liabilities":liabilities,"equity":equity,
      "receivables":receivable,"payables":payable,
      "inventory":stock,"low_stock":low
    }

def monthly_sales():
    con=get_connection()
    rows=con.execute("""SELECT substr(sale_date,1,7) month,
        COALESCE(SUM(subtotal),0) sales,COALESCE(SUM(cost_total),0) cogs
        FROM sales GROUP BY substr(sale_date,1,7) ORDER BY month""").fetchall()
    con.close()
    return rows
