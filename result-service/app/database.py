# Database setup. Each service has its OWN SQLite file (database-per-service).
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# DATABASE_URL can be changed with an environment variable (Docker/Kubernetes use this).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./result.db")

# check_same_thread=False is needed for SQLite when used with FastAPI.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def get_db():
    """Gives each request its own database session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
