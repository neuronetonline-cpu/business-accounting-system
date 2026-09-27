from pathlib import Path
from datetime import datetime
import sqlite3
from app.database import DB_PATH, APP_DIR, get_setting, set_setting

def get_backup_dir():
    raw = get_setting("backup_dir", str(APP_DIR / "backups"))
    path = Path(raw).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path

def set_backup_dir(path):
    path = Path(path).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    set_setting("backup_dir", str(path))
    return path

def create_backup():
    dest = get_backup_dir() / f"business_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    # SQLite backup API gives a consistent snapshot even when WAL is active.
    src = sqlite3.connect(DB_PATH)
    try:
        dst = sqlite3.connect(dest)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    return dest

def restore_backup(path):
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError("Backup file not found.")
    # Validate before replacing the active database.
    check = sqlite3.connect(source)
    try:
        check.execute("PRAGMA quick_check").fetchone()
    finally:
        check.close()
    # Close/reopen connections are handled by callers; this replacement is atomic.
    temp = DB_PATH.with_suffix('.restore.tmp')
    src = sqlite3.connect(source)
    try:
        dst = sqlite3.connect(temp)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    # Remove sidecar files belonging to the previous live database before swapping.
    for sidecar in (Path(str(DB_PATH) + '-wal'), Path(str(DB_PATH) + '-shm')):
        try:
            sidecar.unlink()
        except FileNotFoundError:
            pass
    Path(temp).replace(DB_PATH)
    return DB_PATH
