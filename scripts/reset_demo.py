#!/usr/bin/env python3
"""Reset local SQLite Scheme Mitra state. Stop the app before running this script."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy.engine import make_url  # noqa: E402

from backend.config import DATABASE_URL  # noqa: E402


def main() -> int:
    url = make_url(DATABASE_URL)
    if not url.drivername.startswith("sqlite") or not url.database or url.database == ":memory:":
        raise SystemExit("Reset is allowed only for a file-backed SQLite development database; refusing to touch other databases.")
    db_path = Path(url.database)
    if not db_path.is_absolute():
        db_path = ROOT / db_path
    for suffix in ("", "-wal", "-shm"):
        target = Path(str(db_path) + suffix)
        if target.exists():
            target.unlink()
    print(f"Removed local database {db_path}. Start the app to recreate the synthetic demo seed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
