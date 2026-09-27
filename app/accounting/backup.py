
from pathlib import Path
import shutil
from datetime import datetime
from app.database import DB_PATH, APP_DIR

BACKUP_DIR = APP_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

def create_backup():
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    dest=BACKUP_DIR/f"business_{stamp}.db"
    shutil.copy2(DB_PATH,dest)
    return dest

def restore_backup(path):
    source=Path(path)
    if not source.exists():
        raise FileNotFoundError("Backup file not found.")
    shutil.copy2(source,DB_PATH)
    return DB_PATH
