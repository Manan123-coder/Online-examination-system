import os

os.environ["DATABASE_URL"] = "sqlite:///./test_result.db"

import jwt
import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


@pytest.fixture()
def auth_header():
    token = jwt.encode({"sub": "1"}, os.getenv("SECRET_KEY", "dev-secret-change-me"), algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}
