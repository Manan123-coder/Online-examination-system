import os

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import auth, models
from .database import Base, engine, get_db
from .question_client import fetch_correct_answers
from .scoring import calculate_score

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Result Service", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)

bearer = HTTPBearer()


class SubmitIn(BaseModel):
    exam_id: int
    answers: dict[str, str]  # {"question_id": "A"}


def current_student_id(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    try:
        return auth.decode_token(creds.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def result_json(r: models.Result):
    return {"id": r.id, "student_id": r.student_id, "exam_id": r.exam_id, "score": r.score,
            "total_questions": r.total_questions, "percentage": r.percentage}


@app.get("/health")
def health():
    return {"service": "result-service", "status": "running", "version": os.getenv("APP_VERSION", "dev")}


@app.post("/results/submit", status_code=201)
def submit_exam(data: SubmitIn, student_id: int = Depends(current_student_id),
                db: Session = Depends(get_db)):
    # Step 1: ask Question Service for the correct answers (REST call)
    correct = fetch_correct_answers(data.exam_id)
    if not correct:
        raise HTTPException(status_code=400, detail="This exam has no questions")
    # Step 2: compare answers, calculate score and percentage
    score, total, percentage = calculate_score(correct, data.answers)
    # Step 3: save the result
    result = models.Result(student_id=student_id, exam_id=data.exam_id, score=score,
                           total_questions=total, percentage=percentage)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result_json(result)


@app.get("/results")  # result history of the logged-in student
def my_results(student_id: int = Depends(current_student_id), db: Session = Depends(get_db)):
    rows = db.query(models.Result).filter_by(student_id=student_id).order_by(models.Result.id.desc()).all()
    return [result_json(r) for r in rows]


@app.get("/results/{result_id}")
def get_result(result_id: int, student_id: int = Depends(current_student_id),
               db: Session = Depends(get_db)):
    result = db.get(models.Result, result_id)
    if not result or result.student_id != student_id:
        raise HTTPException(status_code=404, detail="Result not found")
    return result_json(result)
