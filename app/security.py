import hashlib
import hmac
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.repositories import user as user_repo

ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$")
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), ITERATIONS
    )
    return hmac.compare_digest(candidate.hex(), digest)


def new_token() -> str:
    # ponytail: one opaque token per user without expiry, use JWT with expiry for real deployments
    return secrets.token_urlsafe(32)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = user_repo.get_by_token(db, credentials.credentials)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return user
