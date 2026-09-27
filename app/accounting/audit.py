
from app.database import get_connection
from datetime import datetime

def audit(event_type, reference="", description=""):
    con=get_connection()
    con.execute("INSERT INTO audit_log(event_type,reference,description) VALUES(?,?,?)",
                (event_type,reference,description))
    con.commit(); con.close()
