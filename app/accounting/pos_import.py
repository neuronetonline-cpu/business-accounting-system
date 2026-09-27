import re
from datetime import datetime
from pathlib import Path
from app.database import get_connection
from app.accounting.engine import post_journal
from app.accounting.audit import audit

MONEY_RE = re.compile(r"^\(?-?[\d,]+(?:\.\d+)?\)?%?$")
TX_RE = re.compile(r"^\d{15}$")
BILL_RE = re.compile(r"^\d{6}$")


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def money(s):
    s = str(s or "").replace("Rs.", "").replace(",", "").replace(" ", "")
    s = s.replace("%", "").replace("(", "").replace(")", "")
    return float(s or 0)


def _page_words(pdf_path):
    import pdfplumber
    out=[]
    with pdfplumber.open(pdf_path) as pdf:
        for page_no,page in enumerate(pdf.pages,1):
            for w in page.extract_words():
                w['page']=page_no
                out.append(w)
    return out


def _group_blocks(words):
    starts=[i for i,w in enumerate(words) if TX_RE.fullmatch(w['text'])]
    blocks=[]
    for n,i in enumerate(starts):
        j=starts[n+1] if n+1<len(starts) else len(words)
        block=words[max(0,i-15):j]
        tx_word=words[i]
        after=words[i:min(i+35,j)]
        bill=next((w['text'] for w in after if BILL_RE.fullmatch(w['text'])), None)
        if bill:
            blocks.append((tx_word['text'],bill,block,tx_word['page'],float(tx_word['top'])))
    return blocks


def _item_rows(block, start_page=None, start_y=None):
    sales=[]; qtys=[]; costs=[]
    for w in block:
        x=w['x0']; y=float(w['top']); t=w['text']
        if start_page is not None and (w['page']<start_page or (w['page']==start_page and y < start_y-2)): continue
        clean=t.replace('Rs.','')
        if 338 <= x < 390 and MONEY_RE.fullmatch(clean) and not t.startswith('('):
            try: sales.append((w['page'],y,money(t)))
            except Exception: pass
        if 389 <= x < 412 and re.fullmatch(r"\d+(?:\.\d+)?",t): qtys.append((w['page'],y,float(t)))
        if 272 <= x < 309 and re.fullmatch(r"-?[\d,]+(?:\.\d+)?",clean):
            try: costs.append((w['page'],y,money(t)))
            except Exception: pass
    rows=[]
    for pg,sy,sv in sales:
        qmatches=[q for q in qtys if q[0]==pg and abs(q[1]-sy)<=7]
        if not qmatches: continue
        q=min(qmatches,key=lambda q:abs(q[1]-sy))
        cmatches=[c for c in costs if c[0]==pg and abs(c[1]-sy)<=7]
        cost=min(cmatches,key=lambda c:abs(c[1]-sy))[2] if cmatches else 0.0
        if q[2]>0: rows.append({'page':pg,'y':(sy+q[1])/2,'sale':sv,'qty':q[2],'unit_cost':cost})
    rows.sort(key=lambda r:(r['page'],r['y']))
    return rows


def _product_words(block, row, prev_y=None, next_y=None):
    pg=row['page']; y=row['y']
    lo=y-20; hi=y+20
    ws=[w for w in block if w['page']==pg and 142<=w['x0']<215 and lo<=w['top']<=hi]
    return " ".join(w['text'] for w in sorted(ws,key=lambda z:(z['top'],z['x0'])))


def _match_product(text, products):
    nt=norm(text)
    if not nt: return None, text, 0
    exact=[p for p in products if norm(p['name'])==nt]
    if exact: return exact[0], text, 1.0
    best=None; best_score=0
    for p in products:
        np=norm(p['name'])
        if not np: continue
        if np in nt:
            score=len(np)/max(len(nt),1)
        elif nt in np:
            score=len(nt)/max(len(np),1)*0.85
        else:
            a=set(nt.split()); b=set(np.split())
            score=max(len(a&b)/max(len(b),1), len(a&b)/max(len(a),1))*0.92
        if score>best_score:
            best_score=score; best=p
    return (best,text,best_score) if best_score>=0.60 else (None,text,best_score)


def _bill_meta(block, start_page=None, start_y=None):
    rows=_item_rows(block,start_page,start_y)
    if not rows: return 'CASH'
    pg=rows[0]['page']; y=rows[0]['y']
    payment_words=[]
    for w in block:
        if w['page']==pg and 425<=w['x0']<500 and y-18<=w['top']<=y+18:
            payment_words.append(w['text'])
    p=' '.join(payment_words).lower()
    if 'bank' in p or 'transfer' in p or 'diposit' in p: return 'BANK'
    if 'card' in p: return 'CARD'
    if 'credit' in p: return 'CREDIT'
    if 'cash' in p and 'delivery' in p: return 'COD'
    if 'delivery' in p: return 'COD'
    return 'CASH'


