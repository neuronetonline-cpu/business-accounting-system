
from pathlib import Path
import shutil
from datetime import datetime
from app.database import DB_PATH, APP_DIR
from app.accounting.audit import audit

BACKUP_DIR = APP_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

def create_backup():
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    dest=BACKUP_DIR/f"business_{stamp}.db"
    shutil.copy2(DB_PATH,dest)
    audit("BACKUP_CREATED", dest.name, f"Database backup created: {dest.name}")
    return dest

def restore_backup(path):
    source=Path(path)
    if not source.exists():
        raise FileNotFoundError("Backup file not found.")
    shutil.copy2(source,DB_PATH)
    # Log the restore into the restored database so the action is retained.
    audit("BACKUP_RESTORED", source.name, f"Database restored from: {source.name}")
    return DB_PATH
