import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models
from .database import Base, SessionLocal, engine, get_db
from .seed import seed_sample_exam

Base.metadata.create_all(bind=engine)
with SessionLocal() as _db:
    seed_sample_exam(_db)

app = FastAPI(title="Question Service", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)


class ExamIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    duration: int = Field(ge=1, le=300)  # minutes


class QuestionIn(BaseModel):
    exam_id: int
    question: str = Field(min_length=1, max_length=500)
    option_a: str = Field(min_length=1, max_length=200)
    option_b: str = Field(min_length=1, max_length=200)
    option_c: str = Field(min_length=1, max_length=200)
    option_d: str = Field(min_length=1, max_length=200)
    correct_answer: str = Field(pattern="^[ABCD]$")  # only A, B, C or D


def exam_json(exam, db):
    count = db.query(models.Question).filter_by(exam_id=exam.id).count()
    return {"id": exam.id, "title": exam.title, "duration": exam.duration, "question_count": count}


def question_for_student(q):
    """IMPORTANT: correct_answer is deliberately NOT included here."""
    return {"id": q.id, "exam_id": q.exam_id, "question": q.question,
            "option_a": q.option_a, "option_b": q.option_b,
            "option_c": q.option_c, "option_d": q.option_d}


@app.get("/health")
def health():
    return {"service": "question-service", "status": "running", "version": os.getenv("APP_VERSION", "dev")}


# ---------- Exams ----------
@app.post("/exams", status_code=201)
def create_exam(data: ExamIn, db: Session = Depends(get_db)):
    exam = models.Exam(title=data.title, duration=data.duration)
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam_json(exam, db)


@app.get("/exams")
def list_exams(db: Session = Depends(get_db)):
    return [exam_json(e, db) for e in db.query(models.Exam).all()]


@app.get("/exams/{exam_id}")
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.get(models.Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam_json(exam, db)


# ---------- Questions ----------
@app.post("/questions", status_code=201)
def create_question(data: QuestionIn, db: Session = Depends(get_db)):
    if not db.get(models.Exam, data.exam_id):
        raise HTTPException(status_code=404, detail="Exam not found")
    q = models.Question(**data.model_dump())
    db.add(q)
    db.commit()
    db.refresh(q)
    return question_for_student(q)


@app.get("/questions/{exam_id}")
def list_questions(exam_id: int, db: Session = Depends(get_db)):
    questions = db.query(models.Question).filter_by(exam_id=exam_id).all()
    return [question_for_student(q) for q in questions]  # no correct answers sent


@app.put("/questions/{question_id}")
def update_question(question_id: int, data: QuestionIn, db: Session = Depends(get_db)):
    q = db.get(models.Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    for key, value in data.model_dump().items():
        setattr(q, key, value)
    db.commit()
    return question_for_student(q)


@app.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    q = db.get(models.Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"message": "Question deleted"}


# ---------- Internal endpoint: used ONLY by Result Service (service-to-service REST call) ----------
# The nginx gateway blocks /api/question/internal/, so the browser can never reach it.
@app.get("/internal/answers/{exam_id}")
def internal_answers(exam_id: int, db: Session = Depends(get_db)):
    questions = db.query(models.Question).filter_by(exam_id=exam_id).all()
    return {str(q.id): q.correct_answer for q in questions}