def parse_sales_pdf(pdf_path):
    words=_page_words(pdf_path)
    blocks=_group_blocks(words)
    con=get_connection()
    products=[dict(r) for r in con.execute('SELECT id,name,sku,cost_price,selling_price FROM products WHERE active=1').fetchall()]
    con.close()
    result=[]
    for tx,bill,block,start_page,start_y in blocks:
        rows=_item_rows(block,start_page,start_y)
        if not rows: continue
        items=[]; unresolved=[]
        for i,row in enumerate(rows):
            prev_y=rows[i-1]['y'] if i else None
            next_y=rows[i+1]['y'] if i+1<len(rows) else None
            ptext=_product_words(block,row,prev_y,next_y)
            p,_,score=_match_product(ptext,products)
            item={'product_text':ptext,'qty':row['qty'],'gross':row['sale'],'unit_cost':row['unit_cost'],'product_id':p['id'] if p else None,'match_score':score}
            if not p: unresolved.append(ptext)
            items.append(item)
        # Total column: last monetary value in x >= 540 is the bill total.
        totals=[]
        for w in block:
            if w['x0']>=538 and MONEY_RE.fullmatch(w['text'].replace('Rs.','')):
                try: totals.append((w['page'],w['top'],money(w['text'])))
                except Exception: pass
        bill_total=totals[-1][2] if totals else round(sum(x['gross'] for x in items),2)
        gross_total=round(sum(x['gross']*x['qty'] for x in items),2)
        discount=round(gross_total-bill_total,2)
        customer_tokens=[]
        if rows:
            fy=rows[0]['y']; fpg=rows[0]['page']
            for w in block:
                if w['page']==fpg and 215<=w['x0']<272 and fy-16<=w['top']<=fy+16:
                    if norm(w['text']) not in ('rs',''):
                        customer_tokens.append((w['top'],w['x0'],w['text']))
        customer_name=' '.join(x[2] for x in sorted(customer_tokens,key=lambda z:(z[0],z[1]))).strip()
        result.append({'transaction_id':tx,'bill_no':bill,'payment_type':_bill_meta(block,start_page,start_y),'customer_name':customer_name,'gross_total':gross_total,'final_discount':discount,'total':bill_total,'items':items,'unresolved':unresolved})
    return result


def import_sales(parsed, bank_code='1010', card_code='1030', cod_code='1040'):
    imported=0; skipped=0; errors=[]
    for s in parsed:
        con=get_connection()
        try:
            exists=con.execute('SELECT id FROM sales WHERE invoice_no=?',(s['bill_no'],)).fetchone()
            if exists:
                skipped+=1; continue
            if s['unresolved']:
                raise ValueError('Unmatched product(s): '+', '.join(s['unresolved'][:3]))
            customer_id=None
            # Customer names are deliberately not auto-created from PDF text yet;
            # the import remains safe and customer credit can be mapped later.
            paid=s['total'] if s['payment_type'] in ('CASH','BANK','CARD') else 0
            due=s['total'] if s['payment_type'] in ('CREDIT','COD') else 0
            if s['payment_type']=='BANK': receipt=bank_code
            elif s['payment_type']=='CARD': receipt=card_code
            elif s['payment_type']=='COD': receipt=cod_code
            elif s['payment_type']=='CASH': receipt='1000'
            else: receipt='1100'
            cost_total=round(sum(i['qty'] * (next((float(p['cost_price']) for p in []),0)) for i in []),2)
            item_data=[]
            for i in s['items']:
                p=con.execute('SELECT cost_price FROM products WHERE id=?',(i['product_id'],)).fetchone()
                if not p: raise ValueError('Product no longer exists.')
                cost=float(i['unit_cost']) if 'unit_cost' in i else float(p['cost_price'] or 0)
                item_data.append((i['product_id'],i['qty'],i['gross']/i['qty'] if i['qty'] else 0,cost))
                cost_total += i['qty']*cost
            # Use net bill total after POS final discount for revenue; COGS remains item cost.
            lines=[]
            if paid: lines.append((receipt,paid,0))
            if due: lines.append((receipt if s['payment_type']=='COD' else '1100',due,0))
            lines += [('4000',0,s['total']),('5000',cost_total,0),('1200',0,cost_total)]
            jid=post_journal(datetime.strptime(s['transaction_id'][:6],'%y%m%d').date().isoformat(),s['bill_no'],'POS Sale',lines,'POS_SALE')
            con.execute('INSERT INTO sales(sale_date,invoice_no,customer_id,payment_type,subtotal,cost_total,paid,due,journal_id) VALUES(?,?,?,?,?,?,?,?,?)',
                        (datetime.strptime(s['transaction_id'][:6],'%y%m%d').date().isoformat(),s['bill_no'],customer_id,s['payment_type'],s['total'],cost_total,paid,due,jid))
            sid=con.execute('SELECT last_insert_rowid()').fetchone()[0]
            for i in item_data:
                pid,qty,price,cost=i
                con.execute('INSERT INTO sale_items(sale_id,product_id,qty,unit_price,unit_cost,total,cost_total) VALUES(?,?,?,?,?,?,?)',(sid,pid,qty,price,cost,qty*price,qty*cost))
                con.execute('INSERT INTO stock_movements(product_id,movement_date,reference,movement_type,qty,unit_cost,total_cost,journal_id) VALUES(?,?,?,?,?,?,?,?)',(pid,datetime.strptime(s['transaction_id'][:6],'%y%m%d').date().isoformat(),s['bill_no'],'SALE',qty,cost,qty*cost,jid))
            if due and s['payment_type']=='CREDIT':
                cname=(s.get('customer_name') or 'POS CREDIT CUSTOMER').strip()
                row=con.execute('SELECT id FROM customers WHERE lower(name)=lower(?)',(cname,)).fetchone()
                if not row:
                    con.execute('INSERT INTO customers(name,credit_limit) VALUES(?,?)',(cname,0)); customer_id=con.execute('SELECT last_insert_rowid()').fetchone()[0]
                else: customer_id=row['id']
                con.execute('UPDATE sales SET customer_id=? WHERE id=?',(customer_id,sid))
                con.execute('INSERT INTO receivable_entries(customer_id,entry_date,reference,entry_type,debit,credit,journal_id) VALUES(?,?,?,?,?,?,?)',(customer_id,datetime.strptime(s['transaction_id'][:6],'%y%m%d').date().isoformat(),s['bill_no'],'INVOICE',due,0,jid))
            con.commit(); imported+=1
            audit('POS_SALE_IMPORT',s['bill_no'],f"Imported POS sale / Rs. {s['total']:,.2f}")
        except Exception as e:
            con.rollback(); errors.append(f"{s['bill_no']}: {e}")
        finally: con.close()
    return imported, skipped, errors


