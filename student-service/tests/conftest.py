import os

os.environ["DATABASE_URL"] = "sqlite:///./test_student.db"  # separate DB for tests

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)  # start every test with empty tables
    Base.metadata.create_all(bind=engine)
    return TestClient(app)
