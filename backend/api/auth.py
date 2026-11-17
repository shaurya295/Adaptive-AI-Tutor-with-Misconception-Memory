"""
auth.py
-------
Sign-in and server-side sessions for the web API.

The UI signs in with an email address only (as the reference design shows).
That identifies a person but does not prove it, so this module adds the part
that matters for safety: after sign-in the server issues a random session
token in an HttpOnly cookie, remembers who it belongs to and what role they
have, and every API route checks it. A student can only read and change their
own data; teacher-only routes need a teacher session.

Who counts as a teacher (settings in .env):
    TEACHER_EMAILS          comma-separated exact addresses, always teachers
    TEACHER_EMAIL_DOMAINS   comma-separated domain endings
                            (default: .edu, .ac.in, .ac.uk, .edu.au, .k12.us)
"""

from __future__ import annotations

import hashlib
import os
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import HTTPException, Request, Response
from sqlalchemy import Column, DateTime, MetaData, String, Table, delete, select

from backend.memory.db import get_engine

load_dotenv()

COOKIE_NAME = "tutor_session"
SESSION_DAYS = 7
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_DEFAULT_TEACHER_DOMAINS = ".edu,.ac.in,.ac.uk,.edu.au,.k12.us"


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(x.strip().lower() for x in os.getenv(name, default).split(",") if x.strip())


TEACHER_EMAILS = _csv("TEACHER_EMAILS")
TEACHER_DOMAINS = _csv("TEACHER_EMAIL_DOMAINS", _DEFAULT_TEACHER_DOMAINS)

_engine = get_engine()
_metadata = MetaData()
auth_sessions = Table(
    "auth_sessions",
    _metadata,
    Column("token_hash", String(64), primary_key=True),
    Column("email", String(256), nullable=False, index=True),
    Column("role", String(16), nullable=False),
    Column("expires_at", DateTime, nullable=False),
)
_metadata.create_all(_engine)


@dataclass(frozen=True)
class Caller:
    email: str
    role: str

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"


def is_valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email))


def infer_role(email: str) -> str:
    email = email.lower()
    if email in TEACHER_EMAILS:
        return "teacher"
    domain = email.rsplit("@", 1)[-1]
    return "teacher" if any(domain.endswith(s) for s in TEACHER_DOMAINS) else "student"


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)     # stored as naive UTC


def start_session(response: Response, email: str, role: str) -> None:
    token = secrets.token_urlsafe(32)
    with _engine.begin() as conn:
        conn.execute(delete(auth_sessions).where(auth_sessions.c.expires_at < _now()))
        conn.execute(
            auth_sessions.insert(),
            {"token_hash": _hash(token), "email": email, "role": role, "expires_at": _now() + timedelta(days=SESSION_DAYS)},
        )
    response.set_cookie(
        COOKIE_NAME, token, max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax", path="/"
    )


def end_session(request: Request, response: Response) -> None:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        with _engine.begin() as conn:
            conn.execute(delete(auth_sessions).where(auth_sessions.c.token_hash == _hash(token)))
    response.delete_cookie(COOKIE_NAME, path="/")


def current_caller(request: Request) -> Caller:
    """FastAPI dependency: who is calling. 401 if not signed in or the session expired."""
    token = request.cookies.get(COOKIE_NAME)
    if token:
        with _engine.connect() as conn:
            row = conn.execute(select(auth_sessions).where(auth_sessions.c.token_hash == _hash(token))).mappings().first()
        if row and row["expires_at"] > _now():
            return Caller(email=row["email"], role=row["role"])
    raise HTTPException(status_code=401, detail="Please sign in again.")


def readable_by(caller: Caller, student_id: Optional[str]) -> str:
    """The student whose data may be read: yourself, or anyone if you are a teacher."""
    if not student_id:
        if caller.is_teacher:
            raise HTTPException(status_code=400, detail="Choose a student first.")
        return caller.email
    student_id = student_id.strip().lower()
    if caller.is_teacher or student_id == caller.email:
        return student_id
    raise HTTPException(status_code=403, detail="You can only see your own progress.")


def own_account(caller: Caller, student_id: Optional[str]) -> str:
    """For actions that change a student's record: only the signed-in student, for themselves."""
    if student_id and student_id.strip().lower() != caller.email:
        raise HTTPException(status_code=403, detail="You can only work on your own account.")
    return caller.email


def require_teacher(caller: Caller) -> Caller:
    if not caller.is_teacher:
        raise HTTPException(status_code=403, detail="This page is for teachers.")
    return caller