def opening_stock_value(opening_date):
    con=get_connection()
    try:
        r=con.execute("SELECT COALESCE(SUM(total_cost),0) v FROM stock_movements WHERE movement_date=? AND movement_type='OPENING'",(opening_date,)).fetchone()
        return round(float(r['v'] or 0),2)
    finally: con.close()


def import_opening_stock_xlsx(path, opening_date):
    from openpyxl import load_workbook
    wb=load_workbook(path,data_only=True,read_only=True); ws=wb.active
    rows=ws.iter_rows(values_only=True)
    header=next(rows,None)
    if not header: raise ValueError('Empty stock workbook.')
    idx={str(v or '').strip().lower():i for i,v in enumerate(header)}
    def col(*names):
        for n in names:
            if n in idx: return idx[n]
        return None
    name_i=col('name','product name'); sku_i=col('barcode','sku'); cost_i=col('cost price','cost'); sale_i=col('sale price','selling price'); qty_i=col('total stock','qty(price wise)','quantity')
    if name_i is None or qty_i is None: raise ValueError('Stock Excel must contain NAME and TOTAL STOCK/QTY columns.')
    con=get_connection(); created=updated=0; total_value=0; count=0
    try:
        for row in rows:
            if not row or name_i>=len(row) or not row[name_i]: continue
            name=str(row[name_i]).strip(); sku=str(row[sku_i] or '').strip() if sku_i is not None else ''
            qty=float(str(row[qty_i] or 0).replace(',',''))
            cost=float(str(row[cost_i] or 0).replace(',','')) if cost_i is not None else 0
            sale=float(str(row[sale_i] or 0).replace(',','')) if sale_i is not None else 0
            if qty < 0: raise ValueError(f'Negative opening stock for {name}.')
            product=None
            if sku: product=con.execute('SELECT * FROM products WHERE sku=?',(sku,)).fetchone()
            if not product: product=con.execute('SELECT * FROM products WHERE lower(name)=lower(?)',(name,)).fetchone()
            if product:
                pid=product['id']; con.execute("UPDATE products SET sku=COALESCE(NULLIF(sku,''),?), cost_price=CASE WHEN cost_price=0 THEN ? ELSE cost_price END, selling_price=CASE WHEN selling_price=0 THEN ? ELSE selling_price END WHERE id=?",(sku or None,cost,sale,pid)); updated+=1
            else:
                con.execute('INSERT INTO products(sku,name,cost_price,selling_price) VALUES(?,?,?,?)',(sku or None,name,cost,sale)); pid=con.execute('SELECT last_insert_rowid()').fetchone()[0]; created+=1
            # Replace an existing OPENING movement for the same product/date so re-import is safe.
            old=con.execute("SELECT id FROM stock_movements WHERE product_id=? AND movement_date=? AND movement_type='OPENING'",(pid,opening_date)).fetchall()
            if old:
                con.execute("DELETE FROM stock_movements WHERE product_id=? AND movement_date=? AND movement_type='OPENING'",(pid,opening_date))
            total=round(qty*cost,2); total_value += total; count += 1
            if qty:
                con.execute('INSERT INTO stock_movements(product_id,movement_date,reference,movement_type,qty,unit_cost,total_cost) VALUES(?,?,?,?,?,?,?)',(pid,opening_date,'OPENING-STOCK','OPENING',qty,cost,total))
        con.commit()
    except Exception:
        con.rollback(); raise
    finally: con.close()
    actual_value=opening_stock_value(opening_date)
    audit('OPENING_STOCK_IMPORT',Path(path).name,f'Opening stock imported: {count} product row(s), value Rs. {actual_value:,.2f}')
    return {'count':count,'created':created,'updated':updated,'value':actual_value}
