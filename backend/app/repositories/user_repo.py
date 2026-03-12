from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_by_reset_token(db: Session, token: str) -> Optional[User]:
    return db.query(User).filter(User.reset_token == token).first()


def update_reset_token(db: Session, user: User, token: str, expires_at):
    user.reset_token = token
    user.reset_token_expires_at = expires_at
    db.commit()
    db.refresh(user)
    return user


def clear_reset_token(db: Session, user: User):
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()
    db.refresh(user)
    return user


def update_password(db: Session, user: User, hashed_password: str):
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user


def _apply_search(query, search: Optional[str]):
    if search:
        like = f"%{search}%"
        query = query.filter(
            (User.username.ilike(like))
            | (User.full_name.ilike(like))
            | (User.email.ilike(like))
        )
    return query


def list_users(db: Session, search: Optional[str] = None, limit: int = 20, skip: int = 0):
    query = db.query(User)
    query = _apply_search(query, search)
    return query.order_by(User.id.asc()).offset(skip).limit(limit).all()


def count_users(db: Session, search: Optional[str] = None) -> int:
    query = db.query(User)
    query = _apply_search(query, search)
    return query.count()


def update_user(db: Session, user: User, data: dict):
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def create_user(
    db: Session,
    username: str,
    full_name: str,
    role: str,
    hashed_password: str,
    permissions: list[str],
    email: Optional[str] = None,
) -> User:
    user = User(
        username=username,
        full_name=full_name,
        role=role,
        hashed_password=hashed_password,
        permissions=",".join(permissions),
        email=email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
