from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.repositories import user as user_repo
from app.schemas.user import Token, UserCredentials, UserOut
from app.security import get_current_user, hash_password, new_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserCredentials, db: Annotated[Session, Depends(get_db)]) -> UserOut:
    if user_repo.get_by_email(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    return user_repo.create(db, data.email, hash_password(data.password))


@router.post("/login")
def login(data: UserCredentials, db: Annotated[Session, Depends(get_db)]) -> Token:
    user = user_repo.get_by_email(db, data.email)
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    token = new_token()
    user_repo.set_token(db, user, token)
    return Token(access_token=token)


@router.get("/me")
def me(user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return user
