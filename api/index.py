import os
import sys
import shutil
from pathlib import Path

# Add project root to sys.path so 'backend' module is discoverable
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Handle SQLite DB in Vercel's read-only serverless environment
db_src = root_dir / "backend" / "procureshield.db"
db_dst = Path("/tmp/procureshield.db")

if not db_dst.exists() and db_src.exists():
    try:
        shutil.copy2(str(db_src), str(db_dst))
    except Exception:
        pass

if db_dst.exists():
    os.environ["DATABASE_URL"] = f"sqlite:///{db_dst}"

from backend.app.main import app
