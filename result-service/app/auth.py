# The Result Service only CHECKS tokens (it never creates them). It uses the same SECRET_KEY
# as the Student Service, so it can verify a token without calling the Student Service.
import os

import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"


def decode_token(token: str) -> int:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])
