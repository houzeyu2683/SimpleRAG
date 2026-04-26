"""Seed initial admin account. Run after alembic upgrade head."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.init_db import main

if __name__ == "__main__":
    asyncio.run(main())
