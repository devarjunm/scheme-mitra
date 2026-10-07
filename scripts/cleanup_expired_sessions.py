#!/usr/bin/env python3
"""Purge expired/revoked auth-session rows older than the configured retention period."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import delete, or_  # noqa: E402

from backend.db import SessionLocal  # noqa: E402
from backend.models import AuthSession  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retention-days", type=int, default=30, help="retain expired/revoked sessions for this many days (default: 30)")
    args = parser.parse_args()
    if args.retention_days < 1 or args.retention_days > 3650:
        parser.error("--retention-days must be between 1 and 3650")
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=args.retention_days)
    with SessionLocal() as db:
        result = db.execute(delete(AuthSession).where(or_(AuthSession.expires_at < cutoff, AuthSession.revoked_at < cutoff)))
        db.commit()
        print(f"Deleted {result.rowcount or 0} auth-session rows older than {args.retention_days} days.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
