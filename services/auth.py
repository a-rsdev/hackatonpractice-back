import base64
import hashlib
import hmac
import json
import secrets
import time

from config import JWT_SECRET, JWT_TTL_SECONDS
from contracts.responses.auth import AuthResponse
from core.result import Result
from repositories.users import UserRepository

try:
    import bcrypt
except ImportError:
    bcrypt = None


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, nickname: str, password: str) -> Result[AuthResponse]:
        created = self.users.create(nickname, self._hash_password(password))
        if not created.is_success:
            return Result(error=created.error)
        user = created.value
        return Result.success(AuthResponse(token=self.create_token(user.id), user_id=user.id))

    def login(self, nickname: str, password: str) -> Result[AuthResponse]:
        found = self.users.get_by_nickname(nickname)
        if not found.is_success:
            return Result(error=found.error)
        user = found.value
        if user is None or not self._verify_password(password, user.password_hash):
            return Result.failure("invalid_credentials", 401)
        return Result.success(AuthResponse(token=self.create_token(user.id), user_id=user.id))

    def authenticate(self, token: str) -> Result[str]:
        try:
            header, payload, signature = token.split(".")
            expected = hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
            data = json.loads(_b64decode(payload))
            if not hmac.compare_digest(expected, _b64decode(signature)):
                return Result.failure("invalid_token", 401)
            if data.get("exp", 0) <= int(time.time()) or not data.get("sub"):
                return Result.failure("invalid_token", 401)
        except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
            return Result.failure("invalid_token", 401)
        found = self.users.get_by_id(data["sub"])
        if not found.is_success:
            return Result(error=found.error)
        if found.value is None:
            return Result.failure("invalid_token", 401)
        return Result.success(found.value.id)

    @staticmethod
    def _hash_password(password: str) -> str:
        raw = password.encode()
        if bcrypt:
            return bcrypt.hashpw(raw, bcrypt.gensalt()).decode()
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(raw, salt=salt, n=16384, r=8, p=1)
        return f"scrypt${_b64encode(salt)}${_b64encode(digest)}"

    @staticmethod
    def _verify_password(password: str, encoded: str) -> bool:
        if encoded.startswith("$2") and bcrypt:
            return bcrypt.checkpw(password.encode(), encoded.encode())
        try:
            scheme, salt, expected = encoded.split("$", 2)
            if scheme != "scrypt":
                return False
            actual = hashlib.scrypt(password.encode(), salt=_b64decode(salt), n=16384, r=8, p=1)
            return hmac.compare_digest(actual, _b64decode(expected))
        except (ValueError, TypeError):
            return False

    @staticmethod
    def create_token(user_id: str) -> str:
        now = int(time.time())
        header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
        payload = _b64encode(json.dumps(
            {"sub": user_id, "iat": now, "exp": now + JWT_TTL_SECONDS}, separators=(",", ":")
        ).encode())
        signature = hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        return f"{header}.{payload}.{_b64encode(signature)}"
