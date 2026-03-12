from datetime import datetime, timedelta, timezone
import smtplib
from email.message import EmailMessage
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_reset_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import (
    clear_reset_token,
    get_by_reset_token,
    get_by_username,
    update_password,
    update_reset_token,
)
import logging

from app.core.config import settings


def authenticate(db: Session, username: str, password: str) -> Tuple[Optional[User], str]:
    user = get_by_username(db, username)
    if not user:
        return None, "invalid_credentials"
    if not verify_password(password, user.hashed_password):
        return None, "invalid_credentials"
    if not user.is_active:
        return user, "inactive"
    return user, "ok"


def build_login_response(user: User) -> dict:
    permissions = [p for p in (user.permissions or "").split(",") if p]
    return {
        "access_token": create_access_token(),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "permissions": permissions,
            "is_active": user.is_active,
        },
    }


def request_password_reset(
    db: Session, username: str
) -> Tuple[Optional[User], Optional[str]]:
    user = get_by_username(db, username)
    if not user:
        return None, None
    if not user.email:
        return user, None

    token = create_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    update_reset_token(db, user, token, expires_at)
    return user, token


def send_reset_email(to_email: str, reset_link: str) -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        raise RuntimeError("SMTP configuration is missing.")

    msg = EmailMessage()
    msg["Subject"] = "NEU - Reset mật khẩu"
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg.set_content(
        "\n".join(
            [
                "Bạn đã yêu cầu đặt lại mật khẩu.",
                f"Liên kết đặt lại: {reset_link}",
                "Liên kết có hiệu lực trong 30 phút.",
                "Nếu bạn không yêu cầu, hãy bỏ qua email này.",
            ]
        )
    )

    try:
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(
                settings.smtp_host, settings.smtp_port, timeout=20
            ) as server:
                if settings.smtp_user:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            return

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except Exception:
        logger.exception("SMTP send failed")
        raise


def reset_password(db: Session, token: str, new_password: str) -> Tuple[Optional[User], str]:
    user = get_by_reset_token(db, token)
    if not user or not user.reset_token_expires_at:
        return None, "invalid"

    expires_at = user.reset_token_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        clear_reset_token(db, user)
        return None, "expired"

    update_password(db, user, hash_password(new_password))
    clear_reset_token(db, user)
    return user, "ok"
logger = logging.getLogger(__name__)
