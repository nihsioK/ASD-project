from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_by_token(db: Session, token: str) -> User | None:
    return db.scalar(select(User).where(User.token == token))


def create(db: Session, email: str, password_hash: str) -> User:
    user = User(email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_token(db: Session, user: User, token: str) -> None:
    user.token = token
    db.commit()


def clear_token(db: Session, user: User) -> None:
    user.token = None
    db.commit()
