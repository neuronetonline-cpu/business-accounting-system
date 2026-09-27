from app.database import get_connection

def audit(event_type, reference="", description=""):
    con = get_connection()
    try:
        con.execute("INSERT INTO audit_log(event_type,reference,description) VALUES(?,?,?)",
                    (event_type, reference, description))
        con.commit()
    finally:
        con.close()
