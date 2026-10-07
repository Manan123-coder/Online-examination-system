# Password hashing + JWT helpers. Kept in one small file so it is easy to explain.
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# The secret key signs the tokens. It comes from an environment variable, NOT from GitHub.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_MINUTES = 60


def hash_password(password: str) -> str:
    """bcrypt adds a random 'salt' and is deliberately slow, so passwords are hard to crack."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(student_id: int) -> str:
    """A JWT has 3 parts: header.payload.signature. 'sub' = who the token belongs to."""
    payload = {
        "sub": str(student_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> int:
    """Raises jwt.PyJWTError if the token is fake, changed or expired."""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])
