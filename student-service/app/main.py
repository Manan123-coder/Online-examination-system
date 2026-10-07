import os

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import auth, models
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)  # creates the tables if they do not exist

# Swagger / ReDoc / OpenAPI are disabled on purpose.
app = FastAPI(title="Student Service", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)  # adds /metrics for Prometheus

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


# ---------- Input validation (Pydantic rejects bad input automatically) ----------
class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=120)
    password: str = Field(min_length=6, max_length=72)


class LoginIn(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN)
    password: str = Field(min_length=1)


class UpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    password: str | None = Field(default=None, min_length=6, max_length=72)


def student_json(s: models.Student):
    return {"id": s.id, "name": s.name, "email": s.email}  # password is never returned


# ---------- JWT protection ----------
bearer = HTTPBearer()


def current_student_id(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    """Reads 'Authorization: Bearer <token>' and returns the student id inside the token."""
    try:
        return auth.decode_token(creds.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_own_student(student_id: int, me: int, db: Session) -> models.Student:
    if student_id != me:
        raise HTTPException(status_code=403, detail="You can only access your own account")
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"service": "student-service", "status": "running", "version": os.getenv("APP_VERSION", "dev")}


@app.post("/students/register", status_code=201)  # Create
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(models.Student).filter_by(email=data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    student = models.Student(name=data.name, email=data.email, password=auth.hash_password(data.password))
    db.add(student)
    db.commit()
    db.refresh(student)
    return student_json(student)


@app.post("/students/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter_by(email=data.email).first()
    if not student or not auth.verify_password(data.password, student.password):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return {"access_token": auth.create_token(student.id), "token_type": "bearer",
            "student_id": student.id, "name": student.name}


@app.get("/students/{student_id}")  # Read (protected)
def get_student(student_id: int, me: int = Depends(current_student_id), db: Session = Depends(get_db)):
    return student_json(get_own_student(student_id, me, db))


@app.put("/students/{student_id}")  # Update (protected)
def update_student(student_id: int, data: UpdateIn, me: int = Depends(current_student_id),
                   db: Session = Depends(get_db)):
    student = get_own_student(student_id, me, db)
    if data.name:
        student.name = data.name
    if data.password:
        student.password = auth.hash_password(data.password)
    db.commit()
    return student_json(student)


@app.delete("/students/{student_id}")  # Delete (protected)
def delete_student(student_id: int, me: int = Depends(current_student_id), db: Session = Depends(get_db)):
    student = get_own_student(student_id, me, db)
    db.delete(student)
    db.commit()
    return {"message": "Student deleted"}
