#!/usr/bin/env python3
"""Promote/demote an existing account using a SUPER_ADMIN operator and write an audit log."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import func, select  # noqa: E402

from backend.db import SessionLocal  # noqa: E402
from backend.models import User  # noqa: E402
from backend.api.common import write_audit  # noqa: E402

ALLOWED_ROLES = {"FARMER", "DATA_VERIFIER", "ADMIN"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-email", required=True, help="email of an existing registered account")
    parser.add_argument("--actor-email", required=True, help="active SUPER_ADMIN operator email")
    parser.add_argument("--role", required=True, choices=sorted(ALLOWED_ROLES))
    parser.add_argument("--reason", required=True, help="auditable reason for the role change")
    args = parser.parse_args()
    if len(args.reason.strip()) < 4 or len(args.reason) > 500:
        parser.error("--reason must be between 4 and 500 characters")
    with SessionLocal() as db:
        actor = db.scalar(select(User).where(func.lower(User.email) == args.actor_email.lower(), User.is_active.is_(True)))
        target = db.scalar(select(User).where(func.lower(User.email) == args.target_email.lower()))
        if actor is None or actor.role != "SUPER_ADMIN":
            raise SystemExit("Refusing role change: --actor-email must identify an active SUPER_ADMIN.")
        if target is None:
            raise SystemExit("Target account not found. The user must register before role assignment.")
        if actor.id == target.id and args.role != "SUPER_ADMIN":
            active_admins = db.scalar(select(func.count(User.id)).where(User.role == "SUPER_ADMIN", User.is_active.is_(True))) or 0
            if active_admins <= 1:
                raise SystemExit("Refusing to remove the last active SUPER_ADMIN.")
        old_role = target.role
        target.role = args.role
        write_audit(db, actor, "USER_ROLE_CHANGED", "user", target.id,
                    {"role": old_role}, {"role": args.role}, args.reason.strip())
        db.commit()
        print(f"Updated account {target.id}: {old_role} -> {args.role}; change written to audit log.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
