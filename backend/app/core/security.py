import base64
import hashlib
import secrets
import uuid


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt_b64, digest_b64 = hashed_password.split("$", 1)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
        return secrets.compare_digest(check, expected)
    except ValueError:
        return False


def create_access_token() -> str:
    return str(uuid.uuid4())


def create_reset_token() -> str:
    return secrets.token_urlsafe(32)
