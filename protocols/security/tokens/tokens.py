import secrets
import time
from dataclasses import dataclass


@dataclass
class SecurityToken:
    token: str
    scope: str
    expires_at: float


def generate_token(scope: str, ttl_seconds: int = 300) -> SecurityToken:
    token = secrets.token_urlsafe(32)
    return SecurityToken(
        token=token,
        scope=scope,
        expires_at=time.time() + ttl_seconds,
    )


def is_token_valid(token: SecurityToken) -> bool:
    return time.time() < token.expires_at